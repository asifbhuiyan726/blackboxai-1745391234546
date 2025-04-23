"""
Test Profiler
============

Profile test execution for performance analysis.
"""

import cProfile
import functools
import io
import line_profiler
import memory_profiler
import os
import pstats
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, Set, Union

from django.db import connection, reset_queries
from django.test import TestCase

from .config import TEST_OUTPUT_DIR
from .logging import get_test_logger

logger = get_test_logger(__name__)

class TestProfiler:
    """Profile test execution and collect performance metrics."""
    
    def __init__(self, test_case: TestCase):
        self.test_case = test_case
        self.profiler = cProfile.Profile()
        self.line_profiler = line_profiler.LineProfiler()
        self.query_count = 0
        self.query_time = 0.0
        self.start_time = 0.0
        self.end_time = 0.0
        self.memory_usage = []

    def start(self):
        """Start profiling."""
        self.start_time = time.time()
        reset_queries()
        self.profiler.enable()
        self.line_profiler.enable()

    def stop(self):
        """Stop profiling."""
        self.line_profiler.disable()
        self.profiler.disable()
        self.end_time = time.time()
        self.query_count = len(connection.queries)
        self.query_time = sum(
            float(query.get('time', 0))
            for query in connection.queries
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get profiling statistics."""
        return {
            'duration': self.end_time - self.start_time,
            'query_count': self.query_count,
            'query_time': self.query_time,
            'memory_peak': max(self.memory_usage) if self.memory_usage else 0,
            'memory_average': (
                sum(self.memory_usage) / len(self.memory_usage)
                if self.memory_usage else 0
            ),
        }

    def print_stats(self):
        """Print profiling statistics."""
        stats = self.get_stats()
        
        print("\nTest Profile Results")
        print("===================")
        print(f"Test: {self.test_case.__class__.__name__}.{self.test_case._testMethodName}")
        print(f"Duration: {stats['duration']:.3f}s")
        print(f"Database Queries: {stats['query_count']}")
        print(f"Query Time: {stats['query_time']:.3f}s")
        print(f"Memory Peak: {stats['memory_peak']:.2f} MB")
        print(f"Memory Average: {stats['memory_average']:.2f} MB")
        
        # Print detailed profiling information
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
        ps.print_stats()
        print("\nDetailed Profile:")
        print(s.getvalue())

    def save_stats(self, filename: Optional[str] = None):
        """Save profiling statistics to a file."""
        if filename is None:
            filename = (
                f"{self.test_case.__class__.__name__}"
                f"_{self.test_case._testMethodName}"
                "_profile.txt"
            )
        
        output_path = TEST_OUTPUT_DIR / 'profiles' / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            stats = self.get_stats()
            
            f.write("Test Profile Results\n")
            f.write("===================\n")
            f.write(f"Test: {self.test_case.__class__.__name__}.{self.test_case._testMethodName}\n")
            f.write(f"Duration: {stats['duration']:.3f}s\n")
            f.write(f"Database Queries: {stats['query_count']}\n")
            f.write(f"Query Time: {stats['query_time']:.3f}s\n")
            f.write(f"Memory Peak: {stats['memory_peak']:.2f} MB\n")
            f.write(f"Memory Average: {stats['memory_average']:.2f} MB\n\n")
            
            # Write detailed profiling information
            s = io.StringIO()
            ps = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
            ps.print_stats()
            f.write("Detailed Profile:\n")
            f.write(s.getvalue())

class ProfiledTestCase(TestCase):
    """Base test case with profiling capabilities."""
    
    def setUp(self):
        super().setUp()
        self.profiler = TestProfiler(self)
        self.profiler.start()

    def tearDown(self):
        self.profiler.stop()
        self.profiler.save_stats()
        super().tearDown()

def profile_test(test_func: Callable) -> Callable:
    """Decorator to profile a test method."""
    @functools.wraps(test_func)
    def wrapper(self, *args, **kwargs):
        profiler = TestProfiler(self)
        profiler.start()
        try:
            result = test_func(self, *args, **kwargs)
            return result
        finally:
            profiler.stop()
            profiler.save_stats()
    return wrapper

def profile_memory(test_func: Callable) -> Callable:
    """Decorator to profile memory usage of a test method."""
    @functools.wraps(test_func)
    def wrapper(self, *args, **kwargs):
        @memory_profiler.profile
        def profiled_func():
            return test_func(self, *args, **kwargs)
        return profiled_func()
    return wrapper

def profile_queries(test_func: Callable) -> Callable:
    """Decorator to profile database queries in a test method."""
    @functools.wraps(test_func)
    def wrapper(self, *args, **kwargs):
        reset_queries()
        result = test_func(self, *args, **kwargs)
        queries = connection.queries
        print(f"\nDatabase Queries ({len(queries)}):")
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. Time: {query['time']}s")
            print(f"   SQL: {query['sql']}")
        return result
    return wrapper

@contextmanager
def profile_block(name: str):
    """Context manager to profile a block of code."""
    profiler = cProfile.Profile()
    print(f"\nStarting profile block: {name}")
    profiler.enable()
    start_time = time.time()
    reset_queries()
    
    try:
        yield
    finally:
        end_time = time.time()
        profiler.disable()
        duration = end_time - start_time
        query_count = len(connection.queries)
        
        print(f"\nProfile block results: {name}")
        print(f"Duration: {duration:.3f}s")
        print(f"Queries: {query_count}")
        
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats()
        print(s.getvalue())

@contextmanager
def track_queries():
    """Context manager to track database queries."""
    reset_queries()
    try:
        yield
    finally:
        queries = connection.queries
        print(f"\nDatabase Queries ({len(queries)}):")
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. Time: {query['time']}s")
            print(f"   SQL: {query['sql']}")

@contextmanager
def track_time(name: str):
    """Context manager to track execution time."""
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n{name} took {duration:.3f}s")

def get_slow_tests(threshold: float = 1.0) -> List[str]:
    """Get a list of tests that took longer than the threshold."""
    slow_tests = []
    profile_dir = TEST_OUTPUT_DIR / 'profiles'
    
    if not profile_dir.exists():
        return slow_tests
    
    for profile_file in profile_dir.glob('*_profile.txt'):
        with open(profile_file) as f:
            for line in f:
                if line.startswith('Duration:'):
                    duration = float(line.split(':')[1].strip()[:-1])
                    if duration > threshold:
                        slow_tests.append(profile_file.stem[:-8])  # Remove '_profile'
                    break
    
    return sorted(slow_tests)

def analyze_test_performance(test_pattern: Optional[str] = None):
    """Analyze test performance metrics."""
    profile_dir = TEST_OUTPUT_DIR / 'profiles'
    
    if not profile_dir.exists():
        print("No profile data found.")
        return
    
    total_duration = 0
    total_queries = 0
    test_count = 0
    slowest_tests = []
    
    for profile_file in profile_dir.glob('*_profile.txt'):
        if test_pattern and test_pattern not in profile_file.name:
            continue
            
        with open(profile_file) as f:
            test_name = profile_file.stem[:-8]  # Remove '_profile'
            duration = 0
            queries = 0
            
            for line in f:
                if line.startswith('Duration:'):
                    duration = float(line.split(':')[1].strip()[:-1])
                    total_duration += duration
                elif line.startswith('Database Queries:'):
                    queries = int(line.split(':')[1].strip())
                    total_queries += queries
            
            test_count += 1
            slowest_tests.append((test_name, duration, queries))
    
    if test_count == 0:
        print("No matching tests found.")
        return
    
    print("\nTest Performance Analysis")
    print("========================")
    print(f"Total Tests: {test_count}")
    print(f"Total Duration: {total_duration:.3f}s")
    print(f"Average Duration: {total_duration/test_count:.3f}s")
    print(f"Total Queries: {total_queries}")
    print(f"Average Queries: {total_queries/test_count:.1f}")
    
    print("\nSlowest Tests:")
    for test_name, duration, queries in sorted(
        slowest_tests,
        key=lambda x: x[1],
        reverse=True
    )[:5]:
        print(f"  {test_name}:")
        print(f"    Duration: {duration:.3f}s")
        print(f"    Queries: {queries}")

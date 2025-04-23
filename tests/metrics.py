"""
Test Metrics Collection and Reporting
===================================

Collect and report various metrics about test execution.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

from .config import TEST_REPORT_DIR
from .logging import get_test_logger

logger = get_test_logger(__name__)

@dataclass
class TestMetric:
    """Base class for test metrics."""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)

@dataclass
class TestDuration(TestMetric):
    """Metric for test execution duration."""
    pass

@dataclass
class TestMemoryUsage(TestMetric):
    """Metric for test memory usage."""
    peak_usage: float = 0.0

@dataclass
class DatabaseMetrics(TestMetric):
    """Metrics for database operations."""
    query_count: int = 0
    total_time: float = 0.0
    queries: List[str] = field(default_factory=list)

@dataclass
class CacheMetrics(TestMetric):
    """Metrics for cache operations."""
    hits: int = 0
    misses: int = 0
    total_operations: int = 0

@dataclass
class TestResult:
    """Container for test results and metrics."""
    test_name: str
    success: bool
    duration: float
    start_time: datetime
    end_time: datetime
    error: Optional[Exception] = None
    skipped: bool = False
    skip_reason: Optional[str] = None
    metrics: Dict[str, TestMetric] = field(default_factory=dict)

class MetricsCollector:
    """Collect and store test metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, List[TestMetric]] = defaultdict(list)
        self.results: Dict[str, TestResult] = {}
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.current_test: Optional[str] = None
        self._test_timers: Dict[str, float] = {}

    def start_test(self, test_name: str):
        """Start timing a test."""
        self.current_test = test_name
        self._test_timers[test_name] = time.time()

    def end_test(
        self,
        test_name: str,
        success: bool,
        error: Optional[Exception] = None,
        skipped: bool = False,
        skip_reason: Optional[str] = None
    ):
        """End timing a test and record results."""
        if test_name not in self._test_timers:
            logger.warning(f"No start time found for test {test_name}")
            return

        end_time = time.time()
        duration = end_time - self._test_timers.pop(test_name)
        
        self.results[test_name] = TestResult(
            test_name=test_name,
            success=success,
            duration=duration,
            start_time=datetime.fromtimestamp(end_time - duration),
            end_time=datetime.fromtimestamp(end_time),
            error=error,
            skipped=skipped,
            skip_reason=skip_reason
        )

        self.add_metric(
            TestDuration(
                name=f"{test_name}_duration",
                value=duration
            )
        )

    def add_metric(self, metric: TestMetric):
        """Add a metric to the collection."""
        self.metrics[metric.name].append(metric)

    def get_metrics(self, metric_type: Optional[type] = None) -> List[TestMetric]:
        """Get all metrics of a specific type."""
        if metric_type is None:
            return [m for metrics in self.metrics.values() for m in metrics]
        return [
            m for metrics in self.metrics.values()
            for m in metrics
            if isinstance(m, metric_type)
        ]

    def get_test_result(self, test_name: str) -> Optional[TestResult]:
        """Get the result for a specific test."""
        return self.results.get(test_name)

    def get_summary(self) -> Dict[str, any]:
        """Get a summary of test results and metrics."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r.success)
        failed_tests = sum(1 for r in self.results.values() if not r.success and not r.skipped)
        skipped_tests = sum(1 for r in self.results.values() if r.skipped)
        
        durations = self.get_metrics(TestDuration)
        total_duration = sum(m.value for m in durations)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'total_duration': total_duration,
            'average_duration': avg_duration,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }

    def generate_report(self) -> str:
        """Generate a detailed report of test results and metrics."""
        summary = self.get_summary()
        
        report = [
            "Test Execution Report",
            "===================\n",
            f"Run at: {self.start_time}",
            f"Duration: {timedelta(seconds=int(summary['total_duration']))}",
            f"\nResults Summary:",
            f"  Total Tests: {summary['total_tests']}",
            f"  Passed: {summary['passed_tests']}",
            f"  Failed: {summary['failed_tests']}",
            f"  Skipped: {summary['skipped_tests']}",
            f"  Success Rate: {summary['success_rate']:.1f}%\n",
            "Detailed Results:",
            "----------------"
        ]

        # Add detailed test results
        for test_name, result in sorted(self.results.items()):
            status = "PASSED" if result.success else "SKIPPED" if result.skipped else "FAILED"
            report.append(
                f"\n{test_name}:"
                f"\n  Status: {status}"
                f"\n  Duration: {result.duration:.3f}s"
            )
            if result.error:
                report.append(f"  Error: {str(result.error)}")
            if result.skip_reason:
                report.append(f"  Skip Reason: {result.skip_reason}")

        # Add metrics summary
        report.extend([
            "\nMetrics Summary:",
            "--------------"
        ])

        for metric_name, metrics in self.metrics.items():
            if metrics:
                avg_value = sum(m.value for m in metrics) / len(metrics)
                report.append(
                    f"\n{metric_name}:"
                    f"\n  Count: {len(metrics)}"
                    f"\n  Average: {avg_value:.3f}"
                )

        return "\n".join(report)

    def save_report(self, filename: Optional[str] = None):
        """Save the report to a file."""
        if filename is None:
            filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        report_path = TEST_REPORT_DIR / filename
        report_content = self.generate_report()
        
        report_path.write_text(report_content)
        logger.info(f"Test report saved to {report_path}")

class MetricsContext:
    """Context manager for collecting metrics during a test."""
    
    def __init__(
        self,
        collector: MetricsCollector,
        test_name: str
    ):
        self.collector = collector
        self.test_name = test_name
        self.start_time: Optional[float] = None

    def __enter__(self):
        """Start collecting metrics."""
        self.start_time = time.time()
        self.collector.start_test(self.test_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop collecting metrics and record results."""
        success = exc_type is None
        self.collector.end_test(
            self.test_name,
            success=success,
            error=exc_val
        )

# Global metrics collector instance
collector = MetricsCollector()

def collect_metrics(test_name: str):
    """Decorator to collect metrics for a test."""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            with MetricsContext(collector, test_name):
                return test_func(*args, **kwargs)
        return wrapper
    return decorator

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return collector

def reset_metrics():
    """Reset the global metrics collector."""
    global collector
    collector = MetricsCollector()

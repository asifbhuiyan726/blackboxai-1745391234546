import os
import sys
import time
from typing import List, Optional, Set, Type

from django.conf import settings
from django.test.runner import DiscoverRunner
from django.test.utils import get_runner
from django.utils.termcolors import colorize

class BreakSphereTestRunner(DiscoverRunner):
    """Custom test runner for BreakSphere project."""

    def __init__(self, *args, **kwargs):
        self.slow_test_threshold = float(
            os.getenv('SLOW_TEST_THRESHOLD', 0.5)
        )
        self.slow_tests = []
        self.timings = {}
        self.failed_tests = set()
        super().__init__(*args, **kwargs)

    def run_suite(self, suite, **kwargs):
        """Run the test suite with timing."""
        start_time = time.time()
        result = super().run_suite(suite, **kwargs)
        total_time = time.time() - start_time
        
        if self.slow_tests:
            self.report_slow_tests()
        
        if self.verbosity > 0:
            self.report_timing(total_time)
        
        return result

    def run_tests(self, test_labels: List[str], **kwargs) -> int:
        """
        Run the test suite with setup and teardown.
        """
        self.setup_test_environment()
        start_time = time.time()
        
        try:
            result = super().run_tests(test_labels, **kwargs)
        finally:
            self.teardown_test_environment()
            
        total_time = time.time() - start_time
        
        if self.verbosity > 0:
            self.report_summary(result, total_time)
        
        return result

    def run_test(self, test, **kwargs):
        """Run a single test with timing."""
        start_time = time.time()
        result = super().run_test(test, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        self.timings[test] = duration
        
        if duration > self.slow_test_threshold:
            self.slow_tests.append((test, duration))
        
        if not result.wasSuccessful():
            self.failed_tests.add(test)
        
        return result

    def setup_test_environment(self, **kwargs):
        """Set up the test environment."""
        super().setup_test_environment(**kwargs)
        
        # Configure test settings
        settings.DEBUG = False
        settings.TESTING = True
        
        # Configure test database
        settings.DATABASES['default']['ATOMIC_REQUESTS'] = True
        
        # Configure test cache
        settings.CACHES['default']['BACKEND'] = (
            'django.core.cache.backends.locmem.LocMemCache'
        )
        
        # Configure test email backend
        settings.EMAIL_BACKEND = (
            'django.core.mail.backends.locmem.EmailBackend'
        )
        
        # Configure test file storage
        settings.DEFAULT_FILE_STORAGE = (
            'django.core.files.storage.InMemoryStorage'
        )
        
        # Configure test Celery
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.CELERY_TASK_EAGER_PROPAGATES = True
        
        # Configure test channels
        settings.CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels.layers.InMemoryChannelLayer',
            },
        }

    def teardown_test_environment(self, **kwargs):
        """Clean up the test environment."""
        # Clear test files
        if hasattr(settings, 'MEDIA_ROOT'):
            self.clean_test_files()
        
        super().teardown_test_environment(**kwargs)

    def clean_test_files(self):
        """Clean up test files."""
        import shutil
        try:
            shutil.rmtree(settings.MEDIA_ROOT)
        except OSError:
            pass

    def report_slow_tests(self):
        """Report slow tests."""
        print("\nSlow Tests (>{:.1f}s):".format(self.slow_test_threshold))
        for test, duration in sorted(
            self.slow_tests,
            key=lambda x: x[1],
            reverse=True
        ):
            print(
                colorize(
                    f"  {test}: {duration:.3f}s",
                    fg='yellow'
                )
            )

    def report_timing(self, total_time: float):
        """Report test timing statistics."""
        if not self.timings:
            return
        
        print("\nTiming Report:")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Average time: {sum(self.timings.values())/len(self.timings):.3f}s")
        print(f"  Median time: {sorted(self.timings.values())[len(self.timings)//2]:.3f}s")
        print(f"  Fastest test: {min(self.timings.values()):.3f}s")
        print(f"  Slowest test: {max(self.timings.values()):.3f}s")

    def report_summary(self, result: int, total_time: float):
        """Report test suite summary."""
        print("\nTest Suite Summary:")
        print(f"  Run time: {total_time:.3f}s")
        print(f"  Tests run: {self.test_count}")
        print(f"  Failures: {len(self.failed_tests)}")
        print(f"  Errors: {len(result.errors)}")
        print(f"  Skipped: {len(result.skipped)}")
        
        if self.failed_tests:
            print("\nFailed Tests:")
            for test in self.failed_tests:
                print(
                    colorize(
                        f"  {test}",
                        fg='red'
                    )
                )

    @property
    def test_count(self) -> int:
        """Get the total number of tests run."""
        return len(self.timings)

class ParallelTestRunner(BreakSphereTestRunner):
    """Test runner that runs tests in parallel."""

    def __init__(self, *args, **kwargs):
        self.parallel_jobs = int(
            os.getenv('TEST_PARALLEL_JOBS', os.cpu_count() or 1)
        )
        super().__init__(*args, **kwargs)

    def run_suite(self, suite, **kwargs):
        """Run the test suite in parallel."""
        from concurrent.futures import ThreadPoolExecutor
        
        with ThreadPoolExecutor(max_workers=self.parallel_jobs) as executor:
            futures = []
            for test in suite:
                futures.append(
                    executor.submit(self.run_test, test)
                )
            
            results = [f.result() for f in futures]
        
        return self.combine_results(results)

    def combine_results(self, results: List) -> object:
        """Combine multiple test results."""
        from unittest.result import TestResult
        
        combined = TestResult()
        for result in results:
            combined.failures.extend(result.failures)
            combined.errors.extend(result.errors)
            combined.skipped.extend(result.skipped)
            combined.testsRun += result.testsRun
        
        return combined

class FailFastTestRunner(BreakSphereTestRunner):
    """Test runner that stops on first failure."""

    def __init__(self, *args, **kwargs):
        kwargs['failfast'] = True
        super().__init__(*args, **kwargs)

class RerunFailedTestRunner(BreakSphereTestRunner):
    """Test runner that reruns failed tests."""

    def __init__(self, *args, **kwargs):
        self.rerun_count = int(os.getenv('TEST_RERUN_COUNT', 3))
        self.rerun_delay = float(os.getenv('TEST_RERUN_DELAY', 1.0))
        super().__init__(*args, **kwargs)

    def run_test(self, test, **kwargs):
        """Run a test with retries on failure."""
        for attempt in range(self.rerun_count):
            result = super().run_test(test, **kwargs)
            if result.wasSuccessful():
                return result
            
            if attempt < self.rerun_count - 1:
                print(
                    colorize(
                        f"\nRetrying {test} (attempt {attempt + 2}/{self.rerun_count})",
                        fg='yellow'
                    )
                )
                time.sleep(self.rerun_delay)
        
        return result

class RandomOrderTestRunner(BreakSphereTestRunner):
    """Test runner that runs tests in random order."""

    def __init__(self, *args, **kwargs):
        self.seed = os.getenv('TEST_RANDOM_SEED')
        if self.seed:
            self.seed = int(self.seed)
        super().__init__(*args, **kwargs)

    def run_suite(self, suite, **kwargs):
        """Run the test suite in random order."""
        import random
        
        if self.seed:
            random.seed(self.seed)
        
        tests = list(suite)
        random.shuffle(tests)
        
        if self.verbosity > 1:
            print(f"\nRandom seed: {self.seed or 'None'}")
        
        suite._tests = tests
        return super().run_suite(suite, **kwargs)

def get_test_runner_class() -> Type[DiscoverRunner]:
    """Get the appropriate test runner class."""
    runner_name = os.getenv('TEST_RUNNER', 'default')
    runners = {
        'default': BreakSphereTestRunner,
        'parallel': ParallelTestRunner,
        'failfast': FailFastTestRunner,
        'rerun': RerunFailedTestRunner,
        'random': RandomOrderTestRunner,
    }
    return runners.get(runner_name, BreakSphereTestRunner)

def run_tests(
    test_labels: Optional[List[str]] = None,
    **kwargs
) -> int:
    """Run the test suite."""
    if test_labels is None:
        test_labels = []
    
    runner_class = get_test_runner_class()
    runner = runner_class(**kwargs)
    
    return runner.run_tests(test_labels)

if __name__ == '__main__':
    sys.exit(run_tests(sys.argv[1:]))

import functools
import os
import time
from typing import Any, Callable, Optional, Type, Union
from unittest.mock import patch

from django.conf import settings
from django.core.cache import cache
from django.db import connection, reset_queries
from django.test import override_settings, tag
from django.utils import timezone

def slow_test(test_func: Callable) -> Callable:
    """
    Mark a test as slow-running.
    Usage: @slow_test
    """
    return tag('slow')(test_func)

def quick_test(test_func: Callable) -> Callable:
    """
    Mark a test as quick-running.
    Usage: @quick_test
    """
    return tag('quick')(test_func)

def integration_test(test_func: Callable) -> Callable:
    """
    Mark a test as an integration test.
    Usage: @integration_test
    """
    return tag('integration')(test_func)

def api_test(test_func: Callable) -> Callable:
    """
    Mark a test as an API test.
    Usage: @api_test
    """
    return tag('api')(test_func)

def websocket_test(test_func: Callable) -> Callable:
    """
    Mark a test as a WebSocket test.
    Usage: @websocket_test
    """
    return tag('websocket')(test_func)

def skip_in_ci(test_func: Callable) -> Callable:
    """
    Skip a test when running in CI environment.
    Usage: @skip_in_ci
    """
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        if os.environ.get('CI'):
            from unittest import skip
            return skip('Test skipped in CI environment')(test_func)(*args, **kwargs)
        return test_func(*args, **kwargs)
    return wrapper

def requires_redis(test_func: Callable) -> Callable:
    """
    Skip a test if Redis is not available.
    Usage: @requires_redis
    """
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        try:
            import redis
            client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0
            )
            client.ping()
        except (ImportError, redis.ConnectionError):
            from unittest import skip
            return skip('Redis is not available')(test_func)(*args, **kwargs)
        return test_func(*args, **kwargs)
    return wrapper

def requires_celery(test_func: Callable) -> Callable:
    """
    Skip a test if Celery is not available.
    Usage: @requires_celery
    """
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        try:
            from celery import current_app
            current_app.connection().ensure_connection()
        except Exception:
            from unittest import skip
            return skip('Celery is not available')(test_func)(*args, **kwargs)
        return test_func(*args, **kwargs)
    return wrapper

def requires_channels(test_func: Callable) -> Callable:
    """
    Skip a test if Channels is not available.
    Usage: @requires_channels
    """
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        try:
            import channels
            from channels.testing import WebsocketCommunicator
        except ImportError:
            from unittest import skip
            return skip('Channels is not available')(test_func)(*args, **kwargs)
        return test_func(*args, **kwargs)
    return wrapper

def timer(test_func: Callable) -> Callable:
    """
    Time a test's execution.
    Usage: @timer
    """
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = test_func(*args, **kwargs)
        end_time = time.time()
        print(f"\n{test_func.__name__} took {end_time - start_time:.3f} seconds")
        return result
    return wrapper

def count_queries(test_func: Callable) -> Callable:
    """
    Count database queries during a test.
    Usage: @count_queries
    """
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        reset_queries()
        result = test_func(*args, **kwargs)
        query_count = len(connection.queries)
        print(f"\n{test_func.__name__} made {query_count} queries")
        return result
    return wrapper

def with_cache(test_func: Callable) -> Callable:
    """
    Clear cache before and after a test.
    Usage: @with_cache
    """
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        cache.clear()
        try:
            return test_func(*args, **kwargs)
        finally:
            cache.clear()
    return wrapper

def freeze_time(timestamp: Union[str, timezone.datetime]) -> Callable:
    """
    Freeze time during a test.
    Usage: @freeze_time('2024-01-01 12:00:00')
    """
    def decorator(test_func: Callable) -> Callable:
        @functools.wraps(test_func)
        def wrapper(*args, **kwargs):
            with patch('django.utils.timezone.now') as mock_now:
                if isinstance(timestamp, str):
                    mock_now.return_value = timezone.datetime.strptime(
                        timestamp,
                        '%Y-%m-%d %H:%M:%S'
                    ).replace(tzinfo=timezone.utc)
                else:
                    mock_now.return_value = timestamp
                return test_func(*args, **kwargs)
        return wrapper
    return decorator

def with_permissions(*permissions: str) -> Callable:
    """
    Add permissions to test user.
    Usage: @with_permissions('add_user', 'change_user')
    """
    def decorator(test_func: Callable) -> Callable:
        @functools.wraps(test_func)
        def wrapper(self, *args, **kwargs):
            from django.contrib.auth.models import Permission
            from django.contrib.contenttypes.models import ContentType
            
            user = getattr(self, 'user', None)
            if user:
                for permission in permissions:
                    app_label, codename = permission.split('.')
                    content_type = ContentType.objects.get(app_label=app_label)
                    permission = Permission.objects.get(
                        content_type=content_type,
                        codename=codename
                    )
                    user.user_permissions.add(permission)
            return test_func(self, *args, **kwargs)
        return wrapper
    return decorator

def with_media_root(test_func: Callable) -> Callable:
    """
    Use a temporary media root during a test.
    Usage: @with_media_root
    """
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        with override_settings(MEDIA_ROOT=temp_dir):
            try:
                return test_func(*args, **kwargs)
            finally:
                shutil.rmtree(temp_dir)
    return wrapper

def retry_on_failure(max_attempts: int = 3, delay: float = 1.0) -> Callable:
    """
    Retry a test on failure.
    Usage: @retry_on_failure(max_attempts=3, delay=1.0)
    """
    def decorator(test_func: Callable) -> Callable:
        @functools.wraps(test_func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return test_func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"\nRetrying {test_func.__name__} after failure: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

def expected_failure(exception: Type[Exception]) -> Callable:
    """
    Mark a test as expected to fail with a specific exception.
    Usage: @expected_failure(ValueError)
    """
    def decorator(test_func: Callable) -> Callable:
        @functools.wraps(test_func)
        def wrapper(*args, **kwargs):
            try:
                test_func(*args, **kwargs)
            except exception:
                pass  # Expected failure
            else:
                raise AssertionError(f"Expected {exception.__name__} was not raised")
        return wrapper
    return decorator

def benchmark(test_func: Callable) -> Callable:
    """
    Benchmark a test's performance.
    Usage: @benchmark
    """
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        import cProfile
        import pstats
        import io
        
        pr = cProfile.Profile()
        pr.enable()
        result = test_func(*args, **kwargs)
        pr.disable()
        
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        print(f"\nProfile for {test_func.__name__}:")
        print(s.getvalue())
        
        return result
    return wrapper

def require_debug(test_func: Callable) -> Callable:
    """
    Only run a test when DEBUG is True.
    Usage: @require_debug
    """
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        if not settings.DEBUG:
            from unittest import skip
            return skip('Test requires DEBUG=True')(test_func)(*args, **kwargs)
        return test_func(*args, **kwargs)
    return wrapper

def require_production(test_func: Callable) -> Callable:
    """
    Only run a test when DEBUG is False.
    Usage: @require_production
    """
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        if settings.DEBUG:
            from unittest import skip
            return skip('Test requires DEBUG=False')(test_func)(*args, **kwargs)
        return test_func(*args, **kwargs)
    return wrapper

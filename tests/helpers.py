import functools
import json
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, Type, Union
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection, reset_queries
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

User = get_user_model()

def with_test_database(func: Callable) -> Callable:
    """
    Decorator to run tests with a test database.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from django.test.utils import setup_databases, teardown_databases
        old_db_config = setup_databases(verbosity=0, interactive=False)
        try:
            return func(*args, **kwargs)
        finally:
            teardown_databases(old_db_config, verbosity=0)
    return wrapper

def with_test_cache(func: Callable) -> Callable:
    """
    Decorator to run tests with a test cache.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cache.clear()
        try:
            return func(*args, **kwargs)
        finally:
            cache.clear()
    return wrapper

def with_test_celery(func: Callable) -> Callable:
    """
    Decorator to run tests with Celery in eager mode.
    """
    @functools.wraps(func)
    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True
    )
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def with_test_websocket(func: Callable) -> Callable:
    """
    Decorator to run tests with WebSocket support.
    """
    @functools.wraps(func)
    @override_settings(
        CHANNEL_LAYERS={
            'default': {
                'BACKEND': 'channels.layers.InMemoryChannelLayer',
            },
        }
    )
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@contextmanager
def mock_now(dt: timezone.datetime):
    """
    Context manager to mock the current time.
    """
    with patch('django.utils.timezone.now') as mock_now:
        mock_now.return_value = dt
        yield mock_now

@contextmanager
def count_queries():
    """
    Context manager to count database queries.
    """
    reset_queries()
    yield
    query_count = len(connection.queries)
    print(f"Number of queries: {query_count}")
    for query in connection.queries:
        print(f"Query: {query['sql']}")

@contextmanager
def temporary_media_root():
    """
    Context manager to use a temporary media root.
    """
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp()
    with override_settings(MEDIA_ROOT=temp_dir):
        yield temp_dir
    shutil.rmtree(temp_dir)

def create_test_image(filename: str = 'test.jpg') -> str:
    """
    Create a test image file and return its path.
    """
    from PIL import Image
    import tempfile
    import os

    image = Image.new('RGB', (100, 100), 'white')
    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    image.save(tmp_file)
    tmp_file.close()
    
    return tmp_file.name

def create_test_file(content: bytes = b'test content') -> str:
    """
    Create a test file and return its path.
    """
    import tempfile
    
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_file.write(content)
    tmp_file.close()
    
    return tmp_file.name

def get_test_user(
    username: str = 'testuser',
    password: str = 'testpass123',
    **kwargs
) -> User:
    """
    Get or create a test user.
    """
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@example.com',
            **kwargs
        }
    )
    if created:
        user.set_password(password)
        user.save()
    return user

def get_auth_client(user: Optional[User] = None) -> APIClient:
    """
    Get an authenticated API client.
    """
    client = APIClient()
    if user is None:
        user = get_test_user()
    client.force_authenticate(user=user)
    return client

def json_response(data: Dict[str, Any], status: int = 200) -> str:
    """
    Create a JSON response string.
    """
    return json.dumps(data)

def setup_test_environment() -> None:
    """
    Set up the test environment.
    """
    # Configure test settings
    settings.DEBUG = False
    settings.TESTING = True
    
    # Clear caches
    cache.clear()
    
    # Reset database
    reset_queries()

def teardown_test_environment() -> None:
    """
    Tear down the test environment.
    """
    # Clear caches
    cache.clear()
    
    # Clear uploaded files
    import shutil
    shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

def create_test_data() -> Dict[str, Any]:
    """
    Create a set of test data.
    """
    from .factories import (
        UserFactory, RoomFactory, EventFactory,
        PostFactory, ChatMessageFactory
    )
    
    # Create users
    users = UserFactory.create_batch(3)
    
    # Create rooms
    rooms = RoomFactory.create_batch(2)
    
    # Create events
    events = EventFactory.create_batch(2)
    
    # Create posts
    posts = PostFactory.create_batch(3)
    
    # Create messages
    messages = ChatMessageFactory.create_batch(3)
    
    return {
        'users': users,
        'rooms': rooms,
        'events': events,
        'posts': posts,
        'messages': messages,
    }

def benchmark(func: Callable) -> Callable:
    """
    Decorator to benchmark function execution time.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

def skip_in_ci(func: Callable) -> Callable:
    """
    Decorator to skip tests in CI environment.
    """
    import os
    import unittest
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if os.environ.get('CI'):
            raise unittest.SkipTest('Test skipped in CI environment')
        return func(*args, **kwargs)
    return wrapper

def requires_redis(func: Callable) -> Callable:
    """
    Decorator to skip tests if Redis is not available.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import redis
        try:
            client = redis.Redis(host='localhost', port=6379, db=0)
            client.ping()
        except redis.ConnectionError:
            import unittest
            raise unittest.SkipTest('Redis is not available')
        return func(*args, **kwargs)
    return wrapper

def requires_celery(func: Callable) -> Callable:
    """
    Decorator to skip tests if Celery is not available.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from celery.app.base import Celery
        try:
            app = Celery()
            app.broker_url = 'memory://'
        except Exception:
            import unittest
            raise unittest.SkipTest('Celery is not available')
        return func(*args, **kwargs)
    return wrapper

def requires_websocket(func: Callable) -> Callable:
    """
    Decorator to skip tests if WebSocket support is not available.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            import channels
        except ImportError:
            import unittest
            raise unittest.SkipTest('WebSocket support is not available')
        return func(*args, **kwargs)
    return wrapper

def load_fixture(filename: str) -> Dict[str, Any]:
    """
    Load test fixture data from a JSON file.
    """
    import os
    fixture_path = os.path.join(settings.BASE_DIR, 'tests', 'fixtures', filename)
    with open(fixture_path, 'r') as f:
        return json.load(f)

def create_temp_file(content: str) -> str:
    """
    Create a temporary file with given content.
    """
    import tempfile
    import os
    
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(content)
    except Exception:
        os.unlink(path)
        raise
    return path

import json
import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type, Union
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.http import HttpResponse
from django.test import Client
from django.utils import timezone
from rest_framework.test import APIClient
from faker import Faker

User = get_user_model()
fake = Faker()

class TestDataMixin:
    """Mixin providing methods for generating test data."""
    
    @staticmethod
    def generate_string(length: int = 10) -> str:
        """Generate a random string of given length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def generate_email() -> str:
        """Generate a random email address."""
        return f"{TestDataMixin.generate_string()}@example.com"

    @staticmethod
    def generate_phone() -> str:
        """Generate a random phone number."""
        return f"+1{random.randint(1000000000, 9999999999)}"

    @staticmethod
    def generate_url() -> str:
        """Generate a random URL."""
        return f"https://example.com/{TestDataMixin.generate_string()}"

    @staticmethod
    def generate_datetime(
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        future: bool = True
    ) -> datetime:
        """Generate a datetime object relative to now."""
        delta = timedelta(days=days, hours=hours, minutes=minutes)
        return timezone.now() + delta if future else timezone.now() - delta

    @staticmethod
    def generate_file(
        name: Optional[str] = None,
        content: Optional[bytes] = None,
        content_type: str = 'text/plain'
    ) -> SimpleUploadedFile:
        """Generate a file for testing uploads."""
        if name is None:
            name = f"test_file_{TestDataMixin.generate_string()}.txt"
        if content is None:
            content = b"Test file content"
        return SimpleUploadedFile(name, content, content_type)

class MockRequestsMixin:
    """Mixin providing methods for mocking HTTP requests."""
    
    @staticmethod
    def mock_response(
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> MagicMock:
        """Create a mock response object."""
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        
        if json_data is not None:
            mock_resp.json.return_value = json_data
        if text is not None:
            mock_resp.text = text
        if headers is not None:
            mock_resp.headers = headers
            
        return mock_resp

    def mock_requests_get(self, *args, **kwargs):
        """Context manager for mocking requests.get."""
        return patch('requests.get', *args, **kwargs)

    def mock_requests_post(self, *args, **kwargs):
        """Context manager for mocking requests.post."""
        return patch('requests.post', *args, **kwargs)

class DatabaseTestMixin:
    """Mixin providing database-related test utilities."""
    
    @staticmethod
    def refresh_from_db(instance: models.Model) -> models.Model:
        """Refresh instance from database."""
        return type(instance).objects.get(pk=instance.pk)

    @staticmethod
    def get_or_none(model: Type[models.Model], **kwargs) -> Optional[models.Model]:
        """Get model instance or None if it doesn't exist."""
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            return None

    @staticmethod
    def count_queries(func):
        """Decorator to count database queries."""
        from django.db import connection, reset_queries
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            reset_queries()
            result = func(*args, **kwargs)
            query_count = len(connection.queries)
            print(f"Function {func.__name__} made {query_count} queries")
            return result
        return wrapper

class WebSocketTestMixin:
    """Mixin providing WebSocket test utilities."""
    
    async def connect_websocket(self, path: str) -> bool:
        """Connect to WebSocket and return connection status."""
        from channels.testing import WebsocketCommunicator
        from channels.routing import URLRouter
        from channels.auth import AuthMiddlewareStack
        
        application = URLRouter([
            # Add your WebSocket URL patterns here
        ])
        
        communicator = WebsocketCommunicator(
            AuthMiddlewareStack(application),
            path
        )
        connected, _ = await communicator.connect()
        return connected

    async def send_websocket_message(
        self,
        communicator,
        message_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Send a message through WebSocket."""
        await communicator.send_json_to({
            'type': message_type,
            'data': data
        })

    async def receive_websocket_message(
        self,
        communicator,
        timeout: float = 1
    ) -> Optional[Dict[str, Any]]:
        """Receive a message from WebSocket."""
        try:
            return await communicator.receive_json_from()
        except TimeoutError:
            return None

class APITestMixin:
    """Mixin providing API test utilities."""
    
    def api_client(self) -> APIClient:
        """Get an API test client."""
        return APIClient()

    def authenticated_client(self, user: User) -> APIClient:
        """Get an authenticated API client."""
        client = self.api_client()
        client.force_authenticate(user=user)
        return client

    def assert_response(
        self,
        response: HttpResponse,
        expected_status: int,
        expected_data: Optional[Union[Dict, List]] = None
    ) -> None:
        """Assert response status and data."""
        self.assertEqual(response.status_code, expected_status)
        if expected_data is not None:
            self.assertEqual(response.json(), expected_data)

class CeleryTestMixin:
    """Mixin providing Celery test utilities."""
    
    def setup_celery(self):
        """Configure Celery for testing."""
        import celery
        celery.current_app.conf.update(
            CELERY_ALWAYS_EAGER=True,
            CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        )

    @staticmethod
    def mock_task_delay(*args, **kwargs):
        """Mock task.delay() to execute synchronously."""
        from celery import current_app
        task = current_app.tasks[args[0]]
        return task.apply(args=args[1:], kwargs=kwargs)

class AuthTestMixin:
    """Mixin providing authentication test utilities."""
    
    def create_user(
        self,
        username: Optional[str] = None,
        password: str = 'testpass123',
        **kwargs
    ) -> User:
        """Create a test user."""
        if username is None:
            username = self.generate_string()
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password=password,
            **kwargs
        )

    def create_superuser(
        self,
        username: Optional[str] = None,
        password: str = 'testpass123',
        **kwargs
    ) -> User:
        """Create a test superuser."""
        if username is None:
            username = f"admin_{self.generate_string()}"
        return User.objects.create_superuser(
            username=username,
            email=f"{username}@example.com",
            password=password,
            **kwargs
        )

class PermissionTestMixin:
    """Mixin providing permission test utilities."""
    
    def assert_requires_login(self, url: str, method: str = 'get') -> None:
        """Assert that a URL requires authentication."""
        client = Client()
        response = getattr(client, method)(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def assert_requires_permission(
        self,
        url: str,
        permission: str,
        method: str = 'get'
    ) -> None:
        """Assert that a URL requires specific permission."""
        user = self.create_user()
        client = self.authenticated_client(user)
        response = getattr(client, method)(url)
        self.assertEqual(response.status_code, 403)

class CacheTestMixin:
    """Mixin providing cache test utilities."""
    
    def setup_cache(self):
        """Configure cache for testing."""
        from django.core.cache import cache
        cache.clear()

    def assert_cached(self, key: str, value: Any) -> None:
        """Assert that a value is cached."""
        from django.core.cache import cache
        self.assertEqual(cache.get(key), value)

    def assert_not_cached(self, key: str) -> None:
        """Assert that a value is not cached."""
        from django.core.cache import cache
        self.assertIsNone(cache.get(key))

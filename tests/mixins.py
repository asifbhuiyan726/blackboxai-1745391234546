from typing import Any, Dict, List, Optional, Type, Union
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from channels.testing import WebsocketCommunicator

from .assertions import CustomAssertionsMixin
from .constants import TEST_USER_DATA
from .helpers import (
    create_test_file,
    create_test_image,
    get_auth_client,
    get_test_user,
)

User = get_user_model()

class UserTestMixin:
    """Mixin for user-related test functionality."""
    
    def create_user(
        self,
        username: str = 'testuser',
        password: str = 'testpass123',
        **kwargs
    ) -> User:
        """Create a test user."""
        return get_test_user(username=username, password=password, **kwargs)

    def create_superuser(
        self,
        username: str = 'admin',
        password: str = 'adminpass123'
    ) -> User:
        """Create a test superuser."""
        return User.objects.create_superuser(
            username=username,
            email=f'{username}@example.com',
            password=password
        )

    def login_user(self, user: Optional[User] = None) -> None:
        """Log in a user."""
        if user is None:
            user = self.create_user()
        self.client.login(
            username=user.username,
            password=TEST_USER_DATA['password']
        )

class APITestMixin:
    """Mixin for API test functionality."""
    
    def get_auth_headers(self, user: Optional[User] = None) -> Dict[str, str]:
        """Get authentication headers."""
        if user is None:
            user = self.create_user()
        client = get_auth_client(user)
        auth = client.credentials()
        return {'HTTP_AUTHORIZATION': auth.get('Authorization')}

    def api_call(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        user: Optional[User] = None,
        format: str = 'json',
        **kwargs
    ) -> HttpResponse:
        """Make an API call."""
        client = get_auth_client(user)
        func = getattr(client, method.lower())
        return func(url, data=data, format=format, **kwargs)

class WebSocketTestMixin:
    """Mixin for WebSocket test functionality."""
    
    async def connect_websocket(
        self,
        path: str,
        user: Optional[User] = None
    ) -> WebsocketCommunicator:
        """Connect to a WebSocket."""
        application = self.get_application()
        communicator = WebsocketCommunicator(application, path)
        
        if user:
            communicator.scope['user'] = user
        
        connected, _ = await communicator.connect()
        assert connected
        return communicator

    async def send_websocket_message(
        self,
        communicator: WebsocketCommunicator,
        message: Dict[str, Any]
    ) -> None:
        """Send a WebSocket message."""
        await communicator.send_json_to(message)

    async def receive_websocket_message(
        self,
        communicator: WebsocketCommunicator,
        timeout: float = 1
    ) -> Optional[Dict[str, Any]]:
        """Receive a WebSocket message."""
        try:
            return await communicator.receive_json_from(timeout=timeout)
        except TimeoutError:
            return None

class CeleryTestMixin:
    """Mixin for Celery test functionality."""
    
    def setUp(self):
        super().setUp()
        self.celery_patches = []
        self._patch_celery()

    def tearDown(self):
        super().tearDown()
        for patch in self.celery_patches:
            patch.stop()

    def _patch_celery(self):
        """Patch Celery task execution."""
        from celery import current_app
        current_app.conf.CELERY_ALWAYS_EAGER = True
        current_app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

    def assert_task_called(
        self,
        task_name: str,
        *args,
        **kwargs
    ) -> None:
        """Assert that a Celery task was called."""
        mock = MagicMock()
        patch_path = f'breaksphere.tasks.{task_name}.delay'
        patcher = patch(patch_path, mock)
        self.celery_patches.append(patcher)
        patcher.start()
        
        # Call the task
        task = current_app.tasks[task_name]
        task.delay(*args, **kwargs)
        
        mock.assert_called_once_with(*args, **kwargs)

class CacheTestMixin:
    """Mixin for cache test functionality."""
    
    def setUp(self):
        super().setUp()
        from django.core.cache import cache
        self.cache = cache
        self.cache.clear()

    def tearDown(self):
        super().tearDown()
        self.cache.clear()

    def assert_cached(
        self,
        key: str,
        value: Any,
        timeout: Optional[int] = None
    ) -> None:
        """Assert that a value is cached."""
        cached_value = self.cache.get(key)
        self.assertEqual(cached_value, value)
        if timeout:
            import time
            time.sleep(timeout + 1)
            self.assertIsNone(self.cache.get(key))

class FileTestMixin:
    """Mixin for file-related test functionality."""
    
    def create_test_file(
        self,
        name: str = 'test.txt',
        content: bytes = b'test content'
    ) -> SimpleUploadedFile:
        """Create a test file."""
        return SimpleUploadedFile(name, content)

    def create_test_image(
        self,
        name: str = 'test.jpg',
        size: tuple = (100, 100)
    ) -> SimpleUploadedFile:
        """Create a test image."""
        path = create_test_image()
        with open(path, 'rb') as f:
            return SimpleUploadedFile(
                name,
                f.read(),
                content_type='image/jpeg'
            )

class DatabaseTestMixin:
    """Mixin for database test functionality."""
    
    def assert_object_exists(
        self,
        model_class: Type[models.Model],
        **kwargs
    ) -> None:
        """Assert that an object exists."""
        self.assertTrue(model_class.objects.filter(**kwargs).exists())

    def assert_object_count(
        self,
        model_class: Type[models.Model],
        expected_count: int,
        **kwargs
    ) -> None:
        """Assert the count of objects."""
        self.assertEqual(
            model_class.objects.filter(**kwargs).count(),
            expected_count
        )

    def refresh_from_db(
        self,
        instance: models.Model
    ) -> models.Model:
        """Refresh an instance from the database."""
        return type(instance).objects.get(pk=instance.pk)

class ViewTestMixin:
    """Mixin for view test functionality."""
    
    def get_url(
        self,
        viewname: str,
        *args,
        **kwargs
    ) -> str:
        """Get a URL by name."""
        return reverse(viewname, args=args, kwargs=kwargs)

    def get_view_response(
        self,
        viewname: str,
        *args,
        **kwargs
    ) -> HttpResponse:
        """Get a response from a view."""
        url = self.get_url(viewname, *args, **kwargs)
        return self.client.get(url)

    def post_to_view(
        self,
        viewname: str,
        data: Dict[str, Any],
        *args,
        **kwargs
    ) -> HttpResponse:
        """Post data to a view."""
        url = self.get_url(viewname, *args, **kwargs)
        return self.client.post(url, data)

class PermissionTestMixin:
    """Mixin for permission test functionality."""
    
    def assert_login_required(
        self,
        viewname: str,
        *args,
        **kwargs
    ) -> None:
        """Assert that a view requires login."""
        url = self.get_url(viewname, *args, **kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def assert_permission_required(
        self,
        viewname: str,
        permission: str,
        *args,
        **kwargs
    ) -> None:
        """Assert that a view requires a permission."""
        user = self.create_user()
        self.login_user(user)
        url = self.get_url(viewname, *args, **kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

class TestCase(TestCase, CustomAssertionsMixin):
    """Base test case with custom assertions."""
    pass

class APITestCase(APITestCase, CustomAssertionsMixin):
    """Base API test case with custom assertions."""
    pass

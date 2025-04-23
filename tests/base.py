from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APITransactionTestCase
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
import json
import pytest
from unittest.mock import Mock, patch

User = get_user_model()

class BaseTestCase(TestCase):
    """
    Base test case for standard Django tests.
    """
    def setUp(self):
        super().setUp()
        self.user = self.create_user()
        self.client.login(username=self.user.username, password='testpass123')

    @classmethod
    def create_user(cls, username='testuser', password='testpass123', **kwargs):
        """Create a test user."""
        return User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password=password,
            **kwargs
        )

    def assert_object_exists(self, model_class, **kwargs):
        """Assert that an object exists with given attributes."""
        self.assertTrue(model_class.objects.filter(**kwargs).exists())

    def assert_object_does_not_exist(self, model_class, **kwargs):
        """Assert that an object does not exist with given attributes."""
        self.assertFalse(model_class.objects.filter(**kwargs).exists())

    def assert_response_contains(self, response, text):
        """Assert that response content contains text."""
        self.assertContains(response, text)

    def assert_response_does_not_contain(self, response, text):
        """Assert that response content does not contain text."""
        self.assertNotContains(response, text)

class BaseAPITestCase(APITestCase):
    """
    Base test case for REST API tests.
    """
    def setUp(self):
        super().setUp()
        self.user = self.create_user()
        self.client.force_authenticate(user=self.user)

    @classmethod
    def create_user(cls, username='testuser', password='testpass123', **kwargs):
        """Create a test user."""
        return User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password=password,
            **kwargs
        )

    def get_response_json(self, response):
        """Get JSON response content."""
        return json.loads(response.content.decode())

    def assert_status_code(self, response, expected_status):
        """Assert response status code."""
        self.assertEqual(response.status_code, expected_status)

    def assert_response_keys(self, response, expected_keys):
        """Assert response JSON contains expected keys."""
        content = self.get_response_json(response)
        self.assertTrue(all(key in content for key in expected_keys))

    def assert_error_response(self, response, expected_error):
        """Assert error response content."""
        content = self.get_response_json(response)
        self.assertIn('error', content)
        self.assertEqual(content['error'], expected_error)

class BaseWebSocketTestCase(TestCase):
    """
    Base test case for WebSocket tests.
    """
    async def setUp(self):
        super().setUp()
        self.user = await self.create_user_async()
        self.communicator = await self.create_communicator()

    @classmethod
    async def create_user_async(cls, username='testuser', password='testpass123', **kwargs):
        """Create a test user asynchronously."""
        return await cls.create_user(username, password, **kwargs)

    async def create_communicator(self, path='/ws/test/'):
        """Create a WebSocket communicator."""
        application = URLRouter([
            # Add your WebSocket URL patterns here
        ])
        communicator = WebsocketCommunicator(
            AuthMiddlewareStack(application),
            path
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        return communicator

    async def tearDown(self):
        """Clean up after tests."""
        await self.communicator.disconnect()
        await super().tearDown()

    async def send_json_to(self, data):
        """Send JSON data through WebSocket."""
        await self.communicator.send_json_to(data)

    async def receive_json_from(self):
        """Receive JSON data from WebSocket."""
        response = await self.communicator.receive_json_from()
        return response

    async def assert_message_received(self, expected_message):
        """Assert that a specific message is received."""
        response = await self.receive_json_from()
        self.assertEqual(response, expected_message)

class BaseCeleryTestCase(TestCase):
    """
    Base test case for Celery task tests.
    """
    def setUp(self):
        super().setUp()
        self.mock_task = Mock()
        self.patcher = patch('celery.app.task.Task.delay', self.mock_task)
        self.patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
        super().tearDown()

    def assert_task_called(self, task_name, *args, **kwargs):
        """Assert that a Celery task was called with specific arguments."""
        task_path = f'breaksphere.tasks.{task_name}'
        self.mock_task.assert_called_with(*args, **kwargs)

    def assert_task_not_called(self):
        """Assert that no Celery task was called."""
        self.mock_task.assert_not_called()

class BaseTransactionTestCase(TransactionTestCase):
    """
    Base test case for database transaction tests.
    """
    def setUp(self):
        super().setUp()
        self.user = self.create_user()

    def assert_atomic_operation(self, callable_obj, *args, **kwargs):
        """Assert that an operation is atomic."""
        from django.db import transaction
        try:
            with transaction.atomic():
                callable_obj(*args, **kwargs)
        except Exception as e:
            self.fail(f"Operation was not atomic: {str(e)}")

class BasePermissionTestCase(APITestCase):
    """
    Base test case for permission tests.
    """
    def setUp(self):
        super().setUp()
        self.admin_user = self.create_user(is_staff=True, is_superuser=True)
        self.regular_user = self.create_user(username='regular')
        self.unauthorized_user = self.create_user(username='unauthorized')

    def assert_permission_required(self, url, method='get'):
        """Assert that a view requires authentication."""
        self.client.force_authenticate(user=None)
        response = getattr(self.client, method)(url)
        self.assertEqual(response.status_code, 401)

    def assert_admin_required(self, url, method='get'):
        """Assert that a view requires admin privileges."""
        self.client.force_authenticate(user=self.regular_user)
        response = getattr(self.client, method)(url)
        self.assertEqual(response.status_code, 403)

class BaseFactoryTestCase(TestCase):
    """
    Base test case for factory tests.
    """
    def setUp(self):
        super().setUp()
        self.user = self.create_user()

    @classmethod
    def create_batch(cls, factory_class, size=3, **kwargs):
        """Create a batch of objects using a factory."""
        return [factory_class(**kwargs) for _ in range(size)]

    def assert_factory_attributes(self, obj, expected_attrs):
        """Assert that a factory-created object has expected attributes."""
        for attr, value in expected_attrs.items():
            self.assertEqual(getattr(obj, attr), value)

class BaseViewTestCase(TestCase):
    """
    Base test case for view tests.
    """
    def setUp(self):
        super().setUp()
        self.user = self.create_user()
        self.client.login(username=self.user.username, password='testpass123')

    def get_url(self, url_name, *args, **kwargs):
        """Get URL by name."""
        return reverse(url_name, args=args, kwargs=kwargs)

    def assert_template_used(self, response, template_name):
        """Assert that a specific template was used."""
        self.assertTemplateUsed(response, template_name)

    def assert_redirects_to(self, response, url_name, *args, **kwargs):
        """Assert that response redirects to a specific URL."""
        self.assertRedirects(response, self.get_url(url_name, *args, **kwargs))

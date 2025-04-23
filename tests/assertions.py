from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union
from unittest import TestCase

from django.db import models
from django.http import HttpResponse
from django.test import Client
from rest_framework.response import Response
from rest_framework.test import APIClient

class CustomAssertionsMixin:
    """Custom assertions for testing Django applications."""

    def assertModelExists(
        self: TestCase,
        model_class: Type[models.Model],
        **kwargs
    ) -> None:
        """Assert that a model instance exists with given attributes."""
        exists = model_class.objects.filter(**kwargs).exists()
        self.assertTrue(
            exists,
            f"Model {model_class.__name__} with attributes {kwargs} does not exist"
        )

    def assertModelNotExists(
        self: TestCase,
        model_class: Type[models.Model],
        **kwargs
    ) -> None:
        """Assert that a model instance does not exist with given attributes."""
        exists = model_class.objects.filter(**kwargs).exists()
        self.assertFalse(
            exists,
            f"Model {model_class.__name__} with attributes {kwargs} exists"
        )

    def assertResponseContains(
        self: TestCase,
        response: Union[HttpResponse, Response],
        expected_data: Any,
        status_code: int = 200
    ) -> None:
        """Assert that response contains expected data and status code."""
        self.assertEqual(response.status_code, status_code)
        if hasattr(response, 'data'):
            # DRF Response
            self.assertIn(expected_data, response.data)
        else:
            # Django HttpResponse
            self.assertIn(expected_data, response.content.decode())

    def assertResponseNotContains(
        self: TestCase,
        response: Union[HttpResponse, Response],
        unexpected_data: Any,
        status_code: int = 200
    ) -> None:
        """Assert that response does not contain unexpected data."""
        self.assertEqual(response.status_code, status_code)
        if hasattr(response, 'data'):
            # DRF Response
            self.assertNotIn(unexpected_data, response.data)
        else:
            # Django HttpResponse
            self.assertNotIn(unexpected_data, response.content.decode())

    def assertResponseKeys(
        self: TestCase,
        response: Response,
        expected_keys: List[str],
        status_code: int = 200
    ) -> None:
        """Assert that response data contains expected keys."""
        self.assertEqual(response.status_code, status_code)
        for key in expected_keys:
            self.assertIn(
                key,
                response.data,
                f"Response data missing expected key: {key}"
            )

    def assertDatetimeEqual(
        self: TestCase,
        dt1: datetime,
        dt2: datetime,
        delta_seconds: int = 1
    ) -> None:
        """Assert that two datetimes are equal within a delta."""
        difference = abs((dt1 - dt2).total_seconds())
        self.assertLessEqual(
            difference,
            delta_seconds,
            f"Datetimes differ by {difference} seconds"
        )

    def assertQuerysetEqual(
        self: TestCase,
        qs: models.QuerySet,
        values: List[Any],
        transform: Optional[callable] = None,
        ordered: bool = True
    ) -> None:
        """Assert that a queryset equals a list of values."""
        if transform is None:
            transform = lambda x: x
        qs_values = list(map(transform, qs))
        if not ordered:
            qs_values = sorted(qs_values)
            values = sorted(values)
        self.assertEqual(
            qs_values,
            values,
            "Queryset values do not match expected values"
        )

    def assertPermissionRequired(
        self: TestCase,
        url: str,
        method: str = 'get',
        client: Optional[Union[Client, APIClient]] = None
    ) -> None:
        """Assert that a view requires authentication."""
        if client is None:
            client = self.client
        client.logout()
        response = getattr(client, method)(url)
        self.assertIn(
            response.status_code,
            [302, 401, 403],
            "View does not require authentication"
        )

    def assertCacheHit(
        self: TestCase,
        key: str,
        expected_value: Any
    ) -> None:
        """Assert that a cache key exists with expected value."""
        from django.core.cache import cache
        cached_value = cache.get(key)
        self.assertEqual(
            cached_value,
            expected_value,
            f"Cache miss or unexpected value for key: {key}"
        )

    def assertCacheMiss(
        self: TestCase,
        key: str
    ) -> None:
        """Assert that a cache key does not exist."""
        from django.core.cache import cache
        self.assertIsNone(
            cache.get(key),
            f"Cache hit for key that should not exist: {key}"
        )

    def assertTaskCalled(
        self: TestCase,
        task_name: str,
        *expected_args,
        **expected_kwargs
    ) -> None:
        """Assert that a Celery task was called with expected arguments."""
        from unittest.mock import patch
        with patch(f'celery.app.task.Task.delay') as mock_task:
            mock_task.assert_called_with(*expected_args, **expected_kwargs)

    def assertWebSocketConnected(
        self: TestCase,
        path: str
    ) -> None:
        """Assert that a WebSocket connection can be established."""
        from channels.testing import WebsocketCommunicator
        from channels.routing import URLRouter
        from channels.auth import AuthMiddlewareStack
        
        application = URLRouter([])  # Add your URL patterns
        communicator = WebsocketCommunicator(
            AuthMiddlewareStack(application),
            path
        )
        connected, _ = await communicator.connect()
        self.assertTrue(
            connected,
            f"WebSocket connection failed for path: {path}"
        )
        await communicator.disconnect()

    def assertValidationError(
        self: TestCase,
        callable_obj: callable,
        expected_message: str,
        *args,
        **kwargs
    ) -> None:
        """Assert that a callable raises a ValidationError with expected message."""
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError) as cm:
            callable_obj(*args, **kwargs)
        self.assertIn(
            expected_message,
            str(cm.exception),
            "Validation error message does not match"
        )

    def assertQueryCount(
        self: TestCase,
        expected_count: int,
        callable_obj: callable,
        *args,
        **kwargs
    ) -> None:
        """Assert that a callable executes expected number of queries."""
        from django.db import connection, reset_queries
        reset_queries()
        callable_obj(*args, **kwargs)
        actual_count = len(connection.queries)
        self.assertEqual(
            actual_count,
            expected_count,
            f"Expected {expected_count} queries, got {actual_count}"
        )

    def assertTemplateRendered(
        self: TestCase,
        response: HttpResponse,
        template_name: str,
        context_keys: Optional[List[str]] = None
    ) -> None:
        """Assert that a template was rendered with expected context keys."""
        self.assertTemplateUsed(response, template_name)
        if context_keys:
            for key in context_keys:
                self.assertIn(
                    key,
                    response.context,
                    f"Template context missing key: {key}"
                )

    def assertFileUploaded(
        self: TestCase,
        file_field: models.FileField,
        expected_name: str
    ) -> None:
        """Assert that a file was uploaded with expected name."""
        self.assertTrue(
            file_field,
            "File field is empty"
        )
        self.assertEqual(
            file_field.name,
            expected_name,
            "Uploaded file name does not match"
        )

    def assertJsonResponse(
        self: TestCase,
        response: HttpResponse,
        expected_data: Dict[str, Any],
        status_code: int = 200
    ) -> None:
        """Assert that response is JSON with expected data."""
        import json
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(
            response['Content-Type'],
            'application/json',
            "Response is not JSON"
        )
        data = json.loads(response.content)
        self.assertEqual(
            data,
            expected_data,
            "JSON response data does not match"
        )

    def assertModelField(
        self: TestCase,
        model_class: Type[models.Model],
        field_name: str,
        field_type: Type[models.Field],
        **field_attrs
    ) -> None:
        """Assert that a model has a field of expected type and attributes."""
        field = model_class._meta.get_field(field_name)
        self.assertIsInstance(
            field,
            field_type,
            f"Field {field_name} is not of type {field_type}"
        )
        for attr, value in field_attrs.items():
            self.assertEqual(
                getattr(field, attr),
                value,
                f"Field {field_name} attribute {attr} does not match"
            )

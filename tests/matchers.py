from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type, Union
from unittest.mock import Mock

from django.db import models
from django.http import HttpResponse
from django.test import TestCase
from rest_framework.response import Response

class BaseMatcher:
    """Base class for custom matchers."""
    
    def __init__(self, expected: Any):
        self.expected = expected
        self.actual = None
        self.message = None

    def matches(self, actual: Any) -> bool:
        """Check if actual value matches expected value."""
        self.actual = actual
        return self._matches()

    def _matches(self) -> bool:
        """Implement actual matching logic."""
        raise NotImplementedError

    def message_for_failed_match(self) -> str:
        """Get message explaining why match failed."""
        return self.message or f"Expected {self.expected}, got {self.actual}"

class IsInstanceOf(BaseMatcher):
    """Match if value is instance of expected type."""
    
    def _matches(self) -> bool:
        return isinstance(self.actual, self.expected)

    def message_for_failed_match(self) -> str:
        return f"Expected instance of {self.expected.__name__}, got {type(self.actual).__name__}"

class HasAttributes(BaseMatcher):
    """Match if object has expected attributes."""
    
    def _matches(self) -> bool:
        for key, value in self.expected.items():
            if not hasattr(self.actual, key):
                self.message = f"Object missing attribute '{key}'"
                return False
            if getattr(self.actual, key) != value:
                self.message = f"Attribute '{key}' has value {getattr(self.actual, key)}, expected {value}"
                return False
        return True

class HasDictItems(BaseMatcher):
    """Match if dictionary contains expected items."""
    
    def _matches(self) -> bool:
        if not isinstance(self.actual, dict):
            self.message = f"Expected dict, got {type(self.actual).__name__}"
            return False
        for key, value in self.expected.items():
            if key not in self.actual:
                self.message = f"Dict missing key '{key}'"
                return False
            if self.actual[key] != value:
                self.message = f"Key '{key}' has value {self.actual[key]}, expected {value}"
                return False
        return True

class HasLength(BaseMatcher):
    """Match if object has expected length."""
    
    def _matches(self) -> bool:
        try:
            return len(self.actual) == self.expected
        except TypeError:
            self.message = f"Object {self.actual} has no length"
            return False

class IsEmpty(BaseMatcher):
    """Match if object is empty."""
    
    def __init__(self):
        super().__init__(None)

    def _matches(self) -> bool:
        try:
            return len(self.actual) == 0
        except TypeError:
            self.message = f"Object {self.actual} has no length"
            return False

class IsTrue(BaseMatcher):
    """Match if value is True."""
    
    def __init__(self):
        super().__init__(True)

    def _matches(self) -> bool:
        return bool(self.actual) is True

class IsFalse(BaseMatcher):
    """Match if value is False."""
    
    def __init__(self):
        super().__init__(False)

    def _matches(self) -> bool:
        return bool(self.actual) is False

class IsNone(BaseMatcher):
    """Match if value is None."""
    
    def __init__(self):
        super().__init__(None)

    def _matches(self) -> bool:
        return self.actual is None

class IsNotNone(BaseMatcher):
    """Match if value is not None."""
    
    def __init__(self):
        super().__init__(None)

    def _matches(self) -> bool:
        return self.actual is not None

class IsCallable(BaseMatcher):
    """Match if value is callable."""
    
    def __init__(self):
        super().__init__(None)

    def _matches(self) -> bool:
        return callable(self.actual)

class RaisesException(BaseMatcher):
    """Match if callable raises expected exception."""
    
    def _matches(self) -> bool:
        if not callable(self.actual):
            self.message = f"Expected callable, got {type(self.actual).__name__}"
            return False
        try:
            self.actual()
            self.message = "No exception raised"
            return False
        except Exception as e:
            return isinstance(e, self.expected)

class MatchesRegex(BaseMatcher):
    """Match if string matches regex pattern."""
    
    def _matches(self) -> bool:
        import re
        try:
            return bool(re.match(self.expected, str(self.actual)))
        except Exception as e:
            self.message = str(e)
            return False

class IsDatetime(BaseMatcher):
    """Match if value is a datetime within expected range."""
    
    def __init__(self, expected: datetime, delta: timedelta = timedelta(seconds=1)):
        self.delta = delta
        super().__init__(expected)

    def _matches(self) -> bool:
        if not isinstance(self.actual, datetime):
            self.message = f"Expected datetime, got {type(self.actual).__name__}"
            return False
        difference = abs((self.actual - self.expected).total_seconds())
        return difference <= self.delta.total_seconds()

class HasStatus(BaseMatcher):
    """Match if response has expected status code."""
    
    def _matches(self) -> bool:
        if not isinstance(self.actual, (HttpResponse, Response)):
            self.message = f"Expected response object, got {type(self.actual).__name__}"
            return False
        return self.actual.status_code == self.expected

class WasCalled(BaseMatcher):
    """Match if mock was called with expected arguments."""
    
    def _matches(self) -> bool:
        if not isinstance(self.actual, Mock):
            self.message = f"Expected Mock object, got {type(self.actual).__name__}"
            return False
        if self.expected is None:
            return self.actual.called
        return self.actual.call_args == self.expected

class HasQueryCount(BaseMatcher):
    """Match if number of database queries matches expected count."""
    
    def _matches(self) -> bool:
        from django.db import connection
        query_count = len(connection.queries)
        if query_count != self.expected:
            self.message = f"Expected {self.expected} queries, got {query_count}"
            return False
        return True

class ModelExists(BaseMatcher):
    """Match if model instance exists with expected attributes."""
    
    def _matches(self) -> bool:
        if not issubclass(self.actual, models.Model):
            self.message = f"Expected model class, got {type(self.actual).__name__}"
            return False
        return self.actual.objects.filter(**self.expected).exists()

class MatchersMixin:
    """Mixin providing matcher assertions."""
    
    def assert_that(self: TestCase, actual: Any, matcher: BaseMatcher) -> None:
        """Assert that value matches expected matcher."""
        if not matcher.matches(actual):
            self.fail(matcher.message_for_failed_match())

    def assert_all(self: TestCase, items: List[Any], matcher: BaseMatcher) -> None:
        """Assert that all items match expected matcher."""
        for item in items:
            self.assert_that(item, matcher)

    def assert_any(self: TestCase, items: List[Any], matcher: BaseMatcher) -> None:
        """Assert that any item matches expected matcher."""
        if not any(matcher.matches(item) for item in items):
            self.fail("No items matched the expected condition")

# Matcher factory functions
def instance_of(expected_type: Type) -> IsInstanceOf:
    return IsInstanceOf(expected_type)

def has_attributes(**attrs) -> HasAttributes:
    return HasAttributes(attrs)

def has_items(**items) -> HasDictItems:
    return HasDictItems(items)

def has_length(length: int) -> HasLength:
    return HasLength(length)

def is_empty() -> IsEmpty:
    return IsEmpty()

def is_true() -> IsTrue:
    return IsTrue()

def is_false() -> IsFalse:
    return IsFalse()

def is_none() -> IsNone:
    return IsNone()

def is_not_none() -> IsNotNone:
    return IsNotNone()

def is_callable() -> IsCallable:
    return IsCallable()

def raises(exception: Type[Exception]) -> RaisesException:
    return RaisesException(exception)

def matches_regex(pattern: str) -> MatchesRegex:
    return MatchesRegex(pattern)

def is_datetime(dt: datetime, delta: timedelta = timedelta(seconds=1)) -> IsDatetime:
    return IsDatetime(dt, delta)

def has_status(status_code: int) -> HasStatus:
    return HasStatus(status_code)

def was_called(call_args: Optional[tuple] = None) -> WasCalled:
    return WasCalled(call_args)

def has_query_count(count: int) -> HasQueryCount:
    return HasQueryCount(count)

def model_exists(**attrs) -> ModelExists:
    return ModelExists(attrs)

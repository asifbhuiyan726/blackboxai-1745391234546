from typing import Any, Dict, List, Optional, Type, Union

class TestError(Exception):
    """Base class for test exceptions."""
    pass

class TestSetupError(TestError):
    """Exception raised when test setup fails."""
    
    def __init__(
        self,
        message: str,
        setup_step: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.setup_step = setup_step
        self.details = details or {}
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        parts = [message]
        if self.setup_step:
            parts.append(f"Setup step: {self.setup_step}")
        if self.details:
            parts.append("Details:")
            for key, value in self.details.items():
                parts.append(f"  {key}: {value}")
        return "\n".join(parts)

class TestTeardownError(TestError):
    """Exception raised when test teardown fails."""
    
    def __init__(
        self,
        message: str,
        teardown_step: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.teardown_step = teardown_step
        self.details = details or {}
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        parts = [message]
        if self.teardown_step:
            parts.append(f"Teardown step: {self.teardown_step}")
        if self.details:
            parts.append("Details:")
            for key, value in self.details.items():
                parts.append(f"  {key}: {value}")
        return "\n".join(parts)

class TestDataError(TestError):
    """Exception raised when test data is invalid or missing."""
    
    def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        expected: Optional[Any] = None,
        actual: Optional[Any] = None
    ):
        self.data_type = data_type
        self.expected = expected
        self.actual = actual
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        parts = [message]
        if self.data_type:
            parts.append(f"Data type: {self.data_type}")
        if self.expected is not None:
            parts.append(f"Expected: {self.expected}")
        if self.actual is not None:
            parts.append(f"Actual: {self.actual}")
        return "\n".join(parts)

class TestDependencyError(TestError):
    """Exception raised when a test dependency is missing."""
    
    def __init__(
        self,
        message: str,
        dependency: str,
        required_version: Optional[str] = None
    ):
        self.dependency = dependency
        self.required_version = required_version
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        parts = [message]
        parts.append(f"Dependency: {self.dependency}")
        if self.required_version:
            parts.append(f"Required version: {self.required_version}")
        return "\n".join(parts)

class TestConfigurationError(TestError):
    """Exception raised when test configuration is invalid."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None
    ):
        self.config_key = config_key
        self.config_value = config_value
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        parts = [message]
        if self.config_key:
            parts.append(f"Configuration key: {self.config_key}")
        if self.config_value is not None:
            parts.append(f"Configuration value: {self.config_value}")
        return "\n".join(parts)

class TestTimeoutError(TestError):
    """Exception raised when a test operation times out."""
    
    def __init__(
        self,
        message: str,
        operation: str,
        timeout: Union[int, float],
        elapsed: Optional[Union[int, float]] = None
    ):
        self.operation = operation
        self.timeout = timeout
        self.elapsed = elapsed
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        parts = [message]
        parts.append(f"Operation: {self.operation}")
        parts.append(f"Timeout: {self.timeout} seconds")
        if self.elapsed is not None:
            parts.append(f"Elapsed time: {self.elapsed} seconds")
        return "\n".join(parts)

class TestAssertionError(TestError):
    """Exception raised when a test assertion fails."""
    
    def __init__(
        self,
        message: str,
        assertion_type: str,
        expected: Any,
        actual: Any,
        diff: Optional[str] = None
    ):
        self.assertion_type = assertion_type
        self.expected = expected
        self.actual = actual
        self.diff = diff
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        parts = [message]
        parts.append(f"Assertion type: {self.assertion_type}")
        parts.append(f"Expected: {self.expected}")
        parts.append(f"Actual: {self.actual}")
        if self.diff:
            parts.append("Diff:")
            parts.append(self.diff)
        return "\n".join(parts)

class TestEnvironmentError(TestError):
    """Exception raised when the test environment is invalid."""
    
    def __init__(
        self,
        message: str,
        environment: str,
        requirements: Optional[List[str]] = None
    ):
        self.environment = environment
        self.requirements = requirements or []
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        parts = [message]
        parts.append(f"Environment: {self.environment}")
        if self.requirements:
            parts.append("Requirements:")
            for req in self.requirements:
                parts.append(f"  - {req}")
        return "\n".join(parts)

class TestFixtureError(TestError):
    """Exception raised when a test fixture fails."""
    
    def __init__(
        self,
        message: str,
        fixture_name: str,
        fixture_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.fixture_name = fixture_name
        self.fixture_type = fixture_type
        self.cause = cause
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        parts = [message]
        parts.append(f"Fixture name: {self.fixture_name}")
        if self.fixture_type:
            parts.append(f"Fixture type: {self.fixture_type}")
        if self.cause:
            parts.append(f"Cause: {str(self.cause)}")
        return "\n".join(parts)

class TestCleanupError(TestError):
    """Exception raised when test cleanup fails."""
    
    def __init__(
        self,
        message: str,
        cleanup_step: str,
        resources: Optional[List[str]] = None,
        cause: Optional[Exception] = None
    ):
        self.cleanup_step = cleanup_step
        self.resources = resources or []
        self.cause = cause
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        parts = [message]
        parts.append(f"Cleanup step: {self.cleanup_step}")
        if self.resources:
            parts.append("Resources:")
            for resource in self.resources:
                parts.append(f"  - {resource}")
        if self.cause:
            parts.append(f"Cause: {str(self.cause)}")
        return "\n".join(parts)

class TestDatabaseError(TestError):
    """Exception raised when a database operation fails during testing."""
    
    def __init__(
        self,
        message: str,
        operation: str,
        model: Optional[str] = None,
        query: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.operation = operation
        self.model = model
        self.query = query
        self.cause = cause
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        parts = [message]
        parts.append(f"Operation: {self.operation}")
        if self.model:
            parts.append(f"Model: {self.model}")
        if self.query:
            parts.append(f"Query: {self.query}")
        if self.cause:
            parts.append(f"Cause: {str(self.cause)}")
        return "\n".join(parts)

class TestWebSocketError(TestError):
    """Exception raised when a WebSocket operation fails during testing."""
    
    def __init__(
        self,
        message: str,
        operation: str,
        connection_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.operation = operation
        self.connection_id = connection_id
        self.data = data
        self.cause = cause
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        parts = [message]
        parts.append(f"Operation: {self.operation}")
        if self.connection_id:
            parts.append(f"Connection ID: {self.connection_id}")
        if self.data:
            parts.append("Data:")
            for key, value in self.data.items():
                parts.append(f"  {key}: {value}")
        if self.cause:
            parts.append(f"Cause: {str(self.cause)}")
        return "\n".join(parts)

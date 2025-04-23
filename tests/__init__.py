"""
BreakSphere Testing Framework
============================

A comprehensive testing framework for the BreakSphere application.

This package provides tools, utilities, and base classes for writing
and running tests for the BreakSphere application.

Usage:
------
from tests import TestCase, APITestCase
from tests.decorators import slow_test, requires_redis
from tests.matchers import assert_that, has_length
from tests.factories import UserFactory, RoomFactory

class MyTest(TestCase):
    @slow_test
    @requires_redis
    def test_something(self):
        user = UserFactory()
        room = RoomFactory()
        assert_that(room.members.all(), has_length(0))
"""

from .assertions import CustomAssertionsMixin
from .base import BaseTestCase
from .constants import *
from .decorators import (
    slow_test,
    quick_test,
    integration_test,
    api_test,
    websocket_test,
    skip_in_ci,
    requires_redis,
    requires_celery,
    requires_channels,
    timer,
    count_queries,
    with_cache,
    freeze_time,
    with_permissions,
    with_media_root,
    retry_on_failure,
    expected_failure,
    benchmark,
    require_debug,
    require_production,
)
from .exceptions import (
    TestError,
    TestSetupError,
    TestTeardownError,
    TestDataError,
    TestDependencyError,
    TestConfigurationError,
    TestTimeoutError,
    TestAssertionError,
    TestEnvironmentError,
    TestFixtureError,
    TestCleanupError,
    TestDatabaseError,
    TestWebSocketError,
)
from .factories import (
    UserFactory,
    StatusFactory,
    UserStatusFactory,
    RoomFactory,
    RoomMembershipFactory,
    EventFactory,
    EventParticipantFactory,
    PostFactory,
    PollOptionFactory,
    CommentFactory,
    ChatMessageFactory,
    PairingRequestFactory,
    PairingMatchFactory,
    IcebreakerCategoryFactory,
    IcebreakerQuestionFactory,
    IcebreakerSessionFactory,
    UserAchievementFactory,
    UserConnectionFactory,
    UserStreakFactory,
    ChatReactionFactory,
    ChatNotificationFactory,
    EventReminderFactory,
    PairingPreferenceFactory,
    ReactionFactory,
    VoteFactory,
)
from .fixtures import (
    create_user_fixtures,
    create_status_fixtures,
    create_room_fixtures,
    create_event_fixtures,
    create_post_fixtures,
    create_icebreaker_fixtures,
    create_message_fixtures,
    create_all_fixtures,
    load_all_fixtures,
)
from .helpers import (
    with_test_database,
    with_test_cache,
    with_test_celery,
    with_test_websocket,
    mock_now,
    count_queries,
    temporary_media_root,
    create_test_image,
    create_test_file,
    get_test_user,
    get_auth_client,
    json_response,
    setup_test_environment,
    teardown_test_environment,
    create_test_data,
    benchmark,
    skip_in_ci,
    requires_redis,
    requires_celery,
    requires_websocket,
    load_fixture,
    create_temp_file,
)
from .matchers import (
    BaseMatcher,
    IsInstanceOf,
    HasAttributes,
    HasDictItems,
    HasLength,
    IsEmpty,
    IsTrue,
    IsFalse,
    IsNone,
    IsNotNone,
    IsCallable,
    RaisesException,
    MatchesRegex,
    IsDatetime,
    HasStatus,
    WasCalled,
    HasQueryCount,
    ModelExists,
    MatchersMixin,
    instance_of,
    has_attributes,
    has_items,
    has_length,
    is_empty,
    is_true,
    is_false,
    is_none,
    is_not_none,
    is_callable,
    raises,
    matches_regex,
    is_datetime,
    has_status,
    was_called,
    has_query_count,
    model_exists,
)
from .mixins import (
    UserTestMixin,
    APITestMixin,
    WebSocketTestMixin,
    CeleryTestMixin,
    CacheTestMixin,
    FileTestMixin,
    DatabaseTestMixin,
    ViewTestMixin,
    PermissionTestMixin,
)
from .runner import (
    BreakSphereTestRunner,
    ParallelTestRunner,
    FailFastTestRunner,
    RerunFailedTestRunner,
    RandomOrderTestRunner,
    get_test_runner_class,
    run_tests,
)
from .utils import (
    TestDataMixin,
    MockRequestsMixin,
    DatabaseTestMixin,
    WebSocketTestMixin,
    APITestMixin,
    CeleryTestMixin,
    AuthTestMixin,
    PermissionTestMixin,
    CacheTestMixin,
)

# Create base test case classes that combine all the mixins
class TestCase(
    BaseTestCase,
    CustomAssertionsMixin,
    TestDataMixin,
    DatabaseTestMixin,
    FileTestMixin,
    CacheTestMixin,
    MatchersMixin,
):
    """Base test case for BreakSphere tests."""
    pass

class APITestCase(
    BaseTestCase,
    CustomAssertionsMixin,
    APITestMixin,
    TestDataMixin,
    DatabaseTestMixin,
    FileTestMixin,
    CacheTestMixin,
    MatchersMixin,
):
    """Base test case for BreakSphere API tests."""
    pass

class WebSocketTestCase(
    BaseTestCase,
    CustomAssertionsMixin,
    WebSocketTestMixin,
    TestDataMixin,
    DatabaseTestMixin,
    CacheTestMixin,
    MatchersMixin,
):
    """Base test case for BreakSphere WebSocket tests."""
    pass

class IntegrationTestCase(
    BaseTestCase,
    CustomAssertionsMixin,
    TestDataMixin,
    DatabaseTestMixin,
    FileTestMixin,
    CacheTestMixin,
    CeleryTestMixin,
    WebSocketTestMixin,
    MatchersMixin,
):
    """Base test case for BreakSphere integration tests."""
    pass

__all__ = [
    'TestCase',
    'APITestCase',
    'WebSocketTestCase',
    'IntegrationTestCase',
    'CustomAssertionsMixin',
    'TestDataMixin',
    'MockRequestsMixin',
    'DatabaseTestMixin',
    'WebSocketTestMixin',
    'APITestMixin',
    'CeleryTestMixin',
    'AuthTestMixin',
    'PermissionTestMixin',
    'CacheTestMixin',
    'MatchersMixin',
    'BaseTestCase',
    'BreakSphereTestRunner',
    'ParallelTestRunner',
    'FailFastTestRunner',
    'RerunFailedTestRunner',
    'RandomOrderTestRunner',
]

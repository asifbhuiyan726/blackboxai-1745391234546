import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from pytest_factoryboy import register
from faker import Faker

from accounts.factories import UserFactory
from status.factories import StatusFactory, UserStatusFactory
from rooms.factories import RoomFactory, RoomMembershipFactory
from events.factories import EventFactory, EventParticipantFactory
from feed.factories import PostFactory, CommentFactory
from pairing.factories import PairingRequestFactory, PairingMatchFactory
from chat.factories import ChatMessageFactory
from icebreaker.factories import IcebreakerQuestionFactory

# Register factories
register(UserFactory)
register(StatusFactory)
register(UserStatusFactory)
register(RoomFactory)
register(RoomMembershipFactory)
register(EventFactory)
register(EventParticipantFactory)
register(PostFactory)
register(CommentFactory)
register(PairingRequestFactory)
register(PairingMatchFactory)
register(ChatMessageFactory)
register(IcebreakerQuestionFactory)

# Initialize Faker
fake = Faker()

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass

@pytest.fixture
def api_client():
    """Return an API client."""
    return APIClient()

@pytest.fixture
def authenticated_client(user):
    """Return an authenticated API client."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def web_client():
    """Return a Django test client."""
    return Client()

@pytest.fixture
def user():
    """Create and return a regular user."""
    return UserFactory()

@pytest.fixture
def admin_user():
    """Create and return an admin user."""
    return UserFactory(is_staff=True, is_superuser=True)

@pytest.fixture
def websocket_client(application):
    """Return a WebSocket client."""
    return WebsocketCommunicator(
        AuthMiddlewareStack(URLRouter(application.routing)),
        "ws/testws/"
    )

@pytest.fixture
def room_with_members(room_factory, user_factory):
    """Create a room with members."""
    room = room_factory()
    members = user_factory.create_batch(3)
    room.members.add(*members)
    return room, members

@pytest.fixture
def event_with_participants(event_factory, user_factory):
    """Create an event with participants."""
    event = event_factory()
    participants = user_factory.create_batch(3)
    for participant in participants:
        EventParticipantFactory(event=event, user=participant)
    return event, participants

@pytest.fixture
def post_with_comments(post_factory, comment_factory, user_factory):
    """Create a post with comments."""
    post = post_factory()
    comments = comment_factory.create_batch(3, post=post, author=user_factory())
    return post, comments

@pytest.fixture
def pairing_match_with_users(pairing_match_factory, user_factory):
    """Create a pairing match with users."""
    user1 = user_factory()
    user2 = user_factory()
    match = pairing_match_factory(request__user=user1, matched_user=user2)
    return match, user1, user2

@pytest.fixture
def chat_message_with_reactions(chat_message_factory, user_factory):
    """Create a chat message with reactions."""
    message = chat_message_factory()
    reactors = user_factory.create_batch(3)
    for reactor in reactors:
        message.reactions.create(user=reactor, emoji='👍')
    return message, reactors

@pytest.fixture
def icebreaker_session_with_responses(icebreaker_session_factory, user_factory):
    """Create an icebreaker session with responses."""
    session = icebreaker_session_factory()
    participants = user_factory.create_batch(3)
    session.participants.add(*participants)
    return session, participants

# Test data generators
@pytest.fixture
def create_test_data():
    """Create a set of test data."""
    def _create_test_data(num_users=5, num_rooms=3, num_events=2):
        users = UserFactory.create_batch(num_users)
        rooms = RoomFactory.create_batch(num_rooms)
        events = EventFactory.create_batch(num_events)
        return {'users': users, 'rooms': rooms, 'events': events}
    return _create_test_data

# Mock external services
@pytest.fixture
def mock_redis(mocker):
    """Mock Redis connection."""
    return mocker.patch('django_redis.cache.RedisCache')

@pytest.fixture
def mock_celery(mocker):
    """Mock Celery tasks."""
    return mocker.patch('celery.app.task.Task.delay')

@pytest.fixture
def mock_websocket(mocker):
    """Mock WebSocket connection."""
    return mocker.patch('channels.layers.get_channel_layer')

# Test utilities
@pytest.fixture
def assert_no_database_queries():
    """Assert that no database queries are made."""
    from django.db import connection
    initial_queries = len(connection.queries)
    yield
    final_queries = len(connection.queries)
    assert initial_queries == final_queries, (
        f"{final_queries - initial_queries} unexpected database queries"
    )

@pytest.fixture
def temporary_media_root(tmpdir):
    """Create a temporary media root."""
    settings.MEDIA_ROOT = str(tmpdir)
    return settings.MEDIA_ROOT

@pytest.fixture
def temporary_file():
    """Create a temporary file."""
    import tempfile
    with tempfile.NamedTemporaryFile() as f:
        f.write(b'test content')
        f.seek(0)
        yield f

# Test environment setup
def pytest_configure():
    """Configure test environment."""
    settings.TESTING = True
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Cleanup after tests
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    User = get_user_model()
    User.objects.all().delete()

# Error handling
@pytest.fixture
def assert_raises_validation_error():
    """Assert that a validation error is raised."""
    from django.core.exceptions import ValidationError
    with pytest.raises(ValidationError) as excinfo:
        yield excinfo

# Performance testing
@pytest.fixture
def benchmark_database_queries():
    """Benchmark database queries."""
    from django.db import connection
    from time import time
    
    start_queries = len(connection.queries)
    start_time = time()
    yield
    end_time = time()
    end_queries = len(connection.queries)
    
    print(f"\nQueries executed: {end_queries - start_queries}")
    print(f"Time taken: {end_time - start_time:.2f}s")

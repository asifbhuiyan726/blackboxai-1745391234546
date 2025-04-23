from datetime import timedelta
from typing import Dict, List, Any

# Test User Data
TEST_USER_DATA = {
    'username': 'testuser',
    'email': 'testuser@example.com',
    'password': 'testpass123',
    'first_name': 'Test',
    'last_name': 'User',
}

TEST_ADMIN_DATA = {
    'username': 'admin',
    'email': 'admin@example.com',
    'password': 'adminpass123',
    'is_staff': True,
    'is_superuser': True,
}

# Test Status Data
TEST_STATUS_DATA = {
    'available': {
        'name': 'Available',
        'code': 'available',
        'icon': 'fa-circle',
        'color': 'text-green-500',
        'priority': 100,
        'is_available': True,
    },
    'break': {
        'name': 'On Break',
        'code': 'break',
        'icon': 'fa-coffee',
        'color': 'text-yellow-500',
        'priority': 80,
        'is_available': False,
    },
    'dnd': {
        'name': 'Do Not Disturb',
        'code': 'dnd',
        'icon': 'fa-ban',
        'color': 'text-red-500',
        'priority': 60,
        'is_available': False,
    },
}

# Test Room Data
TEST_ROOM_DATA = {
    'title': 'Test Room',
    'description': 'A test room for unit testing',
    'room_type': 'public',
    'icon_url': 'https://example.com/icon.png',
    'is_official': False,
    'max_members': 10,
}

# Test Event Data
TEST_EVENT_DATA = {
    'title': 'Test Event',
    'description': 'A test event for unit testing',
    'event_type': 'social',
    'location': 'Virtual',
    'is_virtual': True,
    'join_url': 'https://meet.example.com/test',
    'max_participants': 20,
}

# Test Post Data
TEST_POST_DATA = {
    'content': 'This is a test post',
    'post_type': 'text',
    'visibility': 'public',
}

TEST_POLL_DATA = {
    'content': 'Test poll question',
    'post_type': 'poll',
    'visibility': 'public',
    'options': ['Option 1', 'Option 2', 'Option 3'],
}

# Test Chat Message Data
TEST_MESSAGE_DATA = {
    'content': 'Test message content',
    'message_type': 'text',
}

# Test Icebreaker Data
TEST_ICEBREAKER_DATA = {
    'question_text': 'What is your favorite programming language?',
    'difficulty': 'easy',
}

# Test Pairing Data
TEST_PAIRING_DATA = {
    'preferred_duration': 30,
    'meeting_preference': 'video',
    'timezone_preference': 'exact',
}

# Test File Data
TEST_FILE_DATA = {
    'name': 'test_file.txt',
    'content': b'Test file content',
    'content_type': 'text/plain',
}

# Test Image Data
TEST_IMAGE_DATA = {
    'name': 'test_image.jpg',
    'content_type': 'image/jpeg',
    'width': 800,
    'height': 600,
}

# Test Time Intervals
TIME_INTERVALS = {
    'MINUTE': timedelta(minutes=1),
    'HOUR': timedelta(hours=1),
    'DAY': timedelta(days=1),
    'WEEK': timedelta(weeks=1),
    'MONTH': timedelta(days=30),
}

# Test API Endpoints
API_ENDPOINTS = {
    'auth': {
        'login': '/api/accounts/login/',
        'register': '/api/accounts/register/',
        'logout': '/api/accounts/logout/',
        'profile': '/api/accounts/profile/',
    },
    'status': {
        'list': '/api/status/',
        'current': '/api/status/current/',
        'update': '/api/status/update/',
    },
    'rooms': {
        'list': '/api/rooms/',
        'create': '/api/rooms/create/',
        'join': '/api/rooms/{id}/join/',
        'leave': '/api/rooms/{id}/leave/',
    },
    'events': {
        'list': '/api/events/',
        'create': '/api/events/create/',
        'rsvp': '/api/events/{id}/rsvp/',
    },
    'feed': {
        'list': '/api/feed/',
        'create': '/api/feed/create/',
        'vote': '/api/feed/{id}/vote/',
    },
    'chat': {
        'messages': '/api/chat/messages/',
        'reactions': '/api/chat/messages/{id}/reactions/',
    },
    'pairing': {
        'request': '/api/pairing/request/',
        'match': '/api/pairing/match/',
    },
    'icebreaker': {
        'random': '/api/icebreaker/random/',
        'response': '/api/icebreaker/response/',
    },
}

# Test WebSocket Endpoints
WS_ENDPOINTS = {
    'chat': 'ws/rooms/{room_id}/',
    'notifications': 'ws/notifications/',
    'status': 'ws/status/',
}

# Test Response Messages
RESPONSE_MESSAGES = {
    'success': {
        'created': 'Resource created successfully',
        'updated': 'Resource updated successfully',
        'deleted': 'Resource deleted successfully',
    },
    'error': {
        'not_found': 'Resource not found',
        'permission_denied': 'Permission denied',
        'validation_error': 'Validation error',
    },
}

# Test Permissions
TEST_PERMISSIONS = {
    'admin': [
        'add_user',
        'change_user',
        'delete_user',
        'view_user',
    ],
    'moderator': [
        'moderate_room',
        'pin_message',
        'delete_message',
    ],
    'user': [
        'join_room',
        'send_message',
        'create_post',
    ],
}

# Test Cache Keys
CACHE_KEYS = {
    'user_status': 'user_status_{user_id}',
    'room_members': 'room_members_{room_id}',
    'event_participants': 'event_participants_{event_id}',
    'post_reactions': 'post_reactions_{post_id}',
}

# Test Metrics
TEST_METRICS = {
    'response_time_threshold': 200,  # milliseconds
    'max_database_queries': 50,
    'cache_hit_ratio': 0.8,
}

# Test Environment Variables
TEST_ENV_VARS = {
    'DJANGO_SETTINGS_MODULE': 'breaksphere.settings_test',
    'DJANGO_DEBUG': 'False',
    'DJANGO_SECRET_KEY': 'test-secret-key',
    'POSTGRES_DB': 'breaksphere_test',
    'REDIS_URL': 'redis://localhost:6379/1',
}

# Test Feature Flags
TEST_FEATURES = {
    'ENABLE_WEBSOCKETS': True,
    'ENABLE_NOTIFICATIONS': True,
    'ENABLE_ANALYTICS': False,
    'ENABLE_CACHING': True,
}

# Test Rate Limits
RATE_LIMITS = {
    'login_attempts': '5/minute',
    'api_requests': '100/hour',
    'websocket_messages': '60/minute',
}

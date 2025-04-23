import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta
from django.utils import timezone

# Base directory for fixtures
FIXTURES_DIR = Path(__file__).parent / 'fixtures_data'
FIXTURES_DIR.mkdir(exist_ok=True)

def load_fixture(filename: str) -> Dict[str, Any]:
    """Load fixture data from JSON file."""
    filepath = FIXTURES_DIR / filename
    if not filepath.exists():
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)

def save_fixture(filename: str, data: Dict[str, Any]) -> None:
    """Save fixture data to JSON file."""
    filepath = FIXTURES_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

# User Fixtures
def create_user_fixtures() -> Dict[str, Any]:
    """Create user fixtures."""
    return {
        'regular_user': {
            'username': 'regular_user',
            'email': 'regular@example.com',
            'password': 'testpass123',
            'first_name': 'Regular',
            'last_name': 'User',
            'is_active': True,
            'date_joined': timezone.now().isoformat(),
        },
        'admin_user': {
            'username': 'admin_user',
            'email': 'admin@example.com',
            'password': 'adminpass123',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'date_joined': timezone.now().isoformat(),
        },
        'inactive_user': {
            'username': 'inactive_user',
            'email': 'inactive@example.com',
            'password': 'testpass123',
            'is_active': False,
            'date_joined': timezone.now().isoformat(),
        },
    }

# Status Fixtures
def create_status_fixtures() -> Dict[str, Any]:
    """Create status fixtures."""
    return {
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
            'auto_reset_after': 30,
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

# Room Fixtures
def create_room_fixtures() -> Dict[str, Any]:
    """Create room fixtures."""
    return {
        'general': {
            'title': 'General',
            'description': 'General discussion room',
            'room_type': 'public',
            'icon_url': 'https://example.com/icons/general.png',
            'is_official': True,
            'max_members': 0,
        },
        'random': {
            'title': 'Random',
            'description': 'Random discussions and fun',
            'room_type': 'public',
            'icon_url': 'https://example.com/icons/random.png',
            'is_official': True,
            'max_members': 0,
        },
        'private_room': {
            'title': 'Private Room',
            'description': 'Private discussion room',
            'room_type': 'private',
            'icon_url': 'https://example.com/icons/private.png',
            'is_official': False,
            'max_members': 10,
        },
    }

# Event Fixtures
def create_event_fixtures() -> Dict[str, Any]:
    """Create event fixtures."""
    now = timezone.now()
    return {
        'coffee_meetup': {
            'title': 'Virtual Coffee Meetup',
            'description': 'Join us for a virtual coffee break!',
            'event_type': 'social',
            'start_time': (now + timedelta(days=1)).isoformat(),
            'end_time': (now + timedelta(days=1, hours=1)).isoformat(),
            'is_virtual': True,
            'join_url': 'https://meet.example.com/coffee',
            'max_participants': 10,
        },
        'game_night': {
            'title': 'Game Night',
            'description': 'Fun and games with colleagues',
            'event_type': 'game',
            'start_time': (now + timedelta(days=2)).isoformat(),
            'end_time': (now + timedelta(days=2, hours=2)).isoformat(),
            'is_virtual': True,
            'join_url': 'https://meet.example.com/games',
            'max_participants': 20,
        },
    }

# Post Fixtures
def create_post_fixtures() -> Dict[str, Any]:
    """Create post fixtures."""
    return {
        'text_post': {
            'content': 'This is a test post',
            'post_type': 'text',
            'visibility': 'public',
        },
        'poll_post': {
            'content': 'What is your favorite programming language?',
            'post_type': 'poll',
            'visibility': 'public',
            'options': [
                'Python',
                'JavaScript',
                'Java',
                'Other',
            ],
        },
    }

# Icebreaker Fixtures
def create_icebreaker_fixtures() -> Dict[str, Any]:
    """Create icebreaker fixtures."""
    return {
        'categories': {
            'tech': {
                'name': 'Technology',
                'description': 'Tech-related questions',
                'icon': 'fa-laptop-code',
            },
            'fun': {
                'name': 'Fun',
                'description': 'Fun and casual questions',
                'icon': 'fa-smile',
            },
        },
        'questions': {
            'tech_easy': {
                'category': 'tech',
                'question_text': 'What was your first programming language?',
                'difficulty': 'easy',
            },
            'fun_easy': {
                'category': 'fun',
                'question_text': 'If you could have any superpower, what would it be?',
                'difficulty': 'easy',
            },
        },
    }

# Chat Message Fixtures
def create_message_fixtures() -> Dict[str, Any]:
    """Create chat message fixtures."""
    return {
        'text_message': {
            'content': 'Hello, everyone!',
            'message_type': 'text',
        },
        'system_message': {
            'content': 'User joined the room',
            'message_type': 'system',
        },
    }

# Create all fixtures
def create_all_fixtures() -> None:
    """Create all fixtures and save them to files."""
    fixtures = {
        'users.json': create_user_fixtures(),
        'statuses.json': create_status_fixtures(),
        'rooms.json': create_room_fixtures(),
        'events.json': create_event_fixtures(),
        'posts.json': create_post_fixtures(),
        'icebreakers.json': create_icebreaker_fixtures(),
        'messages.json': create_message_fixtures(),
    }
    
    for filename, data in fixtures.items():
        save_fixture(filename, data)

# Load all fixtures
def load_all_fixtures() -> Dict[str, Any]:
    """Load all fixtures from files."""
    return {
        'users': load_fixture('users.json'),
        'statuses': load_fixture('statuses.json'),
        'rooms': load_fixture('rooms.json'),
        'events': load_fixture('events.json'),
        'posts': load_fixture('posts.json'),
        'icebreakers': load_fixture('icebreakers.json'),
        'messages': load_fixture('messages.json'),
    }

if __name__ == '__main__':
    create_all_fixtures()

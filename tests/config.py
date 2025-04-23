"""
Test Configuration
=================

Configuration settings for the BreakSphere test suite.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Base test directory
TEST_DIR = Path(__file__).parent

# Test data directory for fixtures and resources
TEST_DATA_DIR = TEST_DIR / 'data'
TEST_DATA_DIR.mkdir(exist_ok=True)

# Test output directory for reports and logs
TEST_OUTPUT_DIR = TEST_DIR / 'output'
TEST_OUTPUT_DIR.mkdir(exist_ok=True)

# Test media directory for uploaded files during tests
TEST_MEDIA_DIR = TEST_OUTPUT_DIR / 'media'
TEST_MEDIA_DIR.mkdir(exist_ok=True)

# Test static directory for collected static files during tests
TEST_STATIC_DIR = TEST_OUTPUT_DIR / 'static'
TEST_STATIC_DIR.mkdir(exist_ok=True)

# Test log directory
TEST_LOG_DIR = TEST_OUTPUT_DIR / 'logs'
TEST_LOG_DIR.mkdir(exist_ok=True)

# Test report directory
TEST_REPORT_DIR = TEST_OUTPUT_DIR / 'reports'
TEST_REPORT_DIR.mkdir(exist_ok=True)

# Test coverage directory
TEST_COVERAGE_DIR = TEST_OUTPUT_DIR / 'coverage'
TEST_COVERAGE_DIR.mkdir(exist_ok=True)

# Test environment settings
TEST_ENVIRONMENT = {
    'DEBUG': True,
    'TESTING': True,
    'SECRET_KEY': 'test-secret-key',
    'ALLOWED_HOSTS': ['*'],
    'DATABASE_URL': 'sqlite://:memory:',
    'REDIS_URL': 'redis://localhost:6379/1',
    'CELERY_BROKER_URL': 'memory://',
    'CELERY_RESULT_BACKEND': 'cache',
    'MEDIA_ROOT': str(TEST_MEDIA_DIR),
    'STATIC_ROOT': str(TEST_STATIC_DIR),
}

# Test database settings
TEST_DATABASE = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}

# Test cache settings
TEST_CACHE = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
}

# Test email settings
TEST_EMAIL = {
    'BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
}

# Test file storage settings
TEST_FILE_STORAGE = {
    'DEFAULT_FILE_STORAGE': 'django.core.files.storage.InMemoryStorage',
    'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.StaticFilesStorage',
}

# Test Celery settings
TEST_CELERY = {
    'CELERY_TASK_ALWAYS_EAGER': True,
    'CELERY_TASK_EAGER_PROPAGATES': True,
}

# Test Channels settings
TEST_CHANNELS = {
    'CHANNEL_LAYERS': {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    },
}

# Test authentication settings
TEST_AUTH = {
    'AUTH_USER_MODEL': 'accounts.User',
    'LOGIN_URL': '/login/',
    'LOGIN_REDIRECT_URL': '/',
    'LOGOUT_REDIRECT_URL': '/',
}

# Test REST framework settings
TEST_REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# Test logging settings
TEST_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': str(TEST_LOG_DIR / 'test.log'),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# Test runner settings
TEST_RUNNER = {
    'TEST_RUNNER': 'tests.runner.BreakSphereTestRunner',
    'PARALLEL_TESTS': int(os.getenv('TEST_PARALLEL_JOBS', 1)),
    'RERUN_FAILED_TESTS': int(os.getenv('TEST_RERUN_COUNT', 0)),
    'RANDOM_ORDER': bool(os.getenv('TEST_RANDOM_ORDER', False)),
    'FAIL_FAST': bool(os.getenv('TEST_FAIL_FAST', False)),
    'SLOW_TEST_THRESHOLD': float(os.getenv('TEST_SLOW_THRESHOLD', 0.5)),
}

# Test coverage settings
TEST_COVERAGE = {
    'COVERAGE_MODULE_EXCLUDES': [
        'tests.*',
        'migrations',
        'fixtures',
        'admin',
        'debug_toolbar',
    ],
    'COVERAGE_REPORT_HTML_OUTPUT_DIR': str(TEST_COVERAGE_DIR),
    'COVERAGE_USE_SUBPROCESS': True,
    'COVERAGE_REPORT_FAIL_UNDER': 80,
}

# Test timeout settings
TEST_TIMEOUTS = {
    'DEFAULT': 5,  # seconds
    'DATABASE': 2,
    'CACHE': 1,
    'HTTP': 3,
    'WEBSOCKET': 2,
    'CELERY': 5,
}

# Test rate limits
TEST_RATE_LIMITS = {
    'USER': '1000/hour',
    'ANON': '100/hour',
}

# Test feature flags
TEST_FEATURES = {
    'ENABLE_WEBSOCKETS': True,
    'ENABLE_CELERY': True,
    'ENABLE_CACHING': True,
    'ENABLE_EMAILS': False,
    'ENABLE_FILE_UPLOADS': True,
}

# Test constants
TEST_CONSTANTS = {
    'DEFAULT_PASSWORD': 'testpass123',
    'DEFAULT_EMAIL_DOMAIN': 'example.com',
    'DEFAULT_PHONE': '+1234567890',
    'DEFAULT_TIMEZONE': 'UTC',
}

# Test paths
TEST_PATHS = {
    'BASE': TEST_DIR,
    'DATA': TEST_DATA_DIR,
    'OUTPUT': TEST_OUTPUT_DIR,
    'MEDIA': TEST_MEDIA_DIR,
    'STATIC': TEST_STATIC_DIR,
    'LOGS': TEST_LOG_DIR,
    'REPORTS': TEST_REPORT_DIR,
    'COVERAGE': TEST_COVERAGE_DIR,
}

# Combine all settings
TEST_SETTINGS: Dict[str, Any] = {
    **TEST_ENVIRONMENT,
    'DATABASES': {'default': TEST_DATABASE},
    'CACHES': {'default': TEST_CACHE},
    'EMAIL': TEST_EMAIL,
    'FILE_STORAGE': TEST_FILE_STORAGE,
    'CELERY': TEST_CELERY,
    'CHANNELS': TEST_CHANNELS,
    'AUTH': TEST_AUTH,
    'REST_FRAMEWORK': TEST_REST_FRAMEWORK,
    'LOGGING': TEST_LOGGING,
    'TEST_RUNNER': TEST_RUNNER,
    'COVERAGE': TEST_COVERAGE,
    'TIMEOUTS': TEST_TIMEOUTS,
    'RATE_LIMITS': TEST_RATE_LIMITS,
    'FEATURES': TEST_FEATURES,
    'CONSTANTS': TEST_CONSTANTS,
    'PATHS': TEST_PATHS,
}

def get_test_setting(key: str, default: Any = None) -> Any:
    """Get a test setting by key."""
    return TEST_SETTINGS.get(key, default)

def update_test_setting(key: str, value: Any) -> None:
    """Update a test setting."""
    TEST_SETTINGS[key] = value

def reset_test_settings() -> None:
    """Reset test settings to defaults."""
    global TEST_SETTINGS
    TEST_SETTINGS = {
        **TEST_ENVIRONMENT,
        'DATABASES': {'default': TEST_DATABASE},
        'CACHES': {'default': TEST_CACHE},
        'EMAIL': TEST_EMAIL,
        'FILE_STORAGE': TEST_FILE_STORAGE,
        'CELERY': TEST_CELERY,
        'CHANNELS': TEST_CHANNELS,
        'AUTH': TEST_AUTH,
        'REST_FRAMEWORK': TEST_REST_FRAMEWORK,
        'LOGGING': TEST_LOGGING,
        'TEST_RUNNER': TEST_RUNNER,
        'COVERAGE': TEST_COVERAGE,
        'TIMEOUTS': TEST_TIMEOUTS,
        'RATE_LIMITS': TEST_RATE_LIMITS,
        'FEATURES': TEST_FEATURES,
        'CONSTANTS': TEST_CONSTANTS,
        'PATHS': TEST_PATHS,
    }

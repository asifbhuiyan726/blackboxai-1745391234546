"""
Test Logging Configuration
=========================

Logging configuration for the BreakSphere test suite.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .config import TEST_LOG_DIR

# Ensure log directory exists
TEST_LOG_DIR.mkdir(parents=True, exist_ok=True)

# Log file naming
def get_log_filename(prefix: str = 'test') -> str:
    """Generate a log filename with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.log"

# Logging formats
VERBOSE_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
SIMPLE_FORMAT = '%(levelname)s: %(message)s'
DEBUG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'

# Custom log levels
TEST_SETUP = 21
TEST_TEARDOWN = 22
TEST_FIXTURE = 23
TEST_ASSERTION = 24

# Register custom log levels
logging.addLevelName(TEST_SETUP, 'SETUP')
logging.addLevelName(TEST_TEARDOWN, 'TEARDOWN')
logging.addLevelName(TEST_FIXTURE, 'FIXTURE')
logging.addLevelName(TEST_ASSERTION, 'ASSERTION')

class TestLogger(logging.Logger):
    """Custom logger for test-specific logging."""
    
    def setup(self, msg: str, *args, **kwargs):
        """Log a test setup message."""
        self.log(TEST_SETUP, msg, *args, **kwargs)

    def teardown(self, msg: str, *args, **kwargs):
        """Log a test teardown message."""
        self.log(TEST_TEARDOWN, msg, *args, **kwargs)

    def fixture(self, msg: str, *args, **kwargs):
        """Log a test fixture message."""
        self.log(TEST_FIXTURE, msg, *args, **kwargs)

    def assertion(self, msg: str, *args, **kwargs):
        """Log a test assertion message."""
        self.log(TEST_ASSERTION, msg, *args, **kwargs)

# Register custom logger class
logging.setLoggerClass(TestLogger)

class TestLogHandler(logging.Handler):
    """Custom handler that maintains a buffer of log records."""
    
    def __init__(self):
        super().__init__()
        self.buffer = []

    def emit(self, record):
        """Store the log record in the buffer."""
        self.buffer.append(record)

    def get_logs(self) -> list:
        """Get all logged messages."""
        return [self.format(record) for record in self.buffer]

    def clear(self):
        """Clear the log buffer."""
        self.buffer = []

class TestFormatter(logging.Formatter):
    """Custom formatter that includes test-specific information."""
    
    def format(self, record):
        """Format the log record with additional test information."""
        # Add test name if available
        if hasattr(record, 'test_name'):
            record.msg = f"[{record.test_name}] {record.msg}"
        
        # Add test phase if available
        if hasattr(record, 'test_phase'):
            record.msg = f"({record.test_phase}) {record.msg}"
        
        return super().format(record)

def setup_test_logging(
    level: int = logging.DEBUG,
    filename: Optional[str] = None,
    format_string: Optional[str] = None
) -> Dict[str, Any]:
    """
    Set up logging configuration for tests.
    
    Args:
        level: The logging level to use
        filename: Optional specific log filename
        format_string: Optional specific format string
    
    Returns:
        Dict containing the logging configuration
    """
    if filename is None:
        filename = get_log_filename()
    
    if format_string is None:
        format_string = DEBUG_FORMAT

    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                '()': TestFormatter,
                'format': VERBOSE_FORMAT
            },
            'simple': {
                '()': TestFormatter,
                'format': SIMPLE_FORMAT
            },
            'debug': {
                '()': TestFormatter,
                'format': DEBUG_FORMAT
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'level': level
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': str(TEST_LOG_DIR / filename),
                'formatter': 'verbose',
                'level': level
            },
            'buffer': {
                'class': 'tests.logging.TestLogHandler',
                'formatter': 'debug',
                'level': level
            }
        },
        'loggers': {
            'tests': {
                'handlers': ['console', 'file', 'buffer'],
                'level': level,
                'propagate': False
            },
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False
            }
        }
    }

    return config

def get_test_logger(name: str) -> TestLogger:
    """Get a logger instance for tests."""
    return logging.getLogger(f"tests.{name}")

class LogCapture:
    """Context manager for capturing log output."""
    
    def __init__(self, logger_name: str = 'tests'):
        self.logger_name = logger_name
        self.handler = TestLogHandler()
        self.logger = logging.getLogger(logger_name)
        self.old_handlers = []

    def __enter__(self):
        """Start capturing logs."""
        self.old_handlers = self.logger.handlers[:]
        self.logger.handlers = [self.handler]
        return self.handler

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop capturing logs and restore original handlers."""
        self.logger.handlers = self.old_handlers

def log_test_result(
    test_name: str,
    result: bool,
    duration: float,
    error: Optional[Exception] = None
):
    """Log test result with details."""
    logger = get_test_logger('results')
    
    if result:
        logger.info(
            f"Test '{test_name}' passed in {duration:.3f}s"
        )
    else:
        logger.error(
            f"Test '{test_name}' failed in {duration:.3f}s",
            exc_info=error
        )

def configure_test_logging():
    """Configure logging for the test suite."""
    config = setup_test_logging()
    logging.config.dictConfig(config)

def clear_test_logs():
    """Clear all test log files."""
    for file in TEST_LOG_DIR.glob('*.log'):
        try:
            file.unlink()
        except OSError:
            pass

# Configure logging when module is imported
configure_test_logging()

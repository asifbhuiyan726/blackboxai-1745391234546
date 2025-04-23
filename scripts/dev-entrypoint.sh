#!/bin/bash

# Exit on error
set -e

# Function to wait for a service to be ready
wait_for_service() {
    local host="$1"
    local port="$2"
    local service="$3"
    
    echo "Waiting for $service to be ready..."
    
    while ! nc -z "$host" "$port"; do
        echo "$service is unavailable - sleeping"
        sleep 1
    done
    
    echo "$service is up and running!"
}

# Function to run Django management commands
run_django_commands() {
    echo "Running Django management commands..."
    
    # Collect static files
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    
    # Apply database migrations
    echo "Applying database migrations..."
    python manage.py migrate --noinput
    
    # Create cache tables
    echo "Creating cache tables..."
    python manage.py createcachetable
    
    # Load initial data if needed
    if [ -f "fixtures/initial_data.json" ]; then
        echo "Loading initial data..."
        python manage.py loaddata fixtures/initial_data.json
    fi
}

# Function to set up development environment
setup_dev_environment() {
    echo "Setting up development environment..."
    
    # Install pre-commit hooks
    if [ -f ".pre-commit-config.yaml" ]; then
        echo "Installing pre-commit hooks..."
        pre-commit install
    fi
    
    # Create necessary directories
    mkdir -p logs media staticfiles
    
    # Set correct permissions
    chown -R appuser:appuser logs media staticfiles
}

# Function to check system health
check_system_health() {
    echo "Checking system health..."
    
    # Check disk space
    df -h
    
    # Check memory usage
    free -m
    
    # Check Python environment
    python --version
    pip list
}

# Wait for required services
wait_for_service db 5432 "PostgreSQL"
wait_for_service redis 6379 "Redis"

# Set up development environment
setup_dev_environment

# Run Django commands
run_django_commands

# Check system health
check_system_health

# Start development server with hot reload
if [ "$1" = "runserver" ]; then
    echo "Starting development server..."
    python manage.py runserver 0.0.0.0:8000
    
# Start Celery worker
elif [ "$1" = "celery_worker" ]; then
    echo "Starting Celery worker..."
    celery -A breaksphere worker -l DEBUG
    
# Start Celery beat
elif [ "$1" = "celery_beat" ]; then
    echo "Starting Celery beat..."
    celery -A breaksphere beat -l DEBUG
    
# Start Jupyter notebook
elif [ "$1" = "jupyter" ]; then
    echo "Starting Jupyter notebook..."
    python manage.py shell_plus --notebook
    
# Start documentation server
elif [ "$1" = "docs" ]; then
    echo "Starting documentation server..."
    cd docs && make html && python -m http.server 7000
    
# Start test watcher
elif [ "$1" = "test_watch" ]; then
    echo "Starting test watcher..."
    ptw
    
# Run tests with coverage
elif [ "$1" = "test_coverage" ]; then
    echo "Running tests with coverage..."
    coverage run -m pytest
    coverage report
    coverage html
    
# Start debugger
elif [ "$1" = "debug" ]; then
    echo "Starting debugger..."
    python -m debugpy --listen 0.0.0.0:5678 manage.py runserver 0.0.0.0:8000 --noreload
    
# Start load testing
elif [ "$1" = "loadtest" ]; then
    echo "Starting load testing..."
    locust -f loadtests/locustfile.py --host=http://web:8000
    
# Start development shell
elif [ "$1" = "shell" ]; then
    echo "Starting development shell..."
    python manage.py shell_plus
    
# Run security checks
elif [ "$1" = "security_check" ]; then
    echo "Running security checks..."
    bandit -r . -ll -ii -x tests/
    safety check
    
# Default command
else
    echo "Starting default development server..."
    python manage.py runserver 0.0.0.0:8000
fi

# Keep the container running
exec "$@"

.PHONY: help install dev-install test lint format clean build run migrate shell coverage docs deploy

# Colors for terminal output
BLUE=\033[0;34m
GREEN=\033[0;32m
RED=\033[0;31m
YELLOW=\033[0;33m
NC=\033[0m # No Color

# Help command to list all available commands
help:
	@echo "${BLUE}BreakSphere Development Commands${NC}"
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@echo "Available commands:"
	@echo "${GREEN}install${NC}      - Install production dependencies"
	@echo "${GREEN}dev-install${NC}  - Install development dependencies"
	@echo "${GREEN}test${NC}         - Run tests"
	@echo "${GREEN}lint${NC}         - Run code linting"
	@echo "${GREEN}format${NC}       - Format code"
	@echo "${GREEN}clean${NC}        - Clean up temporary files"
	@echo "${GREEN}build${NC}        - Build Docker images"
	@echo "${GREEN}run${NC}          - Run development server"
	@echo "${GREEN}migrate${NC}      - Run database migrations"
	@echo "${GREEN}shell${NC}        - Open Django shell"
	@echo "${GREEN}coverage${NC}     - Run tests with coverage"
	@echo "${GREEN}docs${NC}         - Generate documentation"
	@echo "${GREEN}deploy${NC}       - Deploy to production"

# Installation commands
install:
	@echo "${BLUE}Installing production dependencies...${NC}"
	pip install -r requirements.txt

dev-install:
	@echo "${BLUE}Installing development dependencies...${NC}"
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

# Testing commands
test:
	@echo "${BLUE}Running tests...${NC}"
	pytest

lint:
	@echo "${BLUE}Running linters...${NC}"
	flake8 .
	mypy .
	pylint **/*.py
	bandit -r . -ll -ii -x tests/

format:
	@echo "${BLUE}Formatting code...${NC}"
	black .
	isort .

# Cleanup commands
clean:
	@echo "${BLUE}Cleaning up...${NC}"
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	rm -f coverage.xml
	rm -f .coverage
	rm -rf .tox/

# Docker commands
build:
	@echo "${BLUE}Building Docker images...${NC}"
	docker-compose build

run:
	@echo "${BLUE}Starting development server...${NC}"
	python manage.py runserver 0.0.0.0:8000

run-docker:
	@echo "${BLUE}Starting Docker containers...${NC}"
	docker-compose up

# Database commands
migrate:
	@echo "${BLUE}Running migrations...${NC}"
	python manage.py makemigrations
	python manage.py migrate

shell:
	@echo "${BLUE}Opening Django shell...${NC}"
	python manage.py shell_plus

# Coverage commands
coverage:
	@echo "${BLUE}Running tests with coverage...${NC}"
	coverage run -m pytest
	coverage report
	coverage html

# Documentation commands
docs:
	@echo "${BLUE}Generating documentation...${NC}"
	cd docs && make html

# Deployment commands
deploy:
	@echo "${BLUE}Deploying to production...${NC}"
	bash deploy.sh

# Development setup
setup: dev-install migrate
	@echo "${GREEN}Development environment setup complete!${NC}"
	@echo "Run 'make run' to start the development server"

# Create a new app
new-app:
	@read -p "Enter app name: " app_name; \
	python manage.py startapp $$app_name

# Database backup
backup:
	@echo "${BLUE}Creating database backup...${NC}"
	python manage.py dumpdata --exclude auth.permission --exclude contenttypes > backup.json

# Database restore
restore:
	@echo "${BLUE}Restoring database from backup...${NC}"
	python manage.py loaddata backup.json

# Celery commands
celery-worker:
	@echo "${BLUE}Starting Celery worker...${NC}"
	celery -A breaksphere worker -l INFO

celery-beat:
	@echo "${BLUE}Starting Celery beat...${NC}"
	celery -A breaksphere beat -l INFO

# Static files
collectstatic:
	@echo "${BLUE}Collecting static files...${NC}"
	python manage.py collectstatic --noinput

# Security checks
security-check:
	@echo "${BLUE}Running security checks...${NC}"
	bandit -r . -ll -ii -x tests/
	safety check

# Performance checks
check-performance:
	@echo "${BLUE}Checking performance...${NC}"
	python manage.py check --deploy
	python manage.py validate_templates
	python manage.py check --database default

# Create superuser
createsuperuser:
	@echo "${BLUE}Creating superuser...${NC}"
	python manage.py createsuperuser

# Show URLs
show-urls:
	@echo "${BLUE}Showing URL patterns...${NC}"
	python manage.py show_urls

# Check migrations
check-migrations:
	@echo "${BLUE}Checking migrations...${NC}"
	python manage.py makemigrations --check --dry-run

# Run all checks
check-all: lint test security-check check-performance check-migrations
	@echo "${GREEN}All checks completed!${NC}"

# Production deployment checks
pre-deploy-check:
	@echo "${BLUE}Running pre-deployment checks...${NC}"
	python manage.py check --deploy
	python manage.py check --database default
	python manage.py validate_templates
	python manage.py collectstatic --dry-run
	@echo "${GREEN}Pre-deployment checks completed!${NC}"

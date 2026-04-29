.PHONY: help install migrate migrations test run shell workers beat clean lint format check-env m-migrate setup

# Переменные
PORT ?= 8000
PYTHON = poetry run python
CELERY = poetry run celery

# Default target - show help
help:
	@echo "FrutiShop Django Makefile - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "Environment Setup:"
	@echo "  make install           - Install dependencies with Poetry"
	@echo "  make check-env         - Verify .env file exists"
	@echo ""
	@echo "Database & Migrations:"
	@echo "  make migrate           - Apply all pending migrations"
	@echo "  make migrations        - Create new migrations from model changes"
	@echo "  make m-migrate         - Create and apply migrations in one command"
	@echo "  make showmigrations    - Show migration status"
	@echo ""
	@echo "Development Server:"
	@echo "  make run               - Start server (default port 8000, use PORT=9000 to change)"
	@echo "  make shell             - Start Django shell"
	@echo ""
	@echo "Celery Tasks:"
	@echo "  make worker            - Start Celery worker"
	@echo "  make beat              - Start Celery beat"
	@echo "  make worker-beat       - Start Celery worker with beat"
	@echo ""
	@echo "Utilities:"
	@echo "  make createsuperuser   - Create admin superuser"
	@echo "  make format            - Format code with black"
	@echo "  make clean             - Remove cache files"
	@echo "  make flush             - Clear database (DANGER!)"

# ============ Environment Setup ============

install:
	@echo "Installing dependencies..."
	poetry install
	@echo "✅ Dependencies installed"

check-env:
	@if [ -f .env ]; then \
		echo "✅ .env file found"; \
	else \
		echo "❌ .env file not found!"; \
		echo "Create .env file with required variables (DEBUG, SECRET_KEY, DB settings, etc.)"; \
		exit 1; \
	fi

# ============ Database & Migrations ============

migrate:
	@echo "Applying migrations..."
	$(PYTHON) manage.py migrate
	@echo "✅ Migrations applied"

migrations:
	@echo "Creating migrations..."
	$(PYTHON) manage.py makemigrations
	@echo "✅ Migrations created"

m-migrate: migrations migrate

showmigrations:
	$(PYTHON) manage.py showmigrations

sqlmigrate:
	@if [ -z "$(APP)" ] || [ -z "$(MIGRATION)" ]; then \
		echo "Error: Use with APP=app_name MIGRATION=0001"; \
		exit 1; \
	fi
	$(PYTHON) manage.py sqlmigrate $(APP) $(MIGRATION)

# ============ Development Server ============

run: check-env
	@echo "Starting server on port $(PORT)..."
	$(PYTHON) manage.py runserver 0.0.0.0:$(PORT)

shell:
	$(PYTHON) manage.py shell

# ============ Celery Tasks ============

worker:
	$(CELERY) -A config worker -l info

beat:
	$(CELERY) -A config beat -l info

worker-beat:
	$(CELERY) -A config worker -l info --beat

# ============ User Management ============

createsuperuser:
	$(PYTHON) manage.py createsuperuser

# ============ Testing & Quality ============

test:
	$(PYTHON) manage.py test

format:
	poetry run black src/ config/ manage.py

lint:
	poetry run flake8 src/ config/ --max-line-length=120

# ============ Utilities ============

clean:
	@echo "Cleaning cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned"

flush:
	@echo "WARNING: This will DELETE all data!"
	@read -p "Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		$(PYTHON) manage.py flush; \
	else \
		echo "Cancelled"; \
	fi

setup: install check-env migrate createsuperuser
	@echo "✅ Setup complete! Use 'make run' to start."
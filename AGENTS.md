# FrutiShop - AI Coding Agent Guide

## Project Overview
FrutiShop is an e-commerce platform built with **Django 5.0+**, Celery, Redis, and WebSocket support via Channels. It's a fruit trading/shop application designed with modular Django apps. The project is in early development with a custom User model and multi-service architecture.

**Stack**: Python 3.12.3, Django 5.0+, PostgreSQL, Celery, Redis, Django Ninja, Channels  
**Package Manager**: Poetry  

---

## Architecture & Key Components

### Project Structure Pattern
- **Config Layer**: `/config/` - Django settings, ASGI, WSGI, URL routing
- **Apps Layer**: `/src/` - All Django apps live here (not in root)
  - Each app follows standard Django structure: `models.py`, `views.py`, `admin.py`, `tests.py`, `migrations/`
  - Apps: `users`, `actions`, `trading`, `communication`, `authorization`
- **Settings**: Environment variables via dotenv (`.env` file required for local dev)

### Critical Path System Design
1. **Custom User Model** (`src/user/models.py`): Extends `AbstractUser` - always import this, not Django's built-in User
2. **Database**: PostgreSQL (configured in `config/settings.py` via env vars: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`)
3. **Async Tasks**: Celery + Redis for background jobs
4. **Real-time**: Channels for WebSocket support (ASGI configured but not yet integrated)
5. **API Layer**: Django Ninja planned for modern API endpoints (currently only admin URLs registered)

### App Responsibilities (Intended)
- **users**: User profile and authentication management
- **trading**: Marketplace/shop transaction logic
- **communication**: User messaging and notifications (has Message model)
- **actions**: User activity tracking and events
- **authorization**: Permission and access control logic

---

## Developer Workflows & Commands

### Setup & Dependencies
```bash
# Install dependencies with Poetry
poetry install

# Create virtual environment and load it
poetry shell  # or: poetry env use 3.12.3

# Load environment variables
cp .env.example .env  # Create with: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, CELERY_BROKER_URL, DEBUG, SECRET_KEY, ALLOWED_HOSTS
source .env  # or manually set vars
```

### Running the Project
```bash
# Run development server
python manage.py runserver

# Run Celery worker
celery -A config worker -l info

# Run Celery beat (scheduled tasks)
celery -A config beat -l info

# Run WebSocket server (Channels)
# Not yet configured - requires daphne or similar ASGI server

# Migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access admin
# http://localhost:8000/admin/
```

### Testing
```bash
# All tests
python manage.py test

# Specific app tests
python manage.py test src.users
```

---

## Critical Conventions & Patterns

### Import Paths
- **Apps are under `/src/`**: Always import as `from src.user.models import User`, not `from user.models`
- **Settings path modification**: `config/settings.py` modifies `sys.path` to add `/src/` - this is non-standard but required
- **Settings module**: Always set `DJANGO_SETTINGS_MODULE=config.settings` when running management commands

### Model Creation & Relationships
- When creating new models, import custom User: `from src.user.models import User`
- Use `ForeignKey(User, on_delete=models.CASCADE, related_name='...')` pattern
- Add `__str__()` and `Meta` classes with `verbose_name` and `verbose_name_plural` for admin UI

### Environment Variables Required
```
DEBUG=True|False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=frutishop_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Media & Static Files Configuration
- Static files: `/static/` (development only)
- Media uploads: `/media/` (created at runtime)
- Templates: Not yet configured in DIRS, relies on app `templates/` convention

---

## Integration Points & Dependencies

### Redis Usage (Current & Planned)
- **Celery Broker/Result Backend**: Primary use (required for async tasks)
- **Caching**: Can be extended with cache framework
- **Sessions**: Can be configured to use Redis instead of database

### PostgreSQL Schema Pattern
- Uses Django ORM migrations exclusively - never write direct SQL
- `BigAutoField` as default primary key
- Foreign keys use `CASCADE` delete strategy by default

### Celery Integration
- Broker: Redis
- Serializer: JSON (configured explicitly in settings)
- No tasks defined yet - new tasks go in `tasks.py` files within apps

### Django Ninja (Prepared but Not Yet Used)
- Installed but not integrated into URLs yet
- Pattern: Create API routers in app `api.py` and register in `config/urls.py`
- Example endpoint pattern:
  ```python
  # app/api.py
  from ninja import Router
  router = Router()
  
  @router.get("/items/")
  def list_items(request):
      return {"items": [...]}
  ```

---

## Immediate Considerations for Agent Tasks

### Before Adding Features
1. **Verify app placement**: Is this feature in the right `/src/` app?
2. **Check custom User import**: Don't use Django's default User model
3. **Update migrations**: Always run migrations after model changes
4. **Test paths**: Use full import paths with `/src/` prefix

### Common Pitfalls
- ❌ Forgetting to import from `src.user.models` instead of Django's User
- ❌ Not running `makemigrations` → `migrate` after model changes
- ❌ Not setting `DJANGO_SETTINGS_MODULE` before running manage.py
- ❌ Pushing `.env` to git (already in `.gitignore`)
- ❌ Trying to use Django Ninja endpoints without registering routers in `config/urls.py`

### References
- Django: https://docs.djangoproject.com/en/5.2/
- Django Ninja: https://django-ninja.rest-framework.com/
- Celery: https://docs.celeryproject.org/
- Channels: https://channels.readthedocs.io/
- Poetry: https://python-poetry.io/


# Backend Architecture Guide

## Layer Architecture

```text
HTTP Request
  -> Routers
  -> Controllers
  -> Services
  -> Models
  -> PostgreSQL
```

This backend now has the same layers claimed in the documentation and represented in the codebase.

## Layer Responsibilities

### Routers (`app/routers/`)

- Define URL paths and HTTP methods
- Declare FastAPI dependencies
- Attach request/response schemas
- Keep route handlers thin
- Delegate request handling to controllers

Files:

- `auth.py`
- `users.py`
- `projects.py`
- `tasks.py`
- `dashboard.py`

### Controllers (`app/controllers/`)

- Orchestrate request-specific flows
- Convert service outcomes into HTTP responses
- Raise HTTP exceptions where needed
- Resolve authenticated users
- Keep routers from directly owning business flow

Files:

- `auth_controller.py`
- `user_controller.py`
- `project_controller.py`
- `task_controller.py`
- `dashboard_controller.py`

Example:

```python
async def login(credentials: UserLogin, db: AsyncSession) -> TokenResponse:
    user = await UserService.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(...)
```

### Services (`app/services/`)

- Business logic
- Authorization checks
- Cross-entity operations
- Database query orchestration

Files:

- `user_service.py`
- `project_service.py`
- `task_service.py`

### Models (`app/models/`)

- SQLAlchemy ORM models
- Table relationships
- Constraints and indexes

Main file:

- `models.py`

### Schemas (`app/schemas/`)

- Pydantic request validation
- Response serialization
- API typing

Main file:

- `schemas.py`

### Core (`app/core/`)

- Application settings
- Database session management
- JWT and password utilities
- Rate limiting middleware

Files:

- `config.py`
- `database.py`
- `security.py`
- `rate_limiter.py`

## Request Flow Example

Creating a task:

```text
POST /api/v1/tasks/
  -> routers/tasks.py validates the route and dependencies
  -> controllers/task_controller.py coordinates the request
  -> services/task_service.py validates business rules
  -> models/models.py persists the task
  -> TaskResponse is returned to the client
```

## Authentication Flow

```text
User sends email/password
  -> Auth router
  -> Auth controller
  -> UserService.authenticate_user()
  -> bcrypt password verification
  -> JWT access and refresh token generation
  -> Frontend stores token and sends Authorization: Bearer <token>
```

The `get_current_user` dependency reads the `Authorization` header, decodes the JWT, and loads the current user from the database.

## Database Migrations

Alembic is configured in:

- `alembic.ini`
- `migrations/env.py`
- `migrations/versions/20260501_0001_initial_schema.py`

Apply migrations:

```bash
cd team-task-manager-backend
alembic upgrade head
```

Create future migrations:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

The Railway `Procfile` runs migrations before starting the backend:

```text
web: alembic upgrade head && gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:$PORT
```

## Security Hardening

Implemented:

- JWT access tokens
- Refresh tokens
- bcrypt password hashing
- CORS allow-listing
- SQL injection protection through SQLAlchemy
- Basic in-memory API rate limiting

Rate limiter settings:

```env
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
```

The current limiter is suitable for demo and assignment review. For multi-instance production, replace it with Redis or an API gateway limiter.

## Deployment Checklist

- [ ] Public GitHub repository created
- [ ] Railway PostgreSQL provisioned
- [ ] Backend deployed on Railway
- [ ] `DATABASE_URL` configured
- [ ] `SECRET_KEY` changed
- [ ] `DEBUG=False`
- [ ] `ALLOWED_ORIGINS` set to the live frontend URL
- [ ] `alembic upgrade head` completed during deploy
- [x] Rate limiting middleware enabled
- [ ] Frontend deployed
- [ ] README Submission Links updated with live URLs

## Production Notes

- Keep Alembic migrations committed with every schema change.
- Do not submit placeholder live URLs.
- Use a distributed rate limiter if the backend runs more than one instance.
- Keep secrets in Railway environment variables, not in source code.

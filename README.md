# Team Task Manager

A full-stack task management application for teams, built with FastAPI, React/Vite, PostgreSQL, SQLAlchemy, and Tailwind CSS.

## Submission Links

Assignment submission requires all three links below. Replace these values after deploying.

| Item | URL |
| --- | --- |
| Live Frontend | `https://team-task-manager-eta-neon.vercel.app` |
| Live Backend API | `https://team-task-manager-mygg.onrender.com/api/v1` |
| API Docs | `https://team-task-manager-mygg.onrender.com/docs` |
| Public GitHub Repo | `PASTE_PUBLIC_GITHUB_REPO_URL_HERE` |

Do not submit while these placeholders are still present.

## Features

- JWT authentication with refresh tokens
- Password hashing with bcrypt
- Projects with team members
- Task CRUD with priority, status, due date, search, and overdue views
- Dashboard statistics with charts
- Protected frontend routes
- Dark and light mode
- Responsive React UI
- FastAPI Swagger documentation
- Basic in-memory API rate limiting
- Alembic database migrations

## Tech Stack

**Backend:** FastAPI, SQLAlchemy async ORM, PostgreSQL, Pydantic, PyJWT, Alembic, Uvicorn/Gunicorn

**Frontend:** React 18, Vite, Tailwind CSS, React Router, Axios, Recharts, Lucide React

**Deployment:** Railway for backend and database; Railway or Vercel for frontend

## Architecture

```text
HTTP request
  -> Routers: route paths, methods, dependencies, response models
  -> Controllers: request orchestration and HTTP-specific decisions
  -> Services: business logic and authorization rules
  -> Models: SQLAlchemy entities and relationships
  -> PostgreSQL
```

Backend folders:

```text
team-task-manager-backend/
  app/
    controllers/       # Request orchestration layer
    routers/           # FastAPI route declarations
    services/          # Business logic
    models/            # SQLAlchemy models
    schemas/           # Pydantic request/response schemas
    core/              # Config, security, database, rate limiter
    main.py            # FastAPI app setup
  migrations/          # Alembic migrations
  alembic.ini
  Procfile
  requirements.txt
```

Frontend folders:

```text
team-task-manager-frontend/
  src/
    pages/
    components/
    context/
    hooks/
    services/
    styles/
```

## Local Setup

### Backend

Use Python 3.11 for the backend. Python 3.14 is not recommended for this dependency set because some packages may need native compilation on Windows.

```bash
cd team-task-manager-backend
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --reload-dir app --reload-dir migrations --reload-exclude "venv/*" --reload-exclude "venv\\*" --host 0.0.0.0 --port 8000
```

`0.0.0.0` is only the server bind address. Open the app in your browser using `http://localhost:8000` or `http://127.0.0.1:8000`, not `http://0.0.0.0:8000`.

If the Windows file watcher still reacts to virtualenv package files, run without reload:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API docs:

```text
http://localhost:8000/docs
```

### Frontend

```bash
cd team-task-manager-frontend
npm install
copy .env.example .env
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

## Database Migrations

Alembic is configured in `team-task-manager-backend/alembic.ini`.

Apply migrations:

```bash
cd team-task-manager-backend
alembic upgrade head
```

Create a new migration after changing models:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

The Railway `Procfile` runs migrations before starting the backend:

```text
web: alembic upgrade head && gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:$PORT
```

## Rate Limiting

The backend includes a lightweight in-memory rate limiter:

```text
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
```

This is enough for assignment/demo hardening. For production across multiple instances, replace it with Redis or an API gateway limiter.

## Environment Variables

Backend `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/team_task_manager
SECRET_KEY=change-this-to-a-strong-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=False
ENVIRONMENT=production
ALLOWED_ORIGINS=["https://your-frontend-domain.com"]
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
```

Frontend `.env`:

```env
VITE_API_URL=https://your-backend-domain.com/api/v1
```

## API Endpoints

Authentication:

- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`

Projects:

- `GET /api/v1/projects/`
- `POST /api/v1/projects/`
- `GET /api/v1/projects/{project_id}`
- `PUT /api/v1/projects/{project_id}`
- `DELETE /api/v1/projects/{project_id}`
- `POST /api/v1/projects/{project_id}/members`
- `DELETE /api/v1/projects/{project_id}/members/{member_id}`
- `GET /api/v1/projects/{project_id}/progress`

Tasks:

- `GET /api/v1/tasks/`
- `POST /api/v1/tasks/`
- `GET /api/v1/tasks/{task_id}`
- `PUT /api/v1/tasks/{task_id}`
- `DELETE /api/v1/tasks/{task_id}`
- `GET /api/v1/tasks/project/{project_id}`
- `GET /api/v1/tasks/search/{project_id}?q=keyword`
- `GET /api/v1/tasks/overdue`

Dashboard:

- `GET /api/v1/dashboard/stats`

## Deployment Checklist

- Push public GitHub repository
- Create Railway PostgreSQL database
- Deploy backend on Railway
- Set backend environment variables
- Confirm `alembic upgrade head` runs during deploy
- Deploy frontend on Railway or Vercel
- Set `VITE_API_URL` to the live backend API URL
- Set backend `ALLOWED_ORIGINS` to the live frontend URL
- Paste live URLs into the Submission Links table

## Verification

Backend:

```bash
cd team-task-manager-backend
python -m compileall app
```

Frontend:

```bash
cd team-task-manager-frontend
npm run build
```

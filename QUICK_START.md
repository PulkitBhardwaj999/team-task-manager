# ⚡ Quick Start Guide

Get Team Task Manager running in 5 minutes!

## Prerequisites

- Python 3.11
- Node.js 16+
- PostgreSQL 12+
- Git

## Option 1: Local Setup (Development)

### Backend (3 minutes)

```bash
# 1. Navigate to backend
cd team-task-manager-backend

# 2. Create virtual environment
py -3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Update DATABASE_URL if needed (default: postgres://postgres@localhost/team_task_manager)

# 5. Apply database migrations
alembic upgrade head

# 6. Run server
uvicorn app.main:app --reload --reload-dir app --reload-dir migrations --reload-exclude "venv/*" --reload-exclude "venv\\*" --host 0.0.0.0 --port 8000
```

**Backend running at:** http://localhost:8000
- API Docs: http://localhost:8000/docs

**Live backend (deployed):** https://team-task-manager-mygg.onrender.com
- API Docs: https://team-task-manager-mygg.onrender.com/docs

Note: `0.0.0.0` is only the server bind address. In the browser, use `http://localhost:8000` or `http://127.0.0.1:8000`.

### Frontend (2 minutes)

```bash
# 1. In new terminal, navigate to frontend
cd team-task-manager-frontend

# 2. Install dependencies
npm install

# 3. Create .env file (optional for local dev)
cp .env.example .env

# 4. Start dev server
npm run dev
```

**Frontend running at:** http://localhost:5173

**Live frontend (deployed):** https://team-task-manager-eta-neon.vercel.app

### Test the App

1. Open http://localhost:5173
2. Click "Sign Up" or use demo login:
   - Email: `admin@example.com`
   - Password: `password123`
3. Explore the dashboard!

---

## Option 2: Docker Setup

### With Docker Compose

```bash
# 1. Create docker-compose.yml in root directory
cd team-task-manager

# 2. Run containers
docker-compose up -d

# 3. Access services:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# Database: localhost:5432
```

---

## Option 3: Production Deployment (Railway)

### Deploy Backend

```bash
# 1. Prepare backend code
cd team-task-manager-backend
git init && git add . && git commit -m "Initial"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/team-task-manager-backend
git push -u origin main

# 2. Go to Railway.app
# - Click "New Project"
# - Connect GitHub repo
# - Set environment variables:
#   - DATABASE_URL
#   - SECRET_KEY
#   - ENVIRONMENT=production
# - Deploy!
```

### Deploy Frontend

```bash
# 1. Prepare frontend code
cd team-task-manager-frontend
git init && git add . && git commit -m "Initial"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/team-task-manager-frontend
git push -u origin main

# 2. Go to Vercel or Railway
# - Connect GitHub repo
# - Set environment:
#   - VITE_API_URL=https://your-backend-url/api/v1
# - Deploy!
```

---


## Database Setup

### PostgreSQL Local

```bash
# Windows/Mac/Linux - Using postgresql
createdb team_task_manager

# Or using Docker
docker run -d \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15
```

### Connection String

```
PostgreSQL (sync):
postgresql://postgres:postgres@localhost:5432/team_task_manager

PostgreSQL (async):
postgresql+asyncpg://postgres:postgres@localhost:5432/team_task_manager
```

Tables are auto-created on first API request!

---

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/team_task_manager

# Security
SECRET_KEY=your-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
DEBUG=True
ENVIRONMENT=development
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## Useful Commands

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --reload-dir app --reload-dir migrations --reload-exclude "venv/*" --reload-exclude "venv\\*"

# If Windows still watches virtualenv files, run without reload
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run production server
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4

# Database migrations
alembic upgrade head

# Create migrations when schema changes
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Frontend

```bash
# Install dependencies
npm install

# Start development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

---

## API Examples

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123"}'

# Response: {
#   "access_token": "eyJ...",
#   "refresh_token": "eyJ...",
#   "token_type": "bearer"
# }
```

### Create Project

```bash
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"My Project","description":"Description"}'
```

### Create Task

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "project_id":1,
    "title":"My Task",
    "description":"Task description",
    "priority":"high",
    "due_date":"2024-12-31T23:59:59"
  }'
```

---

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# macOS/Linux
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Database connection error:**
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Update DATABASE_URL in .env
```

**Module not found:**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Frontend Issues

**Port 5173 already in use:**
```bash
# Change port in vite.config.js or
npm run dev -- --port 3000
```

**API connection error:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Update VITE_API_URL in .env
```

**Build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## Performance Tips

### Backend
- Use async/await for I/O operations
- Add database indexes for frequently queried fields
- Implement caching for dashboard stats
- Use connection pooling

### Frontend
- Enable gzip compression
- Use code splitting
- Lazy load routes
- Optimize images
- Use ServiceWorker caching

---

## Security Best Practices

- ✅ Change `SECRET_KEY` in production
- ✅ Use HTTPS in production
- ✅ Set `DEBUG=False` in production
- ✅ Validate all inputs
- ✅ Use environment variables for secrets
- ✅ Enable CORS only for trusted origins
- ✅ Implement rate limiting
- ✅ Use strong passwords

---

## File Structure Quick Reference

```
team-task-manager/
├── team-task-manager-backend/
│   ├── app/
│   │   ├── core/          # Config, security, database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── routers/       # API endpoints
│   │   └── main.py        # FastAPI app
│   ├── requirements.txt
│   └── .env
│
├── team-task-manager-frontend/
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   ├── services/      # API calls
│   │   ├── context/       # Auth context
│   │   ├── hooks/         # Custom hooks
│   │   ├── styles/        # Global CSS
│   │   └── App.jsx
│   ├── package.json
│   └── .env
│
├── README.md              # Main documentation
├── DEPLOYMENT_GUIDE.md    # Deployment instructions
├── DEMO_SCRIPT.md         # Demo walkthrough
├── BACKEND_ARCHITECTURE.md
└── FRONTEND_ARCHITECTURE.md
```

---

## Next Steps

1. ✅ Run both backend and frontend locally
2. ✅ Create a test project
3. ✅ Create test tasks
4. ✅ Explore the dashboard
5. ✅ Read the architecture guides
6. ✅ Deploy to production
7. ✅ Set up monitoring and backups

---

## Useful Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com
- **PostgreSQL**: https://www.postgresql.org/docs
- **Railway Docs**: https://docs.railway.app

---

## Support & Questions

- Read the full [README.md](./README.md)
- Check [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for production setup
- Review [BACKEND_ARCHITECTURE.md](./BACKEND_ARCHITECTURE.md)
- Review [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md)

---

**Happy coding! 🚀**

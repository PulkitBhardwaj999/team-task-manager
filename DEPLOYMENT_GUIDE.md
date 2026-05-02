# 🚀 Team Task Manager - Deployment Guide

Complete step-by-step guide for deploying to production using Railway.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Post-Deployment](#post-deployment)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

- GitHub account
- Railway account (https://railway.app)
- PostgreSQL database (or use Railway Postgres)
- Domain name (optional)

## Database Setup

### Option 1: Railway PostgreSQL

1. Go to https://railway.app
2. Create new project → PostgreSQL
3. Wait for deployment
4. Copy connection string from Variables tab
5. Use this as `DATABASE_URL`

**Connection String Format:**
```
postgresql://[user]:[password]@[host]:[port]/[database]
# For async:
postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]
```

### Option 2: External PostgreSQL

Use your existing PostgreSQL provider (AWS RDS, Azure, DigitalOcean, etc.)

---

## Backend Deployment

### Step 1: Prepare Backend Code

1. **Update dependencies** (if needed)
   ```bash
   pip freeze > requirements.txt
   ```

2. **Create Procfile** in backend root:
   ```
   web: gunicorn app.main:app -w 4 -b 0.0.0.0:$PORT
   ```

3. **Add gunicorn to requirements.txt**
   ```
   gunicorn==21.2.0
   ```

4. **Create runtime.txt** (included, specifies Python version):
   ```
   python-3.11.9
   ```

### Step 2: Push to GitHub

```bash
cd team-task-manager-backend
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/team-task-manager-backend.git
git push -u origin main
```

### Step 3: Deploy on Railway

1. Go to https://railway.app
2. Click "Create New Project"
3. Select "Deploy from GitHub repo"
4. Authorize GitHub and select your backend repo
5. Railway will auto-detect FastAPI
6. Click "Deploy"

### Step 4: Configure Environment Variables

In Railway dashboard → Variables tab:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/db
SECRET_KEY=your-super-secure-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=False
ENVIRONMENT=production
ALLOWED_ORIGINS=["https://your-frontend-domain.com"]
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
```

⚠️ **IMPORTANT**: Change `SECRET_KEY` to a strong, random value!

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Initialize Database

After deployment:

1. Get your Railway app URL (e.g., `https://app-production-123.up.railway.app`)
2. Visit the health endpoint: `https://app-production-123.up.railway.app/health`
3. Confirm the deploy logs show `alembic upgrade head` completed successfully

Example (deployed backend for this project):

```
https://team-task-manager-mygg.onrender.com
https://team-task-manager-mygg.onrender.com/health
```

The backend `Procfile` runs migrations automatically before the app starts:

```text
web: alembic upgrade head && gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:$PORT
```

To run migrations manually from the backend directory:

```bash
alembic upgrade head
```

**Verify deployment:**
```bash
curl https://your-backend-url/docs
```

Should return Swagger UI HTML.

---

## Frontend Deployment

### Option A: Deploy on Vercel (Recommended)

#### Step 1: Prepare Frontend

1. **Update API URL** in `.env`:
   ```
   VITE_API_URL=https://your-backend-url/api/v1
   ```

2. **Create .vercelignore**:
   ```
   node_modules/
   ```

#### Step 2: Deploy

1. Push code to GitHub
2. Go to https://vercel.com/import
3. Select your frontend repository
4. Configure:
   - **Framework**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variables:
   ```
   VITE_API_URL=https://your-backend-url/api/v1
   ```
6. Click "Deploy"

### Option B: Deploy on Railway

#### Step 1: Prepare Frontend

Same as Vercel, but create `Procfile`:
```
web: npm run build && npx serve -s dist -l $PORT
```

Or use static site setup.

#### Step 2: Deploy

1. Push to GitHub
2. In Railway, create new project
3. Select GitHub repo
4. Set build command: `npm run build`
5. Set start command: `npx serve -s dist -l $PORT`
6. Add environment variables
7. Deploy

---

## Post-Deployment

### Step 1: Test API Endpoints

```bash
# Login
curl -X POST https://your-backend-url/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123"}'

# Check health
curl https://your-backend-url/health
```

### Step 2: Test Frontend

Visit your frontend URL and:
- Test login
- Create a project
- Create tasks
- Check dashboard

### Step 3: Set Up Custom Domain

#### For Vercel Frontend:
1. Vercel Dashboard → Settings → Domains
2. Add your domain
3. Follow DNS instructions

#### For Railway:
1. Go to deployment settings
2. Add custom domain
3. Configure DNS records

### Step 4: Enable HTTPS

- Vercel: Automatic
- Railway: Automatic

### Step 5: Set Up Monitoring

Railway provides logs automatically. Monitor:
```bash
# Backend logs
railway logs -d <deployment-id>
```

---

## Troubleshooting

### Database Connection Error

**Problem**: `connection refused`

**Solution**:
- Verify `DATABASE_URL` is correct
- Check database is running
- Ensure firewall allows connections
- Test connection:
  ```bash
  psql -d "postgresql://user:password@host/db"
  ```

### CORS Errors

**Problem**: Frontend can't reach backend

**Solution**:
- Verify `ALLOWED_ORIGINS` includes your frontend URL
- Check API URL in frontend `.env`
- Ensure both are using HTTPS in production

### 500 Errors on API Calls

**Problem**: Server errors

**Solution**:
- Check logs: `railway logs -d <id>`
- Verify environment variables
- Check database migration ran
- Review recent code changes

### Static Files Not Loading

**Problem**: Frontend styles/images broken

**Solution**:
- Rebuild: `npm run build`
- Check build output: `dist/` folder
- Verify static file serving

### Performance Issues

**Optimize**:
- Enable caching
- Add CDN (Cloudflare)
- Database indexing
- API rate limiting

---

## Production Checklist

- [ ] Database backup configured
- [ ] Environment variables secured (no secrets in code)
- [ ] HTTPS enabled
- [ ] Custom domain configured
- [ ] Monitoring/alerts set up
- [ ] Error tracking (e.g., Sentry)
- [ ] Load testing completed
- [ ] Database migrations tested
- [ ] Rate limiting configured
- [ ] Live frontend URL added to README
- [ ] Live backend URL added to README
- [ ] Public GitHub repo URL added to README
- [ ] Secrets management in place
- [ ] Documentation updated

---

## Scaling Tips

1. **Database**: Use connection pooling
2. **Backend**: Use Gunicorn workers (4-8)
3. **Frontend**: Enable compression, minimize bundles
4. **CDN**: Use Cloudflare for static assets
5. **Caching**: Implement Redis for session storage

---

## Support

For issues:
1. Check Railway docs: https://docs.railway.app
2. Review FastAPI docs: https://fastapi.tiangolo.com
3. Check React docs: https://react.dev
4. Check logs for errors

---

Happy Deploying! 🚀

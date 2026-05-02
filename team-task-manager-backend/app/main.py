"""
Main FastAPI application
"""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.rate_limiter import RateLimitMiddleware

# Import routers
from app.routers import auth, users, projects, tasks, dashboard

logger = logging.getLogger(__name__)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup on startup/shutdown"""
    # Startup
    print("Starting up - Checking database connection...")
    await init_db()
    print("Database connection verified")
    yield
    # Shutdown
    print("Shutting down...")
    await close_db()
    print("Database connections closed")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Basic in-memory rate limiting for assignment/demo hardening.
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
)

# Add CORS middleware last so it wraps custom middleware responses too.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(tasks.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Team Task Manager API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Error handlers
@app.exception_handler(ValueError)
async def value_error_exception_handler(request, exc):
    """Handle ValueError"""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return JSON for unexpected errors so browser clients receive CORS headers."""
    logger.exception("Unhandled error for %s %s", request.method, request.url.path, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

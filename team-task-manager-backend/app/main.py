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

from app.routers import auth, users, projects, tasks, dashboard

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup on startup/shutdown."""
    print("Starting up — checking database connection...")
    await init_db()
    print("Database connection verified.")
    yield
    print("Shutting down — closing DB connections...")
    await close_db()
    print("Done.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# ── Middleware stack (added in reverse execution order) ────────────────────────
#
# IMPORTANT: CORSMiddleware MUST be registered BEFORE any other middleware
# that might raise an exception (e.g. RateLimitMiddleware).
#
# Starlette wraps middleware in reverse registration order, so the last
# add_middleware() call ends up as the outermost wrapper.  We want CORS to
# be the absolute outermost layer so that even error responses (429, 500)
# still carry the correct Access-Control-Allow-Origin header.
#
# Order here → outermost first:
#   1. CORSMiddleware  (outermost — always adds CORS headers)
#   2. RateLimitMiddleware
#   3. Application routes

# Step 1: rate limiter (inner)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
)

# Step 2: CORS (outer — registered last so it wraps everything above)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router,      prefix=settings.API_V1_STR)
app.include_router(users.router,     prefix=settings.API_V1_STR)
app.include_router(projects.router,  prefix=settings.API_V1_STR)
app.include_router(tasks.router,     prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)


# ── Root / health ──────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "message": "Welcome to Team Task Manager API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ── Global error handlers ──────────────────────────────────────────────────────
#
# These ensure that even unhandled 500s return a JSON body with CORS headers
# (because CORSMiddleware wraps the entire app including error responses).

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled error for %s %s", request.method, request.url.path,
        exc_info=True,
    )
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
        reload=settings.DEBUG,
    )
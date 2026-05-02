"""
Simple in-memory rate limiting middleware for FastAPI / Starlette.

This is intentionally lightweight for assignment/demo purposes. For production,
use a distributed rate limiter (Redis, API Gateway, or third-party service).
"""
import time
from collections import defaultdict
from typing import Dict, List

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = None, window_seconds: int = None):
        super().__init__(app)
        self.max_requests = max_requests or settings.RATE_LIMIT_REQUESTS
        self.window = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
        self.storage: Dict[str, List[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        client = "unknown"
        try:
            client = request.client.host or "unknown"
        except Exception:
            client = "unknown"

        now = time.time()
        window_start = now - self.window
        timestamps = self.storage[client]

        # purge old timestamps
        while timestamps and timestamps[0] < window_start:
            timestamps.pop(0)

        if len(timestamps) >= self.max_requests:
            return JSONResponse({"detail": "Rate limit exceeded. Try again later."}, status_code=429)

        timestamps.append(now)
        self.storage[client] = timestamps

        response = await call_next(request)
        return response

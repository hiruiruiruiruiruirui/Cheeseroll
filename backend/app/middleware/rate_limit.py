"""Rate-limit middleware — per-user daily request cap.

Uses a simple in-memory dictionary.  For production, swap to Redis
counters so limits survive process restarts and work across workers.

Usage:
    from .middleware.rate_limit import rate_limited

    @app.get("/some-endpoint")
    @rate_limited(max_per_day=10)
    async def some_endpoint(...):
        ...
"""

import time
import threading
from collections import defaultdict
from fastapi import Request, HTTPException, status

from ..config import settings


class RateLimiter:
    """In-memory sliding-window rate limiter (per-user)."""

    def __init__(self):
        self._buckets: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _clean(self, user_key: str, now: float):
        """Remove timestamps older than 24 hours."""
        cutoff = now - 86400  # 24 hours in seconds
        self._buckets[user_key] = [
            t for t in self._buckets[user_key] if t > cutoff
        ]

    def check_and_increment(self, user_key: str, max_per_day: int | None = None) -> bool:
        """Return True if the request is allowed, False if rate-limited.

        Increments the counter on a successful check.
        """
        max_requests = max_per_day or settings.RATE_LIMIT_PER_DAY
        now = time.monotonic()

        with self._lock:
            self._clean(user_key, now)

            if len(self._buckets[user_key]) >= max_requests:
                return False

            self._buckets[user_key].append(now)
            return True

    def remaining(self, user_key: str, max_per_day: int | None = None) -> int:
        max_requests = max_per_day or settings.RATE_LIMIT_PER_DAY
        now = time.monotonic()
        with self._lock:
            self._clean(user_key, now)
            return max(max_requests - len(self._buckets[user_key]), 0)


# Global singleton
_limiter = RateLimiter()


def rate_limited(max_per_day: int | None = None):
    """Decorator / dependency factory: enforce per-user daily rate limit.

    The decorated endpoint must receive a `current_user` dependency
    (or at least a `Request` object to extract the user key).
    """
    from functools import wraps
    import inspect

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the 'request' or 'current_user' in kwargs
            request: Request | None = kwargs.get("request")
            current_user = kwargs.get("current_user")

            if current_user is not None:
                user_key = str(current_user.id)
            elif request is not None:
                user_key = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
            else:
                # Try to find request in args
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                if request:
                    user_key = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
                else:
                    user_key = "unknown"

            if not _limiter.check_and_increment(user_key, max_per_day):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "rate_limited",
                        "message": "今日请求次数已达上限，请明天再试",
                        "code": "RATE_LIMITED",
                    },
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def get_limiter() -> RateLimiter:
    """Return the global rate limiter instance (useful for status checks)."""
    return _limiter

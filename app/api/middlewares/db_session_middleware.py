"""Middleware for managing database sessions per request."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.data.schemas.hygge_database import HyggeDatabase


class DatabaseMiddleware(BaseHTTPMiddleware):
    """Connects to the database at the beginning of a request and closes it at the end."""
    async def dispatch(self, request: Request, call_next):
        try:
            HyggeDatabase.get_instance().connect(reuse_if_open=True)
            response = await call_next(request)
        # Catching a broad exception to ensure the database session is closed
        # even if unexpected errors occur during request processing.
        except Exception as e: # pylint: disable=broad-exception-caught
            response = JSONResponse(status_code=400, content={"detail": str(e)})
        finally:
            if not HyggeDatabase.get_instance().is_closed():
                HyggeDatabase.get_instance().close()
        return response

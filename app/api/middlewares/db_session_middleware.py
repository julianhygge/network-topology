from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.data.schemas.hygge_database import HyggeDatabase


class DatabaseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            HyggeDatabase.get_instance().connect(reuse_if_open=True)
            response = await call_next(request)
        except Exception as e:
            response = JSONResponse(status_code=400, content={"detail": str(e)})
        finally:
            if not HyggeDatabase.get_instance().is_closed():
                HyggeDatabase.get_instance().close()
        return response

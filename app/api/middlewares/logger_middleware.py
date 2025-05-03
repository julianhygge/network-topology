"""Middleware for logging HTTP requests and responses."""
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.utils.logger import logger


class LoggerMiddleware(BaseHTTPMiddleware):
    """Logs incoming requests and outgoing responses."""
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        start_time = time.time()
        body = await request.body()
        await self._process_request(request, body)
        response = await call_next(request)
        response_body = [chunk async for chunk in response.body_iterator]
        response.body_iterator = _aiter(response_body)
        await self._process_response(request, response, response_body, start_time)
        return response

    @staticmethod
    async def _process_response(request, response: Response, response_body, start_time):
        duration = time.time() - start_time
        body = b''.join(response_body)
        try:
            if not request.url.path.endswith('simulate'):
                logger.info('Response Body: %s', body.decode("utf-8"))
        except UnicodeDecodeError:
            logger.info('Response Body: [Could not decode body, might be binary data]')
        logger.info('<---- Response to request %s: %s', request.url, response.status_code)
        logger.debug('Response Headers: %s', dict(response.headers))

        logger.info(
            "End request: %s %s, Status: %s, Duration: %.2fs",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

    @staticmethod
    async def _process_request(request, body):
        user_id = (
            request.state.claims.get('user')
            if hasattr(request.state, 'claims')
            else 'anonymous'
        )
        token = request.headers.get('Authorization', 'No token provided')
        logger.info('----> Request: %s %s', request.method, request.url)
        logger.debug('Request Headers: %s', dict(request.headers))
        if request.method in ('POST', 'PUT', 'PATCH'):
            try:
                logger.info('Request Body: %s', body.decode("utf-8"))
            except UnicodeDecodeError:
                logger.info('Request Body: [Could not decode body, might be binary data]')
        logger.info(
            "Start request: %s %s, User: %s, Token: %s",
            request.method,
            request.url.path,
            user_id,
            token,
        )


async def _aiter(iterable):
    for item in iterable:
        yield item

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
import time
from app.utils.logger import logger


class LoggerMiddleware(BaseHTTPMiddleware):
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
                logger.info(f'Response Body: {body.decode("utf-8")}')
        except UnicodeDecodeError:
            logger.info('Response Body: [Could not decode body, might be binary data]')
        logger.info(f'<---- Response to request {request.url}: {response.status_code}')
        logger.debug('Response Headers: %s' % dict(response.headers))

        logger.info(
            f"End request: {request.method} {request.url.path}, "
            f"Status: {response.status_code}, "
            f"Duration: {duration:.2f} seconds"
        )

    @staticmethod
    async def _process_request(request, body):
        user_id = request.state.claims.get('user') if hasattr(request.state, 'claims') else 'anonymous'
        token = request.headers.get('Authorization', 'No token provided')
        logger.info('----> Request: %s %s' % (request.method, request.url))
        logger.debug('Request Headers: %s' % dict(request.headers))
        if request.method in ('POST', 'PUT', 'PATCH'):
            try:
                logger.info(f'Request Body: {body.decode("utf-8")}')
            except UnicodeDecodeError:
                logger.info('Request Body: [Could not decode body, might be binary data]')
        logger.info(f"Start request: {request.method} {request.url.path}, User: {user_id}, Token: {token}")


async def _aiter(iterable):
    for item in iterable:
        yield item

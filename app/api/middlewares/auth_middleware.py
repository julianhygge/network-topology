from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import status
from starlette.responses import JSONResponse
from app.api.v1.dependencies.container_instance import c
from app.utils.logger import logger
from jwt import ExpiredSignatureError, InvalidSignatureError, DecodeError

not_needed_auth_urls = [
    '/v1/auth/',
    '/docs',
    "/openapi.json"
]


class AuthorizationMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        token_service = c.token_service()
        if request.method.upper() != 'OPTIONS' and not any(
                request.url.path.startswith(url) for url in not_needed_auth_urls):
            auth = request.headers.get('Authorization')
            try:
                if auth is not None:
                    claims = token_service.decode_token(str.replace(str(auth), 'Bearer ', ''))
                    token_service.validate_token_claims(claims)
                    logger.info('user: %s' % claims.get('user'))
                    request.state.claims = claims
                else:
                    request.state.authorization_error = 'Unauthorized'
            except ExpiredSignatureError:
                request.state.authorization_error = 'Expired Signature'
            except InvalidSignatureError:
                request.state.authorization_error = 'Invalid token'
            except DecodeError:
                request.state.authorization_error = 'Invalid token'
            except Exception as ex:
                logger.error("Unknown error when trying to authorize: %s", ex)
                response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "An unexpected error occurred trying to authorize. Please try again later."},
                )
                return response

        if hasattr(request.state, "authorization_error"):
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": request.state.authorization_error},
                headers={"WWW-Authenticate": "Bearer"},
            )
            return response

        response = await call_next(request)
        return response

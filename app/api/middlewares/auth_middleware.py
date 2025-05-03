"""Middleware for handling authorization."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
from jwt import ExpiredSignatureError, InvalidSignatureError, DecodeError

from app.api.v1.dependencies.container_instance import get_token_service
from app.utils.logger import logger

not_needed_auth_urls = [
    '/v1/auth/',
    '/docs',
    "/openapi.json"
]


token_service = get_token_service()


class AuthorizationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle authorization for incoming requests."""

    async def dispatch(self, request: Request, call_next):
        """
        Dispatches the request and handles authorization.

        Args:
            request: The incoming request.
            call_next: The next middleware or endpoint in the chain.

        Returns:
            The response from the next middleware or endpoint, or an
            authorization error response.
        """
        if request.method.upper() != 'OPTIONS' and not any(
                url in request.url.path for url in not_needed_auth_urls):
            auth = request.headers.get('Authorization')
            try:
                if auth is not None:
                    claims = token_service.decode_token(str.replace(str(auth), 'Bearer ', ''))
                    token_service.validate_token_claims(claims)
                    logger.info('user: %s', claims.get('user'))
                    request.state.claims = claims
                else:
                    request.state.authorization_error = 'Unauthorized'
            except ExpiredSignatureError:
                request.state.authorization_error = 'Expired Signature'
            except InvalidSignatureError:
                request.state.authorization_error = 'Invalid token'
            except DecodeError:
                request.state.authorization_error = 'Invalid token'
            # Catching a broad exception to prevent application crashes
            # due to unexpected errors during authorization.
            except Exception as ex: # pylint: disable=broad-exception-caught
                logger.error("Unknown error when trying to authorize: %s", ex)
                response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "detail": "An unexpected error occurred trying to authorize."
                        " Please try again later."
                    },
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

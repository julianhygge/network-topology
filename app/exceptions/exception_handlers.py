from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from starlette import status
from starlette.responses import JSONResponse
from uvicorn.protocols.utils import ClientDisconnected

from app.exceptions.hygge_exceptions import (DatabaseException, HyggeException,
                                             InvalidAttemptState,
                                             NotFoundException,
                                             UnauthorizedError,
                                             UserAlreadyExistException,
                                             UserDoesNotExist)
from app.utils.logger import logger


def add_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def unexpected_error_handler(request, exc):
        if isinstance(exc, ClientDisconnected):
            logger.debug("Client disconnected")
            return JSONResponse(
                status_code=499,
                content={"detail": "Client Disconnected"},
            )
        return await handle_unexpected_error(request, exc)

    @app.exception_handler(HTTPException)
    async def http_error_handler(request, exc):
        return await handle_http_errors(request, exc)

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_error_handler(request, exc: UnauthorizedError):
        return await handle_unauthorized_error(request, exc)

    @app.exception_handler(DatabaseException)
    async def database_error_handler(request, exc):
        return await handle_database_error(request, exc)

    @app.exception_handler(InvalidAttemptState)
    async def invalid_attempt_state_handler(request, exc):
        return await handle_invalid_attempt_state(request, exc)

    @app.exception_handler(UserDoesNotExist)
    async def user_does_not_exist_handler(request, exc):
        return await handle_user_does_not_exist(request, exc)

    @app.exception_handler(NotFoundException)
    async def item_not_found(request, exc):
        return await handle_item_not_found(request, exc)

    @app.exception_handler(UserAlreadyExistException)
    async def user_already_exists(request, exc):
        return await handle_user_already_exist(request, exc)

    @app.exception_handler(HyggeException)
    async def hygge_exception_handler(_: Request, exc: HyggeException):
        return JSONResponse(
            status_code=400,
            content=exc.to_dict()
        )


async def handle_unexpected_error(_, exc):
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Unknown Error"},

    )


async def handle_http_errors(_, exc):
    logger.exception(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def handle_invalid_attempt_state(_, exc):
    logger.exception(exc)
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)}
    )


async def handle_user_does_not_exist(_, exc):
    logger.exception(exc)
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)}
    )


async def handle_user_already_exist(_, exc):
    logger.info(exc)
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )


async def handle_database_error(_, exc: DatabaseException):
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": exc.message, "details": exc.details}
    )


async def handle_unauthorized_error(_, exc: UnauthorizedError):
    logger.exception(exc)
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message}
    )


async def handle_item_not_found(request: Request, exc: NotFoundException):
    message = f"404 Not Found, URL: {request.url.path}"
    logger.error(message, exc)
    response_content = {
        "detail": message,
        "status_code": status.HTTP_404_NOT_FOUND,
        "type": "NOT_FOUND",
        "suggestions": "Check the request and try again.",
    }
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=response_content
    )

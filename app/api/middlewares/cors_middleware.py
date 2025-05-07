"""
Module for configuring and adding CORS (Cross-Origin Resource Sharing)
middleware to the FastAPI application.
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.dependencies.container_instance import get_configuration


def add_cors_middleware(app: FastAPI) -> None:
    """
    Adds CORS middleware to the FastAPI application.

    This function retrieves CORS configuration (allowed origins, methods,
    headers, and credentials) and applies the CORSMiddleware to the
    provided FastAPI application instance.

    Args:
        app: The FastAPI application instance to which the middleware
             will be added.
    """
    cors_config = get_configuration().cors

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.origins,
        allow_methods=cors_config.methods,
        allow_headers=cors_config.headers,
        allow_credentials=cors_config.allow_credentials,
    )

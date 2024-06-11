from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.v1.dependencies.container_instance import get_configuration


def add_cors_middleware(app: FastAPI):
    cors_config = get_configuration().cors

    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=cors_config.origins,
        allow_methods=cors_config.methods,
        allow_headers=cors_config.headers,
        allow_credentials=cors_config.allow_credentials,
    )

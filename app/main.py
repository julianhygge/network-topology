"""Main application file for the Network Topology API."""

from fastapi import FastAPI

from app.api.middlewares.auth_middleware import AuthorizationMiddleware
from app.api.middlewares.cors_middleware import add_cors_middleware
from app.api.middlewares.db_session_middleware import DatabaseMiddleware
from app.api.middlewares.logger_middleware import LoggerMiddleware
from app.api.v1.resources.auth.auth import auth_router
from app.api.v1.resources.electrical_devices.electrical_appliances import (
    appliances_router,
)
from app.api.v1.resources.load_profile.load_profile import load_router
from app.api.v1.resources.simulation.simulation import simulation_router
from app.api.v1.resources.solar.solar import solar_router
from app.api.v1.resources.topology.breadcrumb import breadcrumb_router
from app.api.v1.resources.topology.flags import flag_router
from app.api.v1.resources.topology.house import house_router
from app.api.v1.resources.topology.substation import substation_router
from app.api.v1.resources.topology.transformer import tr_router
from app.api.v1.resources.users.group import group_router
from app.api.v1.resources.users.user import user_router
from app.config.servers import hygge_servers
from app.exceptions.exception_handlers import add_exception_handlers


def add_app_middleware(cc_app: FastAPI):
    """Adds necessary middleware to the FastAPI application."""
    cc_app.add_middleware(DatabaseMiddleware)  # type:ignore
    cc_app.add_middleware(LoggerMiddleware)  # type:ignore
    cc_app.add_middleware(AuthorizationMiddleware)  # type:ignore
    add_cors_middleware(cc_app)
    add_exception_handlers(cc_app)


def add_routes(cc_app: FastAPI):
    """Includes API routers for different functionalities."""
    version_1 = "/v1/"
    cc_app.include_router(auth_router, prefix=f"{version_1}auth")
    cc_app.include_router(user_router, prefix=f"{version_1}users")
    cc_app.include_router(group_router, prefix=f"{version_1}groups")
    cc_app.include_router(substation_router, prefix=f"{version_1}substations")
    cc_app.include_router(tr_router, prefix=f"{version_1}transformers")
    cc_app.include_router(house_router, prefix=f"{version_1}houses")
    cc_app.include_router(load_router, prefix=f"{version_1}load")

    cc_app.include_router(breadcrumb_router, prefix=f"{version_1}breadcrumb")
    cc_app.include_router(appliances_router, prefix=f"{version_1}appliances")
    cc_app.include_router(solar_router, prefix=f"{version_1}solar")
    cc_app.include_router(flag_router, prefix=f"{version_1}flags")
    cc_app.include_router(simulation_router, prefix=f"{version_1}simulation")


app = FastAPI(
    title="Network topology",
    openapi_version="3.1.0",
    root_path="/net-topology-api",
    swagger_ui_parameters={
        "persistAuthorization": True,
        "tryItOutEnabled": True,
    },
    servers=hygge_servers,
)

app.servers = hygge_servers
add_app_middleware(app)
add_routes(app)


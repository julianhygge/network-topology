from fastapi import FastAPI
from app.api.middlewares.auth_middleware import AuthorizationMiddleware
from app.api.middlewares.cors_middleware import add_cors_middleware
from app.api.middlewares.db_session_middleware import DatabaseMiddleware
from app.api.middlewares.logger_middleware import LoggerMiddleware
from app.api.v1.resources.auth.auth import auth_router
from app.api.v1.resources.topology.house import house_router
from app.api.v1.resources.topology.breadcrumb import breadcrumb_router
from app.api.v1.resources.topology.substation import substation_router
from app.api.v1.resources.topology.transformer import transformer_router
from app.api.v1.resources.users.group import group_router
from app.api.v1.resources.users.user import user_router
from app.config.servers import hygge_servers
from app.exceptions.exception_handlers import add_exception_handlers


def add_app_middleware(cc_app: FastAPI):
    cc_app.add_middleware(DatabaseMiddleware)  # type:ignore
    cc_app.add_middleware(LoggerMiddleware)  # type:ignore
    cc_app.add_middleware(AuthorizationMiddleware)  # type:ignore
    add_cors_middleware(cc_app)
    add_exception_handlers(cc_app)


def add_routes(cc_app: FastAPI):
    version_1 = '/v1/'
    cc_app.include_router(auth_router, prefix=f'{version_1}auth')
    cc_app.include_router(user_router, prefix=f'{version_1}users')
    cc_app.include_router(group_router, prefix=f'{version_1}groups')
    cc_app.include_router(substation_router, prefix=f'{version_1}substations')
    cc_app.include_router(transformer_router, prefix=f'{version_1}transformers')
    cc_app.include_router(house_router, prefix=f'{version_1}houses')
    cc_app.include_router(breadcrumb_router, prefix=f'{version_1}breadcrumb')



app = FastAPI(title="Network topology", root_path="/net-topology-api")

app.servers = hygge_servers
add_app_middleware(app)
add_routes(app)

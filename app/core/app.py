from fastapi import FastAPI
from app.core.middleware import register_middleware
from app.core.lifespan import lifespan
from app.api.api_routers import auto_include_routers, register_static_files
from app.core.config import settings

def create_app():
    app = FastAPI(
        title=settings.project_name,
        description=settings.project_description,
        version=settings.project_version,
        lifespan=lifespan,
        openapi_url=f"{settings.api_v1_str}/openapi.json",
    )
    # 注册中间件
    register_middleware(app)
    # 注册路由
    auto_include_routers(app, prefix=settings.api_v1_str)
    # 注册静态文件
    register_static_files(app)
    return app

# 路由聚合
from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
import importlib
import pkgutil
from app.core.logger import logger


# 自动包含所有子模块中的路由
def auto_include_routers(app: FastAPI, prefix: str = ""):
    '''递归自动导入 app/api/endpoints 下的所有路由模块，并注册其中的 router 或 *_router
    注意:
    - 只需在 endpoints 目录下新建文件并定义 router 或 xxx_router，即可自动注册，无需手动维护。
    - 保证每个 endpoint 文件中有 router 或 xxx_router 变量即可
    '''
    router = APIRouter()
    from . import endpoints

    def scan_package(package, prefix):
        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            full_module_name = prefix + module_name
            if is_pkg:
                sub_pkg = importlib.import_module(full_module_name)
                logger.info(f"递归进入子包: {full_module_name}")
                scan_package(sub_pkg, full_module_name + ".")
                continue
            module = importlib.import_module(full_module_name)
            logger.info(f"正在导入路由模块: {full_module_name}")
            found_router = False
            for attr in dir(module):
                if attr == "router" or attr.endswith("_router"):
                    r = getattr(module, attr)
                    if hasattr(r, "routes"):
                        router.include_router(r)
                        logger.info(f"已注册路由: {full_module_name}.{attr}")
                        found_router = True
            if not found_router:
                logger.warning(f"模块 {full_module_name} 未发现 router 或 *_router")

    scan_package(endpoints, endpoints.__name__ + ".")
    # 将聚合的路由注册到应用
    app.include_router(router, prefix=prefix)

    # 注册自定义 Swagger UI 路径
    @app.get("/offline/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=f"{prefix}/openapi.json",
            title="离线API文档",
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
    )


# 注册静态文件
def register_static_files(app: FastAPI):
    app.mount("/static", StaticFiles(directory="static"), name="static")
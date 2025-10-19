from app.core.app import create_app
from app.core.logger import logger

app = create_app()  # 工厂模式创建FastAPI实例


if __name__ == "__main__":
    import uvicorn
    port = 5000
    # 打印当前启动路径
    logger.info(f"OpenAPI V3 URL: http://localhost:{port}/api/v1/openapi.json")
    logger.info(f"离线SwaggerUI文档地址: http://localhost:{port}/offline/docs")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # 启用热部署
        reload_dirs=["app"],          # 监控当前目录下的文件变化
        reload_excludes=["tests/*"],  # 可选：排除某些目录
    )
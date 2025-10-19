from pathlib import Path
import sys
from typing import Annotated, Type
from fastapi import Depends, Request
from loguru import logger
import os

def setup_logging():
    # 日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 按天轮转的日志文件格式
    log_file_format = "{time:YYYY-MM-DD}.log"
    
    # 定义日志格式
    stdout_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[request_id]}</cyan> |"
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{extra[request_id]} | "
        "{name}:{function}:{line} - "
        "{message}"
    )
    
    # 移除默认handler
    logger.remove()
    
    # 添加控制台输出（开发环境）
    if os.getenv("ENV", "dev") == "dev":
        logger.add(
            sink=sys.stdout,
            format=stdout_format,
            level="DEBUG",
            backtrace=True,  # 控制是否在日志中包含完整的回溯信息(异常时的完整调用链)
            diagnose=True    # 控制是否在日志中包含诊断信息
        )
    
    # 添加文件输出（按天轮转）
    logger.add(
        sink=log_dir / log_file_format,
        rotation="00:00",  # 每天午夜轮转
        retention="30 days",  # 保留30天日志
        compression="zip",  # 压缩旧日志
        encoding="utf-8",
        level="INFO",
        format=file_format,
        backtrace=True,
        diagnose=False  # 生产环境关闭敏感信息
    )
    
    return logger.bind(request_id="N/A")  # 绑定默认request_id

# 初始化日志
logger = setup_logging()

def get_request_logger(request: Request):
    """依赖项：获取已绑定请求ID的logger"""
    return logger.bind(request_id=request.state.request_id)

LoguruLogger = Type[type(logger)]  # 获取logger的类型(因为 loguru模块并没有公开导出 Logger类, 所以只能这样获取类型,方便进行类型注解)
# 创建类型别名方便使用
LoggerDep = Annotated[LoguruLogger, Depends(get_request_logger)]
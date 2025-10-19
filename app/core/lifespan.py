from contextlib import asynccontextmanager
from datetime import datetime

import httpx
from fastapi import FastAPI
from app.core.logger import logger
from app.core.db import async_db
from app.models import common, system
from app.core.tenant_init import init_default_tenant


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"应用启动于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        await async_db.init_db_pool()  # 初始化数据库连接池
        await async_db.create_tables()  # 创建数据库表
        
        # 初始化默认租户和基础数据
        async with async_db as session:
            await init_default_tenant(session)
        
        # 异步HTTP连接池
        app.state.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(100.0),  # 100秒超时
            limits=httpx.Limits(
                max_connections=10,  # 最大连接数
                max_keepalive_connections=3,  # 保持活动的连接数
            ),
            transport=httpx.AsyncHTTPTransport(retries=3),  # 自动重试3次
        )
        yield
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
    finally:
        if hasattr(app.state, "http_client"):
            await app.state.http_client.aclose()  # 关闭异步HTTP客户端
        await async_db.close_db_pool()  # 关闭数据库连接池
        logger.info(f"应用关闭于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

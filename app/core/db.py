from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlmodel import SQLModel, text
from app.core.config import settings
from app.core.logger import logger

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


from sqlalchemy import event
from sqlalchemy.engine import Engine
from app.core.system_context import SystemContext

@event.listens_for(Engine, "before_execute", retval=True)
def only_deleted0_and_tenant_filter(conn, clauseelement, multiparams, params):
    # 检查 clauseelement 是否有效且有 whereclause 属性
    if clauseelement is not None and hasattr(clauseelement, 'whereclause'):
        # 检查SQL字符串是否包含 audit_log 表
        sql_str = str(clauseelement)
        if 'audit_log' in sql_str.lower():
            return clauseelement, multiparams, params
        
        # 检查是否包含JOIN查询，如果包含则跳过自动添加deleted=0和tenant_id
        if 'join' in sql_str.lower() or 'outer join' in sql_str.lower():
            return clauseelement, multiparams, params
        
        # 获取当前租户ID
        tenant_id = SystemContext.get_tenant_id()
        
        # 构建过滤条件
        conditions = []
        
        # 添加 deleted=0 条件
        conditions.append(text("deleted=0"))
        
        # 添加租户ID条件（如果存在）
        if tenant_id is not None:
            conditions.append(text(f"tenant_id={tenant_id}"))
        
        # 应用过滤条件
        if conditions:
            combined_condition = conditions[0]
            for condition in conditions[1:]:
                combined_condition = combined_condition & condition
            
            if clauseelement.whereclause is not None:
                clauseelement = clauseelement.where(
                    clauseelement.whereclause & combined_condition
                )
            else:
                clauseelement = clauseelement.where(combined_condition)
    
    return clauseelement, multiparams, params

class AsyncDatabase:
    """异步数据库连接池管理类"""
    
    def __init__(self):
        self.async_engine = None
        self.AsyncSessionLocal = None
    
    async def init_db_pool(self):
        """初始化数据库连接池"""
        self.async_engine = create_async_engine(
            url=settings.async_mysql_dsn,
            echo=True,
            pool_size=10,
            max_overflow=5,
            pool_timeout=30,
            pool_recycle=3600,
        )

        # 异步会话工厂
        self.AsyncSessionLocal = sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False  
        )
        try:
            # 数据库健康检查
            async with self.async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("✅ 数据库连接池已初始化")
        except Exception as e:
            logger.error(f"❌ 数据库连接池初始化失败")
    
    async def get_async_db(self) -> AsyncGenerator:
        """获取数据库会话（依赖注入用）"""
        async with self.AsyncSessionLocal() as session:
            yield session
    
    async def close_db_pool(self):
        """关闭数据库连接池"""
        if self.async_engine:
            await self.async_engine.dispose()
            logger.info("✅ 数据库连接池已关闭")

    async def create_tables(self):
        """创建数据库表"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    async def __aenter__(self):
        self.session = self.AsyncSessionLocal()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
# 创建全局实例
async_db = AsyncDatabase()

# FastAPI依赖项
AsyncSessionDep = Annotated[AsyncSession, Depends(async_db.get_async_db)]
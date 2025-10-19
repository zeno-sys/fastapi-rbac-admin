from typing import List, Optional
from sqlmodel import select
from app.core.db import AsyncSession
from app.core.logger import LoggerDep
from app.models.system import PostModel
from app.utils.tree import build_tree
from app.core.system_context import SystemContext

class PostService:
    def __init__(self, session: AsyncSession, logger: LoggerDep) -> None:
        self.session = session
        self.logger = logger

    async def lists(self) -> List[PostModel]:
        """获取所有岗位"""
        sql = select(PostModel).where(PostModel.deleted == 0)
        result = await self.session.execute(sql)
        return result.scalars().all()

    async def get_post_by_id(self, post_id: int) -> PostModel | None:
        """根据ID获取岗位"""
        sql = select(PostModel).where(PostModel.id == post_id, PostModel.deleted == 0)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()

    async def create_post(self, post: PostModel) -> PostModel:
        """创建岗位"""
        # 设置租户ID
        tenant_id = SystemContext.get_tenant_id()
        if tenant_id:
            post.tenant_id = tenant_id
        
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def update_post(self, post_data: dict) -> PostModel | None:
        """更新岗位"""
        post_id = post_data.pop("id")
        post = await self.get_post_by_id(post_id)
        if not post:
            return None
            
        for key, value in post_data.items():
            setattr(post, key, value)
            
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def delete_post(self, post_id: int) -> bool:
        """逻辑删除岗位"""
        post = await self.get_post_by_id(post_id)
        if not post:
            return False
            
        # 设置逻辑删除标志
        post.deleted = 1
        await self.session.commit()
        return True
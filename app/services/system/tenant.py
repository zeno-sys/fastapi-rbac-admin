from typing import List, Optional
from sqlmodel import select, func
from app.api.vo.system.tenant import TenantPageQuery
from app.core.db import AsyncSession
from app.core.logger import LoggerDep
from app.models.common import PageResponse
from app.models.system import TenantModel


class TenantService:
    def __init__(self, session: AsyncSession, logger: LoggerDep) -> None:
        self.session = session
        self.logger = logger

    async def lists(self) -> List[TenantModel]:
        """获取所有租户"""
        sql = select(TenantModel)
        result = await self.session.execute(sql)
        return result.scalars().all()

    async def get_tenants(self, page_query: TenantPageQuery) -> PageResponse[TenantModel]:
        """获取租户分页列表"""
        # 构建查询条件
        query = select(TenantModel)
        
        if page_query.name:
            query = query.where(TenantModel.name.contains(page_query.name))
            
        if page_query.code:
            query = query.where(TenantModel.code.contains(page_query.code))
            
        if page_query.status is not None:
            query = query.where(TenantModel.status == page_query.status)
            
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        
        # 处理空数据情况
        if total == 0:
            return PageResponse[TenantModel](
                page_num=page_query.page_num,
                page_size=page_query.page_size,
                total=total,
                items=[]
            )
        
        # 查询分页数据
        sql = query\
            .offset(page_query.offset)\
            .limit(page_query.limit)\
            .order_by(TenantModel.create_time.desc())
        
        result = await self.session.execute(sql)
        tenants = result.scalars().all()

        return PageResponse[TenantModel](
            page_num=page_query.page_num,
            page_size=page_query.page_size,
            total=total,
            items=tenants
        )

    async def get_tenant_by_id(self, tenant_id: int) -> Optional[TenantModel]:
        """根据ID获取租户信息"""
        sql = select(TenantModel).where(TenantModel.id == tenant_id)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()

    async def get_tenant_by_code(self, code: str) -> Optional[TenantModel]:
        """根据编码获取租户信息"""
        sql = select(TenantModel).where(TenantModel.code == code)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()

    async def get_tenant_by_domain(self, domain: str) -> Optional[TenantModel]:
        """根据域名获取租户信息"""
        sql = select(TenantModel).where(TenantModel.domain == domain)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()

    async def create_tenant(self, tenant: TenantModel) -> TenantModel:
        """创建租户"""
        self.session.add(tenant)
        await self.session.commit()
        await self.session.refresh(tenant)
        return tenant

    async def update_tenant(self, tenant_data: dict) -> Optional[TenantModel]:
        """更新租户信息"""
        tenant_id = tenant_data.pop("id")
        tenant = await self.get_tenant_by_id(tenant_id)
        if not tenant:
            return None
        
        # 更新租户基本信息
        for key, value in tenant_data.items():
            setattr(tenant, key, value)
        
        await self.session.commit()
        await self.session.refresh(tenant)
        return tenant

    async def delete_tenant(self, tenant_id: int) -> bool:
        """逻辑删除租户"""
        tenant = await self.get_tenant_by_id(tenant_id)
        if not tenant:
            return False
            
        # 设置逻辑删除标志
        tenant.deleted = 1
        await self.session.commit()
        return True

    async def update_status(self, tenant_id: int, status: int) -> bool:
        """更新租户状态"""
        tenant = await self.get_tenant_by_id(tenant_id)
        if not tenant:
            return False
            
        # 更新状态
        tenant.status = status
        await self.session.commit()
        await self.session.refresh(tenant)
        return True

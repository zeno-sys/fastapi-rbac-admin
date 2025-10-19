from typing import List
from sqlmodel import delete, select, func
from app.api.vo.system.role import RolePageQuery
from app.core.db import AsyncSession
from app.core.logger import LoggerDep
from app.models.common import PageResponse
from app.models.system import PermissionModel, RoleModel, RolePermissionModel
from app.utils.tree import build_tree
from app.core.system_context import SystemContext

class RoleService:
    def __init__(self, session: AsyncSession, logger: LoggerDep) -> None:
        self.session = session
        self.logger = logger

    async def lists(self) -> List[RoleModel]:
        """获取所有角色"""
        sql = select(RoleModel)
        result = await self.session.execute(sql)
        return result.scalars().all()

    async def get_roles(self, page_query: RolePageQuery) -> PageResponse[RoleModel]:
        """获取角色分页列表"""
        # 构建查询条件
        query = select(RoleModel)
        
        if page_query.name:
            query = query.where(RoleModel.name.contains(page_query.name))
            
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        
        # 处理空数据情况
        if total == 0:
            return PageResponse[RoleModel](
                page_num=page_query.page_num,
                page_size=page_query.page_size,
                total=total,
                items=[]
            )
        
        # 查询分页数据
        sql = query\
            .offset(page_query.offset)\
            .limit(page_query.limit)\
            .order_by(RoleModel.create_time.desc())
        
        result = await self.session.execute(sql)
        roles = result.scalars().all()
        
        return PageResponse[RoleModel](
            page_num=page_query.page_num,
            page_size=page_query.page_size,
            total=total,
            items=roles
        )


    async def get_role_by_id(self, role_id: int) -> RoleModel | None:
        """根据ID获取角色"""
        sql = select(RoleModel).where(RoleModel.id == role_id)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()

    async def create_role(self, role: RoleModel,menu_ids:List[int]) -> RoleModel:
        """创建角色"""
        # 设置租户ID
        tenant_id = SystemContext.get_tenant_id()
        if tenant_id:
            role.tenant_id = tenant_id
        
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        # 如果提供了权限ID列表，创建角色权限关联
        if menu_ids:
            role_permissions = [
                RolePermissionModel(role_id=role.id, perm_id=perm_id)
                for perm_id in menu_ids
            ]
            self.session.add_all(role_permissions)
            await self.session.commit()
        return role

    async def update_role(self,role_data: dict,menu_ids:List[int]) -> RoleModel | None:
        """更新角色"""
        role_id = role_data.pop("id")
        role = await self.get_role_by_id(role_id)
        if not role:
            return None
            
        for key, value in role_data.items():
            setattr(role, key, value)
            
        await self.session.commit()
        await self.session.refresh(role)
        # 更新角色权限关联
        if menu_ids:
            # 批量删除旧的关联
            await self.session.execute(delete(RolePermissionModel).where(RolePermissionModel.role_id == role_id))
            # 批量添加新的关联
            role_permissions = [
                RolePermissionModel(role_id=role.id, perm_id=perm_id)
                for perm_id in menu_ids
            ]
            self.session.add_all(role_permissions)
            await self.session.commit()
        return role

    async def delete_role(self, role_id: int) -> bool:
        """逻辑删除角色"""
        role = await self.get_role_by_id(role_id)
        if not role:
            return False
            
        # 设置逻辑删除标志
        role.deleted = 1
        await self.session.commit()
        return True
    async def get_menu_by_role_id(self, role_id: int) -> List[int]:
        """根据角色ID获取菜单权限"""
        sql = select(RolePermissionModel.perm_id).where(RolePermissionModel.role_id == role_id)
        result = await self.session.execute(sql)
        perm_ids = result.scalars().all()
        sql = select(PermissionModel).where(PermissionModel.id.in_(perm_ids))
        result = await self.session.execute(sql)
        perms = result.scalars().all()
        # return build_tree([perm.model_dump() for perm in perms])
        return {
            "menu_ids":[perm.id for perm in perms]
        }

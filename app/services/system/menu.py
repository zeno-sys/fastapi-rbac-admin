from typing import List
from sqlmodel import select
from app.core.db import AsyncSession
from app.core.logger import LoggerDep
from app.models.system import PermissionModel
from app.utils.tree import build_tree
from app.core.system_context import SystemContext

class MenuService:
    def __init__(self, session: AsyncSession, logger: LoggerDep) -> None:
        self.session = session
        self.logger = logger

    async def lists(self) -> List[PermissionModel]:
        """获取所有菜单"""
        sql = select(PermissionModel)
        result = await self.session.execute(sql)
        return result.scalars().all()

    
    async def get_menu_by_id(self, menu_id: int) -> PermissionModel | None:
        """根据ID获取菜单"""
        sql = select(PermissionModel).where(PermissionModel.id == menu_id)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()

    async def create_menu(self, menu: PermissionModel) -> PermissionModel:
        """创建菜单"""
        # 设置租户ID
        tenant_id = SystemContext.get_tenant_id()
        if tenant_id:
            menu.tenant_id = tenant_id
        
        self.session.add(menu)
        await self.session.commit()
        await self.session.refresh(menu)
        return menu

    async def update_menu(self, menu_data: dict) -> PermissionModel | None:
        """更新菜单"""
        menu_id = menu_data.pop("id")
        menu = await self.get_menu_by_id(menu_id)
        if not menu:
            return None
            
        for key, value in menu_data.items():
            setattr(menu, key, value)
            
        await self.session.commit()
        await self.session.refresh(menu)
        return menu

    async def delete_menu(self, menu_id: int) -> bool:
        """逻辑删除菜单"""
        menu = await self.get_menu_by_id(menu_id)
        if not menu:
            return False
            
        # 设置逻辑删除标志
        menu.deleted = 1
        await self.session.commit()
        return True

    async def get_menu_tree(self) -> List[dict]:
        """获取菜单树结构"""
        sql = select(PermissionModel)
        result = await self.session.execute(sql)
        menus = result.scalars().all()
        return build_tree([menu.model_dump() for menu in menus])
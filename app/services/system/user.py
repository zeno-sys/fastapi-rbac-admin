from typing import List, Dict
from sqlmodel import delete, select, func
from app.api.vo.system.user import UserPageQuery
from app.core.db import AsyncSession
from app.core.logger import LoggerDep
from app.models.common import PageResponse
from app.models.system import DeptModel, PostModel, UserModel, UserRoleModel
from sqlalchemy.orm import selectinload
from app.core.security import get_password_hash
from app.core.system_context import SystemContext

class UserService:
    def __init__(self, session: AsyncSession, logger: LoggerDep) -> None:
        self.session = session
        self.logger = logger

    async def lists(self) -> List[UserModel]:
        """获取所有用户"""
        sql = select(UserModel)
        result = await self.session.execute(sql)
        return result.scalars().all()

    async def get_users(self, page_query: UserPageQuery) -> PageResponse[UserModel]:
        """获取用户分页列表"""
        # 构建查询条件
        query = select(UserModel)
        
        if page_query.username:
            query = query.where(UserModel.username.contains(page_query.username))
            
        if page_query.nickname:
            query = query.where(UserModel.nickname.contains(page_query.nickname))
            
        if page_query.status is not None:
            query = query.where(UserModel.status == page_query.status)
            
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        
        # 处理空数据情况
        if total == 0:
            return PageResponse[UserModel](
                page_num=page_query.page_num,
                page_size=page_query.page_size,
                total=total,
                items=[]
            )
        
        
        # 查询分页数据
        sql = query\
            .offset(page_query.offset)\
            .limit(page_query.limit)\
            .order_by(UserModel.create_time.desc())
        
        result = await self.session.execute(sql)
        users = result.scalars().all()
        
        final_users = [await self.get_user_by_id(user.id) for user in users]

        # return PageResponse[UserModel](
        #     page_num=page_query.page_num,
        #     page_size=page_query.page_size,
        #     total=total,
        #     items=final_users
        # )
        return {
            "page_num": page_query.page_num,
            "page_size": page_query.page_size,
            "total": total,
            "items": final_users
        }

    async def get_user_by_id(self, user_id: int):
        """根据ID获取用户及其角色信息"""
        # 查询用户基本信息及关联角色(结果分配给关系字段)
        sql = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(
                selectinload(UserModel.roles)  # 加载用户角色关联表
                .selectinload(UserRoleModel.role)  # 加载关联的角色对象
            )
        )
        result = await self.session.execute(sql)
        user = result.scalar_one_or_none()
        if not user:
            return None
        # 部门翻译
        dept_ids = user.dept_ids
        dept_names = []
        if dept_ids:
            sql = select(DeptModel).where(DeptModel.id.in_(dept_ids))
            result = await self.session.execute(sql)
            depts = result.scalars().all()
            dept_names = [dept.name for dept in depts]
        # 职位翻译
        post_id = user.post_id
        position_name =  None
        if post_id:
            sql = select(PostModel).where(PostModel.id == post_id)
            result = await self.session.execute(sql)
            position = result.scalar_one_or_none()
            position_name = position.name if position else None
        return {
            **user.model_dump(),       # 用户基本信息
            "dept_names": dept_names,  # 部门名称列表
            "position": position_name, # 职位名称
            "roles": [
                {
                    "id": user_role.role.id,
                    "name": user_role.role.name,
                    "status": user_role.status
                }
                for user_role in user.roles
            ]
        }

    async def get_users_by_dept_id(self, dept_id: int) -> List[UserModel]:
        """根据部门ID获取用户列表"""
        sql = select(UserModel).where(UserModel.dept_ids.contains(dept_id))
        result = await self.session.execute(sql)
        return result.scalars().all()

    async def remove_user_from_dept(self, dept_id: int, user_id: int) -> bool:
        """从部门中移除用户"""
        user = await self.session.get(UserModel, user_id)
        if not user:
            return False
            
        # 检查用户是否属于该部门
        if not user.dept_ids or dept_id not in user.dept_ids:
            return False
        
        # 从用户的部门列表中移除指定部门
        user.dept_ids = [d for d in user.dept_ids if d != dept_id]
        
        await self.session.commit()
        await self.session.refresh(user)
        return True

    async def create_user(self, user: UserModel, role_ids: List[int]) -> UserModel:
        """创建用户并关联角色"""
        # 设置租户ID
        tenant_id = SystemContext.get_tenant_id()
        if tenant_id:
            user.tenant_id = tenant_id
        
        # 添加用户到数据库
        user.password = get_password_hash(user.password)  # 哈希密码
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        # 如果提供了角色ID列表，创建用户角色关联
        if role_ids:
            user_roles = [
                UserRoleModel(user_id=user.id, role_id=role_id)
                for role_id in role_ids
            ]
            # 设置默认选中用户
            user_roles[0].status = 5 # 5表示选中状态
            self.session.add_all(user_roles)
            await self.session.commit()
        
        return user

    async def update_user(self, user_data: dict, role_ids: List[int]) -> UserModel | None:
        """更新用户信息及角色关联"""
        user_id = user_data.pop("id")
        # user = await self.get_user_by_id(user_id)
        sql = select(UserModel).where(UserModel.id == user_id)
        user = await self.session.execute(sql)
        user = user.scalars().first()
        if not user:
            return None
        # 更新用户基本信息
        for key, value in user_data.items():
            setattr(user, key, value)
        
        # 处理角色关联更新
        if role_ids is not None:  # 只有当role_ids不为None时才更新
            # 删除现有的用户角色关联
            await self.session.execute(
                delete(UserRoleModel).where(UserRoleModel.user_id == user_id)
            )
            
            # 添加新的用户角色关联
            user_roles = [
                UserRoleModel(user_id=user_id, role_id=role_id)
                for role_id in role_ids
            ]
            # 设置默认选中用户
            user_roles[0].status = 5 # 5表示选中状态
            self.session.add_all(user_roles)
        
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        """逻辑删除用户"""
        sql = select(UserModel).where(UserModel.id == user_id)
        user = await self.session.execute(sql)
        user = user.scalars().first()
        if not user:
            return False
            
        # 设置逻辑删除标志
        user.deleted = 1
        await self.session.commit()
        return True
    
    async def switch_user_role(self, role_id: int) -> bool:
        """切换用户当前角色"""
        # 查询当前选中的用户角色
        current_role = await self.session.scalar(
            select(UserRoleModel)
            .where(UserRoleModel.status == 5)  # 5表示选中状态
        )
        if not current_role:
            return False
        
        # 如果当前角色就是要切换的角色，直接返回
        if current_role.role_id == role_id:
            return True
        
        # 查询要切换的目标角色关联
        target_role = await self.session.scalar(
            select(UserRoleModel)
            .where(
                UserRoleModel.user_id == current_role.user_id,
                UserRoleModel.role_id == role_id
            )
        )
        if not target_role:
            return False
        
        # 切换角色状态
        current_role.status = 0  # 设置当前角色为非选中状态
        target_role.status = 5   # 设置目标角色为选中状态
        
        await self.session.commit()
        return True
    
    async def reset_password(self, user_id: int, new_password: str) -> bool:
        """重置用户密码"""
        user = await self.session.get(UserModel, user_id)
        if not user:
            return False
            
        # 更新密码
        user.password = get_password_hash(new_password)
        await self.session.commit()
        await self.session.refresh(user)
        return True
    
    async def update_status(self, user_id: int, status: int) -> bool:
        """更新用户状态"""
        user = await self.session.get(UserModel, user_id)
        if not user:
            return False
            
        # 更新状态
        user.status = status
        await self.session.commit()
        await self.session.refresh(user)
        return True
    
    
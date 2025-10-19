from datetime import datetime, timedelta
from functools import wraps
from typing import Annotated, Any, AsyncGenerator, Callable, Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer
import jwt
from sqlmodel import select
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.core.db import async_db,AsyncSessionDep
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, security, verify_access_token, verify_refresh_token
from app.models.common import TokenPayload
from app.models.system import UserModel, UserRoleModel, RoleModel, RolePermissionModel, PermissionModel, TenantModel
from app.core.system_context import SystemContext




async def get_current_user(
        session: AsyncSessionDep,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    """获取当前用户（使用访问令牌）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = verify_access_token(credentials.credentials, credentials_exception)

    # 根据用户ID获取用户信息
    user = await session.get(UserModel, user_id)
    if not user:
        raise credentials_exception
    # 验证用户是否激活
    if user.status != 0:
        raise credentials_exception
    
    # 设置租户上下文
    if user.tenant_id:
        SystemContext.set_tenant_id(user.tenant_id)
    
    return user

async def get_current_user_with_refresh(
    request: Request,
    session: AsyncSessionDep,
):
    """获取当前用户（使用刷新令牌）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 从请求头获取刷新令牌
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise credentials_exception
    
    refresh_token = authorization.split(" ")[1]
    user_id = verify_refresh_token(refresh_token, credentials_exception)
    user = await session.get(UserModel, user_id)
    if not user:
        raise credentials_exception
    if user.status != 0:
        raise credentials_exception
    return user


async def refresh_access_token(
    session: AsyncSessionDep,
    current_user: UserModel = Depends(get_current_user_with_refresh),  # 验证刷新令牌
):
    """刷新访问令牌"""
    # 发放新的访问令牌
    access_expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_payload = {"sub": current_user.id, "type": "access", "exp": access_expire}
    new_access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": new_access_token, "token_type": "bearer"}

async def get_current_active_user(current_user: UserModel = Depends(get_current_user)):
    """获取当前激活用户"""
    if not current_user.status == 1:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def check_permission(user: UserModel, required_permission: str) -> bool:
    """检查用户是否拥有指定权限"""
    # 这里可以根据业务需求判断是否为超级管理员
    # 例如：用户名是否为admin，或者有特定的角色标识
    if user.username == "admin":
        return True
    async with async_db as session:
        # 查询用户的所有角色
        # 获取用户的所有角色（通过UserRoleModel关联）
        user_roles_query = select(RoleModel).join(UserRoleModel).where(
            UserRoleModel.user_id == user.id,
            UserRoleModel.status == 0,  # 只查询正常状态的角色关联
            RoleModel.status == 0,      # 只查询正常状态的角色
            RoleModel.deleted == 0      # 只查询未删除的角色
        ).options(
            selectinload(RoleModel.permissions).selectinload(RolePermissionModel.permission)
        )
        
        result = await session.execute(user_roles_query)
        roles = result.scalars().all()
        
        # 检查用户角色是否拥有所需权限
        for role in roles:
            for role_perm in role.permissions:
                permission = role_perm.permission
                if permission.identifier == required_permission and permission.status == 0:
                    return True
    return False


def require_permission(permission: str):
    """权限检查装饰器"""
    def permission_checker(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            *args: Any,
            **kwargs: Any
        ) -> Any:
            current_user: UserModel = kwargs.get("current_user") or kwargs.get("user")
            has_permission = await check_permission(current_user, permission)
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要权限: {permission}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return permission_checker


async def get_current_tenant(session: AsyncSessionDep) -> Optional[TenantModel]:
    """获取当前租户"""
    tenant_id = SystemContext.get_tenant_id()
    if not tenant_id:
        return None
    
    tenant = await session.get(TenantModel, tenant_id)
    if tenant and tenant.status == 0 and tenant.deleted == 0:
        return tenant
    return None


CurrentUser = Annotated[UserModel, Depends(get_current_user)]
CurrentTenant = Annotated[Optional[TenantModel], Depends(get_current_tenant)]



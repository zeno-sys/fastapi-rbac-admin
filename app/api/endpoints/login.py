import asyncio
import random
from fastapi import APIRouter,Depends, WebSocket, WebSocketException, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from app.api.vo.system.user import CreateUser
from app.core import security
from app.core.db import AsyncSessionDep
from app.core.logger import LoggerDep
from app.core.security import verify_password,create_tokens
from app.models.common import Token
from app.models.system import UserModel, TenantModel
from app.utils.response import error_response, success_response
from app.core.system_context import SystemContext
from typing import Optional

router = APIRouter(tags=["认证授权"])


@router.post("/login")
async def login_access_token(
    session: AsyncSessionDep,
    logger: LoggerDep, 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """一个符合 OAuth2 标准的令牌登录端点，用于获取后续请求所需的访问令牌"""
    
    # 构建查询条件
    query = select(UserModel).where(UserModel.username == form_data.username)
    
    result = await session.execute(query)
    user = result.scalars().first()
    
    if not user:
        return error_response("用户不存在")
    if not verify_password(form_data.password, user.password):
        return error_response("用户名或密码错误")
    
    # 验证租户状态
    if user.tenant_id:
        tenant_result = await session.execute(select(TenantModel).where(TenantModel.id == user.tenant_id))
        tenant = tenant_result.scalar_one_or_none()
        if not tenant or tenant.status != 0:
            return error_response("租户已被禁用")
    
    # 生成访问令牌和刷新令牌，将租户ID加入token
    logger.info("用户 {} 登录成功，租户ID: {}", user.username, user.tenant_id)
    payload_data:dict = {
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id)
    }
    access_token, refresh_token = create_tokens(payload_data)
    return Token(id=user.id, nickname=user.nickname, access_token=access_token, refresh_token=refresh_token)

@router.post("/register", description="注册新用户")
async def create_user(
    session: AsyncSessionDep,
    user_in: CreateUser,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")
):
    """
    注册新用户
    """
    # 构建查询条件
    query = select(UserModel).where(UserModel.username == user_in.username)
    
    # 如果提供了租户ID，添加租户过滤条件
    if x_tenant_id:
        try:
            tenant_id = int(x_tenant_id)
            query = query.where(UserModel.tenant_id == tenant_id)
        except ValueError:
            return error_response("无效的租户ID格式")
    
    result = await session.execute(query)
    user = result.scalars().first()
    if user:
        return error_response("用户已存在")
    
    user = UserModel(**user_in.model_dump(exclude={"role_ids"}))
    user.password = security.get_password_hash(user.password)
    
    # 设置租户ID
    if x_tenant_id:
        user.tenant_id = int(x_tenant_id)
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return success_response(user)

@router.post("/refresh", description="使用刷新令牌获取新的访问令牌")
async def refresh_token(
    
):
   pass

@router.websocket("/ws", name="系统信息")
async def get_system_info(ws: WebSocket):
    await ws.accept()
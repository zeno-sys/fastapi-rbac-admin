from datetime import datetime, timedelta
import hashlib
from typing import Tuple, Optional

from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.system_context import SystemContext


# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# JWT认证方案
security = HTTPBearer()

# 安全配置
SECRET_KEY = settings.SECRET_KEY
REFRESH_SECRET_KEY = settings.REFRESH_SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES  
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def get_token_hash(token: str) -> str:
    """返回给定Token的哈希值"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_tokens(data: dict) -> Tuple[str, str]:
    """创建访问令牌和刷新令牌"""
    # 访问令牌
    access_expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_payload = data.copy()
    access_payload.update({"exp": access_expire, "type": "access"})
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # 刷新令牌
    refresh_expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_payload = data.copy()
    refresh_payload.update({"exp": refresh_expire, "type": "refresh"})
    refresh_token = jwt.encode(refresh_payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    
    return access_token, refresh_token

def verify_access_token(token: str, credentials_exception):
    """验证访问令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise credentials_exception
        # 从令牌中获取租户ID和用户ID并设置上下文
        user_id = int(payload.get("user_id"))
        SystemContext.set_user_id(user_id)
        SystemContext.set_tenant_id(int(payload.get("tenant_id")))
        return user_id
    except JWTError:
        raise credentials_exception

def verify_refresh_token(token: str, credentials_exception):
    """验证刷新令牌"""
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception
        user_id = int(payload.get("user_id"))
        SystemContext.set_user_id(user_id)
        SystemContext.set_tenant_id(int(payload.get("tenant_id")))
        return user_id
    except JWTError:
        raise credentials_exception
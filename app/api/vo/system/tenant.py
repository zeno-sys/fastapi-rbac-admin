from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.common import BasePageQuery


class TenantBase(BaseModel):
    """租户基础信息"""
    name: str
    code: str
    domain: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: int = 0
    remark: Optional[str] = None
    expire_time: Optional[datetime] = None


class CreateTenant(TenantBase):
    """创建租户"""
    pass


class UpdateTenant(TenantBase):
    """更新租户"""
    id: int


class TenantPageQuery(BasePageQuery):
    """租户分页查询"""
    name: Optional[str] = None
    code: Optional[str] = None
    status: Optional[int] = None


class TenantResponse(TenantBase):
    """租户响应"""
    id: int
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True

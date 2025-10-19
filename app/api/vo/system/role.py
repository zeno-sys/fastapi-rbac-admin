from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from app.models.common import BasePageQuery

class RoleBase(BaseModel):
    """角色基础字段"""
    name: str = Field(max_length=50, description="角色名称")
    remark: Optional[str] = Field(default=None, description="角色描述")
    status: int = Field(default=0, description="状态(0:正常 1:禁用)")


class CreateRole(RoleBase):
    """创建角色DTO"""
    menu_ids: Optional[list[int]] = Field(default_factory=list, description="菜单ID列表")

class UpdateRole(RoleBase):
    """更新角色DTO"""
    id: int = Field(description="角色ID")
    menu_ids: Optional[list[int]] = Field(default_factory=list, description="菜单ID列表")

class RoleResponse(RoleBase):
    """角色响应DTO"""
    pass

class RolePageQuery(BasePageQuery):
    """分页查询角色DTO"""
    name: Optional[str] = Field(None, description="角色名称")

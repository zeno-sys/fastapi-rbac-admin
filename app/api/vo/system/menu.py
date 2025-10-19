# file: d:\5Code\Zeno\zeno-fastapi-admin\app\api\vo\system\menu.py

from typing import Optional
from pydantic import BaseModel
from sqlmodel import Field
from app.models.common import BasePageQuery

class MenuBase(BaseModel):
    """菜单基础字段"""
    pid: Optional[int] = Field(default=None, description="父级ID")
    name: str = Field(max_length=50, description="权限名称")
    type: Optional[int] = Field(default=0, description="类型(0:目录 1:菜单 2:按钮 3:数据)")
    path: Optional[str] = Field(default=None, description="路由地址")
    component: Optional[str] = Field(default=None, description="组件地址")
    icon: Optional[str] = Field(default=None, description="菜单图标")
    identifier: Optional[str] = Field(default=None, description="权限标识 user:add")
    api: Optional[str] = Field(default=None, description="接口地址")
    method: Optional[str] = Field(default=None, description="请求方式")
    sort: int = Field(default=0, description="排序")
    status: int = Field(default=0, description="状态(0:正常 1:禁用)")
    visible: bool = Field(default=True, description="是否可见")
    remark: Optional[str] = Field(default=None, description="权限描述")

class CreateMenu(MenuBase):
    """创建菜单DTO"""
    pass

class UpdateMenu(MenuBase):
    """更新菜单DTO"""
    id: int = Field(description="菜单ID")

class MenuResponse(MenuBase):
    """菜单响应DTO"""
    id: int
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True

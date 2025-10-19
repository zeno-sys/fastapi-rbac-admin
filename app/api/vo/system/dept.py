# file: d:\Code\20250912-ai-cup\ai-coding-cup-2025\backend\app\api\vo\system\dept.py

from typing import Optional, List
from pydantic import BaseModel
from sqlmodel import Field
from app.models.common import BasePageQuery

class DeptBase(BaseModel):
    """部门基础字段"""
    name: str = Field(max_length=50, description="部门名称")
    remark: Optional[str] = Field(default=None, description="部门描述")
    pid: Optional[int] = Field(default=None, description="父级ID")
    level: Optional[int] = Field(default=None, description="部门层级(1:一级部门,2:二级部门...)")
    leader: Optional[str] = Field(default=None, description="负责人")
    phone: Optional[str] = Field(default=None, description="联系电话")
    email: Optional[str] = Field(default=None, description="邮箱")
    sort: int = Field(default=0, description="排序")
    status: int = Field(default=0, description="状态(0:正常 1:禁用)")

class CreateDept(DeptBase):
    """创建部门DTO"""
    pass

class UpdateDept(DeptBase):
    """更新部门DTO"""
    id: int = Field(description="部门ID")

class DeptResponse(DeptBase):
    """部门响应DTO"""
    id: int
    created_at: Optional[str] = Field(None, description="创建时间")

class RemoveDeptMember(BaseModel):
    """移除部门成员DTO"""
    dept_id: int = Field(description="部门ID")
    user_id: int = Field(description="用户ID")
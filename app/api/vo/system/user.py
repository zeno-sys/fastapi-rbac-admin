from typing import Optional, List
from pydantic import BaseModel
from sqlmodel import Field
from app.models.common import BasePageQuery

class UserBase(BaseModel):
    """用户基础字段"""
    username: str = Field(max_length=20, description="账号")
    password: str = Field(max_length=20, description="密码")
    nickname: Optional[str] = Field(default=None, description="昵称/姓名")
    avatar: Optional[str] = Field(default=None, description="头像")
    email: Optional[str] = Field(default=None, description="邮箱")
    phone: Optional[str] = Field(default=None, description="手机号")
    status: int = Field(default=0, description="状态(0:正常 1:禁用)")
    dept_ids: Optional[List[int]] = Field(default=None, description="部门列表")
    post_id: Optional[int] = Field(default=None, description="岗位ID")

class CreateUser(UserBase):
    """创建用户DTO"""
    role_ids: Optional[List[int]] = Field(None, description="选择角色列表")

class UpdateUser(UserBase):
    """更新用户DTO"""
    id: int = Field(description="用户ID")
    role_ids: List[int] = Field(..., description="选择角色列表")

class UserResponse(UserBase):
    """用户响应DTO"""
    id: int
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True

class UserPageQuery(BasePageQuery):
    """分页查询用户DTO"""
    username: Optional[str] = Field(None, description="账号")
    nickname: Optional[str] = Field(None, description="昵称/姓名")
    status: Optional[int] = Field(None, description="状态(0:正常 1:禁用)")

class ResetPassword(BaseModel):
    """重置密码DTO"""
    id: int = Field(description="用户ID")
    password: str = Field(description="新密码", min_length=1, max_length=20)

class UpdateStatus(BaseModel):
    """更新状态DTO"""
    id: int = Field(description="用户ID")
    status: int = Field(description="状态(0:正常 1:禁用)")
from typing import Optional, List
from pydantic import BaseModel
from sqlmodel import Field
from app.models.common import BasePageQuery

class PostBase(BaseModel):
    """岗位基础字段"""
    name: str = Field(max_length=50, description="岗位名称")
    remark: Optional[str] = Field(default=None, description="岗位描述")
    sort: int = Field(default=0, description="排序")
    status: int = Field(default=0, description="状态(0:正常 1:禁用)")

class CreatePost(PostBase):
    """创建岗位DTO"""
    pass

class UpdatePost(PostBase):
    """更新岗位DTO"""
    id: int = Field(description="岗位ID")

class PostResponse(PostBase):
    """岗位响应DTO"""
    id: int
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
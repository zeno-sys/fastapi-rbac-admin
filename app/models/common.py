from pydantic import BaseModel, computed_field
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Generic, List, Optional, Dict, Any, TypeVar

class BaseTable(SQLModel, table=False): 
    """所有数据库表的基类，包含通用字段"""
    
    id: Optional[int] = Field(default=None,primary_key=True,description="主键ID",sa_column_kwargs={"comment": "主键ID"})
    tenant_id: Optional[int] = Field(default=None, foreign_key="sys_tenant.id", description="租户ID", sa_column_kwargs={"comment": "租户ID"})
    create_by: Optional[str] = Field(default=None,description="创建人",sa_column_kwargs={"comment": "创建人"})
    update_by: Optional[str] = Field(default=None,description="更新人",sa_column_kwargs={"comment": "更新人"})
    create_time: Optional[datetime] = Field(default_factory=datetime.now,description="创建时间",sa_column_kwargs={"comment": "创建时间"})
    update_time: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now,"comment": "更新时间"},
        description="更新时间",
    )
    deleted: int = Field(default=0,description="逻辑删除(0:未删除 1:已删除)",sa_column_kwargs={"comment": "逻辑删除(0:未删除 1:已删除)"})
    
    
class BasePageQuery(BaseModel):
    """分页查询基础数据"""
    page_num: int = Field(default=1, description="页码", ge=1)
    page_size: int = Field(default=10, description="数量", ge=1)

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page_num - 1) * self.page_size
    
    @computed_field
    @property
    def limit(self) -> int:
        return self.page_size



T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """所有API响应的基类"""

    success: bool 
    code: int                 # 状态码 (200=成功, 其他=错误码)
    msg: str                  # 用户友好的消息
    data: Optional[T] = None  
    err: Optional[T] = None  




# 分页数据
class PageResponse(BaseModel, Generic[T]):
    page_num: int = Field(1, description="当前页码")
    page_size: int = Field(10, description="每页数量")
    total: int = Field(0, description="总记录数")
    items: List[T] = Field([], description="分页数据")


class Token(BaseModel):
    id: int
    nickname: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    exp: int  # 过期时间（Unix时间戳，必须为整数）
    sub: str | None = None
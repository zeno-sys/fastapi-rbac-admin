from typing import List, Optional
from sqlmodel import JSON, Field, Relationship, SQLModel
from sqlalchemy import UniqueConstraint, Column, String, Integer, Date, Boolean, Text
from app.models.common import BaseTable
from datetime import datetime, date


class TenantModel(BaseTable, table=True):
    __tablename__ = "sys_tenant"
    __table_args__ = {"comment": "租户表"}
    
    """租户表"""
    name: str = Field(max_length=100, description="租户名称", sa_column_kwargs={"comment": "租户名称"})
    code: str = Field(max_length=50, description="租户编码", sa_column_kwargs={"comment": "租户编码"})
    domain: Optional[str] = Field(default=None, max_length=200, description="域名", sa_column_kwargs={"comment": "域名"})
    contact_name: Optional[str] = Field(default=None, max_length=50, description="联系人姓名", sa_column_kwargs={"comment": "联系人姓名"})
    contact_phone: Optional[str] = Field(default=None, max_length=20, description="联系人电话", sa_column_kwargs={"comment": "联系人电话"})
    contact_email: Optional[str] = Field(default=None, max_length=100, description="联系人邮箱", sa_column_kwargs={"comment": "联系人邮箱"})
    status: int = Field(default=0, description="状态(0:正常 1:禁用)", sa_column_kwargs={"comment": "状态(0:正常 1:禁用)"})
    remark: Optional[str] = Field(default=None, description="备注", sa_column_kwargs={"comment": "备注"})
    expire_time: Optional[datetime] = Field(default=None, description="过期时间", sa_column_kwargs={"comment": "过期时间"})
    
    # 关联关系
    users: List["UserModel"] = Relationship(back_populates="tenant")
    depts: List["DeptModel"] = Relationship(back_populates="tenant")
    posts: List["PostModel"] = Relationship(back_populates="tenant")
    roles: List["RoleModel"] = Relationship(back_populates="tenant")
    permissions: List["PermissionModel"] = Relationship(back_populates="tenant")

class PostModel(BaseTable, table=True):
    __tablename__ = "sys_post"
    __table_args__ = {"comment": "岗位表"}
    
    """岗位表"""
    name: str = Field(max_length=50, description="岗位名称", sa_column_kwargs={"comment": "岗位名称"})
    remark: Optional[str] = Field(default=None, description="岗位描述", sa_column_kwargs={"comment": "岗位描述"})
    sort: int = Field(default=0, description="排序", sa_column_kwargs={"comment": "排序"})
    status: int = Field(default=0, description="状态(0:正常 1:禁用)", sa_column_kwargs={"comment": "状态(0:正常 1:禁用)"})

    tenant: Optional[TenantModel] = Relationship(back_populates="posts")
    users: List["UserModel"] = Relationship(back_populates="post")


class DeptModel(BaseTable, table=True):
    __tablename__ = "sys_dept"
    __table_args__ = {"comment": "部门表"}
    
    """部门表"""
    name: str = Field(max_length=50, description="部门名称", sa_column_kwargs={"comment": "部门名称"})
    remark: Optional[str] = Field(default=None, description="部门描述", sa_column_kwargs={"comment": "部门描述"})
    pid: Optional[int] = Field(default=None, description="父级ID", sa_column_kwargs={"comment": "父级ID"})
    level: Optional[int] = Field(default=None, description="部门层级(1:一级部门,2:二级部门...)", sa_column_kwargs={"comment": "部门层级(1:一级部门,2:二级部门...)"})
    leader: Optional[str] = Field(default=None, description="负责人", sa_column_kwargs={"comment": "负责人"})
    phone: Optional[str] = Field(default=None, description="联系电话", sa_column_kwargs={"comment": "联系电话"})
    email: Optional[str] = Field(default=None, description="邮箱", sa_column_kwargs={"comment": "邮箱"})
    sort: int = Field(default=0, description="排序", sa_column_kwargs={"comment": "排序"})
    status: int = Field(default=0, description="状态(0:正常 1:禁用)", sa_column_kwargs={"comment": "状态(0:正常 1:禁用)"})

    tenant: Optional[TenantModel] = Relationship(back_populates="depts")





class UserModel(BaseTable, table=True):
    __tablename__ = "sys_user"
    __table_args__ = {"comment": "注册用户表"}

    """用户表"""
    username: str = Field(max_length=20, description="账号", sa_column_kwargs={"comment": "账号"})
    password: str = Field(max_length=255, description="密码", sa_column_kwargs={"comment": "密码"})
    nickname: Optional[str] = Field(default=None, description="昵称/姓名", sa_column_kwargs={"comment": "昵称/姓名"})
    avatar: Optional[str] = Field(default=None, description="头像", sa_column_kwargs={"comment": "头像"})
    email: Optional[str] = Field(default=None, description="邮箱", sa_column_kwargs={"comment": "邮箱"})
    phone: Optional[str] = Field(default=None, description="手机号", sa_column_kwargs={"comment": "手机号"})
    status: int = Field(default=0, description="状态(0:正常 1:禁用)", sa_column_kwargs={"comment": "状态(0:正常 1:禁用)"})
    dept_ids: Optional[List[int]] = Field(default=None,sa_type=JSON, description="部门列表", sa_column_kwargs={"comment": "部门列表"})
    post_id: Optional[int] = Field(default=None, foreign_key="sys_post.id", description="岗位ID", sa_column_kwargs={"comment": "岗位ID"})

    # 定义与租户的关联关系
    tenant: Optional[TenantModel] = Relationship(back_populates="users")
    # 定义与角色的关联关系
    roles: List["UserRoleModel"] = Relationship(back_populates="user")
    post: Optional[PostModel] = Relationship(back_populates="users", sa_relationship_kwargs={"lazy": "selectin"})



class RoleModel(BaseTable, table=True):
    __tablename__ = "sys_role"
    __table_args__ = {"comment": "角色表"}
    
    """角色表"""
    name: str = Field(max_length=50, description="角色名称", sa_column_kwargs={"comment": "角色名称"})
    remark: Optional[str] = Field(default=None, description="角色描述", sa_column_kwargs={"comment": "备注"})
    status: int = Field(default=0, description="状态(0:正常 1:禁用)", sa_column_kwargs={"comment": "状态(0:正常 1:禁用)"})

    # 定义与租户的关联关系
    tenant: Optional[TenantModel] = Relationship(back_populates="roles")
    # 定义与用户的关联关系
    users: List["UserRoleModel"] = Relationship(back_populates="role")
    # 定义与权限的关联关系
    permissions: List["RolePermissionModel"] = Relationship(back_populates="role")


class PermissionModel(BaseTable, table=True):
    __tablename__ = "sys_perm"
    __table_args__ = {"comment": "权限表"}
    
    """权限表"""
    pid: Optional[int] = Field(default=None, description="父级ID", sa_column_kwargs={"comment": "父级ID"})
    name: str = Field(max_length=50, description="权限名称", sa_column_kwargs={"comment": "权限名称"})
    type: Optional[int] = Field(default=0, description="类型(0:目录 1:菜单 2:按钮 3:数据)", sa_column_kwargs={"comment": "类型(0:目录 1:菜单 2:按钮 3:数据)"})
    path: Optional[str] = Field(default=None, description="路由地址", sa_column_kwargs={"comment": "路由地址"})  
    component: Optional[str] = Field(default=None, description="组件地址", sa_column_kwargs={"comment": "组件地址"})
    icon: Optional[str] = Field(default=None, description="菜单图标", sa_column_kwargs={"comment": "菜单图标"})
    identifier: Optional[str] = Field(default=None, description="权限标识 user:add", sa_column_kwargs={"comment": "权限标识 user:add"})
    api: Optional[str] = Field(default=None, description="接口地址", sa_column_kwargs={"comment": "接口地址"})
    method: Optional[str] = Field(default=None, description="请求方式", sa_column_kwargs={"comment": "请求方式"})
    sort: int = Field(default=0, description="排序", sa_column_kwargs={"comment": "排序"})
    status: int = Field(default=0, description="状态(0:正常 1:禁用)", sa_column_kwargs={"comment": "状态(0:正常 1:禁用)"})
    visible: bool = Field(default=True, description="是否可见", sa_column_kwargs={"comment": "是否可见"})
    remark: Optional[str] = Field(default=None, description="权限描述", sa_column_kwargs={"comment": "权限描述"})
    
    # 定义与租户的关联关系
    tenant: Optional[TenantModel] = Relationship(back_populates="permissions")
    # 定义与角色的关联关系
    role_permissions: List["RolePermissionModel"] = Relationship(back_populates="permission")



class UserRoleModel(BaseTable, table=True):
    __tablename__ = "sys_user_role"
    __table_args__ = {"comment": "用户角色关联表"}
    
    """用户角色关联表"""
    user_id: int = Field(foreign_key="sys_user.id", description="用户ID", sa_column_kwargs={"comment": "用户ID"})
    role_id: int = Field(foreign_key="sys_role.id", description="角色ID", sa_column_kwargs={"comment": "角色ID"})
    status: int = Field(default=0, description="状态(0:正常 1:禁用 5:选中)", sa_column_kwargs={"comment": "状态(0:正常 1:禁用 5:选中)"})

    user: UserModel = Relationship(back_populates="roles")
    role: RoleModel = Relationship(back_populates="users")


class RolePermissionModel(BaseTable, table=True):
    __tablename__ = "sys_role_perm"
    __table_args__ = {"comment": "角色权限关联表"}
    
    """角色权限关联表"""
    role_id: int = Field(foreign_key="sys_role.id", description="角色ID", sa_column_kwargs={"comment": "角色ID"})
    perm_id: int = Field(foreign_key="sys_perm.id", description="权限ID", sa_column_kwargs={"comment": "权限ID"})

    role: RoleModel = Relationship(back_populates="permissions")
    permission: PermissionModel = Relationship(back_populates="role_permissions")


class AuditLogModel(SQLModel, table=True):
    __tablename__ = "audit_log"
    __table_args__ = {"comment": "审计日志表"}
    
    """审计日志表"""
    id: Optional[int] = Field(default=None, primary_key=True, description="主键ID", sa_column_kwargs={"comment": "主键ID"})
    tenant_id: Optional[int] = Field(default=None, foreign_key="sys_tenant.id", description="租户ID", sa_column_kwargs={"comment": "租户ID"})
    user_id: Optional[int] = Field(default=None, description="操作用户ID", sa_column_kwargs={"comment": "操作用户ID"})
    username: Optional[str] = Field(default=None, max_length=50, description="操作用户名", sa_column_kwargs={"comment": "操作用户名"})
    operation_type: str = Field(..., max_length=50, description="操作类型", sa_column_kwargs={"comment": "操作类型（CREATE/UPDATE/DELETE/LOGIN/LOGOUT等）"})
    operation_desc: Optional[str] = Field(default=None, max_length=500, description="操作描述", sa_column_kwargs={"comment": "操作描述"})
    target_type: Optional[str] = Field(default=None, max_length=100, description="目标类型", sa_column_kwargs={"comment": "目标类型（如：用户、角色、菜单、部门等）"})
    target_id: Optional[str] = Field(default=None, max_length=100, description="目标ID", sa_column_kwargs={"comment": "目标ID"})
    operation_result: str = Field(default="SUCCESS", max_length=20, description="操作结果", sa_column_kwargs={"comment": "操作结果（SUCCESS/FAILED）"})
    ip_address: Optional[str] = Field(default=None, max_length=45, description="IP地址", sa_column_kwargs={"comment": "IP地址（支持IPv6）"})
    user_agent: Optional[str] = Field(default=None, max_length=500, description="用户代理信息", sa_column_kwargs={"comment": "用户代理信息"})
    request_method: Optional[str] = Field(default=None, max_length=10, description="请求方法", sa_column_kwargs={"comment": "请求方法（GET/POST/PUT/DELETE等）"})
    request_url: Optional[str] = Field(default=None, max_length=500, description="请求URL", sa_column_kwargs={"comment": "请求URL"})
    request_params: Optional[str] = Field(default=None, description="请求参数", sa_column_kwargs={"comment": "请求参数（JSON格式）"})
    response_data: Optional[str] = Field(default=None, description="响应数据", sa_column_kwargs={"comment": "响应数据（JSON格式）"})
    error_message: Optional[str] = Field(default=None, description="错误信息", sa_column_kwargs={"comment": "错误信息"})
    operation_time: datetime = Field(default_factory=datetime.now, description="操作时间", sa_column_kwargs={"comment": "操作时间"})
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="创建时间", sa_column_kwargs={"comment": "创建时间"})
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="更新时间", sa_column_kwargs={"comment": "更新时间"})
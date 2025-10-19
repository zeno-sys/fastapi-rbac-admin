from sqlmodel import select
from app.core.db import AsyncSession
from app.models.system import TenantModel, UserModel, RoleModel, PermissionModel, DeptModel, PostModel
from app.core.security import get_password_hash
from app.core.logger import logger


async def init_default_tenant(session: AsyncSession):
    """初始化默认租户和基础数据"""
    
    # 检查是否已存在默认租户
    result = await session.execute(select(TenantModel).where(TenantModel.code == "default"))
    existing_tenant = result.scalar_one_or_none()
    
    if existing_tenant:
        logger.info("默认租户已存在，跳过初始化")
        return existing_tenant
    
    # 创建默认租户
    default_tenant = TenantModel(
        name="默认租户",
        code="default",
        domain="localhost",
        contact_name="系统管理员",
        contact_email="admin@example.com",
        status=0,
        remark="系统默认租户"
    )
    session.add(default_tenant)
    await session.commit()
    await session.refresh(default_tenant)
    
    logger.info(f"创建默认租户成功，ID: {default_tenant.id}")
    
    # 创建默认部门
    default_dept = DeptModel(
        tenant_id=default_tenant.id,
        name="总公司",
        remark="默认部门",
        pid=None,
        level=1,
        sort=0,
        status=0
    )
    session.add(default_dept)
    await session.commit()
    await session.refresh(default_dept)
    
    # 创建默认岗位
    default_post = PostModel(
        tenant_id=default_tenant.id,
        name="管理员",
        remark="系统管理员岗位",
        sort=0,
        status=0
    )
    session.add(default_post)
    await session.commit()
    await session.refresh(default_post)
    
    # 创建默认角色
    admin_role = RoleModel(
        tenant_id=default_tenant.id,
        name="超级管理员",
        remark="拥有所有权限",
        status=0
    )
    session.add(admin_role)
    await session.commit()
    await session.refresh(admin_role)
    
    # 创建默认用户
    admin_user = UserModel(
        tenant_id=default_tenant.id,
        username="admin",
        password=get_password_hash("admin123"),
        nickname="系统管理员",
        email="admin@example.com",
        status=0,
        dept_ids=[default_dept.id],
        post_id=default_post.id
    )
    session.add(admin_user)
    await session.commit()
    await session.refresh(admin_user)
    
    # 创建基础权限菜单
    await create_default_permissions(session, default_tenant.id)
    
    logger.info("默认租户初始化完成")
    return default_tenant


async def create_default_permissions(session: AsyncSession, tenant_id: int):
    """创建默认权限菜单"""
    
    # 系统管理菜单
    system_menu = PermissionModel(
        tenant_id=tenant_id,
        name="系统管理",
        type=0,
        path="/system",
        component="Layout",
        icon="system",
        sort=1,
        status=0,
        visible=True,
        remark="系统管理模块"
    )
    session.add(system_menu)
    await session.commit()
    await session.refresh(system_menu)
    
    # 用户管理
    user_menu = PermissionModel(
        tenant_id=tenant_id,
        pid=system_menu.id,
        name="用户管理",
        type=1,
        path="/system/user",
        component="system/user/index",
        icon="user",
        sort=1,
        status=0,
        visible=True,
        remark="用户管理"
    )
    session.add(user_menu)
    
    # 用户管理按钮权限
    user_permissions = [
        ("system:user:list", "用户查询", "GET", "/api/v1/user/page"),
        ("system:user:create", "用户新增", "POST", "/api/v1/user/create"),
        ("system:user:update", "用户修改", "PUT", "/api/v1/user/update"),
        ("system:user:delete", "用户删除", "DELETE", "/api/v1/user")
    ]
    
    for identifier, name, method, api in user_permissions:
        perm = PermissionModel(
            tenant_id=tenant_id,
            pid=user_menu.id,
            name=name,
            type=2,
            identifier=identifier,
            api=api,
            method=method,
            sort=1,
            status=0,
            visible=False,
            remark=name
        )
        session.add(perm)
    
    # 角色管理
    role_menu = PermissionModel(
        tenant_id=tenant_id,
        pid=system_menu.id,
        name="角色管理",
        type=1,
        path="/system/role",
        component="system/role/index",
        icon="peoples",
        sort=2,
        status=0,
        visible=True,
        remark="角色管理"
    )
    session.add(role_menu)
    
    # 部门管理
    dept_menu = PermissionModel(
        tenant_id=tenant_id,
        pid=system_menu.id,
        name="部门管理",
        type=1,
        path="/system/dept",
        component="system/dept/index",
        icon="tree",
        sort=3,
        status=0,
        visible=True,
        remark="部门管理"
    )
    session.add(dept_menu)
    
    # 岗位管理
    post_menu = PermissionModel(
        tenant_id=tenant_id,
        pid=system_menu.id,
        name="岗位管理",
        type=1,
        path="/system/post",
        component="system/post/index",
        icon="post",
        sort=4,
        status=0,
        visible=True,
        remark="岗位管理"
    )
    session.add(post_menu)
    
    # 菜单管理
    menu_menu = PermissionModel(
        tenant_id=tenant_id,
        pid=system_menu.id,
        name="菜单管理",
        type=1,
        path="/system/menu",
        component="system/menu/index",
        icon="menu",
        sort=5,
        status=0,
        visible=True,
        remark="菜单管理"
    )
    session.add(menu_menu)
    
    # 租户管理
    tenant_menu = PermissionModel(
        tenant_id=tenant_id,
        pid=system_menu.id,
        name="租户管理",
        type=1,
        path="/system/tenant",
        component="system/tenant/index",
        icon="tree-table",
        sort=6,
        status=0,
        visible=True,
        remark="租户管理"
    )
    session.add(tenant_menu)
    
    await session.commit()
    logger.info("默认权限菜单创建完成")

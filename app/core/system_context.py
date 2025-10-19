from typing import Optional
from contextvars import ContextVar
from app.models.system import TenantModel


# 系统上下文变量
system_context: ContextVar[Optional[TenantModel]] = ContextVar('system_context', default=None)
tenant_id_context: ContextVar[Optional[int]] = ContextVar('tenant_id_context', default=None)
user_id_context: ContextVar[Optional[int]] = ContextVar('user_id_context', default=None)


class SystemContext:
    """系统上下文管理器"""
    
    @staticmethod
    def set_tenant(tenant: TenantModel) -> None:
        """设置当前租户"""
        system_context.set(tenant)
        tenant_id_context.set(tenant.id)
    
    @staticmethod
    def set_tenant_id(tenant_id: int) -> None:
        """设置当前租户ID"""
        tenant_id_context.set(tenant_id)
    
    @staticmethod
    def set_user_id(user_id: int) -> None:
        """设置当前用户ID"""
        user_id_context.set(user_id)
    
    @staticmethod
    def get_tenant() -> Optional[TenantModel]:
        """获取当前租户"""
        return system_context.get()
    
    @staticmethod
    def get_tenant_id() -> Optional[int]:
        """获取当前租户ID"""
        return tenant_id_context.get()
    
    @staticmethod
    def get_user_id() -> Optional[int]:
        """获取当前用户ID"""
        return user_id_context.get()
    
    @staticmethod
    def clear() -> None:
        """清除系统上下文"""
        system_context.set(None)
        tenant_id_context.set(None)
        user_id_context.set(None)
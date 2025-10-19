from fastapi import APIRouter, Body, Depends, Query
from app.api.vo.system.tenant import TenantPageQuery, CreateTenant, UpdateTenant
from app.core.db import AsyncSessionDep
from app.core.deps import CurrentUser
from app.core.logger import LoggerDep
from app.models.system import TenantModel
from app.services.system.tenant import TenantService
from app.utils.response import success_response
from app.core.deps import require_permission

router = APIRouter(prefix="/tenant", tags=["租户管理"])

async def get_tenant_service(session: AsyncSessionDep, logger: LoggerDep) -> TenantService:
    """获取TenantService实例"""
    return TenantService(session, logger)

@router.get("/list", summary="租户列表")
@require_permission("system:tenant:list")
async def list_tenants(
    current_user: CurrentUser,
    service: TenantService = Depends(get_tenant_service),
):
    return success_response(await service.lists())

@router.get("/page", summary="分页查询")
@require_permission("system:tenant:list")
async def query_tenants(
    current_user: CurrentUser,
    service: TenantService = Depends(get_tenant_service),
    page_query: TenantPageQuery = Query(..., description="查询参数"),
):
    result = await service.get_tenants(page_query)
    return success_response(result)

@router.post("/create", summary="租户新增")
@require_permission("system:tenant:create")
async def create_tenant(
    current_user: CurrentUser,
    tenant: CreateTenant = Body(...),
    service: TenantService = Depends(get_tenant_service),
):
    tenant_model = TenantModel(**tenant.model_dump())
    result = await service.create_tenant(tenant_model)
    return success_response(result)

@router.put("/update", summary="租户更新")
@require_permission("system:tenant:update")
async def update_tenant(
    current_user: CurrentUser,
    tenant: UpdateTenant = Body(...),
    service: TenantService = Depends(get_tenant_service),
):
    result = await service.update_tenant(tenant.model_dump())
    return success_response(result)

@router.delete("/{id}", summary="租户删除")
@require_permission("system:tenant:delete")
async def delete_tenant(
    current_user: CurrentUser,
    id: int,
    service: TenantService = Depends(get_tenant_service),
):
    result = await service.delete_tenant(id)
    return success_response(result)

@router.get("/{id}", summary="获取租户详情")
@require_permission("system:tenant:list")
async def get_tenant_detail(
    current_user: CurrentUser,
    id: int,
    service: TenantService = Depends(get_tenant_service),
):
    result = await service.get_tenant_by_id(id)
    return success_response(result)

@router.put("/update-status", summary="更新租户状态")
@require_permission("system:tenant:update")
async def update_status(
    current_user: CurrentUser,
    status_data: dict = Body(...),
    service: TenantService = Depends(get_tenant_service),
):
    """更新租户状态"""
    result = await service.update_status(status_data["id"], status_data["status"])
    return success_response(msg="状态更新成功")

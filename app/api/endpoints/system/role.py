from fastapi import APIRouter, Body, Depends, Query
from app.api.vo.system.role import RolePageQuery,CreateRole, UpdateRole
from app.core.db import AsyncSessionDep
from app.core.deps import CurrentUser, require_permission
from app.core.logger import LoggerDep
from app.models.system import RoleModel
from app.services.system.role import RoleService
from app.utils.response import success_response

router = APIRouter(prefix="/role", tags=["角色管理"])

async def get_role_service(session: AsyncSessionDep,logger:LoggerDep) -> RoleService:
    """获取RoleService实例"""
    return RoleService(session,logger)
@router.get("/list", summary="角色列表")
@require_permission("system:role:list")
async def list_roles(
    current_user: CurrentUser,
    service: RoleService = Depends(get_role_service),
    ):
    return success_response(await service.lists())

@router.get("/page", summary="分页查询")
@require_permission("system:role:list")
async def query_roles(
    current_user: CurrentUser,
    service: RoleService = Depends(get_role_service),
    page_query: RolePageQuery = Query(..., description="查询参数"),
    ):
    result = await service.get_roles(page_query)
    return success_response(result)

@router.post("/create", summary="角色新增")
@require_permission("system:role:create")
async def create_role(
    current_user: CurrentUser,
    role: CreateRole = Body(...),
    service: RoleService = Depends(get_role_service),
    ):
    role_model = RoleModel(**role.model_dump(exclude={"menu_ids"}))
    result = await service.create_role(role_model,role.menu_ids)
    return success_response(result)

@router.put("/{id}", summary="角色更新")
@require_permission("system:role:update")
async def update_role(
    current_user: CurrentUser,
    role: UpdateRole = Body(...),
    service: RoleService = Depends(get_role_service),
    ):
    result = await service.update_role(role.model_dump(exclude={"menu_ids"}), role.menu_ids)
    return success_response(result)

@router.delete("/{id}", summary="角色删除")
@require_permission("system:role:delete")
async def delete_role(
    current_user: CurrentUser,
    id: int,
    service: RoleService = Depends(get_role_service),
    ):
    result = await service.delete_role(id)
    return success_response(result)

@router.get("/{role_id}/menu", summary="查询角色拥有权限")
@require_permission("system:role:menu")
async def get_menu_by_role_id(
    current_user: CurrentUser,
    role_id: int,
    service: RoleService = Depends(get_role_service),
    ):
    result = await service.get_menu_by_role_id(role_id)
    return success_response(result)


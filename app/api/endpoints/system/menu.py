from fastapi import APIRouter, Body, Depends, Query
from app.api.vo.system.menu import CreateMenu, UpdateMenu
from app.core.db import AsyncSessionDep
from app.core.deps import CurrentUser, require_permission
from app.core.logger import LoggerDep
from app.models.system import PermissionModel
from app.services.system.menu import MenuService
from app.utils.response import success_response

router = APIRouter(prefix="/menu", tags=["菜单管理"])

async def get_menu_service(session: AsyncSessionDep, logger: LoggerDep) -> MenuService:
    """获取MenuService实例"""
    return MenuService(session, logger)


@router.get("/tree", summary="菜单树形结构")
@require_permission("system:menu:tree")
async def tree_menus(
    current_user: CurrentUser,
    service: MenuService = Depends(get_menu_service),
):
    result = await service.get_menu_tree()
    return success_response(result)

@router.post("/create", summary="菜单新增")
@require_permission("system:menu:create")
async def create_menu(
    current_user: CurrentUser,
    menu: CreateMenu = Body(...),
    service: MenuService = Depends(get_menu_service),
):
    if not menu.pid:
        menu.pid = 0
    menu_model = PermissionModel(**menu.model_dump())
    result = await service.create_menu(menu_model)
    return success_response(result)

@router.put("/{id}", summary="菜单更新")
@require_permission("system:menu:update")
async def update_menu(
    current_user: CurrentUser,
    menu: UpdateMenu = Body(...),
    service: MenuService = Depends(get_menu_service),
):
    if not menu.pid:
        menu.pid = 0
    result = await service.update_menu(menu.model_dump())
    return success_response(result)

@router.delete("/{id}", summary="菜单删除")
@require_permission("system:menu:delete")
async def delete_menu(
    current_user: CurrentUser,
    id: int,
    service: MenuService = Depends(get_menu_service),
):
    result = await service.delete_menu(id)
    return success_response(result)

@router.get("/{id}", summary="获取菜单详情")
@require_permission("system:menu:detail")
async def get_menu_detail(
    current_user: CurrentUser,
    id: int,
    service: MenuService = Depends(get_menu_service),
):
    result = await service.get_menu_by_id(id)
    return success_response(result)
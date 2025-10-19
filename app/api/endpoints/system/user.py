from fastapi import APIRouter, Body, Depends, Query
from app.api.vo.system.user import UserPageQuery, CreateUser, UpdateUser, ResetPassword, UpdateStatus
from app.core.db import AsyncSessionDep
from app.core.deps import CurrentUser
from app.core.logger import LoggerDep
from app.models.system import UserModel
from app.services.system.user import UserService
from app.utils.response import success_response
from app.core.deps import require_permission

router = APIRouter(prefix="/user", tags=["用户管理"])

async def get_user_service(session: AsyncSessionDep, logger: LoggerDep) -> UserService:
    """获取UserService实例"""
    return UserService(session, logger)

@router.get("/list", summary="用户列表")
@require_permission("system:user:list")
async def list_users(
    current_user: CurrentUser,
    service: UserService = Depends(get_user_service),
):
    return success_response(await service.lists())

@router.get("/page", summary="分页查询")
@require_permission("system:user:list")
async def query_users(
    current_user: CurrentUser,
    service: UserService = Depends(get_user_service),
    page_query: UserPageQuery = Query(..., description="查询参数"),
):
    result = await service.get_users(page_query)
    return success_response(result)

@router.post("/create", summary="用户新增")
@require_permission("system:user:create")
async def create_user(
    current_user: CurrentUser,
    user: CreateUser = Body(...),
    service: UserService = Depends(get_user_service),
):
    user_model = UserModel(**user.model_dump(exclude={"role_ids"}))
    result = await service.create_user(user_model,user.role_ids)
    return success_response(result)

@router.put("/reset-password", summary="重置用户密码")
@require_permission("system:user:update")
async def reset_password(
    current_user: CurrentUser,
    reset_data: ResetPassword = Body(...),
    service: UserService = Depends(get_user_service),
):
    """重置用户密码"""
    result = await service.reset_password(reset_data.id, reset_data.password)
    return success_response(msg="密码重置成功")

@router.put("/update-status", summary="更新用户状态")
@require_permission("system:user:update")
async def update_status(
    current_user: CurrentUser,
    status_data: UpdateStatus = Body(...),
    service: UserService = Depends(get_user_service),
):
    """更新用户状态"""
    result = await service.update_status(status_data.id, status_data.status)
    return success_response(msg="状态更新成功")

@router.put("/update/{id}", summary="用户更新")
@require_permission("system:user:update")
async def update_user(
    current_user: CurrentUser,
    id:int,
    user_info: dict = Body(...),
    service: UserService = Depends(get_user_service),
):
    user_dict = {
        "id": id,
        "username": user_info.get("username",""),
        "nickname": user_info.get("nickname",""),
        "avatar": user_info.get("avatar",""),
        "phone": user_info.get("phone",""),
        "email": user_info.get("email",""),
        "dept_ids": user_info.get("dept_ids",[]),
        "post_id": user_info.get("post_id",0),
        "status": user_info.get("status",0),
    }
    result = await service.update_user(user_dict, user_info.get("role_ids",[]))
    return success_response(result)

@router.delete("/{id}", summary="用户删除")
@require_permission("system:user:delete")
async def delete_user(
    current_user: CurrentUser,
    id: int,
    service: UserService = Depends(get_user_service),
):
    result = await service.delete_user(id)
    return success_response(result)

@router.get("/{id}", summary="获取用户详情")
@require_permission("system:user:list")
async def get_user_detail(
    current_user: CurrentUser,
    id: int,
    service: UserService = Depends(get_user_service),
):
    result = await service.get_user_by_id(id)
    return success_response(result)

@router.put("/role/{role_id}", summary="用户切换角色")
async def switch_user_role(
    current_user: CurrentUser,
    role_id: int,
    service: UserService = Depends(get_user_service),
):
    result = await service.switch_user_role(role_id)
    return success_response(result)

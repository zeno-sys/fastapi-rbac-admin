# file: d:\Code\20250912-ai-cup\ai-coding-cup-2025\backend\app\api\endpoints\system\dept.py

from fastapi import APIRouter, Body, Depends, UploadFile, File
from typing import List
import json
from app.api.vo.system.dept import CreateDept, UpdateDept

from fastapi import APIRouter, Body, Depends
from app.api.vo.system.dept import CreateDept, UpdateDept, RemoveDeptMember

from app.core.db import AsyncSessionDep
from app.core.deps import CurrentUser, require_permission
from app.core.logger import LoggerDep
from app.models.system import DeptModel
from app.services.system.dept import DeptService
from app.services.system.user import UserService
from app.utils.response import success_response

router = APIRouter(prefix="/dept", tags=["部门管理"])

async def get_dept_service(session: AsyncSessionDep, logger: LoggerDep) -> DeptService:
    """获取DeptService实例"""
    return DeptService(session, logger)


async def get_user_service(session: AsyncSessionDep, logger: LoggerDep) -> UserService:
    """获取UserService实例"""
    return UserService(session, logger)

@router.get("/tree", summary="部门树形结构")
@require_permission("system:dept:tree")
async def tree_depts(
    current_user: CurrentUser,
    dept_id: int = None,
    service: DeptService = Depends(get_dept_service),
):
    result = await service.get_dept_tree(dept_id)
    return success_response(result)

@router.get("/list", summary="部门列表")
@require_permission("system:dept:list")
async def list_depts(
    current_user: CurrentUser,
    service: DeptService = Depends(get_dept_service),
):
    result = await service.lists()
    return success_response(result)

@router.get("/{id}/users", summary="获取部门成员列表")
@require_permission("system:dept:list")
async def list_dept_users(
    current_user: CurrentUser,
    id: int,
    service: UserService = Depends(get_user_service),
):
    """根据部门ID获取部门成员列表"""
    result = await service.get_users_by_dept_id(id)
    return success_response(result)

@router.post("/remove-member", summary="移除部门成员")
@require_permission("system:dept:remove-member")
async def remove_dept_member(
    current_user: CurrentUser,
    member: RemoveDeptMember = Body(...),
    service: UserService = Depends(get_user_service),
):
    """从部门中移除指定成员"""
    result = await service.remove_user_from_dept(member.dept_id, member.user_id)
    if result:
        return success_response(result, "成员移除成功")
    else:
        return success_response(result, "成员移除失败，用户不存在或不属于该部门")

@router.post("/create", summary="部门新增")
@require_permission("system:dept:create")
async def create_dept(
    current_user: CurrentUser,
    dept: CreateDept = Body(...),
    service: DeptService = Depends(get_dept_service),
):
    if not dept.pid:
        dept.pid = 0
    dept_model = DeptModel(**dept.model_dump())
    result = await service.create_dept(dept_model)
    return success_response(result)

@router.put("/update", summary="部门更新")
@require_permission("system:dept:update")
async def update_dept(
    current_user: CurrentUser,
    dept: UpdateDept = Body(...),
    service: DeptService = Depends(get_dept_service),
):
    if not dept.pid:
        dept.pid = 0
    result = await service.update_dept(dept.model_dump())
    return success_response(result)

@router.delete("/{id}", summary="部门删除")
@require_permission("system:dept:delete")
async def delete_dept(
    current_user: CurrentUser,
    id: int,
    service: DeptService = Depends(get_dept_service),
):
    result = await service.delete_dept(id)
    return success_response(result)

@router.get("/{id}", summary="获取部门详情")
@require_permission("system:dept:detail")
async def get_dept_detail(
    current_user: CurrentUser,
    id: int,
    service: DeptService = Depends(get_dept_service),
):
    result = await service.get_dept_by_id(id)
    return success_response(result)


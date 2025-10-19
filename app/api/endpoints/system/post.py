from fastapi import APIRouter, Body, Depends
from typing import List
from app.api.vo.system.post import CreatePost, UpdatePost, PostResponse
from app.core.db import AsyncSessionDep
from app.core.deps import CurrentUser, require_permission
from app.core.logger import LoggerDep
from app.models.system import PostModel
from app.services.system.post import PostService
from app.utils.response import success_response

router = APIRouter(prefix="/post", tags=["岗位管理"])

async def get_post_service(session: AsyncSessionDep, logger: LoggerDep) -> PostService:
    """获取PostService实例"""
    return PostService(session, logger)

@router.get("/list", summary="岗位列表")
@require_permission("system:post:list")
async def list_posts(
    current_user: CurrentUser,
    service: PostService = Depends(get_post_service),
):
    result = await service.lists()
    return success_response(result)

@router.post("/create", summary="岗位新增")
@require_permission("system:post:create")
async def create_post(
    current_user: CurrentUser,
    post: CreatePost = Body(...),
    service: PostService = Depends(get_post_service),
):
    post_model = PostModel(**post.model_dump())
    result = await service.create_post(post_model)
    return success_response(result)

@router.put("/update", summary="岗位更新")
@require_permission("system:post:update")
async def update_post(
    current_user: CurrentUser,
    post: UpdatePost = Body(...),
    service: PostService = Depends(get_post_service),
):
    result = await service.update_post(post.model_dump())
    return success_response(result)

@router.delete("/{id}", summary="岗位删除")
@require_permission("system:post:delete")
async def delete_post(
    current_user: CurrentUser,
    id: int,
    service: PostService = Depends(get_post_service),
):
    result = await service.delete_post(id)
    return success_response(result)

@router.get("/{id}", summary="获取岗位详情")
@require_permission("system:post:query")
async def get_post_detail(
    current_user: CurrentUser,
    id: int,
    service: PostService = Depends(get_post_service),
):
    result = await service.get_post_by_id(id)
    return success_response(result)
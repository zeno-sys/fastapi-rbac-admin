from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, TypeVar

from app.models.common import BaseResponse

T = TypeVar("T")


def success_response(
    data: Optional[T] = None, msg: str = "响应成功", code: int = 200
) -> JSONResponse:
    """成功响应"""
    response = BaseResponse[T](
        success=True,
        code=code,
        msg=msg,
        data=jsonable_encoder(data, exclude_none=True),  # 处理复杂对象序列化
    )
    return JSONResponse(status_code=200, content=response.model_dump(exclude_none=True))


def error_response(
    msg: str, code: int = 456, err: Optional[T] = None
) -> JSONResponse:
    """错误响应"""
    response = BaseResponse[None](
        success=False, code=code, msg=msg, err=err
    )
    return JSONResponse(
        status_code=code, content=response.model_dump(exclude_none=True)
    )


# 大模型流式输出chunk定义
from enum import Enum
from pydantic import BaseModel, Field, field_validator


# 定义枚举类型
class ContentType(str, Enum):
    TEXT = "text"
    HTML = "html"


class ChunkData(BaseModel):
    content: str
    progress: int = Field(..., ge=0, le=100)  # 取值0-100
    content_type: ContentType  # 使用枚举替代Literal，字段名改为content_type

    @field_validator("progress")
    def check_progress(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("progress必须在0-100之间")
        return v

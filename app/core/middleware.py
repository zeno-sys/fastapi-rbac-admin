from datetime import datetime
from uuid import uuid4
from fastapi import Request
from app.core.logger import logger

class RequestContext:
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.start_time = None

def register_middleware(app):
    
    @app.middleware("http")
    async def add_request_logging(request: Request, call_next):
        # 生成或获取请求ID
        request_id = request.headers.get("X-Request-ID", str(uuid4().hex))
        request.state.request_id = request_id
        
        # 创建日志上下文
        request_context = RequestContext(request_id)
        request.state.request_context = request_context
        request_context.start_time = datetime.now()
        
        # 绑定请求ID到日志
        bound_logger = logger.bind(request_id=request_id)
        
        # 记录请求开始
        bound_logger.info(
            "Request started: {} {} from {}",
            request.method, 
            request.url,
            request.client.host if request.client else "unknown"
        )
        
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = (datetime.now() - request_context.start_time).total_seconds()
            
            # 记录请求完成
            bound_logger.info(
                "Request completed: status={} duration={:.3f}s",
                response.status_code,
                process_time
            )
            
            # 添加请求ID到响应头
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            bound_logger.error(
                "Request failed: {}",
                str(e),
                exc_info=True
            )
            raise
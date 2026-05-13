"""Redis 限流中间件"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

from app.database.redis import redis_client

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """基于 Redis 的速率限制中间件"""
    
    def __init__(
        self,
        app,
        max_requests: int = 60,
        window: int = 60,
        exclude_paths: list = None
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.exclude_paths = exclude_paths or ["/api/health", "/docs", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next):
        # 跳过排除的路径
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 检查速率限制
        try:
            is_allowed = await redis_client.check_rate_limit(
                key=client_ip,
                max_requests=self.max_requests,
                window=self.window
            )
            
            if not is_allowed:
                remaining = await redis_client.get_rate_limit_remaining(
                    key=client_ip,
                    max_requests=self.max_requests
                )
                return JSONResponse(
                    status_code=429,
                    content={"error": "Too many requests", "detail": f"Rate limit exceeded. Try again in {self.window} seconds."},
                    headers={"X-RateLimit-Remaining": str(remaining)}
                )
            
            # 获取剩余次数
            remaining = await redis_client.get_rate_limit_remaining(
                key=client_ip,
                max_requests=self.max_requests
            )
            
            # 处理请求
            response = await call_next(request)
            
            # 添加限流头
            response.headers["X-RateLimit-Limit"] = str(self.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(self.window)
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Redis 连接失败时放行
            return await call_next(request)

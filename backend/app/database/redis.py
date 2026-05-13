"""Redis 连接"""

import redis.asyncio as redis
from typing import Optional, Any
import json
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis 客户端封装"""
    
    def __init__(self):
        self.settings = get_settings()
        self.pool: Optional[redis.ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """连接 Redis"""
        try:
            self.pool = redis.ConnectionPool(
                host=self.settings.redis_host,
                port=self.settings.redis_port,
                db=self.settings.redis_db,
                decode_responses=True,
                max_connections=20
            )
            self.client = redis.Redis(connection_pool=self.pool)
            
            # 验证连接
            await self.client.ping()
            logger.info(f"Connected to Redis at {self.settings.redis_host}:{self.settings.redis_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
        logger.info("Disconnected from Redis")
    
    # ==================== 会话管理 ====================
    
    async def save_session(self, session_id: str, data: dict, expire: int = 3600):
        """保存会话数据"""
        key = f"session:{session_id}"
        await self.client.hset(key, mapping={k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) 
                                              for k, v in data.items()})
        await self.client.expire(key, expire)
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话数据"""
        key = f"session:{session_id}"
        data = await self.client.hgetall(key)
        if not data:
            return None
        # 尝试解析 JSON
        result = {}
        for k, v in data.items():
            try:
                result[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                result[k] = v
        return result
    
    async def delete_session(self, session_id: str):
        """删除会话"""
        key = f"session:{session_id}"
        await self.client.delete(key)
    
    async def add_chat_history(self, session_id: str, role: str, content: str, max_history: int = 50):
        """添加聊天历史"""
        key = f"chat_history:{session_id}"
        message = json.dumps({"role": role, "content": content})
        await self.client.rpush(key, message)
        # 保留最近的记录
        await self.client.ltrim(key, -max_history, -1)
        await self.client.expire(key, 3600 * 24)  # 24小时过期
    
    async def get_chat_history(self, session_id: str, limit: int = 20) -> list:
        """获取聊天历史"""
        key = f"chat_history:{session_id}"
        messages = await self.client.lrange(key, -limit, -1)
        return [json.loads(msg) for msg in messages]
    
    # ==================== 缓存 ====================
    
    async def cache_set(self, key: str, value: Any, expire: int = 3600):
        """设置缓存"""
        cache_key = f"cache:{key}"
        if isinstance(value, (dict, list)):
            await self.client.set(cache_key, json.dumps(value, ensure_ascii=False), ex=expire)
        else:
            await self.client.set(cache_key, str(value), ex=expire)
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        cache_key = f"cache:{key}"
        value = await self.client.get(cache_key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def cache_delete(self, key: str):
        """删除缓存"""
        cache_key = f"cache:{key}"
        await self.client.delete(cache_key)
    
    # ==================== 限流 ====================
    
    async def check_rate_limit(self, key: str, max_requests: int = 60, window: int = 60) -> bool:
        """检查速率限制
        
        Args:
            key: 限流键（通常是 IP 地址）
            max_requests: 窗口内最大请求数
            window: 时间窗口（秒）
        
        Returns:
            True: 允许请求, False: 超出限制
        """
        rate_key = f"rate_limit:{key}"
        current = await self.client.get(rate_key)
        
        if current is None:
            await self.client.set(rate_key, 1, ex=window)
            return True
        
        if int(current) >= max_requests:
            return False
        
        await self.client.incr(rate_key)
        return True
    
    async def get_rate_limit_remaining(self, key: str, max_requests: int = 60) -> int:
        """获取剩余请求次数"""
        rate_key = f"rate_limit:{key}"
        current = await self.client.get(rate_key)
        if current is None:
            return max_requests
        return max(0, max_requests - int(current))


# 全局客户端实例
redis_client = RedisClient()

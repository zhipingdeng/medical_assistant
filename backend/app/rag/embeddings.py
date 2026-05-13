"""Embedding 模型封装"""

import httpx
from typing import List
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Ollama Embedding 模型"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.embedding_base_url
        self.model_name = self.settings.embedding_model_name
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量生成文档 embedding"""
        embeddings = []
        for text in texts:
            embedding = await self.embed_query(text)
            embeddings.append(embedding)
        return embeddings
    
    async def embed_query(self, text: str) -> List[float]:
        """生成查询 embedding"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.model_name,
                        "prompt": text
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["embedding"]
        except Exception as e:
            logger.warning(f"Ollama embedding failed, using simple hash: {e}")
            # Fallback: 使用简单 hash embedding
            import hashlib, struct
            hash_bytes = hashlib.sha512(text.encode('utf-8')).digest()
            dim = self.settings.embedding_dimension
            extended = hash_bytes * (dim * 4 // len(hash_bytes) + 1)
            values = []
            for i in range(dim):
                byte_start = i * 4
                val = struct.unpack('f', extended[byte_start:byte_start + 4])[0]
                if val != val:
                    val = 0.0
                val = max(-1.0, min(1.0, val / 1e30)) if abs(val) > 1e30 else val
                values.append(val)
            norm = sum(v ** 2 for v in values) ** 0.5
            if norm > 0:
                values = [v / norm for v in values]
            return values


# 全局实例
embedding_model = EmbeddingModel()

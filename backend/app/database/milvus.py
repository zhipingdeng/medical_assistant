"""Milvus 向量数据库连接"""

from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
from typing import List, Dict, Any, Optional
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


class MilvusClient:
    """Milvus 客户端封装"""
    
    def __init__(self):
        self.settings = get_settings()
        self.collection: Optional[Collection] = None
        self._connected = False
    
    async def connect(self):
        """连接 Milvus"""
        try:
            connections.connect(
                alias="default",
                host=self.settings.milvus_host,
                port=self.settings.milvus_port
            )
            self._connected = True
            logger.info(f"Connected to Milvus at {self.settings.milvus_host}:{self.settings.milvus_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    
    async def disconnect(self):
        """断开连接"""
        try:
            connections.disconnect("default")
            self._connected = False
            logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error disconnecting from Milvus: {e}")
    
    def create_collection(self):
        """创建疾病集合"""
        collection_name = self.settings.milvus_collection_name
        
        # 检查集合是否存在
        if utility.has_collection(collection_name):
            logger.info(f"Collection {collection_name} already exists")
            self.collection = Collection(collection_name)
            return
        
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=8000),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="symptoms", dtype=DataType.VARCHAR, max_length=4000),
            FieldSchema(name="department", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="prevention", dtype=DataType.VARCHAR, max_length=32000),
            FieldSchema(name="treatment", dtype=DataType.VARCHAR, max_length=4000),
            FieldSchema(name="drugs", dtype=DataType.VARCHAR, max_length=4000),
            FieldSchema(name="checks", dtype=DataType.VARCHAR, max_length=4000),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.settings.embedding_dimension)
        ]
        
        schema = CollectionSchema(fields=fields, description="Medical diseases collection")
        self.collection = Collection(name=collection_name, schema=schema)
        
        # 创建向量索引
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)
        logger.info(f"Created collection {collection_name} with index")
    
    def insert(self, data: List[Dict[str, Any]]) -> List[int]:
        """插入数据"""
        if not self.collection:
            self.collection = Collection(self.settings.milvus_collection_name)
        
        # 准备数据
        insert_data = [
            [d["name"] for d in data],
            [d["description"] for d in data],
            [d["category"] for d in data],
            [d["symptoms"] for d in data],
            [d["department"] for d in data],
            [d["prevention"] for d in data],
            [d["treatment"] for d in data],
            [d["drugs"] for d in data],
            [d["checks"] for d in data],
            [d["embedding"] for d in data]
        ]
        
        result = self.collection.insert(insert_data)
        self.collection.flush()
        logger.info(f"Inserted {len(data)} documents")
        return result.primary_keys
    
    def search(self, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """向量检索"""
        if not self.collection:
            self.collection = Collection(self.settings.milvus_collection_name)
        
        self.collection.load()
        
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 16}
        }
        
        results = self.collection.search(
            data=[embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["name", "description", "category", "symptoms", "department", 
                          "prevention", "treatment", "drugs", "checks"]
        )
        
        # 格式化结果
        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    "id": hit.id,
                    "score": hit.score,
                    **hit.entity
                })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        if not self.collection:
            self.collection = Collection(self.settings.milvus_collection_name)
        
        self.collection.flush()
        return {
            "name": self.collection.name,
            "num_entities": self.collection.num_entities,
            "schema": str(self.collection.schema)
        }


# 全局客户端实例
milvus_client = MilvusClient()

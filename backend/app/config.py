"""配置管理模块"""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # ==================== LLM 配置 ====================
    llm_model_name: str = "mimo-v2.5-pro"
    llm_api_key: str = ""
    llm_base_url: str = "https://token-plan-cn.xiaomimimo.com/v1"
    
    # ==================== Embedding 配置 ====================
    embedding_model_name: str = "bge-m3"
    embedding_base_url: str = "http://172.22.80.1:11434"
    embedding_dimension: int = 1024
    
    # ==================== Milvus 配置 ====================
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_collection_name: str = "medical_diseases"
    
    # ==================== Neo4j 配置 ====================
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "medical123"
    
    # ==================== Redis 配置 ====================
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # ==================== 应用配置 ====================
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    
    # ==================== 数据文件 ====================
    data_dir: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    medical_data_file: str = os.path.join(data_dir, "medical.json")
    
    model_config = {
        "env_file": os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()

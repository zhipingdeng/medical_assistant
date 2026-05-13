"""健康检查 API"""

from fastapi import APIRouter
import logging

from app.models.schemas import HealthResponse
from app.database.milvus import milvus_client
from app.database.neo4j import neo4j_client
from app.database.redis import redis_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    services = {}
    
    # 检查 Milvus
    try:
        stats = milvus_client.get_collection_stats()
        services["milvus"] = "connected"
    except Exception as e:
        services["milvus"] = f"error: {str(e)[:50]}"
    
    # 检查 Neo4j
    try:
        await neo4j_client.get_stats()
        services["neo4j"] = "connected"
    except Exception as e:
        services["neo4j"] = f"error: {str(e)[:50]}"
    
    # 检查 Redis
    try:
        if redis_client.client:
            await redis_client.client.ping()
            services["redis"] = "connected"
        else:
            services["redis"] = "not initialized"
    except Exception as e:
        services["redis"] = f"error: {str(e)[:50]}"
    
    return HealthResponse(
        status="ok",
        version="1.0.0",
        services=services
    )

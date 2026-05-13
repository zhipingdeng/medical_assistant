"""FastAPI 应用入口"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from app.config import get_settings
from app.api.v1.chat import router as chat_router
from app.api.v1.disease import router as disease_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.consultation import router as consultation_router
from app.middleware.rate_limit import RateLimitMiddleware

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    settings = get_settings()
    
    # ==================== 启动时初始化 ====================
    logger.info("Starting Medical Assistant API...")
    
    # 初始化 Milvus
    try:
        from app.database.milvus import milvus_client
        await milvus_client.connect()
        milvus_client.create_collection()
        logger.info("Milvus initialized")
    except Exception as e:
        logger.error(f"Milvus initialization failed: {e}")
    
    # 初始化 Neo4j
    try:
        from app.database.neo4j import neo4j_client
        await neo4j_client.connect()
        await neo4j_client.create_constraints()
        logger.info("Neo4j initialized")
    except Exception as e:
        logger.error(f"Neo4j initialization failed: {e}")
    
    # 初始化 Redis
    try:
        from app.database.redis import redis_client
        await redis_client.connect()
        logger.info("Redis initialized")
    except Exception as e:
        logger.error(f"Redis initialization failed: {e}")
    
    # 初始化 MySQL
    try:
        from app.database.mysql import init_db
        init_db()
        logger.info("MySQL initialized")
    except Exception as e:
        logger.error(f"MySQL initialization failed: {e}")
    
    # 初始化 LLM 和智能体
    try:
        from langchain_openai import ChatOpenAI
        from app.agents import init_supervisor, init_diagnosis, init_knowledge, init_symptom
        
        llm = ChatOpenAI(
            model=settings.llm_model_name,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            temperature=0.7,
            streaming=True
        )
        
        init_supervisor(llm)
        init_diagnosis(llm)
        init_knowledge(llm)
        init_symptom(llm)
        logger.info("Agents initialized")
    except Exception as e:
        logger.error(f"Agent initialization failed: {e}")
    
    logger.info(f"Medical Assistant API started on {settings.app_host}:{settings.app_port}")
    
    yield
    
    # ==================== 关闭时清理 ====================
    logger.info("Shutting down Medical Assistant API...")
    
    try:
        from app.database.milvus import milvus_client
        await milvus_client.disconnect()
    except Exception as e:
        logger.error(f"Milvus disconnect error: {e}")
    
    try:
        from app.database.neo4j import neo4j_client
        await neo4j_client.disconnect()
    except Exception as e:
        logger.error(f"Neo4j disconnect error: {e}")
    
    try:
        from app.database.redis import redis_client
        await redis_client.disconnect()
    except Exception as e:
        logger.error(f"Redis disconnect error: {e}")
    
    logger.info("Medical Assistant API stopped")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    settings = get_settings()
    
    app = FastAPI(
        title="Medical Assistant API",
        description="基于 LangGraph 多智能体的医疗智能助手系统",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 限流中间件
    app.add_middleware(RateLimitMiddleware, max_requests=60, window=60)
    
    # 注册路由
    app.include_router(auth_router)
    app.include_router(consultation_router)
    app.include_router(chat_router)
    app.include_router(disease_router)
    app.include_router(knowledge_router)
    app.include_router(health_router)
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )

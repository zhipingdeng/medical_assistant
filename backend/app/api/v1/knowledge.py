"""知识图谱 API"""

from fastapi import APIRouter, HTTPException, Query
import logging

from app.models.schemas import KnowledgeGraphResponse, KnowledgeGraphNode, KnowledgeGraphEdge
from app.database.neo4j import neo4j_client
from app.rag.hybrid_search import hybrid_retriever

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


@router.get("/graph", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(
    center: str = Query(..., description="中心节点名称"),
    depth: int = Query(2, ge=1, le=3, description="图谱深度")
):
    """获取知识图谱数据（用于可视化）"""
    try:
        graph_data = await hybrid_retriever.get_knowledge_graph_data(center, depth)
        
        nodes = [
            KnowledgeGraphNode(
                id=node["id"],
                label=node["label"],
                name=node["name"],
                properties=node.get("properties", {})
            )
            for node in graph_data.get("nodes", [])
        ]
        
        edges = [
            KnowledgeGraphEdge(
                source=edge["source"],
                target=edge["target"],
                type=edge["type"]
            )
            for edge in graph_data.get("edges", [])
        ]
        
        return KnowledgeGraphResponse(nodes=nodes, edges=edges)
        
    except Exception as e:
        logger.error(f"Get knowledge graph failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_knowledge(
    q: str = Query(..., min_length=1, max_length=500, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="返回数量")
):
    """搜索知识图谱"""
    try:
        # 搜索相关疾病
        diseases = await neo4j_client.search_by_symptom(q, limit=limit)
        
        # 搜索相关症状
        results = await hybrid_retriever.search(q, top_k=limit)
        
        return {
            "query": q,
            "diseases": diseases,
            "results": results.get("combined_results", [])
        }
        
    except Exception as e:
        logger.error(f"Knowledge search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_knowledge_stats():
    """获取知识图谱统计信息"""
    try:
        stats = await neo4j_client.get_stats()
        return {"stats": stats}
    except Exception as e:
        logger.error(f"Get knowledge stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

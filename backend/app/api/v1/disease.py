"""疾病查询 API"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from app.models.schemas import (
    DiseaseInfo,
    DiseaseSearchRequest,
    DiseaseSearchResponse,
    KnowledgeGraphRequest,
    KnowledgeGraphResponse
)
from app.rag.hybrid_search import hybrid_retriever
from app.database.neo4j import neo4j_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/diseases", tags=["diseases"])


@router.get("", response_model=DiseaseSearchResponse)
async def search_diseases(
    q: str = Query(..., min_length=1, max_length=500, description="搜索关键词"),
    top_k: int = Query(10, ge=1, le=50, description="返回数量")
):
    """搜索疾病"""
    try:
        results = await hybrid_retriever.search(
            query=q,
            top_k=top_k,
            use_vector=True,
            use_graph=True
        )
        
        diseases = []
        for result in results.get("combined_results", []):
            diseases.append(DiseaseInfo(
                name=result.get("name", ""),
                description=result.get("description"),
                category=result.get("category"),
                symptoms=result.get("symptoms"),
                departments=result.get("departments") or result.get("department"),
                prevention=result.get("prevention"),
                treatment=result.get("treatment"),
                drugs=result.get("drugs"),
                checks=result.get("checks"),
                cured_prob=result.get("cured_prob"),
                cost_money=result.get("cost_money"),
                accompanies=result.get("accompanies")
            ))
        
        return DiseaseSearchResponse(results=diseases, total=len(diseases))
        
    except Exception as e:
        logger.error(f"Disease search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{disease_name}", response_model=DiseaseInfo)
async def get_disease_detail(disease_name: str):
    """获取疾病详情"""
    try:
        disease = await hybrid_retriever.get_disease_detail(disease_name)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease '{disease_name}' not found")
        
        return DiseaseInfo(
            name=disease.get("name", ""),
            description=disease.get("description"),
            category=disease.get("category"),
            symptoms=disease.get("symptoms"),
            departments=disease.get("departments"),
            prevention=disease.get("prevention"),
            treatment=disease.get("treatment"),
            drugs=disease.get("drugs"),
            checks=disease.get("checks"),
            cured_prob=disease.get("cured_prob"),
            cost_money=disease.get("cost_money"),
            accompanies=disease.get("accompanies")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get disease detail failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{disease_name}/related")
async def get_related_diseases(disease_name: str):
    """获取相关疾病"""
    try:
        related = await neo4j_client.get_related_diseases(disease_name)
        return {"disease": disease_name, "related": related}
    except Exception as e:
        logger.error(f"Get related diseases failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
async def get_disease_stats():
    """获取疾病统计概览"""
    try:
        stats = await neo4j_client.get_stats()
        return {"stats": stats}
    except Exception as e:
        logger.error(f"Get disease stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

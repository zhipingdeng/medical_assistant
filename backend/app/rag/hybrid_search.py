"""混合检索 - 结合向量检索和知识图谱"""

from typing import List, Dict, Any, Optional
import logging

from app.database.milvus import milvus_client
from app.database.neo4j import neo4j_client
from app.rag.embeddings import embedding_model

logger = logging.getLogger(__name__)


class HybridRetriever:
    """混合检索器"""
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        use_vector: bool = True,
        use_graph: bool = True
    ) -> Dict[str, Any]:
        """混合检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            use_vector: 是否使用向量检索
            use_graph: 是否使用知识图谱
        
        Returns:
            检索结果
        """
        results = {
            "vector_results": [],
            "graph_results": [],
            "combined_results": []
        }
        
        # 向量检索
        if use_vector:
            try:
                embedding = await embedding_model.embed_query(query)
                vector_results = milvus_client.search(embedding, top_k=top_k)
                results["vector_results"] = vector_results
            except Exception as e:
                logger.error(f"Vector search failed: {e}")
        
        # 知识图谱检索
        if use_graph:
            try:
                # 尝试直接匹配疾病
                disease_info = await neo4j_client.get_disease_info(query)
                if disease_info:
                    results["graph_results"].append(disease_info)
                
                # 根据症状搜索
                symptom_results = await neo4j_client.search_by_symptom(query, limit=top_k)
                results["graph_results"].extend(symptom_results)
            except Exception as e:
                logger.error(f"Graph search failed: {e}")
        
        # RRF 融合排序
        results["combined_results"] = self._rrf_merge(
            results["vector_results"],
            results["graph_results"],
            k=60
        )
        
        return results
    
    def _rrf_merge(
        self,
        vector_results: List[Dict],
        graph_results: List[Dict],
        k: int = 60
    ) -> List[Dict]:
        """RRF (Reciprocal Rank Fusion) 融合排序
        
        Args:
            vector_results: 向量检索结果
            graph_results: 图检索结果
            k: RRF 参数
        
        Returns:
            融合排序后的结果
        """
        scores = {}
        
        # 向量检索结果计分
        for rank, result in enumerate(vector_results):
            name = result.get("name", "")
            if name not in scores:
                scores[name] = {"score": 0, "data": result}
            scores[name]["score"] += 1.0 / (k + rank + 1)
        
        # 图检索结果计分
        for rank, result in enumerate(graph_results):
            name = result.get("name", "")
            if name not in scores:
                scores[name] = {"score": 0, "data": result}
            scores[name]["score"] += 1.0 / (k + rank + 1)
        
        # 按分数排序
        sorted_results = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        return [
            {"name": name, "rrf_score": data["score"], **data["data"]}
            for name, data in sorted_results
        ]
    
    async def get_disease_detail(self, disease_name: str) -> Optional[Dict[str, Any]]:
        """获取疾病详情"""
        # 先从图数据库获取
        graph_info = await neo4j_client.get_disease_info(disease_name)
        if graph_info:
            # 获取相关疾病
            related = await neo4j_client.get_related_diseases(disease_name)
            graph_info["related_diseases"] = related
            return graph_info
        
        # 从向量数据库模糊搜索
        embedding = await embedding_model.embed_query(disease_name)
        results = milvus_client.search(embedding, top_k=1)
        if results:
            return results[0]
        
        return None
    
    async def get_knowledge_graph_data(self, center_node: str, depth: int = 2) -> Dict[str, Any]:
        """获取知识图谱可视化数据"""
        return await neo4j_client.get_knowledge_graph(center_node, depth)


# 全局实例
hybrid_retriever = HybridRetriever()

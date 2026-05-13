"""Neo4j 图数据库连接"""

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from typing import List, Dict, Any, Optional
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j 客户端封装"""
    
    def __init__(self):
        self.settings = get_settings()
        self.driver: Optional[AsyncDriver] = None
    
    async def connect(self):
        """连接 Neo4j"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.settings.neo4j_uri,
                auth=(self.settings.neo4j_user, self.settings.neo4j_password)
            )
            # 验证连接
            await self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.settings.neo4j_uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    async def disconnect(self):
        """断开连接"""
        if self.driver:
            await self.driver.close()
            logger.info("Disconnected from Neo4j")
    
    async def create_constraints(self):
        """创建约束和索引"""
        constraints = [
            "CREATE CONSTRAINT disease_name IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE",
            "CREATE CONSTRAINT symptom_name IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT department_name IF NOT EXISTS FOR (dep:Department) REQUIRE dep.name IS UNIQUE",
            "CREATE CONSTRAINT drug_name IF NOT EXISTS FOR (dr:Drug) REQUIRE dr.name IS UNIQUE",
            "CREATE CONSTRAINT check_name IF NOT EXISTS FOR (c:Check) REQUIRE c.name IS UNIQUE",
        ]
        
        async with self.driver.session() as session:
            for constraint in constraints:
                try:
                    await session.run(constraint)
                except Exception as e:
                    logger.warning(f"Constraint creation warning: {e}")
        
        logger.info("Created Neo4j constraints")
    
    async def create_disease_node(self, disease: Dict[str, Any]):
        """创建疾病节点及相关关系"""
        query = """
        MERGE (d:Disease {name: $name})
        SET d.description = $description,
            d.category = $category,
            d.prevention = $prevention,
            d.cure_way = $treatment,
            d.cured_prob = $cured_prob,
            d.cost_money = $cost_money
        
        WITH d
        UNWIND $symptoms AS symptom_name
        MERGE (s:Symptom {name: symptom_name})
        MERGE (d)-[:HAS_SYMPTOM]->(s)
        
        WITH d
        UNWIND $departments AS dept_name
        MERGE (dep:Department {name: dept_name})
        MERGE (d)-[:BELONGS_TO]->(dep)
        
        WITH d
        UNWIND $drugs AS drug_name
        MERGE (dr:Drug {name: drug_name})
        MERGE (d)-[:RECOMMENDS_DRUG]->(dr)
        
        WITH d
        UNWIND $checks AS check_name
        MERGE (c:Check {name: check_name})
        MERGE (d)-[:REQUIRES_CHECK]->(c)
        """
        
        async with self.driver.session() as session:
            await session.run(query, **disease)
    
    async def create_accompanies_relations(self, disease_name: str, accompanies: List[str]):
        """创建并发症关系"""
        query = """
        MATCH (d:Disease {name: $disease_name})
        UNWIND $accompanies AS acc_name
        MERGE (acc:Disease {name: acc_name})
        MERGE (d)-[:ACCOMPANIES]->(acc)
        """
        
        async with self.driver.session() as session:
            await session.run(query, disease_name=disease_name, accompanies=accompanies)
    
    async def get_disease_info(self, disease_name: str) -> Optional[Dict[str, Any]]:
        """获取疾病详细信息"""
        query = """
        MATCH (d:Disease {name: $name})
        OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
        OPTIONAL MATCH (d)-[:BELONGS_TO]->(dep:Department)
        OPTIONAL MATCH (d)-[:RECOMMENDS_DRUG]->(dr:Drug)
        OPTIONAL MATCH (d)-[:REQUIRES_CHECK]->(c:Check)
        OPTIONAL MATCH (d)-[:ACCOMPANIES]->(acc:Disease)
        RETURN d,
               collect(DISTINCT s.name) AS symptoms,
               collect(DISTINCT dep.name) AS departments,
               collect(DISTINCT dr.name) AS drugs,
               collect(DISTINCT c.name) AS checks,
               collect(DISTINCT acc.name) AS accompanies
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, name=disease_name)
            record = await result.single()
            
            if record:
                d = record["d"]
                return {
                    "name": d["name"],
                    "description": d.get("description", ""),
                    "category": d.get("category", ""),
                    "prevention": d.get("prevention", ""),
                    "treatment": d.get("cure_way", ""),
                    "cured_prob": d.get("cured_prob", ""),
                    "cost_money": d.get("cost_money", ""),
                    "symptoms": record["symptoms"],
                    "departments": record["departments"],
                    "drugs": record["drugs"],
                    "checks": record["checks"],
                    "accompanies": record["accompanies"]
                }
            return None
    
    async def search_by_symptom(self, symptom_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """根据症状搜索疾病"""
        query = """
        MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
        WHERE s.name CONTAINS $symptom
        RETURN d.name AS name, d.description AS description,
               collect(DISTINCT s.name) AS symptoms
        LIMIT $limit
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, symptom=symptom_name, limit=limit)
            records = await result.data()
            return records
    
    async def get_related_diseases(self, disease_name: str) -> List[Dict[str, Any]]:
        """获取相关疾病（相同症状）"""
        query = """
        MATCH (d1:Disease {name: $name})-[:HAS_SYMPTOM]->(s:Symptom)<-[:HAS_SYMPTOM]-(d2:Disease)
        WHERE d1 <> d2
        WITH d2, count(s) AS shared_symptoms
        ORDER BY shared_symptoms DESC
        LIMIT 5
        RETURN d2.name AS name, d2.description AS description, shared_symptoms
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, name=disease_name)
            return await result.data()
    
    async def get_knowledge_graph(self, center_node: str, depth: int = 2) -> Dict[str, Any]:
        """获取知识图谱数据（用于可视化）"""
        # 查询中心节点及其直接关系
        query = """
        MATCH (center {name: $name})-[r]-(related)
        RETURN center, r, related
        LIMIT 100
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, name=center_node)
            
            nodes = []
            seen_ids = set()
            edges = []
            seen_edges = set()
            
            async for record in result:
                center = record["center"]
                related = record["related"]
                rel = record["r"]
                
                # 添加中心节点
                if center and center.element_id not in seen_ids:
                    labels = list(center.labels)
                    nodes.append({
                        "id": center.element_id,
                        "label": labels[0] if labels else "Unknown",
                        "name": center.get("name", ""),
                        "properties": {k: v for k, v in center.items() if k != "name"}
                    })
                    seen_ids.add(center.element_id)
                
                # 添加关联节点
                if related and related.element_id not in seen_ids:
                    labels = list(related.labels)
                    nodes.append({
                        "id": related.element_id,
                        "label": labels[0] if labels else "Unknown",
                        "name": related.get("name", ""),
                        "properties": {k: v for k, v in related.items() if k != "name"}
                    })
                    seen_ids.add(related.element_id)
                
                # 添加边
                if rel is not None:
                    edge_key = (rel.start_node.element_id, rel.end_node.element_id, rel.type)
                    if edge_key not in seen_edges:
                        edges.append({
                            "source": rel.start_node.element_id,
                            "target": rel.end_node.element_id,
                            "type": rel.type
                        })
                        seen_edges.add(edge_key)
            
            return {"nodes": nodes, "edges": edges}
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        query = """
        MATCH (n)
        RETURN labels(n)[0] AS label, count(n) AS count
        ORDER BY count DESC
        """
        
        async with self.driver.session() as session:
            result = await session.run(query)
            records = await result.data()
            return {r["label"]: r["count"] for r in records}


# 全局客户端实例
neo4j_client = Neo4jClient()

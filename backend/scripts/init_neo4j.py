"""初始化 Neo4j 知识图谱"""

import json
import sys
import os
import logging
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import get_settings
from app.database.neo4j import neo4j_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_medical_data(file_path: str) -> List[Dict[str, Any]]:
    """加载医疗数据"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    item = json.loads(line)
                    data.append(item)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse line: {e}")
    return data


def process_disease(disease: Dict[str, Any]) -> Dict[str, Any]:
    """处理疾病数据"""
    # 提取症状
    symptoms = disease.get("symptom", [])
    if not isinstance(symptoms, list):
        symptoms = [str(symptoms)]
    
    # 提取分类
    category = disease.get("category", [])
    if isinstance(category, list):
        category_str = " > ".join(category)
    else:
        category_str = str(category)
    
    # 提取科室
    departments = disease.get("cure_department", [])
    if not isinstance(departments, list):
        departments = [str(departments)]
    
    # 提取药物
    drugs = disease.get("recommand_drug", [])
    if not isinstance(drugs, list):
        drugs = [str(drugs)]
    
    # 提取检查
    checks = disease.get("check", [])
    if not isinstance(checks, list):
        checks = [str(checks)]
    
    # 提取治疗方式
    cure_way = disease.get("cure_way", [])
    if isinstance(cure_way, list):
        treatment = ", ".join(cure_way)
    else:
        treatment = str(cure_way)
    
    # 提取并发症
    accompanies = disease.get("acompany", [])
    if not isinstance(accompanies, list):
        accompanies = [str(accompanies)]
    
    return {
        "name": disease.get("name", ""),
        "description": disease.get("desc", "")[:2000],
        "category": category_str,
        "prevention": disease.get("prevent", "")[:2000],
        "treatment": treatment,
        "cured_prob": disease.get("cured_prob", ""),
        "cost_money": disease.get("cost_money", ""),
        "symptoms": [s for s in symptoms if s],
        "departments": [d for d in departments if d],
        "drugs": [d for d in drugs if d],
        "checks": [c for c in checks if c],
        "accompanies": [a for a in accompanies if a]
    }


async def main():
    """主函数"""
    settings = get_settings()
    
    # 加载数据
    logger.info(f"Loading data from {settings.medical_data_file}")
    raw_data = load_medical_data(settings.medical_data_file)
    logger.info(f"Loaded {len(raw_data)} diseases")
    
    # 处理数据
    processed_data = [process_disease(d) for d in raw_data]
    
    # 连接 Neo4j
    logger.info("Connecting to Neo4j...")
    await neo4j_client.connect()
    
    # 创建约束
    logger.info("Creating constraints...")
    await neo4j_client.create_constraints()
    
    # 导入数据
    logger.info("Importing diseases...")
    for i, disease in enumerate(processed_data):
        try:
            # 创建疾病节点和关系
            await neo4j_client.create_disease_node(disease)
            
            # 创建并发症关系
            if disease.get("accompanies"):
                await neo4j_client.create_accompanies_relations(
                    disease["name"],
                    disease["accompanies"]
                )
            
            if (i + 1) % 10 == 0:
                logger.info(f"Imported {i + 1}/{len(processed_data)} diseases")
                
        except Exception as e:
            logger.error(f"Failed to import {disease.get('name', 'unknown')}: {e}")
    
    # 获取统计
    stats = await neo4j_client.get_stats()
    logger.info(f"Graph stats: {stats}")
    
    # 断开连接
    await neo4j_client.disconnect()
    logger.info("Done!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

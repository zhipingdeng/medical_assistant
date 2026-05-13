"""初始化 Milvus 并导入医疗数据"""

import json
import sys
import os
import hashlib
import struct
import logging
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import get_settings
from app.database.milvus import milvus_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simple_embedding(text: str, dim: int = 1024) -> List[float]:
    """生成简单 embedding"""
    hash_bytes = hashlib.sha512(text.encode('utf-8')).digest()
    extended = hash_bytes * (dim * 4 // len(hash_bytes) + 1)
    values = []
    for i in range(dim):
        byte_start = i * 4
        val = struct.unpack('f', extended[byte_start:byte_start + 4])[0]
        if val != val:  # NaN
            val = 0.0
        val = max(-1.0, min(1.0, val / 1e30)) if abs(val) > 1e30 else val
        values.append(val)
    norm = sum(v ** 2 for v in values) ** 0.5
    if norm > 0:
        values = [v / norm for v in values]
    return values


def safe_str(val, max_len: int = 2000) -> str:
    """安全转换为字符串并截断"""
    if isinstance(val, list):
        val = ", ".join(str(v) for v in val)
    val = str(val) if val else ""
    return val[:max_len]


def load_medical_data(file_path: str) -> List[Dict[str, Any]]:
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return data


def process_disease(disease: Dict[str, Any]) -> Dict[str, Any]:
    name = disease.get("name", "")
    desc = safe_str(disease.get("desc", ""), 2000)
    symptoms = safe_str(disease.get("symptom", []), 1000)
    category = safe_str(disease.get("category", []), 500)
    department = safe_str(disease.get("cure_department", []), 500)
    prevention = safe_str(disease.get("prevent", ""), 2000)
    treatment = safe_str(disease.get("cure_way", ""), 1000)
    drugs = safe_str(disease.get("recommand_drug", []), 1000)
    checks = safe_str(disease.get("check", []), 1000)

    embedding_text = f"{name} {desc} 症状：{symptoms}"

    return {
        "name": name,
        "description": desc,
        "category": category,
        "symptoms": symptoms,
        "department": department,
        "prevention": prevention,
        "treatment": treatment,
        "drugs": drugs,
        "checks": checks,
        "embedding": simple_embedding(embedding_text, 1024)
    }


async def main():
    settings = get_settings()

    logger.info(f"Loading data from {settings.medical_data_file}")
    raw_data = load_medical_data(settings.medical_data_file)
    logger.info(f"Loaded {len(raw_data)} diseases")

    processed_data = [process_disease(d) for d in raw_data]

    logger.info("Connecting to Milvus...")
    await milvus_client.connect()

    logger.info("Creating collection...")
    milvus_client.create_collection()

    logger.info("Inserting data...")
    batch_size = 200
    for i in range(0, len(processed_data), batch_size):
        batch = processed_data[i:i + batch_size]
        try:
            milvus_client.insert(batch)
            logger.info(f"Inserted batch {i // batch_size + 1}/{(len(processed_data) - 1) // batch_size + 1}")
        except Exception as e:
            logger.error(f"Batch {i // batch_size + 1} failed: {e}")
            # Try one by one
            for j, item in enumerate(batch):
                try:
                    milvus_client.insert([item])
                except Exception as e2:
                    logger.error(f"  Record {i + j} ({item['name']}): {e2}")

    stats = milvus_client.get_collection_stats()
    logger.info(f"Collection stats: {stats}")

    await milvus_client.disconnect()
    logger.info("Done!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

#!/usr/bin/env python3
"""Test Milvus connection and insert"""
import json
import sys
import os
import hashlib
import struct
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simple_embedding(text: str, dim: int = 1024):
    """Generate simple embedding"""
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

def safe_str(val, max_len=2000):
    if isinstance(val, list):
        val = ", ".join(str(v) for v in val)
    return str(val)[:max_len] if val else ""

print("Step 1: Import pymilvus")
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility

print("Step 2: Connect to Milvus")
connections.connect(alias="default", host="localhost", port=19530)
print("  Connected!")

print("Step 3: Drop old collection if exists")
if utility.has_collection("medical_diseases"):
    utility.drop_collection("medical_diseases")
    print("  Dropped old collection")

print("Step 4: Create collection")
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
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024)
]
schema = CollectionSchema(fields=fields)
collection = Collection(name="medical_diseases", schema=schema)
print("  Collection created!")

print("Step 5: Create index")
index_params = {"metric_type": "COSINE", "index_type": "IVF_FLAT", "params": {"nlist": 1024}}
collection.create_index(field_name="embedding", index_params=index_params)
print("  Index created!")

print("Step 6: Load medical data")
data_file = "/mnt/e/hermes_code_workspace/medical_assistant/medical.json"
data = []
with open(data_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                data.append(json.loads(line))
            except:
                pass
print(f"  Loaded {len(data)} diseases")

print("Step 7: Process and insert data")
batch_size = 100
total_inserted = 0
for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    names = []
    descs = []
    cats = []
    symps = []
    depts = []
    prevs = []
    treats = []
    drugss = []
    checkss = []
    embeddings = []
    
    for d in batch:
        name = d.get("name", "")
        desc = safe_str(d.get("desc", ""), 2000)
        symptoms = safe_str(d.get("symptom", []), 1000)
        category = safe_str(d.get("category", []), 500)
        department = safe_str(d.get("cure_department", []), 500)
        prevention = safe_str(d.get("prevent", ""), 2000)
        treatment = safe_str(d.get("cure_way", ""), 1000)
        drugs = safe_str(d.get("recommand_drug", []), 1000)
        checks = safe_str(d.get("check", []), 1000)
        
        emb_text = f"{name} {desc} 症状：{symptoms}"
        
        names.append(name)
        descs.append(desc)
        cats.append(category)
        symps.append(symptoms)
        depts.append(department)
        prevs.append(prevention)
        treats.append(treatment)
        drugss.append(drugs)
        checkss.append(checks)
        embeddings.append(simple_embedding(emb_text, 1024))
    
    try:
        collection.insert([names, descs, cats, symps, depts, prevs, treats, drugss, checkss, embeddings])
        total_inserted += len(batch)
        print(f"  Inserted {total_inserted}/{len(data)}")
    except Exception as e:
        print(f"  Batch failed: {e}")
        # Try one by one
        for j in range(len(batch)):
            try:
                collection.insert([[names[j]], [descs[j]], [cats[j]], [symps[j]], [depts[j]], [prevs[j]], [treats[j]], [drugss[j]], [checkss[j]], [embeddings[j]]])
                total_inserted += 1
            except Exception as e2:
                print(f"    Record {i+j} ({names[j]}): {e2}")

print(f"\nStep 8: Flush and verify")
collection.flush()
print(f"  Total entities: {collection.num_entities}")

print("\nDone!")

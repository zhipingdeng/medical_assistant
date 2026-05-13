"""API 测试"""

import pytest
import httpx
import asyncio

BASE_URL = "http://localhost:8787"


@pytest.fixture
def client():
    """创建测试客户端"""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


def test_health_check(client):
    """测试健康检查接口"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "services" in data


def test_chat_non_stream(client):
    """测试非流式对话"""
    response = client.post("/api/v1/chat", json={
        "message": "你好",
        "stream": False
    })
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "session_id" in data


def test_disease_search(client):
    """测试疾病搜索"""
    response = client.get("/api/v1/diseases", params={
        "q": "感冒",
        "top_k": 5
    })
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data


def test_disease_detail(client):
    """测试疾病详情"""
    # 先搜索一个疾病
    search_response = client.get("/api/v1/diseases", params={
        "q": "感冒",
        "top_k": 1
    })
    search_data = search_response.json()
    
    if search_data["results"]:
        disease_name = search_data["results"][0]["name"]
        response = client.get(f"/api/v1/diseases/{disease_name}")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "description" in data


def test_knowledge_graph(client):
    """测试知识图谱接口"""
    response = client.get("/api/v1/knowledge/graph", params={
        "center": "感冒",
        "depth": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data


def test_knowledge_stats(client):
    """测试知识图谱统计"""
    response = client.get("/api/v1/knowledge/stats")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

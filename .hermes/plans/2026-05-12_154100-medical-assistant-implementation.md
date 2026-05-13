# Medical Assistant 项目实现计划

## 项目概述

基于 `new_assistant` 和 `hermes_creative_rag` 的架构，构建一个医疗智能助手系统，使用 LangGraph 多智能体架构，集成 Milvus、Neo4j、Redis 数据库。

## 目录结构

```
medical_assistant/
├── backend/                      # 后端 FastAPI 应用
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 入口 (端口 8787)
│   │   ├── config.py            # 配置管理
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py      # 对话接口
│   │   │   │   ├── disease.py   # 疾病查询接口
│   │   │   │   ├── knowledge.py # 知识图谱接口
│   │   │   │   └── health.py    # 健康检查
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── supervisor.py    # 主管智能体
│   │   │   ├── diagnosis.py     # 诊断智能体
│   │   │   ├── knowledge.py     # 知识检索智能体
│   │   │   ├── symptom.py       # 症状分析智能体
│   │   │   └── state.py         # 状态定义
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── milvus.py        # Milvus 连接
│   │   │   ├── neo4j.py         # Neo4j 连接
│   │   │   └── redis.py         # Redis 连接
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── embeddings.py    # Embedding 模型
│   │   │   ├── vectorstore.py   # Milvus 向量存储
│   │   │   ├── knowledge_graph.py # Neo4j 知识图谱
│   │   │   └── hybrid_search.py # 混合检索
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   └── rate_limit.py    # Redis 限流
│   │   └── models/
│   │       ├── __init__.py
│   │       └── schemas.py       # Pydantic 模型
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_agents.py
│   │   └── test_rag.py
│   ├── scripts/
│   │   ├── init_milvus.py       # 初始化 Milvus 集合
│   │   ├── init_neo4j.py        # 初始化 Neo4j 知识图谱
│   │   └── import_data.py       # 导入 medical.json 数据
│   ├── requirements.txt
│   └── .env.example
├── frontend/                    # 前端 Vue 3 应用
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── api/
│   │   │   ├── index.ts         # Axios 实例
│   │   │   ├── chat.ts          # 对话 API
│   │   │   ├── disease.ts       # 疾病 API
│   │   │   └── knowledge.ts     # 知识图谱 API
│   │   ├── components/
│   │   │   ├── ChatBox.vue      # 对话框组件
│   │   │   ├── DiseaseCard.vue  # 疾病卡片
│   │   │   ├── KnowledgeGraph.vue # 知识图谱可视化
│   │   │   ├── Sidebar.vue      # 侧边栏
│   │   │   └── Header.vue       # 顶部导航
│   │   ├── views/
│   │   │   ├── Home.vue         # 首页
│   │   │   ├── Chat.vue         # 对话页面
│   │   │   ├── DiseaseList.vue  # 疾病列表
│   │   │   ├── DiseaseDetail.vue # 疾病详情
│   │   │   └── Knowledge.vue    # 知识图谱页面
│   │   ├── stores/
│   │   │   ├── chat.ts          # 对话状态
│   │   │   └── disease.ts       # 疾病状态
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript 类型
│   │   ├── router/
│   │   │   └── index.ts         # 路由配置
│   │   └── assets/
│   │       └── styles/
│   │           └── main.css     # 全局样式
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── data/
│   └── medical.json             # 医疗数据源
├── docker-compose.yml           # 数据库服务
├── Makefile                     # 常用命令
├── README.md
└── .gitignore
```

## 技术栈

### 后端
- **FastAPI** - Web 框架 (端口 8787)
- **LangGraph** - 多智能体编排
- **LangChain** - LLM 集成
- **Milvus** - 向量数据库 (业务数据)
- **Neo4j** - 图数据库 (医疗知识图谱)
- **Redis** - 缓存/会话/限流
- **Pydantic** - 数据验证

### 前端
- **Vue 3** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具 (端口 5173)
- **Pinia** - 状态管理
- **Vue Router** - 路由
- **Tailwind CSS** - 样式框架
- **D3.js** - 知识图谱可视化

## 数据库设计

### Milvus 集合
```python
# disease_collection
- id: INT64 (主键)
- name: VARCHAR (疾病名称)
- description: VARCHAR (疾病描述)
- category: VARCHAR (分类)
- symptoms: VARCHAR (症状 JSON)
- embedding: FLOAT_VECTOR (1536维)
```

### Neo4j 知识图谱
```cypher
// 节点类型
(:Disease {name, category, description})
(:Symptom {name})
(:Department {name})
(:Drug {name})
(:Check {name})

// 关系类型
(Disease)-[:HAS_SYMPTOM]->(Symptom)
(Disease)-[:BELONGS_TO]->(Department)
(Disease)-[:RECOMMENDS_DRUG]->(Drug)
(Disease)-[:REQUIRES_CHECK]->(Check)
(Disease)-[:ACCOMPANIES]->(Disease)
```

### Redis 键设计
```
session:{session_id}        # 会话历史 (Hash)
rate_limit:{ip}             # 限流计数 (String)
cache:disease:{id}          # 疾病缓存 (Hash)
```

## 实现步骤

### Phase 1: 环境搭建与数据库初始化

1. **创建 conda 环境**
   ```bash
   conda create -n medical_assistant python=3.11
   conda activate medical_assistant
   ```

2. **启动数据库服务**
   ```bash
   # 使用现有的 Milvus、Neo4j、Redis 容器
   docker ps | grep -E "milvus|neo4j|redis"
   ```

3. **安装后端依赖**
   ```bash
   pip install fastapi uvicorn langgraph langchain pymilvus neo4j redis pydantic-settings
   ```

### Phase 2: 后端核心开发

4. **配置管理** (`backend/app/config.py`)
   - 使用 pydantic-settings
   - 支持 .env 文件
   - 配置所有连接参数

5. **数据库连接层** (`backend/app/database/`)
   - Milvus 客户端封装
   - Neo4j 驱动封装
   - Redis 连接池

6. **RAG 检索层** (`backend/app/rag/`)
   - Embedding 模型加载
   - Milvus 向量检索
   - Neo4j 图检索
   - RRF 混合排序

7. **智能体层** (`backend/app/agents/`)
   - State 定义 (TypedDict)
   - Supervisor 路由
   - Diagnosis Agent (诊断建议)
   - Knowledge Agent (知识检索)
   - Symptom Agent (症状分析)
   - LangGraph 图构建

8. **API 路由层** (`backend/app/api/v1/`)
   - POST /api/v1/chat - 对话接口 (SSE 流式)
   - GET /api/v1/diseases - 疾病列表
   - GET /api/v1/diseases/{id} - 疾病详情
   - GET /api/v1/knowledge/graph - 知识图谱数据
   - GET /api/v1/health - 健康检查

### Phase 3: 数据导入

9. **Milvus 数据导入** (`backend/scripts/init_milvus.py`)
   - 解析 medical.json
   - 生成 embedding
   - 插入 Milvus

10. **Neo4j 知识图谱构建** (`backend/scripts/init_neo4j.py`)
    - 解析疾病-症状-药物关系
    - 创建节点和关系
    - 建立索引

### Phase 4: 前端开发

11. **Vue 3 项目初始化**
    ```bash
    npm create vite@latest frontend -- --template vue-ts
    cd frontend
    npm install vue-router pinia axios tailwindcss d3
    ```

12. **核心组件开发**
    - ChatBox - 对话界面 (流式显示)
    - DiseaseCard - 疾病信息卡片
    - KnowledgeGraph - D3 力导向图
    - Sidebar - 导航侧边栏

13. **页面开发**
    - Home - 首页 (疾病统计、快速入口)
    - Chat - 对话页面
    - DiseaseList - 疾病浏览
    - DiseaseDetail - 疾病详情 (症状、药物、检查)
    - Knowledge - 知识图谱可视化

### Phase 5: 测试与优化

14. **后端测试**
    - API 接口测试
    - 智能体功能测试
    - RAG 检索质量测试

15. **前端测试**
    - 组件渲染测试
    - API 调用测试

16. **集成测试**
    - 端到端对话流程
    - 知识图谱查询
    - 性能优化

## 评分标准 (目标 8.5+/10)

| 维度 | 权重 | 评分项 |
|------|------|--------|
| 前端设计 | 30% | 页面美观、交互流畅、响应式设计 |
| 接口测试 | 30% | API 成功率 > 95%、错误处理完善 |
| 核心功能 | 40% | 对话质量、知识检索准确性、图谱可视化 |

## 关键文件清单

### 需要创建的文件 (按优先级)

1. `backend/app/config.py` - 配置
2. `backend/app/database/*.py` - 数据库连接
3. `backend/app/rag/*.py` - RAG 检索
4. `backend/app/agents/*.py` - 智能体
5. `backend/app/api/v1/*.py` - API 路由
6. `backend/app/main.py` - FastAPI 入口
7. `backend/scripts/*.py` - 数据导入
8. `frontend/src/views/*.vue` - 页面
9. `frontend/src/components/*.vue` - 组件
10. `frontend/src/api/*.ts` - API 调用

## 风险与对策

| 风险 | 对策 |
|------|------|
| Milvus 连接失败 | 检查 Docker 容器状态，使用 172.22.80.1 网关 IP |
| Neo4j 认证失败 | 默认 neo4j/neo4j，首次登录需改密码 |
| Embedding 模型加载慢 | 使用本地 bge-m3 或缓存机制 |
| 前端跨域问题 | FastAPI CORS 中间件配置 |

## 验证步骤

1. **后端验证**
   ```bash
   cd backend
   python -m pytest tests/ -v
   curl http://localhost:8787/api/health
   ```

2. **前端验证**
   ```bash
   cd frontend
   npm run dev
   # 访问 http://localhost:5173
   ```

3. **集成验证**
   - 发送对话请求，验证流式响应
   - 搜索疾病，验证 Milvus 检索
   - 查看知识图谱，验证 Neo4j 查询

## 时间估算

- Phase 1: 30 分钟
- Phase 2: 2 小时
- Phase 3: 30 分钟
- Phase 4: 1.5 小时
- Phase 5: 1 小时

**总计: 约 5.5 小时**

---

*计划创建时间: 2026-05-12*
*参考项目: new_assistant, hermes_creative_rag*

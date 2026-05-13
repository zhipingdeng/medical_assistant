# 🏥 Medical Assistant - 医疗智能助手

基于 LangGraph 多智能体架构的医疗智能助手系统，集成 Milvus 向量检索、Neo4j 知识图谱和 Redis 缓存。

## ✨ 功能特性

- **智能问诊** - AI 驱动的症状分析和疾病诊断建议
- **疾病百科** - 全面的疾病数据库，支持搜索和浏览
- **知识图谱** - 可视化展示疾病、症状、药物之间的关联
- **流式对话** - 实时流式响应，提升用户体验
- **会话管理** - Redis 存储对话历史，支持多轮对话

## 🛠️ 技术栈

### 后端
- **FastAPI** - Web 框架
- **LangGraph** - 多智能体编排
- **LangChain** - LLM 集成
- **Milvus** - 向量数据库
- **Neo4j** - 图数据库
- **Redis** - 缓存/会话

### 前端
- **Vue 3** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **D3.js** - 知识图谱可视化

## 📦 项目结构

```
medical_assistant/
├── backend/                 # 后端应用
│   ├── app/
│   │   ├── api/v1/         # API 路由
│   │   ├── agents/         # LangGraph 智能体
│   │   ├── database/       # 数据库连接
│   │   ├── rag/            # RAG 检索
│   │   └── models/         # 数据模型
│   ├── scripts/            # 数据导入脚本
│   └── requirements.txt
├── frontend/                # 前端应用
│   ├── src/
│   │   ├── api/            # API 调用
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   └── stores/         # 状态管理
│   └── package.json
├── data/                    # 数据文件
│   └── medical.json
├── docker-compose.yml       # Docker 服务
└── .env                     # 环境配置
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建 conda 环境
conda create -n medical_assistant python=3.11
conda activate medical_assistant

# 安装后端依赖
cd backend
pip install -r requirements.txt
```

### 2. 启动数据库服务

```bash
# 启动 Milvus、Neo4j、Redis
docker-compose up -d

# 检查服务状态
docker-compose ps
```

### 3. 导入数据

```bash
cd backend

# 导入 Milvus 向量数据
python scripts/init_milvus.py

# 导入 Neo4j 知识图谱
python scripts/init_neo4j.py
```

### 4. 启动后端

```bash
cd backend
python -m app.main
# 或者
uvicorn app.main:app --host 0.0.0.0 --port 8787 --reload
```

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 6. 访问应用

- 前端: http://localhost:5173
- API 文档: http://localhost:8787/docs
- 健康检查: http://localhost:8787/api/health

## 📡 API 接口

### 对话接口
- `POST /api/v1/chat` - 发送消息（支持流式响应）
- `GET /api/v1/chat/history/{session_id}` - 获取聊天历史
- `DELETE /api/v1/chat/history/{session_id}` - 清空聊天历史

### 疾病接口
- `GET /api/v1/diseases?q={query}` - 搜索疾病
- `GET /api/v1/diseases/{name}` - 获取疾病详情
- `GET /api/v1/diseases/{name}/related` - 获取相关疾病
- `GET /api/v1/diseases/stats/overview` - 疾病统计

### 知识图谱接口
- `GET /api/v1/knowledge/graph?center={node}&depth={n}` - 获取知识图谱
- `GET /api/v1/knowledge/search?q={query}` - 搜索知识
- `GET /api/v1/knowledge/stats` - 图谱统计

### 健康检查
- `GET /api/health` - 服务健康状态

## ⚙️ 配置说明

### 环境变量 (.env)

```bash
# LLM 配置
LLM_MODEL_NAME=mimo-v2.5-pro
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.example.com/v1

# Embedding 配置
EMBEDDING_MODEL_NAME=bge-m3
EMBEDDING_BASE_URL=http://172.22.80.1:11434
EMBEDDING_DIMENSION=1024

# Milvus 配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# Neo4j 配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=medical123

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379

# 应用配置
APP_PORT=8787
```

## 📊 数据库端口

| 服务 | 端口 | 用途 |
|------|------|------|
| FastAPI | 8787 | 后端 API |
| Vue Dev | 5173 | 前端开发 |
| Milvus | 19530 | 向量数据库 |
| Neo4j | 7687 | 图数据库 (Bolt) |
| Neo4j | 7474 | 图数据库 (Web) |
| Redis | 6379 | 缓存 |

## 🧪 测试

```bash
# 后端测试
cd backend
pytest tests/ -v

# 前端构建
cd frontend
npm run build
```

## 📝 注意事项

1. **免责声明**: 本系统提供的医疗建议仅供参考，不能替代专业医生的诊断
2. **数据安全**: 请勿在生产环境中使用默认密码
3. **性能优化**: 生产环境建议配置 Nginx 反向代理

## 📄 License

MIT License

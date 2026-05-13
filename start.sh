#!/bin/bash
# Medical Assistant - 快速启动脚本

set -e

echo "🏥 Medical Assistant - 医疗智能助手"
echo "=================================="

# 检查 Docker
echo "📦 检查 Docker 服务..."
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 启动数据库服务
echo "🚀 启动数据库服务..."
docker-compose up -d

# 等待服务就绪
echo "⏳ 等待服务就绪..."
sleep 10

# 检查服务状态
echo "✅ 检查服务状态..."
docker-compose ps

# 激活 conda 环境
echo "🐍 激活 conda 环境..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate medical_assistant || {
    echo "创建 conda 环境..."
    conda create -n medical_assistant python=3.11 -y
    conda activate medical_assistant
    pip install -r backend/requirements.txt
}

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install
cd ..

# 启动后端
echo "🔧 启动后端服务..."
cd backend
python -m app.main &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "⏳ 等待后端启动..."
sleep 5

# 启动前端
echo "🎨 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Medical Assistant 已启动！"
echo ""
echo "📱 前端: http://localhost:5173"
echo "🔧 API: http://localhost:8787"
echo "📚 API 文档: http://localhost:8787/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker-compose down; exit 0" INT TERM

wait

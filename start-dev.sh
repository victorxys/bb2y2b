#!/bin/bash

# BB2Y2B 开发环境启动脚本

echo "🚀 启动 BB2Y2B 开发环境..."

# 检查是否在项目根目录
if [ ! -d "bb2y2b-backend" ] || [ ! -d "bb2y2b-vite-frontend" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端
echo "📡 启动后端服务..."
cd bb2y2b-backend
if [ ! -d "venv" ]; then
    echo "🔧 创建Python虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# 初始化数据库（如果需要）
if [ ! -f "bb2y2b.db" ]; then
    echo "🗄️ 初始化数据库..."
    python init_db.py
fi

# 后台启动后端
echo "🔄 启动FastAPI服务器..."
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

cd ..

# 启动前端
echo "🎨 启动前端服务..."
cd bb2y2b-vite-frontend

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

echo "🔄 启动Vite开发服务器..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 开发环境启动完成！"
echo "📡 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo "🎨 前端界面: http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
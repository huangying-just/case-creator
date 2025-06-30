#!/bin/bash

# Docker容器环境启动脚本
# 适配容器部署环境

echo "🚀 Docker容器环境启动中..."

# 确保在正确的工作目录
cd /app

# 检查环境变量配置文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 配置文件，使用默认配置"
    cp .env.example .env 2>/dev/null || echo "# 默认配置" > .env
fi

# 读取环境变量
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 设置默认端口
export BACKEND_PORT=${BACKEND_PORT:-8865}
export FRONTEND_PORT=${FRONTEND_PORT:-8866}

echo "📋 环境信息："
echo "   工作目录: $(pwd)"
echo "   后端端口: $BACKEND_PORT"
echo "   前端端口: $FRONTEND_PORT"

# 后端环境准备
echo "🐍 准备后端环境..."
cd /app/backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "   创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "   激活虚拟环境..."
source venv/bin/activate

echo "   安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 后台启动后端服务
echo "🚀 启动后端服务..."
python3 run.py &
BACKEND_PID=$!

# 等待后端启动
echo "   等待后端服务启动..."
sleep 5

# 前端环境准备
echo "🎨 准备前端环境..."
cd /app/frontend

# 安装前端依赖
echo "   安装前端依赖..."
npm install

# 启动前端服务
echo "🌐 启动前端服务..."
npm run dev &
FRONTEND_PID=$!

# 等待前端启动
echo "   等待前端服务启动..."
sleep 3

echo ""
echo "✅ 服务启动完成！"
echo "📍 访问地址："
echo "   🌐 前端界面: http://localhost:$FRONTEND_PORT"
echo "   ⚙️  后端API: http://localhost:$BACKEND_PORT"
echo "   📊 健康检查: http://localhost:$BACKEND_PORT/api/workflow/status"
echo ""
echo "📊 进程信息："
echo "   后端PID: $BACKEND_PID"
echo "   前端PID: $FRONTEND_PID"

# 清理函数
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "   已停止后端服务"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "   已停止前端服务"
    fi
    echo "👋 服务已停止"
    exit 0
}

# 注册信号处理
trap cleanup SIGINT SIGTERM

# 监控服务状态
echo "🔍 开始监控服务状态..."
while true; do
    # 检查后端服务
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ 后端服务已停止，重启中..."
        cd /app/backend
        source venv/bin/activate
        python3 run.py &
        BACKEND_PID=$!
    fi
    
    # 检查前端服务
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ 前端服务已停止，重启中..."
        cd /app/frontend
        npm run dev &
        FRONTEND_PID=$!
    fi
    
    # 等待60秒后再次检查
    sleep 60
done 
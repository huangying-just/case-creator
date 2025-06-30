#!/bin/bash

# 案例改编专家启动脚本
# 支持环境变量配置

echo "🚀 案例改编专家启动中..."

# 检查环境变量配置文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 配置文件"
    echo "📋 正在创建默认配置文件..."
    
    cat > .env << 'EOF'
# 案例改编专家 - 环境变量配置
# 请根据您的实际情况填写以下配置

# ===== OpenRouter API 配置 =====
# 必填：您的OpenRouter API密钥，在 https://openrouter.ai/ 获取
OPENROUTER_API_KEY=

# 可选：默认使用的模型，推荐 gpt-4o-mini（成本较低）
DEFAULT_MODEL=gpt-4o-mini

# ===== 应用配置 =====
# 开发模式（生产环境请设置为false）
FLASK_DEBUG=true

# 应用密钥（用于session加密，生产环境请使用随机字符串）
SECRET_KEY=your-secret-key-change-in-production

# 数据库路径
DATABASE_URL=sqlite:///case_creator.db

# ===== 服务端口配置 =====
# 后端服务端口
BACKEND_PORT=8865

# 前端服务端口
FRONTEND_PORT=8866

# ===== 用户配置（可选） =====
# 默认用户UUID（可选，如果设置则自动登录该用户）
DEFAULT_USER_UUID=

# 默认用户昵称
DEFAULT_USER_NICKNAME=案例改编用户

# ===== 系统配置 =====
# 每日最大请求次数限制
MAX_DAILY_REQUESTS=100

# 是否启用用户注册
ENABLE_REGISTRATION=true

# 维护模式
MAINTENANCE_MODE=false

# 日志级别
LOG_LEVEL=INFO
EOF
    
    echo "✅ 已创建 .env 配置文件"
    echo "⚠️  请编辑 .env 文件，填入您的 OpenRouter API 密钥"
    echo "🔗 获取API密钥: https://openrouter.ai/"
    echo ""
    read -p "按回车键继续启动，或按 Ctrl+C 退出先配置API密钥..."
fi

# 读取环境变量
source .env

# 检查关键配置
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "⚠️  警告：未设置 OPENROUTER_API_KEY"
    echo "📝 您可以："
    echo "   1. 在 .env 文件中设置 OPENROUTER_API_KEY"
    echo "   2. 在应用中通过用户设置页面配置API密钥"
    echo ""
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 python3 命令"
    echo "请安装 Python 3.8 或更高版本"
    exit 1
fi

# 检查Node.js环境
if ! command -v npm &> /dev/null; then
    echo "❌ 错误：未找到 npm 命令"
    echo "请安装 Node.js 和 npm"
    exit 1
fi

# 创建后端虚拟环境（如果不存在）
if [ ! -d "backend/venv" ]; then
    echo "🐍 创建Python虚拟环境..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# 激活虚拟环境并安装依赖
echo "📦 安装后端依赖..."
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 启动后端服务
echo "🚀 启动后端服务 (端口: ${BACKEND_PORT:-8865})..."
python3 run.py &
BACKEND_PID=$!

cd ..

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install

# 启动前端服务
echo "🎨 启动前端服务 (端口: ${FRONTEND_PORT:-8866})..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ 服务启动完成！"
echo "🌐 前端地址: http://localhost:${FRONTEND_PORT:-8866}"
echo "⚙️  后端API: http://localhost:${BACKEND_PORT:-8865}"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待中断信号
trap 'echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT

# 保持脚本运行
wait 
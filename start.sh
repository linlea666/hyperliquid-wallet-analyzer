#!/bin/bash

# HyperLiquid 钱包分析系统 - 启动脚本（macOS）

echo "🚀 启动 HyperLiquid 钱包分析系统..."

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python 3.10+"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js，请先安装 Node.js 18+"
    exit 1
fi

# 启动后端
echo "📦 启动后端服务..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
if [ ! -f "venv/.installed" ]; then
    echo "📦 安装后端依赖..."
    # 使用国内镜像加速
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    touch venv/.installed
fi

# 启动后端（后台运行）
echo "🚀 启动后端 API 服务器..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../.backend.pid

# 等待后端启动
sleep 3

# 启动前端
echo "📦 启动前端服务..."
cd ../frontend

# 清除 npm 代理配置（解决代理问题）
npm config delete proxy 2>/dev/null
npm config delete https-proxy 2>/dev/null
npm config set registry https://registry.npmmirror.com

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    # 临时禁用代理环境变量
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
    npm install
fi

# 启动前端（后台运行）
echo "🚀 启动前端开发服务器..."
# 临时禁用代理环境变量
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../.frontend.pid

# 等待前端启动
sleep 5

echo ""
echo "✅ 系统启动完成！"
echo ""
echo "📊 后端 API: http://localhost:8000"
echo "📚 API 文档: http://localhost:8000/docs"
echo "🌐 前端界面: http://localhost:5173"
echo ""
echo "📝 日志文件:"
echo "   - 后端日志: logs/backend.log"
echo "   - 前端日志: logs/frontend.log"
echo ""
echo "⏹️  停止服务: ./stop.sh"
echo ""

# 保存 PID 到文件
cd "$SCRIPT_DIR"
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid


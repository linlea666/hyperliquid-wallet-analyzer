#!/bin/bash

# 服务器更新脚本（从 GitHub 拉取最新代码）

echo "🔄 开始更新 HyperLiquid 钱包分析系统..."

# 获取项目目录
if [ -d "/www/wwwroot/gendan" ]; then
    PROJECT_DIR="/www/wwwroot/gendan"
else
    PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

cd "$PROJECT_DIR" || exit 1

echo "📁 项目目录: $PROJECT_DIR"

# 1. 拉取最新代码
echo ""
echo "📥 拉取最新代码..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Git pull 失败，请检查网络连接和仓库配置"
    exit 1
fi

# 2. 更新后端依赖
echo ""
echo "📦 更新后端依赖..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

# 检查 requirements.txt 是否有更新
if [ -f "requirements.txt" ]; then
    echo "安装/更新依赖..."
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt --upgrade
fi

# 3. 更新前端
echo ""
echo "📦 更新前端..."
cd ../frontend

# 检查 package.json 是否有更新
if [ -f "package.json" ]; then
    echo "安装/更新依赖..."
    npm config set registry https://registry.npmmirror.com
    npm install
    
    echo "构建前端..."
    npm run build
fi

# 4. 重启后端服务
echo ""
echo "🔄 重启后端服务..."

# 检查是否使用 PM2
if command -v pm2 &> /dev/null; then
    if pm2 list | grep -q "hyperliquid-backend"; then
        pm2 restart hyperliquid-backend
        echo "✅ PM2 服务已重启"
    else
        echo "⚠️  PM2 服务未找到，请手动重启"
    fi
else
    echo "⚠️  PM2 未安装，请通过宝塔面板 Python 项目管理器重启"
fi

echo ""
echo "✅ 更新完成！"
echo ""
echo "📊 检查服务状态:"
if command -v pm2 &> /dev/null; then
    pm2 status | grep hyperliquid-backend || echo "请通过宝塔面板检查服务状态"
fi


#!/bin/bash

# 打包部署文件脚本（在本地运行）

echo "📦 开始打包部署文件..."

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# 打包文件名
PACKAGE_NAME="gendan-deploy-$(date +%Y%m%d-%H%M%S).zip"

echo "📁 项目目录: $PROJECT_DIR"
echo "📦 打包文件: $PACKAGE_NAME"

# 打包（排除不需要的文件）
zip -r "$PACKAGE_NAME" . \
  -x "*.git*" \
  -x "*.DS_Store" \
  -x "node_modules/*" \
  -x "backend/venv/*" \
  -x "backend/__pycache__/*" \
  -x "backend/**/__pycache__/*" \
  -x "backend/logs/*" \
  -x "logs/*" \
  -x "*.pid" \
  -x ".backend.pid" \
  -x ".frontend.pid" \
  -x "frontend/dist/*" \
  -x "frontend/node_modules/*" \
  -x "*.log" \
  -x "*.zip" \
  -x "deploy.sh" \
  -x "start.sh" \
  -x "stop.sh" \
  -x "fix-proxy.sh" \
  -x "打包部署文件.sh"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 打包完成！"
    echo "📦 文件位置: $PROJECT_DIR/$PACKAGE_NAME"
    echo ""
    echo "📋 下一步："
    echo "1. 上传 $PACKAGE_NAME 到服务器"
    echo "2. 解压到 /www/wwwroot/gendan"
    echo "3. 运行 ./deploy.sh"
    echo ""
else
    echo "❌ 打包失败"
    exit 1
fi


#!/bin/bash

# 使用 GitHub 镜像推送代码

echo "🚀 使用 GitHub 镜像推送代码..."

cd /Users/huahua/Documents/gendan

# 备份原始远程地址
ORIGINAL_URL=$(git remote get-url origin 2>/dev/null)
echo "原始远程地址: $ORIGINAL_URL"

# 使用 ghproxy.com 镜像
MIRROR_URL="https://ghproxy.com/https://github.com/linlea666/hyperliquid-wallet-analyzer.git"

echo ""
echo "切换到镜像地址: $MIRROR_URL"
git remote set-url origin "$MIRROR_URL"

echo ""
echo "📤 开始推送..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
    echo ""
    echo "是否改回原始地址？(y/n)"
    read -p "> " answer
    if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
        git remote set-url origin "$ORIGINAL_URL"
        echo "✅ 已改回原始地址"
    fi
else
    echo ""
    echo "❌ 推送失败"
    echo "尝试改回原始地址..."
    git remote set-url origin "$ORIGINAL_URL"
fi



#!/bin/bash

# 一键提交并推送代码到 GitHub

echo "🚀 开始提交并推送代码..."

cd /Users/huahua/Documents/gendan

# 检查是否有修改
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ 没有需要提交的修改"
    exit 0
fi

# 显示修改的文件
echo ""
echo "📋 修改的文件："
git status --short

# 询问提交信息
echo ""
read -p "请输入提交说明: " commit_message

if [ -z "$commit_message" ]; then
    commit_message="更新代码"
fi

# 添加所有修改
echo ""
echo "📦 添加文件..."
git add .

# 提交
echo "💾 提交代码..."
git commit -m "$commit_message"

# 推送
echo "📤 推送到 GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 代码已成功推送到 GitHub！"
    echo "🌐 查看仓库: https://github.com/linlea666/hyperliquid-wallet-analyzer"
else
    echo ""
    echo "❌ 推送失败，请检查错误信息"
    exit 1
fi


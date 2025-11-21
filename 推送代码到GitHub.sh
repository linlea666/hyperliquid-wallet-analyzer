#!/bin/bash

# 推送代码到 GitHub 的脚本

echo "🚀 开始推送代码到 GitHub..."

cd /Users/huahua/Documents/gendan

# 1. 初始化 Git（如果还没有）
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
fi

# 2. 添加所有文件
echo "📦 添加文件..."
git add .

# 3. 提交
echo "💾 提交更改..."
git commit -m "Initial commit: HyperLiquid 钱包分析系统"

# 4. 设置主分支
git branch -M main

# 5. 添加远程仓库（如果还没有）
if git remote get-url origin > /dev/null 2>&1; then
    echo "✅ 远程仓库已存在"
    git remote set-url origin https://github.com/linlea666/hyperliquid-wallet-analyzer.git
else
    echo "📡 添加远程仓库..."
    git remote add origin https://github.com/linlea666/hyperliquid-wallet-analyzer.git
fi

# 6. 推送代码
echo "📤 推送代码到 GitHub..."
echo ""
echo "⚠️  如果提示输入用户名和密码："
echo "   用户名：linlea666"
echo "   密码：直接回车（Public 仓库不需要密码）"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 代码已成功推送到 GitHub！"
    echo "🌐 查看仓库: https://github.com/linlea666/hyperliquid-wallet-analyzer"
else
    echo ""
    echo "❌ 推送失败，请检查错误信息"
fi


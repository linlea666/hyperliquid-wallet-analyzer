#!/bin/bash

# 初始化 Git 仓库并推送到 GitHub

echo "🚀 初始化 Git 仓库..."

cd /Users/huahua/Documents/gendan

# 检查是否已经是 Git 仓库
if [ -d ".git" ]; then
    echo "⚠️  已经是 Git 仓库"
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    # 初始化 Git
    git init
    echo "✅ Git 仓库已初始化"
fi

# 添加所有文件
echo "📦 添加文件..."
git add .

# 提交
echo "💾 提交更改..."
git commit -m "Initial commit: HyperLiquid 钱包分析系统"

echo ""
echo "✅ 本地 Git 仓库已创建！"
echo ""
echo "📋 下一步："
echo "1. 在 GitHub 创建新仓库"
echo "2. 运行以下命令推送代码："
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "   或使用 SSH："
echo "   git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""


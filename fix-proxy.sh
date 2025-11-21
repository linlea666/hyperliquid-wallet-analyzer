#!/bin/bash

# 修复代理问题脚本

echo "🔧 修复代理和镜像配置..."

# 1. 禁用代理环境变量
unset http_proxy
unset https_proxy
unset HTTP_PROXY
unset HTTPS_PROXY

echo "✅ 已禁用代理环境变量"

# 2. 配置 npm 镜像
npm config set registry https://registry.npmmirror.com
npm config delete proxy 2>/dev/null
npm config delete https-proxy 2>/dev/null

echo "✅ 已配置 npm 镜像"

# 3. 配置 pip 镜像
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

echo "✅ 已配置 pip 镜像"

echo ""
echo "🎉 配置完成！现在可以运行: ./start.sh"


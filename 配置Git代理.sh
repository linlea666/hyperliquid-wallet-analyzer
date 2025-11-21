#!/bin/bash

# 配置 Git 使用代理的脚本

echo "🔧 配置 Git 代理..."

# 默认代理端口（根据您的代理软件修改）
HTTP_PROXY_PORT=${1:-7890}
SOCKS5_PROXY_PORT=${2:-7891}

echo ""
echo "请选择代理类型："
echo "1) HTTP 代理 (端口 $HTTP_PROXY_PORT)"
echo "2) SOCKS5 代理 (端口 $SOCKS5_PROXY_PORT)"
echo "3) 只对 GitHub 使用 HTTP 代理"
echo "4) 取消代理配置"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo "配置 HTTP 代理..."
        git config --global http.proxy http://127.0.0.1:$HTTP_PROXY_PORT
        git config --global https.proxy http://127.0.0.1:$HTTP_PROXY_PORT
        echo "✅ HTTP 代理已配置: http://127.0.0.1:$HTTP_PROXY_PORT"
        ;;
    2)
        echo "配置 SOCKS5 代理..."
        git config --global http.proxy socks5://127.0.0.1:$SOCKS5_PROXY_PORT
        git config --global https.proxy socks5://127.0.0.1:$SOCKS5_PROXY_PORT
        echo "✅ SOCKS5 代理已配置: socks5://127.0.0.1:$SOCKS5_PROXY_PORT"
        ;;
    3)
        echo "配置 GitHub 专用代理..."
        git config --global http.https://github.com.proxy http://127.0.0.1:$HTTP_PROXY_PORT
        git config --global https.https://github.com.proxy http://127.0.0.1:$HTTP_PROXY_PORT
        echo "✅ GitHub 专用代理已配置: http://127.0.0.1:$HTTP_PROXY_PORT"
        ;;
    4)
        echo "取消代理配置..."
        git config --global --unset http.proxy
        git config --global --unset https.proxy
        git config --global --unset http.https://github.com.proxy
        git config --global --unset https.https://github.com.proxy
        echo "✅ 代理配置已取消"
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "当前 Git 代理配置："
git config --get http.proxy || echo "  HTTP 代理: 未配置"
git config --get https.proxy || echo "  HTTPS 代理: 未配置"
git config --get http.https://github.com.proxy || echo "  GitHub HTTP 代理: 未配置"

echo ""
echo "📤 现在可以尝试推送代码："
echo "   cd /Users/huahua/Documents/gendan"
echo "   git push -u origin main"



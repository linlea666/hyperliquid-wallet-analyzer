#!/bin/bash

# HyperLiquid 钱包分析系统 - 停止脚本（macOS）

echo "⏹️  停止 HyperLiquid 钱包分析系统..."

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 停止后端
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "🛑 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        # 强制杀死（如果还在运行）
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill -9 $BACKEND_PID
        fi
    fi
    rm -f .backend.pid
fi

# 停止前端
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "🛑 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        # 强制杀死（如果还在运行）
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill -9 $FRONTEND_PID
        fi
    fi
    rm -f .frontend.pid
fi

# 清理可能的残留进程
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null

echo "✅ 系统已停止"


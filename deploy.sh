#!/bin/bash

# HyperLiquid 钱包分析系统 - 宝塔面板一键部署脚本

echo "🚀 开始部署 HyperLiquid 钱包分析系统..."

# 检测操作系统
if [ -f /etc/redhat-release ]; then
    OS="centos"
elif [ -f /etc/debian_version ]; then
    OS="debian"
else
    echo "❌ 不支持的操作系统"
    exit 1
fi

# 获取项目目录（默认当前目录，如果在服务器上则为 /www/wwwroot/gendan）
if [ -d "/www/wwwroot/gendan" ]; then
    PROJECT_DIR="/www/wwwroot/gendan"
else
    PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

echo "📁 项目目录: $PROJECT_DIR"

# 进入项目目录
cd "$PROJECT_DIR" || exit 1

# 1. 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python 版本: $PYTHON_VERSION"

# 2. 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Node.js 版本: $NODE_VERSION"

# 3. 配置后端
echo ""
echo "📦 配置后端..."
cd backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖（使用国内镜像）
echo "安装后端依赖..."
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

if [ $? -ne 0 ]; then
    echo "⚠️  使用清华镜像失败，尝试使用阿里云镜像..."
    pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
fi

# 4. 配置前端
echo ""
echo "📦 配置前端..."
cd ../frontend

# 设置 npm 镜像
npm config set registry https://registry.npmmirror.com

# 安装依赖
echo "安装前端依赖..."
npm install

if [ $? -ne 0 ]; then
    echo "⚠️  使用淘宝镜像失败，尝试使用官方源..."
    npm config set registry https://registry.npmjs.org
    npm install
fi

# 构建生产版本
echo "构建前端..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ 前端构建失败"
    exit 1
fi

# 5. 创建后端启动脚本
echo ""
echo "📦 创建启动脚本..."
cd ..

cat > start-backend.sh << 'EOF'
#!/bin/bash
cd /www/wwwroot/gendan/backend
source venv/bin/activate
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
EOF

chmod +x start-backend.sh

# 6. 检查 PM2
if ! command -v pm2 &> /dev/null; then
    echo "📦 安装 PM2..."
    npm install -g pm2
fi

# 7. 启动服务
echo ""
echo "🚀 启动服务..."

# 停止旧服务（如果存在）
pm2 delete hyperliquid-backend 2>/dev/null

# 启动新服务
pm2 start start-backend.sh --name hyperliquid-backend --interpreter bash

# 保存 PM2 配置
pm2 save

# 设置开机自启
pm2 startup | tail -1 | bash

# 8. 检查服务状态
sleep 2
pm2 status

echo ""
echo "✅ 部署完成！"
echo ""
echo "📊 服务状态:"
pm2 list | grep hyperliquid-backend
echo ""
echo "📝 查看日志: pm2 logs hyperliquid-backend"
echo "🔄 重启服务: pm2 restart hyperliquid-backend"
echo "⏹️  停止服务: pm2 stop hyperliquid-backend"
echo ""
echo "🌐 前端文件位置: $PROJECT_DIR/frontend/dist"
echo "📊 后端运行在: http://127.0.0.1:8000"
echo ""
echo "⚠️  请配置 Nginx 反向代理，参考：宝塔面板部署指南.md"


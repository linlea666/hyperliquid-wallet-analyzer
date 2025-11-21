# GitHub 部署方案

## 🎯 使用 GitHub 管理项目的优势

- ✅ 版本控制：所有修改都有记录
- ✅ 代码同步：本地和服务器代码保持一致
- ✅ 协作方便：多人协作更容易
- ✅ 更新简单：服务器直接 `git pull` 即可更新
- ✅ 备份安全：代码自动备份到 GitHub

---

## 📦 第一步：上传到 GitHub

### 1.1 初始化 Git 仓库（如果还没有）

```bash
cd /Users/huahua/Documents/gendan

# 初始化 Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: HyperLiquid 钱包分析系统"
```

### 1.2 创建 GitHub 仓库

1. 登录 GitHub
2. 点击右上角「+」→ 「New repository」
3. 填写信息：
   - Repository name: `hyperliquid-wallet-analyzer`（或自定义）
   - Description: `HyperLiquid 钱包分析系统`
   - 选择 Public 或 Private
   - **不要**勾选「Initialize this repository with a README」
4. 点击「Create repository」

### 1.3 推送代码到 GitHub

```bash
cd /Users/huahua/Documents/gendan

# 添加远程仓库（替换 YOUR_USERNAME 和 REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 推送代码
git branch -M main
git push -u origin main
```

---

## 🚀 第二步：服务器从 GitHub 部署

### 2.1 通过 SSH 克隆项目

```bash
# SSH 登录服务器
ssh root@your-server-ip

# 进入网站目录
cd /www/wwwroot

# 克隆项目
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git gendan

# 或使用 SSH（如果配置了 SSH key）
# git clone git@github.com:YOUR_USERNAME/REPO_NAME.git gendan
```

### 2.2 或通过宝塔面板克隆

1. **宝塔面板 → 「文件」→ `/www/wwwroot/`**
2. **点击「终端」**
3. **运行**：
```bash
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git gendan
```

---

## 🔧 第三步：服务器部署

### 3.1 使用宝塔面板 Python 项目管理器

按照 **`宝塔面板图形化部署.md`** 的步骤：

1. **添加 Python 项目**
2. **构建前端**
3. **配置网站和反向代理**

### 3.2 或使用一键部署脚本

```bash
cd /www/wwwroot/gendan
chmod +x deploy.sh
./deploy.sh
```

---

## 🔄 第四步：更新代码流程

### 本地开发 → GitHub → 服务器更新

#### 1. 本地修改代码

```bash
cd /Users/huahua/Documents/gendan

# 修改代码...

# 提交更改
git add .
git commit -m "更新说明"
git push origin main
```

#### 2. 服务器更新

**方式一：通过 SSH**

```bash
ssh root@your-server-ip
cd /www/wwwroot/gendan

# 拉取最新代码
git pull origin main

# 更新后端依赖（如果有新依赖）
cd backend
source venv/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 更新前端
cd ../frontend
npm install
npm run build

# 重启后端服务
pm2 restart hyperliquid-backend
# 或通过宝塔面板 Python 项目管理器点击「重启」
```

**方式二：通过宝塔面板**

1. **「文件」→ `/www/wwwroot/gendan` → 「终端」**
2. **运行**：
```bash
git pull origin main
```
3. **如果有后端代码更新**：
   - Python 项目管理器 → 点击「重启」
4. **如果有前端代码更新**：
   - 「文件」→ `/www/wwwroot/gendan/frontend` → 「终端」
   - 运行：`npm run build`

---

## 📝 创建更新脚本

创建 `/www/wwwroot/gendan/update.sh`：

```bash
#!/bin/bash

echo "🔄 开始更新..."

cd /www/wwwroot/gendan

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

# 更新后端依赖
echo "📦 更新后端依赖..."
cd backend
source venv/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 更新前端
echo "📦 更新前端..."
cd ../frontend
npm install
npm run build

# 重启后端服务
echo "🔄 重启后端服务..."
pm2 restart hyperliquid-backend

echo "✅ 更新完成！"
```

使用：
```bash
chmod +x update.sh
./update.sh
```

---

## 🔐 配置 SSH Key（可选，推荐）

### 本地生成 SSH Key

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### 添加到 GitHub

1. 复制公钥：`cat ~/.ssh/id_ed25519.pub`
2. GitHub → Settings → SSH and GPG keys → New SSH key
3. 粘贴公钥并保存

### 服务器配置 SSH Key（可选）

如果服务器也需要通过 SSH 克隆：

```bash
# 在服务器生成 SSH key
ssh-keygen -t ed25519 -C "server@yourdomain.com"

# 复制公钥并添加到 GitHub
cat ~/.ssh/id_ed25519.pub
```

---

## 📋 GitHub 仓库文件结构

确保以下文件已提交：

```
gendan/
├── .gitignore          ✅ 已创建
├── README.md           ✅ 已创建
├── backend/            ✅ 代码目录
├── frontend/           ✅ 代码目录
├── deploy.sh           ✅ 部署脚本
├── nginx.conf.example  ✅ Nginx 配置示例
└── docs/               ✅ 文档目录
```

**不提交的文件**（已在 .gitignore 中）：
- `node_modules/`
- `backend/venv/`
- `backend/data/wallets/*.json`（数据文件）
- `backend/logs/`（日志文件）
- `*.zip`（压缩包）

---

## 🎯 推荐工作流程

### 日常开发

1. **本地修改代码**
2. **测试功能**
3. **提交到 GitHub**：
   ```bash
   git add .
   git commit -m "功能描述"
   git push origin main
   ```

### 服务器更新

1. **SSH 登录服务器**（或使用宝塔终端）
2. **运行更新脚本**：
   ```bash
   cd /www/wwwroot/gendan
   ./update.sh
   ```
3. **或手动更新**：
   ```bash
   git pull origin main
   # 然后重启服务
   ```

---

## ✅ 优势总结

- ✅ **版本控制**：所有修改都有历史记录
- ✅ **代码同步**：本地和服务器代码一致
- ✅ **更新简单**：`git pull` 即可更新
- ✅ **备份安全**：代码自动备份到 GitHub
- ✅ **协作方便**：多人协作更容易
- ✅ **回滚方便**：可以回退到任意版本

---

## 📚 相关文档

- **`宝塔面板图形化部署.md`** - 首次部署步骤
- **`update.sh`** - 更新脚本（需要创建）

---

**使用 GitHub 管理项目，让开发和部署更简单！** 🚀


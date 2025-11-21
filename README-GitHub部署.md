# 🚀 GitHub 部署完整指南

## 📦 第一步：上传到 GitHub

### 1.1 初始化 Git 仓库

```bash
cd /Users/huahua/Documents/gendan

# 运行初始化脚本
./初始化Git仓库.sh

# 或手动初始化
git init
git add .
git commit -m "Initial commit: HyperLiquid 钱包分析系统"
```

### 1.2 创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角「+」→ 「New repository」
3. 填写信息：
   - **Repository name**: `hyperliquid-wallet-analyzer`
   - **Description**: `HyperLiquid 钱包分析系统`
   - **Public** 或 **Private**（根据需求选择）
   - ⚠️ **不要**勾选「Initialize this repository with a README」
4. 点击「Create repository」

### 1.3 推送代码

```bash
# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git

# 推送代码
git branch -M main
git push -u origin main
```

---

## 🖥️ 第二步：服务器从 GitHub 部署

### 方式一：通过 SSH（推荐）

```bash
# SSH 登录服务器
ssh root@your-server-ip

# 克隆项目
cd /www/wwwroot
git clone https://github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git gendan

# 进入项目目录
cd gendan
```

### 方式二：通过宝塔面板

1. **「文件」→ `/www/wwwroot/` → 「终端」**
2. **运行**：
```bash
git clone https://github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git gendan
cd gendan
```

---

## 🔧 第三步：首次部署

### 3.1 创建配置文件

```bash
cd /www/wwwroot/gendan/backend/data/config

# 复制示例配置文件
cp system.json.example system.json
cp scoring.json.example scoring.json 2>/dev/null || echo "{}" > scoring.json
cp recommendation.json.example recommendation.json 2>/dev/null || echo "{}" > recommendation.json
cp filters.json.example filters.json 2>/dev/null || echo "{}" > filters.json
cp notifications.json.example notifications.json 2>/dev/null || echo "{}" > notifications.json
```

### 3.2 使用宝塔面板部署

按照 **`宝塔面板图形化部署.md`** 的步骤：

1. **添加 Python 项目**（后端）
2. **构建前端**
3. **创建网站并配置反向代理**

---

## 🔄 第四步：日常更新流程

### 本地开发 → GitHub → 服务器

#### 1. 本地修改代码

```bash
cd /Users/huahua/Documents/gendan

# 修改代码...

# 提交更改
git add .
git commit -m "更新说明：修复了XX问题"
git push origin main
```

#### 2. 服务器更新（一键更新）

**通过 SSH**：
```bash
ssh root@your-server-ip
cd /www/wwwroot/gendan
./update.sh
```

**通过宝塔面板**：
1. 「文件」→ `/www/wwwroot/gendan` → 「终端」
2. 运行：`./update.sh`

---

## 📝 更新脚本说明

`update.sh` 会自动：
- ✅ 拉取最新代码（`git pull`）
- ✅ 更新后端依赖（如果有新依赖）
- ✅ 更新前端依赖并重新构建
- ✅ 重启后端服务（PM2）

---

## 🔐 配置 SSH Key（可选，推荐）

### 本地配置

```bash
# 生成 SSH Key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 查看公钥
cat ~/.ssh/id_ed25519.pub
```

### 添加到 GitHub

1. 复制公钥内容
2. GitHub → Settings → SSH and GPG keys → New SSH key
3. 粘贴并保存

### 使用 SSH 克隆（更快）

```bash
# 使用 SSH URL
git remote set-url origin git@github.com:YOUR_USERNAME/hyperliquid-wallet-analyzer.git
```

---

## 📋 工作流程总结

### 开发流程

```
本地修改代码
    ↓
git add .
    ↓
git commit -m "更新说明"
    ↓
git push origin main
    ↓
服务器运行 ./update.sh
    ↓
完成更新
```

### 优势

- ✅ **版本控制**：所有修改都有记录
- ✅ **代码同步**：本地和服务器代码一致
- ✅ **更新简单**：一条命令即可更新
- ✅ **备份安全**：代码自动备份到 GitHub
- ✅ **协作方便**：多人协作更容易

---

## 🎯 快速命令参考

### 本地操作

```bash
# 初始化仓库
./初始化Git仓库.sh

# 提交更改
git add .
git commit -m "更新说明"
git push origin main

# 查看状态
git status
git log --oneline
```

### 服务器操作

```bash
# 首次克隆
git clone https://github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git gendan

# 更新代码
cd /www/wwwroot/gendan
./update.sh

# 或手动更新
git pull origin main
pm2 restart hyperliquid-backend
```

---

## ✅ 完成！

现在您的项目已经在 GitHub 上了，可以：
- ✅ 随时查看代码历史
- ✅ 轻松更新服务器代码
- ✅ 多人协作开发
- ✅ 代码自动备份

**详细文档**：
- **`GitHub部署方案.md`** - 完整部署方案
- **`GitHub快速开始.md`** - 快速开始指南


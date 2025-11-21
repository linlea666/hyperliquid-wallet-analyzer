# GitHub 快速开始指南

## 🚀 3步上传到 GitHub

### 步骤 1: 初始化 Git 仓库

在终端运行：

```bash
cd /Users/huahua/Documents/gendan
./初始化Git仓库.sh
```

或手动运行：

```bash
cd /Users/huahua/Documents/gendan
git init
git add .
git commit -m "Initial commit: HyperLiquid 钱包分析系统"
```

### 步骤 2: 在 GitHub 创建仓库

1. 登录 GitHub
2. 点击右上角「+」→ 「New repository」
3. 填写：
   - Repository name: `hyperliquid-wallet-analyzer`
   - Description: `HyperLiquid 钱包分析系统`
   - 选择 Public 或 Private
   - **不要**勾选 README
4. 点击「Create repository」

### 步骤 3: 推送代码

```bash
# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git

# 推送代码
git branch -M main
git push -u origin main
```

---

## 🖥️ 服务器从 GitHub 部署

### 方式一：通过 SSH

```bash
ssh root@your-server-ip
cd /www/wwwroot
git clone https://github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git gendan
cd gendan
chmod +x deploy.sh
./deploy.sh
```

### 方式二：通过宝塔面板

1. **「文件」→ `/www/wwwroot/` → 「终端」**
2. **运行**：
```bash
git clone https://github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git gendan
cd gendan
chmod +x deploy.sh
./deploy.sh
```

然后按照 **`宝塔面板图形化部署.md`** 配置 Python 项目和网站。

---

## 🔄 更新代码（本地 → GitHub → 服务器）

### 本地修改并推送

```bash
cd /Users/huahua/Documents/gendan

# 修改代码...

# 提交并推送
git add .
git commit -m "更新说明"
git push origin main
```

### 服务器更新

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

## ✅ 完成！

现在您的代码已经在 GitHub 上了，可以：
- ✅ 随时查看代码历史
- ✅ 轻松更新服务器代码
- ✅ 多人协作开发
- ✅ 代码自动备份


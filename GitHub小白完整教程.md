# GitHub 小白完整教程（一步一步）

## 📋 第一步：在 GitHub 创建仓库

### 1.1 登录 GitHub

1. 打开浏览器，访问：https://github.com
2. 如果没有账号，点击「Sign up」注册
3. 如果有账号，点击「Sign in」登录

### 1.2 创建新仓库

1. **登录后，点击右上角的「+」号**
2. **选择「New repository」（新建仓库）**
   - ⚠️ 选择「新建仓库」，不是「导入仓库」

### 1.3 填写仓库信息

**Repository name（仓库名称）**：
- 填写：`hyperliquid-wallet-analyzer`
- 或自定义名称，如：`wallet-analyzer`

**Description（描述）**（可选）：
- 填写：`HyperLiquid 钱包分析系统`

**Public 还是 Private？**

- ✅ **Public（公开）**：
  - 任何人都能看到代码
  - 服务器拉取：直接 `git clone` 即可，最简单
  - 推荐：如果代码不敏感，选择这个

- 🔒 **Private（私有）**：
  - 只有您能看到代码
  - 服务器拉取：需要配置认证（稍复杂）
  - 推荐：如果代码敏感，选择这个

**其他选项**：
- ⚠️ **不要**勾选「Add a README file」
- ⚠️ **不要**勾选「Add .gitignore」
- ⚠️ **不要**勾选「Choose a license」

### 1.4 创建仓库

点击绿色的「Create repository」按钮

---

## 📤 第二步：上传代码到 GitHub

### 2.1 初始化本地 Git 仓库

打开终端（Terminal），运行：

```bash
cd /Users/huahua/Documents/gendan
```

然后运行初始化脚本：

```bash
./初始化Git仓库.sh
```

**如果提示权限错误**，运行：

```bash
chmod +x 初始化Git仓库.sh
./初始化Git仓库.sh
```

### 2.2 连接 GitHub 仓库

**复制 GitHub 仓库地址**：

创建仓库后，GitHub 会显示仓库地址，类似：
```
https://github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git
```

**在终端运行**（替换 YOUR_USERNAME 为您的 GitHub 用户名）：

```bash
cd /Users/huahua/Documents/gendan

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git

# 推送代码
git branch -M main
git push -u origin main
```

**如果选择的是 Private 仓库**，会提示输入用户名和密码：
- 用户名：您的 GitHub 用户名
- 密码：**不是登录密码**，需要使用 Personal Access Token（见下方说明）

---

## 🔐 Private 仓库认证配置（如果选择私有）

### 方式一：使用 Personal Access Token（推荐）

#### 1. 生成 Token

1. GitHub → 右上角头像 → **Settings**
2. 左侧菜单 → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. **Generate new token** → **Generate new token (classic)**
5. 填写信息：
   - **Note**: `服务器部署`
   - **Expiration**: 选择过期时间（建议 90 天或 No expiration）
   - **Select scopes**: 勾选 `repo`（全部仓库权限）
6. 点击「Generate token」
7. **⚠️ 重要：复制生成的 Token**（只显示一次）

#### 2. 使用 Token

推送代码时：
```bash
git push -u origin main
# 用户名：输入您的 GitHub 用户名
# 密码：输入刚才复制的 Token（不是登录密码）
```

#### 3. 服务器拉取 Private 仓库

**方法 A：使用 Token（推荐）**

```bash
# 在服务器上克隆时使用 Token
git clone https://YOUR_TOKEN@github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git gendan
```

**方法 B：配置 SSH Key（更安全）**

1. 在服务器生成 SSH Key：
```bash
ssh-keygen -t ed25519 -C "server@yourdomain.com"
cat ~/.ssh/id_ed25519.pub
```

2. 复制公钥，添加到 GitHub：
   - GitHub → Settings → SSH and GPG keys → New SSH key

3. 使用 SSH URL 克隆：
```bash
git clone git@github.com:YOUR_USERNAME/hyperliquid-wallet-analyzer.git gendan
```

---

## 🎯 推荐方案对比

### 方案一：Public 仓库（最简单）⭐ 推荐小白

**优点**：
- ✅ 最简单，无需配置认证
- ✅ 服务器直接 `git clone` 即可
- ✅ 更新代码也简单

**缺点**：
- ⚠️ 代码公开，任何人都能看到

**适用场景**：
- 代码不敏感
- 学习项目
- 开源项目

### 方案二：Private 仓库（更安全）

**优点**：
- ✅ 代码私有，更安全
- ✅ 适合商业项目

**缺点**：
- ⚠️ 需要配置认证（Token 或 SSH Key）
- ⚠️ 服务器拉取稍复杂

**适用场景**：
- 代码敏感
- 商业项目
- 需要保密

---

## 📝 完整操作步骤（Public 仓库）

### 步骤 1: 创建 GitHub 仓库

1. 登录 GitHub
2. 点击「+」→ 「New repository」
3. 填写：
   - Repository name: `hyperliquid-wallet-analyzer`
   - 选择：**Public** ✅
   - 其他都不勾选
4. 点击「Create repository」

### 步骤 2: 初始化本地仓库

```bash
cd /Users/huahua/Documents/gendan
chmod +x 初始化Git仓库.sh
./初始化Git仓库.sh
```

### 步骤 3: 连接并推送

```bash
# 替换 YOUR_USERNAME 为您的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git
git branch -M main
git push -u origin main
```

**如果提示输入用户名密码**：
- 用户名：您的 GitHub 用户名
- 密码：如果选择 Public，直接回车（不需要密码）

### 步骤 4: 验证

刷新 GitHub 页面，应该能看到所有文件了！

---

## 📝 完整操作步骤（Private 仓库）

### 步骤 1: 创建 GitHub 仓库

1. 登录 GitHub
2. 点击「+」→ 「New repository」
3. 填写：
   - Repository name: `hyperliquid-wallet-analyzer`
   - 选择：**Private** 🔒
   - 其他都不勾选
4. 点击「Create repository」

### 步骤 2: 生成 Personal Access Token

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. 勾选 `repo` 权限
4. 生成并**复制 Token**（只显示一次！）

### 步骤 3: 初始化本地仓库

```bash
cd /Users/huahua/Documents/gendan
chmod +x 初始化Git仓库.sh
./初始化Git仓库.sh
```

### 步骤 4: 连接并推送

```bash
# 替换 YOUR_USERNAME 为您的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git
git branch -M main
git push -u origin main
```

**输入认证信息**：
- Username: 您的 GitHub 用户名
- Password: 粘贴刚才复制的 Token

### 步骤 5: 验证

刷新 GitHub 页面，应该能看到所有文件了！

---

## 🖥️ 服务器部署（Public 仓库）

### 通过宝塔面板

1. **「文件」→ `/www/wwwroot/` → 「终端」**
2. **运行**：
```bash
git clone https://github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git gendan
cd gendan
```

就这么简单！✅

---

## 🖥️ 服务器部署（Private 仓库）

### 方法一：使用 Token（简单）

1. **「文件」→ `/www/wwwroot/` → 「终端」**
2. **运行**（替换 YOUR_TOKEN 和 YOUR_USERNAME）：
```bash
git clone https://YOUR_TOKEN@github.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git gendan
cd gendan
```

### 方法二：配置 SSH Key（推荐）

1. **在服务器生成 SSH Key**：
```bash
ssh-keygen -t ed25519 -C "server@yourdomain.com"
# 一路回车
cat ~/.ssh/id_ed25519.pub
```

2. **复制公钥，添加到 GitHub**：
   - GitHub → Settings → SSH and GPG keys → New SSH key
   - 粘贴公钥并保存

3. **使用 SSH 克隆**：
```bash
git clone git@github.com:YOUR_USERNAME/hyperliquid-wallet-analyzer.git gendan
```

---

## 🔄 日常更新流程

### 本地修改代码后：

```bash
cd /Users/huahua/Documents/gendan

# 查看修改
git status

# 添加修改
git add .

# 提交
git commit -m "更新说明"

# 推送到 GitHub
git push origin main
```

### 服务器更新：

```bash
cd /www/wwwroot/gendan
./update.sh
```

---

## ❓ 常见问题

### Q1: Public 还是 Private？

**推荐小白选择 Public**：
- 更简单，无需配置认证
- 代码不敏感的话，公开也没关系
- 服务器拉取最简单

### Q2: 选择 Private 会不会很麻烦？

**不会很麻烦**：
- 只需要配置一次 Token 或 SSH Key
- 配置好后，使用和 Public 一样简单

### Q3: Token 安全吗？

**安全**：
- Token 可以设置过期时间
- 可以随时撤销
- 比密码更安全

### Q4: 忘记 Token 了怎么办？

**重新生成**：
- GitHub → Settings → Developer settings → Personal access tokens
- 生成新的 Token
- 旧的 Token 可以删除

---

## ✅ 推荐方案（小白）

1. **选择 Public 仓库**（最简单）
2. **按照 Public 仓库步骤操作**
3. **服务器直接 `git clone` 即可**

---

## 📚 下一步

上传到 GitHub 后，按照 **`宝塔面板图形化部署.md`** 在服务器上部署。

---

**有问题随时问我！** 😊


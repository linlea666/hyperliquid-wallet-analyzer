# GitHub 认证解决方案

## ❌ 问题

GitHub 已经不支持密码认证，需要使用 **Personal Access Token**。

---

## ✅ 解决方案

### 方案一：使用 Personal Access Token（推荐）

#### 1. 生成 Token

1. **访问 GitHub**：https://github.com
2. **右上角头像** → **Settings**
3. **左侧菜单** → **Developer settings**
4. **Personal access tokens** → **Tokens (classic)**
5. **Generate new token** → **Generate new token (classic)**
6. **填写信息**：
   - **Note**: `本地开发`
   - **Expiration**: 选择过期时间（建议 90 天或 No expiration）
   - **Select scopes**: 勾选 `repo`（全部仓库权限）
7. **点击「Generate token」**
8. **⚠️ 重要：复制生成的 Token**（只显示一次，要保存好！）

#### 2. 使用 Token 推送

在终端运行：

```bash
cd /Users/huahua/Documents/gendan
git push -u origin main
```

**当提示输入密码时**：
- Username: `linlea666`
- Password: **粘贴刚才复制的 Token**（不是登录密码！）

#### 3. 保存 Token（可选）

配置 Git 记住 Token：

```bash
# 配置 credential helper
git config --global credential.helper store

# 推送（输入一次 Token 后会自动保存）
git push -u origin main
```

---

### 方案二：使用 SSH（更安全，推荐长期使用）

#### 1. 生成 SSH Key

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
# 一路回车，使用默认路径
```

#### 2. 复制公钥

```bash
cat ~/.ssh/id_ed25519.pub
```

#### 3. 添加到 GitHub

1. **GitHub** → **Settings** → **SSH and GPG keys**
2. **New SSH key**
3. **Title**: `MacBook Air`
4. **Key**: 粘贴刚才复制的公钥
5. **Add SSH key**

#### 4. 修改远程仓库地址为 SSH

```bash
cd /Users/huahua/Documents/gendan
git remote set-url origin git@github.com:linlea666/hyperliquid-wallet-analyzer.git
```

#### 5. 推送代码

```bash
git push -u origin main
```

（SSH 方式不需要输入密码）

---

### 方案三：使用 GitHub CLI（最简单）

#### 1. 安装 GitHub CLI

```bash
brew install gh
```

#### 2. 登录

```bash
gh auth login
```

按照提示操作，选择：
- GitHub.com
- HTTPS
- 登录方式（浏览器或 Token）

#### 3. 推送代码

```bash
cd /Users/huahua/Documents/gendan
git push -u origin main
```

---

## 🎯 推荐方案

**快速解决（推荐）**：使用 Personal Access Token
- ✅ 最简单
- ✅ 5 分钟搞定
- ✅ 一次配置，后续自动保存

**长期使用（推荐）**：使用 SSH
- ✅ 更安全
- ✅ 不需要每次输入
- ✅ 配置一次永久使用

---

## 📋 快速操作步骤（Token 方式）

1. **生成 Token**：
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic)
   - 勾选 `repo`
   - 生成并复制 Token

2. **推送代码**：
```bash
cd /Users/huahua/Documents/gendan
git push -u origin main
# Username: linlea666
# Password: 粘贴 Token（不是登录密码！）
```

3. **保存凭证**（可选）：
```bash
git config --global credential.helper store
```

---

## ✅ 验证

推送成功后，访问：

https://github.com/linlea666/hyperliquid-wallet-analyzer

应该能看到所有文件了！

---

**现在去生成 Token，然后推送代码！** 🚀


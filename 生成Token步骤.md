# 🔑 生成 GitHub Personal Access Token

## 📋 详细步骤

### 1. 打开 GitHub 设置

访问：https://github.com/settings/tokens

或手动：
- GitHub → 右上角头像 → **Settings**
- 左侧菜单 → **Developer settings**
- **Personal access tokens** → **Tokens (classic)**

### 2. 生成新 Token

1. 点击 **「Generate new token」** → **「Generate new token (classic)」**

2. **填写信息**：
   - **Note（备注）**: `本地开发` 或 `MacBook Air`
   - **Expiration（过期时间）**: 
     - 选择 **90 days**（90 天）
     - 或 **No expiration**（永不过期，不推荐）
   - **Select scopes（权限）**: 
     - ✅ 勾选 **`repo`**（全部仓库权限）
     - 这会自动勾选所有 repo 相关权限

3. 滚动到底部，点击 **「Generate token」**

### 3. 复制 Token

**⚠️ 重要**：
- Token 只显示一次！
- 立即复制并保存好
- 格式类似：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 4. 使用 Token

在终端推送代码时：
```bash
cd /Users/huahua/Documents/gendan
git push -u origin main
```

**输入**：
- Username: `linlea666`
- Password: **粘贴刚才复制的 Token**（不是登录密码！）

### 5. 保存凭证（可选）

配置 Git 记住 Token，以后就不需要再输入了：

```bash
git config --global credential.helper store
```

---

## ✅ 完成

推送成功后，Token 会自动保存，以后就不需要再输入了！

---

**现在去生成 Token 吧！** 🚀


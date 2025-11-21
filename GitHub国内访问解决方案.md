# GitHub 国内访问解决方案

## 🔍 问题诊断

如果 `git push` 一直卡住或失败，可能是网络问题。

---

## ✅ 解决方案

### 方案一：配置 Git 代理（推荐）

如果您有代理（如 Clash、V2Ray 等），可以配置 Git 使用代理：

#### 1. 查看代理端口

通常代理端口是：
- HTTP 代理：`127.0.0.1:7890` 或 `127.0.0.1:1080`
- SOCKS5 代理：`127.0.0.1:7891` 或 `127.0.0.1:1080`

#### 2. 配置 Git 代理

**HTTP/HTTPS 代理**：
```bash
# HTTP 代理（端口通常是 7890）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 或者 SOCKS5 代理
git config --global http.proxy socks5://127.0.0.1:7891
git config --global https.proxy socks5://127.0.0.1:7891
```

**只对 GitHub 使用代理**（推荐）：
```bash
# 只对 GitHub 使用代理，其他网站不走代理
git config --global http.https://github.com.proxy http://127.0.0.1:7890
git config --global https.https://github.com.proxy http://127.0.0.1:7890
```

#### 3. 测试推送

```bash
cd /Users/huahua/Documents/gendan
git push -u origin main
```

#### 4. 取消代理（如果不需要）

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

---

### 方案二：使用 GitHub 镜像（临时）

如果代理不可用，可以使用 GitHub 镜像：

#### 1. 修改远程仓库地址为镜像

```bash
cd /Users/huahua/Documents/gendan

# 使用 GitHub 镜像（ghproxy.com）
git remote set-url origin https://ghproxy.com/https://github.com/linlea666/hyperliquid-wallet-analyzer.git

# 或者使用其他镜像
# git remote set-url origin https://mirror.ghproxy.com/https://github.com/linlea666/hyperliquid-wallet-analyzer.git
```

#### 2. 推送代码

```bash
git push -u origin main
```

#### 3. 推送成功后，改回原地址（可选）

```bash
git remote set-url origin https://github.com/linlea666/hyperliquid-wallet-analyzer.git
```

---

### 方案三：使用 SSH（如果已配置）

如果您的代理支持 SSH，可以使用 SSH 方式：

#### 1. 修改远程仓库地址为 SSH

```bash
cd /Users/huahua/Documents/gendan
git remote set-url origin git@github.com:linlea666/hyperliquid-wallet-analyzer.git
```

#### 2. 配置 SSH 代理

编辑 `~/.ssh/config` 文件：

```bash
nano ~/.ssh/config
```

添加：

```
Host github.com
    HostName github.com
    User git
    ProxyCommand nc -X 5 -x 127.0.0.1:7891 %h %p
```

（替换 `7891` 为您的 SOCKS5 代理端口）

#### 3. 推送代码

```bash
git push -u origin main
```

---

### 方案四：使用 Gitee 镜像（备选）

如果 GitHub 完全无法访问，可以先推送到 Gitee（码云），然后再同步到 GitHub：

#### 1. 在 Gitee 创建仓库

访问：https://gitee.com

创建同名仓库：`hyperliquid-wallet-analyzer`

#### 2. 添加 Gitee 远程仓库

```bash
cd /Users/huahua/Documents/gendan
git remote add gitee https://gitee.com/YOUR_USERNAME/hyperliquid-wallet-analyzer.git
git push -u gitee main
```

#### 3. 后续同步到 GitHub

等网络恢复后，再推送到 GitHub。

---

## 🔧 快速诊断脚本

创建一个诊断脚本：

```bash
#!/bin/bash

echo "🔍 诊断 GitHub 连接..."

# 测试 GitHub 连接
echo "1. 测试 GitHub 连接..."
curl -I https://github.com 2>&1 | head -3

# 检查 Git 配置
echo ""
echo "2. Git 代理配置："
git config --get http.proxy || echo "  未配置 HTTP 代理"
git config --get https.proxy || echo "  未配置 HTTPS 代理"

# 检查远程仓库
echo ""
echo "3. 远程仓库配置："
git remote -v

# 测试推送（不实际推送）
echo ""
echo "4. 测试推送连接..."
git ls-remote origin 2>&1 | head -3
```

---

## 📋 推荐操作步骤

### 如果您有代理：

1. **配置 Git 代理**：
```bash
git config --global http.https://github.com.proxy http://127.0.0.1:7890
git config --global https.https://github.com.proxy http://127.0.0.1:7890
```

2. **推送代码**：
```bash
cd /Users/huahua/Documents/gendan
git push -u origin main
```

### 如果您没有代理：

1. **使用镜像**：
```bash
cd /Users/huahua/Documents/gendan
git remote set-url origin https://ghproxy.com/https://github.com/linlea666/hyperliquid-wallet-analyzer.git
git push -u origin main
```

---

## ✅ 验证

推送成功后，访问：

https://github.com/linlea666/hyperliquid-wallet-analyzer

应该能看到所有文件了！

---

## 💡 常见问题

### Q: 如何查看代理端口？

**A**: 
- Clash: 通常 HTTP 是 7890，SOCKS5 是 7891
- V2Ray: 通常 HTTP 是 1080，SOCKS5 是 1080
- 查看代理软件设置中的端口号

### Q: 代理配置后还是不行？

**A**: 
1. 确认代理软件正在运行
2. 确认端口号正确
3. 尝试使用镜像方案

### Q: 推送时提示认证失败？

**A**: 
- Public 仓库：直接回车（不需要密码）
- Private 仓库：需要 Personal Access Token

---

**先尝试配置代理，如果不行再使用镜像方案！** 🚀



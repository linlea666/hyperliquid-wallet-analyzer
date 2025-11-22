# Git 工作流程与部署指南

## 📌 GitHub 仓库信息

**仓库地址**: https://github.com/linlea666/hyperliquid-wallet-analyzer

**当前状态**: 
- ✅ 已创建并推送 V1.0 版本
- ✅ 包含基础功能和文档
- 🚀 准备开始 V2.0 升级

---

## 一、Git 工作流程

### 1.1 分支策略

```
main (主分支)
  ↓
develop (开发分支) ← 当前工作分支
  ↓
feature/v2-database      (数据库功能)
feature/v2-scoring       (评分模型)
feature/v2-admin         (后台管理)
feature/v2-frontend      (前端UI)
feature/v2-ai            (AI扩展)
```

**分支说明**:
- `main`: 稳定版本，只接受经过测试的代码
- `develop`: 开发分支，所有功能在这里集成
- `feature/*`: 功能分支，每个大功能独立开发

---

### 1.2 开发流程

#### 步骤1: 创建开发分支

```bash
# 从 main 创建 develop 分支
git checkout main
git pull origin main
git checkout -b develop
git push -u origin develop
```

#### 步骤2: 创建功能分支（按需）

```bash
# 从 develop 创建功能分支
git checkout develop
git checkout -b feature/v2-database

# 开发完成后合并回 develop
git checkout develop
git merge feature/v2-database
git push origin develop
```

#### 步骤3: 提交代码

```bash
# 添加修改
git add .

# 提交（使用有意义的提交信息）
git commit -m "feat: 实现数据库设计和创建"

# 推送到远程
git push origin develop
```

#### 步骤4: 发布版本

```bash
# 开发完成后，合并到 main
git checkout main
git merge develop

# 打标签
git tag -a v2.0.0 -m "V2.0 正式版本"

# 推送
git push origin main --tags
```

---

### 1.3 提交信息规范

**格式**: `<type>(<scope>): <subject>`

**类型 (type)**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试
- `chore`: 构建/工具变动

**示例**:
```bash
git commit -m "feat(database): 实现 SQLite 数据库设计"
git commit -m "feat(scoring): 添加 6 大维度评分模型"
git commit -m "fix(api): 修复 API 调用超时问题"
git commit -m "docs: 更新 API 集成文档"
```

---

## 二、服务器部署流程

### 2.1 首次部署

#### 在服务器上克隆仓库

```bash
# SSH 登录服务器
ssh root@your-server-ip

# 进入网站目录
cd /www/wwwroot/

# 克隆仓库
git clone https://github.com/linlea666/hyperliquid-wallet-analyzer.git gendan

# 进入项目目录
cd gendan

# 切换到 main 分支（生产环境）
git checkout main
```

---

#### 配置 Git 凭证（使用 PAT）

```bash
# 配置 Git 使用 credential helper
git config --global credential.helper store

# 第一次 pull 时会提示输入用户名和密码
# 用户名: linlea666
# 密码: 你的 Personal Access Token (ghp_xxxx...)

# 之后会自动保存，不需要每次输入
```

---

### 2.2 日常更新流程

#### 方式1: 手动拉取更新

```bash
# SSH 登录服务器
ssh root@your-server-ip

# 进入项目目录
cd /www/wwwroot/gendan

# 拉取最新代码
git pull origin main

# 重启后端服务（如果使用 PM2）
pm2 restart hyperliquid-backend

# 重新构建前端（如果前端有更新）
cd frontend
npm install  # 如果有新依赖
npm run build

# 重启 Nginx（如果配置有变化）
nginx -s reload
```

---

#### 方式2: 一键更新脚本

创建 `/www/wwwroot/gendan/update.sh`:

```bash
#!/bin/bash

echo "🔄 开始更新 HyperLiquid 钱包分析系统..."

# 进入项目目录
cd /www/wwwroot/gendan

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

# 检查后端依赖
echo "🔍 检查后端依赖..."
cd backend
source /www/server/pyporject_evn/hyperliquid/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 检查前端依赖
echo "🔍 检查前端依赖..."
cd ../frontend
npm install --registry=https://registry.npmmirror.com

# 构建前端
echo "🏗️  构建前端..."
npm run build

# 重启后端服务
echo "🔄 重启后端服务..."
pm2 restart hyperliquid-backend

# 重启 Nginx
echo "🔄 重启 Nginx..."
nginx -s reload

echo "✅ 更新完成！"
echo "📊 后端 API: http://your-domain/api"
echo "🌐 前端界面: http://your-domain"
```

**使用方法**:
```bash
# 添加执行权限
chmod +x /www/wwwroot/gendan/update.sh

# 执行更新
/www/wwwroot/gendan/update.sh
```

---

### 2.3 自动化部署（可选）

#### 使用 GitHub Actions（推荐）

创建 `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Server

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to Server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SERVER_SSH_KEY }}
        script: |
          cd /www/wwwroot/gendan
          git pull origin main
          ./update.sh
```

**配置 GitHub Secrets**:
1. 进入仓库 Settings → Secrets and variables → Actions
2. 添加以下 secrets:
   - `SERVER_HOST`: 服务器 IP
   - `SERVER_USER`: SSH 用户名（root）
   - `SERVER_SSH_KEY`: SSH 私钥

**效果**: 每次推送到 main 分支，自动部署到服务器！

---

#### 使用 Webhook（备选）

在服务器上创建 webhook 服务:

```python
# /www/wwwroot/gendan/webhook.py
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # 执行更新脚本
        subprocess.run(['/www/wwwroot/gendan/update.sh'])
        return 'OK', 200
    return 'Method Not Allowed', 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
```

**在 GitHub 配置 Webhook**:
1. 仓库 Settings → Webhooks → Add webhook
2. Payload URL: `http://your-server-ip:9000/webhook`
3. Content type: `application/json`
4. Events: `Just the push event`

---

## 三、开发与部署最佳实践

### 3.1 开发环境

**本地开发**:
```bash
# 在本地开发和测试
cd /Users/huahua/Documents/gendan

# 开发完成后提交
git add .
git commit -m "feat: 添加新功能"
git push origin develop
```

**测试通过后合并到 main**:
```bash
git checkout main
git merge develop
git push origin main
```

---

### 3.2 版本管理

**版本号规则**: `v主版本.次版本.修订版本`

- **主版本**: 重大更新（如 V1.0 → V2.0）
- **次版本**: 新功能添加（如 V2.0 → V2.1）
- **修订版本**: Bug 修复（如 V2.1.0 → V2.1.1）

**打标签**:
```bash
# 发布 V2.0.0
git tag -a v2.0.0 -m "V2.0 正式版本 - 核心升级"
git push origin v2.0.0

# 发布 V2.1.0（添加 AI 功能）
git tag -a v2.1.0 -m "V2.1 - AI 扩展功能"
git push origin v2.1.0
```

---

### 3.3 回滚策略

**如果更新出现问题**:

```bash
# 查看提交历史
git log --oneline

# 回滚到上一个版本
git reset --hard HEAD~1
git push origin main --force

# 或回滚到指定版本
git reset --hard v2.0.0
git push origin main --force
```

**注意**: 使用 `--force` 需谨慎，确保团队成员知晓。

---

### 3.4 数据备份

**在更新前备份数据**:

```bash
# 备份数据目录
cd /www/wwwroot/gendan
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/data/

# 保留最近 7 天的备份
find . -name "backup_*.tar.gz" -mtime +7 -delete
```

**自动备份脚本** (`backup.sh`):

```bash
#!/bin/bash

BACKUP_DIR="/www/backup/gendan"
PROJECT_DIR="/www/wwwroot/gendan"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据
cd $PROJECT_DIR
tar -czf $BACKUP_DIR/data_$DATE.tar.gz backend/data/

# 删除 7 天前的备份
find $BACKUP_DIR -name "data_*.tar.gz" -mtime +7 -delete

echo "✅ 备份完成: $BACKUP_DIR/data_$DATE.tar.gz"
```

**添加到 crontab（每天凌晨 2 点自动备份）**:
```bash
crontab -e

# 添加以下行
0 2 * * * /www/wwwroot/gendan/backup.sh
```

---

## 四、我的建议

### 4.1 推荐的工作流程

#### 阶段1: 本地开发（当前）

1. **在本地开发和测试**
   - 路径: `/Users/huahua/Documents/gendan`
   - 分支: `develop`

2. **功能完成后提交到 GitHub**
   ```bash
   git add .
   git commit -m "feat: 完成数据库设计"
   git push origin develop
   ```

3. **测试通过后合并到 main**
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```

---

#### 阶段2: 服务器部署

1. **首次部署**
   ```bash
   # 在服务器上
   cd /www/wwwroot/
   git clone https://github.com/linlea666/hyperliquid-wallet-analyzer.git gendan
   cd gendan
   ./deploy.sh  # 使用部署脚本
   ```

2. **日常更新**
   ```bash
   # 在服务器上
   cd /www/wwwroot/gendan
   ./update.sh  # 一键更新
   ```

---

### 4.2 建议的提交频率

**开发阶段**:
- 每完成一个小功能就提交（如"实现钱包表设计"）
- 每天至少提交一次（保存进度）

**测试阶段**:
- 修复一个 bug 就提交
- 优化一个功能就提交

**发布阶段**:
- 合并到 main 并打标签
- 部署到服务器

---

### 4.3 代码审查（可选）

如果是团队开发，建议使用 Pull Request:

1. 在 GitHub 上创建 PR（develop → main）
2. 审查代码
3. 测试通过后合并

**单人开发可以跳过这一步，直接合并。**

---

## 五、故障排查

### 5.1 Git 常见问题

#### 问题1: 推送失败（认证错误）

```bash
# 解决方案：使用 Personal Access Token
git config --global credential.helper store
# 下次 push 时输入 PAT 作为密码
```

---

#### 问题2: 代码冲突

```bash
# 拉取最新代码
git pull origin main

# 如果有冲突，手动解决后
git add .
git commit -m "fix: 解决合并冲突"
git push origin main
```

---

#### 问题3: 误提交敏感信息

```bash
# 从历史中删除文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/data/config/api_keys.json" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin --force --all
```

---

### 5.2 部署常见问题

#### 问题1: 拉取代码失败

```bash
# 检查网络
ping github.com

# 检查 Git 配置
git config --list

# 重新配置凭证
git config --global credential.helper store
```

---

#### 问题2: 依赖安装失败

```bash
# Python 依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Node.js 依赖
npm install --registry=https://registry.npmmirror.com
```

---

#### 问题3: 服务启动失败

```bash
# 查看后端日志
pm2 logs hyperliquid-backend

# 查看 Nginx 日志
tail -f /www/wwwlogs/kpl.17kx.net.error.log

# 检查端口占用
netstat -tlnp | grep 8000
```

---

## 六、总结

### 推荐的完整流程

1. **本地开发**
   - 在 `develop` 分支开发
   - 频繁提交，保存进度

2. **测试验证**
   - 本地测试通过
   - 合并到 `main` 分支

3. **推送到 GitHub**
   - `git push origin main`
   - 打标签（如 v2.0.0）

4. **服务器部署**
   - SSH 登录服务器
   - 执行 `./update.sh`
   - 验证功能

5. **监控和维护**
   - 查看日志
   - 监控性能
   - 定期备份

---

### 关键命令速查

```bash
# 本地开发
git add .
git commit -m "feat: 添加新功能"
git push origin develop

# 合并到 main
git checkout main
git merge develop
git push origin main

# 打标签
git tag -a v2.0.0 -m "V2.0 正式版本"
git push origin v2.0.0

# 服务器更新
ssh root@your-server
cd /www/wwwroot/gendan
./update.sh
```

---

**准备好了！让我们开始 V2.0 的开发之旅！** 🚀


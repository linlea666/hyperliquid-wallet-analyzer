# AI 系统部署指南

## 📋 概述

本指南将帮助你在服务器（宝塔面板）上部署 AI 智能分析系统。

---

## 🔧 前置准备

### 1. 确认环境

- ✅ Python 3.11+ 已安装
- ✅ Node.js 16+ 已安装
- ✅ 数据库已初始化
- ✅ 后端和前端已部署
- ✅ DeepSeek API Key: `sk-95468bc93340462e81772278f0ae6058`

### 2. 依赖包

确保 `requirements.txt` 包含所有依赖：

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
httpx==0.25.2
pandas==2.1.3
numpy==1.26.2
apscheduler==3.10.4
loguru==0.7.2
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
websockets==12.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
aiosmtplib==1.2.0
email-validator==2.1.0.post1
psutil==5.9.8
```

---

## 📦 部署步骤

### 步骤 1: 更新代码到 GitHub

在本地执行：

```bash
cd /Users/huahua/Documents/gendan

# 添加所有新文件
git add .

# 提交更改
git commit -m "feat: 添加 AI 智能分析系统

- 集成 DeepSeek API
- 实现交易风格分析、策略识别、风险评估
- 添加 AI 调度系统和缓存机制
- 新增系统监控页面和 AI 分析页面
- 完善前端路由和 API 集成"

# 推送到 GitHub
git push origin main
```

### 步骤 2: 服务器拉取更新

在宝塔面板的终端或 SSH 中执行：

```bash
# 进入项目目录
cd /www/wwwroot/gendan

# 拉取最新代码
git pull origin main
```

### 步骤 3: 更新后端依赖

```bash
# 进入后端目录
cd /www/wwwroot/gendan/backend

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt
```

### 步骤 4: 初始化 AI 配置

```bash
# 在后端目录下执行
python init_ai_config.py
```

**预期输出**:
```
============================================================
初始化 AI 配置
============================================================
创建 AI 配置...
✓ AI 配置已创建

当前 AI 配置:
{
  "enabled": true,
  "provider": "deepseek",
  "api_key": "sk-95468bc93340462e81772278f0ae6058",
  "api_url": "https://api.deepseek.com/v1",
  "model": "deepseek-chat",
  "max_tokens": 2000,
  "temperature": 0.7,
  "daily_limit": 1000,
  "cost_limit": 10.0,
  "score_threshold": 75
}

完成！
```

### 步骤 5: 测试 AI 系统

```bash
# 测试 AI 功能
python test_ai.py
```

**如果测试成功，继续下一步。如果失败，检查**:
- API Key 是否正确
- 网络连接是否正常
- 依赖包是否完整

### 步骤 6: 重启后端服务

在宝塔面板中：

1. 找到 Python 项目管理
2. 找到 `gendan` 项目
3. 点击"重启"按钮

或在终端执行：

```bash
# 如果使用 PM2
pm2 restart gendan-backend

# 如果使用 supervisor
supervisorctl restart gendan-backend
```

### 步骤 7: 更新前端

```bash
# 进入前端目录
cd /www/wwwroot/gendan/frontend

# 安装新依赖（如果有）
npm install

# 重新构建
npm run build
```

### 步骤 8: 验证部署

1. **检查后端日志**:
   ```bash
   # 查看最新日志
   tail -f /www/wwwroot/gendan/backend/logs/app.log
   ```
   
   应该看到：
   ```
   🚀 HyperLiquid 钱包分析系统启动中...
   📁 数据目录: /www/wwwroot/gendan/backend/data
   📊 初始化数据库...
   ✅ 数据库初始化完成
   ⏰ 启动数据采集调度器...
   🤖 启动 AI 调度器...
   ✅ 系统启动完成
   ```

2. **测试 API 端点**:
   ```bash
   # 测试 AI 配置
   curl http://localhost:8000/api/ai/config \
     -H "Authorization: Bearer YOUR_TOKEN"
   
   # 测试 AI 统计
   curl http://localhost:8000/api/ai/statistics \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **访问前端页面**:
   - 系统监控: http://kpl.17kx.net/system/monitor
   - AI 分析: http://kpl.17kx.net/ai/analysis

---

## 🧪 功能测试

### 1. 测试系统监控页面

1. 登录系统
2. 访问"系统监控"页面
3. 检查是否显示：
   - CPU、内存、磁盘使用率
   - 资源使用趋势图
   - 进程信息
   - 数据库指标

### 2. 测试 AI 分析功能

1. 访问"AI 分析"页面
2. 检查 AI 服务状态（应该显示"已启用"）
3. 选择一个钱包
4. 选择分析类型（交易风格、策略、风险）
5. 点击"开始分析"
6. 等待 10-15 秒
7. 查看分析结果

### 3. 测试 AI API

使用 Postman 或 curl 测试：

```bash
# 1. 登录获取 token
curl -X POST http://kpl.17kx.net/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin888"}'

# 保存返回的 access_token

# 2. 测试 AI 连接
curl -X POST http://kpl.17kx.net/api/ai/test \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. 分析钱包
curl -X POST http://kpl.17kx.net/api/ai/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "wallet_address": "0x...",
    "analysis_types": ["style"],
    "priority": "high"
  }'

# 4. 查看结果
curl -X GET http://kpl.17kx.net/api/ai/analysis/0x... \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ⚙️ 配置调整

### 1. 修改 AI 配置

可以通过 API 或直接修改数据库：

**方法 1: 使用 API**

```bash
curl -X PUT http://kpl.17kx.net/api/ai/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "enabled": true,
    "daily_limit": 2000,
    "cost_limit": 20.0
  }'
```

**方法 2: 修改数据库**

```sql
UPDATE system_configs
SET config_value = json_set(
  config_value,
  '$.daily_limit', 2000,
  '$.cost_limit', 20.0
)
WHERE config_key = 'ai';
```

### 2. 调整缓存时间

编辑 `backend/app/services/ai/ai_scheduler.py`:

```python
self.cache_ttl = {
    'style': 86400 * 7,      # 7天
    'strategy': 86400 * 7,   # 7天
    'risk': 86400 * 3,       # 3天（可调整为 5天或更长）
    'market': 3600           # 1小时
}
```

修改后需要重启后端服务。

### 3. 调整调度优先级

编辑 `backend/app/services/ai/ai_scheduler.py`，修改优先级判断逻辑。

---

## 🔍 故障排查

### 问题 1: AI 服务显示"已禁用"

**原因**: 配置未正确初始化或被禁用

**解决**:
```bash
cd /www/wwwroot/gendan/backend
python init_ai_config.py
# 重启后端服务
```

### 问题 2: API 调用失败

**原因**: API Key 无效或网络问题

**检查**:
1. 验证 API Key 是否正确
2. 检查服务器是否能访问 `api.deepseek.com`
3. 查看后端日志中的错误信息

**测试网络**:
```bash
curl https://api.deepseek.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-95468bc93340462e81772278f0ae6058" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### 问题 3: 分析任务一直在队列中

**原因**: AI 调度器未启动或出错

**检查**:
```bash
# 查看调度器状态
curl http://localhost:8000/api/ai/queue \
  -H "Authorization: Bearer YOUR_TOKEN"

# 查看后端日志
tail -f /www/wwwroot/gendan/backend/logs/app.log | grep "AI"
```

**解决**: 重启后端服务

### 问题 4: 前端页面无法访问

**原因**: 路由配置或构建问题

**解决**:
```bash
cd /www/wwwroot/gendan/frontend
npm run build
# 检查 Nginx 配置
```

### 问题 5: 成本过高

**原因**: 分析频率过高或缓存失效

**解决**:
1. 增加缓存时间
2. 降低每日限制
3. 提高评分阈值（只分析高分钱包）
4. 检查是否有重复分析

**查看使用情况**:
```bash
curl http://kpl.17kx.net/api/ai/statistics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 监控和维护

### 1. 每日检查

- 查看 AI 使用统计
- 检查成本是否在预算内
- 查看分析任务完成情况

### 2. 每周维护

- 清理过期缓存
- 检查分析结果质量
- 优化提示词（如需要）

### 3. 日志管理

```bash
# 查看 AI 相关日志
cd /www/wwwroot/gendan/backend
grep "AI\|DeepSeek" logs/app.log

# 查看错误日志
grep "ERROR" logs/app.log | grep "AI"
```

### 4. 数据库维护

```sql
-- 查看 AI 使用统计
SELECT 
    DATE(created_at) as date,
    COUNT(*) as calls,
    SUM(total_tokens) as tokens,
    SUM(cost) as cost
FROM ai_usage_stats
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 7;

-- 查看缓存情况
SELECT 
    analysis_type,
    COUNT(*) as count,
    AVG(julianday('now') - julianday(created_at)) as avg_age_days
FROM ai_analysis_cache
WHERE expires_at > datetime('now')
GROUP BY analysis_type;

-- 清理过期缓存
DELETE FROM ai_analysis_cache
WHERE expires_at < datetime('now');
```

---

## 🔒 安全建议

### 1. API Key 保护

- ✅ 不要在前端暴露 API Key
- ✅ 定期轮换 API Key
- ⚠️ 考虑使用环境变量存储

### 2. 访问控制

- ✅ AI 功能需要登录
- ✅ 配置修改需要管理员权限
- ⚠️ 考虑添加 IP 白名单

### 3. 成本控制

- ✅ 设置每日调用限制
- ✅ 设置单次成本上限
- ⚠️ 设置预算告警

### 4. 数据安全

- ✅ 定期备份数据库
- ✅ 加密敏感配置
- ⚠️ 定期审计日志

---

## 📝 更新流程

### 日常更新

```bash
# 1. 本地开发和测试
cd /Users/huahua/Documents/gendan
# ... 修改代码 ...
# ... 测试 ...

# 2. 提交到 GitHub
git add .
git commit -m "描述更新内容"
git push origin main

# 3. 服务器拉取更新
ssh root@your-server
cd /www/wwwroot/gendan
git pull origin main

# 4. 更新依赖（如有）
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 5. 重启服务
# 在宝塔面板中重启 Python 项目

# 6. 验证
curl http://localhost:8000/health
```

### 重大更新

如果有数据库结构变更或重大功能更新：

1. 备份数据库
2. 测试更新脚本
3. 执行更新
4. 验证功能
5. 回滚准备（如需要）

---

## ✅ 部署检查清单

部署完成后，请确认以下项目：

- [ ] 代码已更新到 GitHub
- [ ] 服务器已拉取最新代码
- [ ] 后端依赖已更新
- [ ] AI 配置已初始化
- [ ] AI 测试通过
- [ ] 后端服务已重启
- [ ] 前端已重新构建
- [ ] 系统监控页面可访问
- [ ] AI 分析页面可访问
- [ ] AI 功能测试通过
- [ ] 日志无错误信息
- [ ] 成本监控已设置

---

## 🎉 完成

恭喜！AI 智能分析系统已成功部署到服务器。

**访问地址**:
- 系统监控: http://kpl.17kx.net/system/monitor
- AI 分析: http://kpl.17kx.net/ai/analysis

**默认配置**:
- 每日限制: 1000 次
- 成本上限: ¥10/天
- 缓存时间: 3-7 天

**支持**:
如有问题，请查看：
- 后端日志: `/www/wwwroot/gendan/backend/logs/app.log`
- 错误日志: 在日志管理页面查看
- API 文档: http://kpl.17kx.net/docs

---

**文档版本**: 1.0  
**最后更新**: 2025-11-22  
**作者**: AI Assistant


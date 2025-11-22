# WebSocket 实时通信实现文档

## 📋 概述

WebSocket 实时通信系统已完成，支持实时进度推送、通知推送、数据更新等功能。

## ✅ 已完成功能

### 1. 核心组件

#### 1.1 ConnectionManager (连接管理器)
- **文件**: `backend/app/services/websocket_manager.py`
- **功能**:
  - 管理所有活跃的 WebSocket 连接
  - 支持用户身份识别和连接映射
  - 主题订阅/取消订阅机制
  - 消息广播和点对点发送
  - 连接统计和监控

#### 1.2 WebSocketHandler (消息处理器)
- **功能**:
  - 处理客户端消息
  - 支持订阅/取消订阅
  - 心跳检测 (ping/pong)
  - 统计信息查询

#### 1.3 WebSocket API
- **文件**: `backend/app/api/websocket.py`
- **端点**:
  - `WS /api/ws` - WebSocket 连接端点
  - `GET /api/ws/stats` - 获取连接统计
  - `POST /api/ws/broadcast` - 管理员广播消息
  - `POST /api/ws/notify` - 发送通知

### 2. 消息类型

#### 2.1 客户端 → 服务端

```json
// 订阅主题
{
  "type": "subscribe",
  "topic": "wallet_updates"
}

// 取消订阅
{
  "type": "unsubscribe",
  "topic": "wallet_updates"
}

// 心跳检测
{
  "type": "ping"
}

// 获取统计信息
{
  "type": "get_stats"
}
```

#### 2.2 服务端 → 客户端

```json
// 连接成功
{
  "type": "connection",
  "status": "connected",
  "client_id": "uuid",
  "timestamp": "2025-11-22T10:00:00"
}

// 订阅确认
{
  "type": "subscribed",
  "topic": "wallet_updates",
  "success": true
}

// 心跳响应
{
  "type": "pong",
  "timestamp": "2025-11-22T10:00:00"
}

// 导入进度更新
{
  "type": "import_progress",
  "task_id": "task-uuid",
  "topic": "import:task-uuid",
  "data": {
    "status": "processing",
    "total": 1000,
    "processed": 500,
    "success": 480,
    "failed": 20,
    "progress": 50.0,
    "eta": 120
  },
  "timestamp": "2025-11-22T10:00:00"
}

// 钱包数据更新
{
  "type": "wallet_update",
  "wallet_address": "0x...",
  "data": {...},
  "timestamp": "2025-11-22T10:00:00"
}

// 通知消息
{
  "type": "notification",
  "data": {
    "title": "通知标题",
    "content": "通知内容",
    "level": "info"
  },
  "timestamp": "2025-11-22T10:00:00"
}

// 系统状态更新
{
  "type": "system_status",
  "data": {
    "cpu": 45.2,
    "memory": 60.5,
    "active_wallets": 150
  },
  "timestamp": "2025-11-22T10:00:00"
}

// 错误消息
{
  "type": "error",
  "message": "错误描述"
}
```

### 3. 支持的主题

| 主题名称 | 说明 | 订阅方式 |
|---------|------|---------|
| `import:{task_id}` | 特定导入任务的进度 | 订阅时指定任务 ID |
| `wallet_updates` | 钱包数据更新 | 订阅后接收所有钱包更新 |
| `system_status` | 系统状态更新 | 订阅后接收系统状态 |
| `notifications` | 通知消息 | 订阅后接收所有通知 |

## 🔧 使用方法

### 1. 前端连接示例 (JavaScript)

```javascript
// 建立连接（带认证）
const token = localStorage.getItem('access_token');
const ws = new WebSocket(`ws://localhost:8000/api/ws?token=${token}`);

// 连接成功
ws.onopen = () => {
  console.log('WebSocket 连接成功');
  
  // 订阅导入进度
  ws.send(JSON.stringify({
    type: 'subscribe',
    topic: 'import:task-123'
  }));
};

// 接收消息
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'import_progress':
      updateProgressBar(data.data.progress);
      break;
    case 'wallet_update':
      refreshWalletData(data.wallet_address);
      break;
    case 'notification':
      showNotification(data.data);
      break;
  }
};

// 连接关闭
ws.onclose = () => {
  console.log('WebSocket 连接关闭');
};

// 错误处理
ws.onerror = (error) => {
  console.error('WebSocket 错误:', error);
};

// 心跳保活
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'ping' }));
  }
}, 30000);
```

### 2. 后端推送示例 (Python)

```python
from app.services.websocket_manager import ws_manager

# 推送导入进度
await ws_manager.send_import_progress(
    task_id="task-123",
    progress={
        "status": "processing",
        "progress": 50.0,
        "processed": 500,
        "total": 1000
    }
)

# 推送钱包更新
await ws_manager.send_wallet_update(
    wallet_address="0x...",
    data={
        "score": 85,
        "pnl": 12500.50
    }
)

# 发送通知（广播）
await ws_manager.send_notification({
    "title": "系统通知",
    "content": "数据更新完成",
    "level": "success"
})

# 发送通知（指定用户）
await ws_manager.send_notification(
    notification={
        "title": "个人通知",
        "content": "您的任务已完成"
    },
    target_users=["admin", "user123"]
)

# 发布到主题
await ws_manager.publish(
    topic="custom_topic",
    message={"data": "custom data"}
)
```

## 🧪 测试

### 1. 运行测试脚本

```bash
# 确保后端服务已启动
cd backend
python test_websocket.py
```

### 2. 测试项目

- ✅ 基本连接和消息
- ✅ 导入进度推送
- ✅ 多客户端连接
- ✅ 心跳检测
- ✅ 订阅/取消订阅

### 3. 手动测试

使用浏览器控制台或 Postman 等工具测试 WebSocket 连接：

```javascript
// 浏览器控制台
const ws = new WebSocket('ws://localhost:8000/api/ws');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.onopen = () => ws.send(JSON.stringify({type: 'ping'}));
```

## 📊 集成情况

### 1. 导入管理器集成

`backend/app/services/import_manager.py` 已集成 WebSocket 进度推送：

```python
async def notify_progress(self):
    """通知进度更新"""
    progress_data = self.get_progress()
    
    # 通过 WebSocket 推送进度
    await ws_manager.send_import_progress(self.task_id, progress_data)
```

### 2. 主应用集成

`backend/app/main.py` 已注册 WebSocket 路由：

```python
from app.api import websocket

app.include_router(websocket.router, prefix="/api", tags=["WebSocket"])
```

## 🔒 安全性

### 1. 认证

- 支持通过 Query 参数传递 JWT Token
- 自动验证 Token 并识别用户身份
- 未认证用户也可连接，但功能受限

### 2. 权限控制

- 管理员 API 需要认证
- 广播和通知功能需要管理员权限
- 普通用户只能接收消息，不能发送

### 3. 连接管理

- 自动清理断开的连接
- 异常处理和错误恢复
- 连接数量监控

## 📈 性能优化

### 1. 连接管理

- 使用字典存储连接，O(1) 查找
- 订阅使用集合，高效的增删操作
- 自动清理断开的连接

### 2. 消息推送

- 批量推送优化
- 异步非阻塞处理
- 错误隔离，单个连接失败不影响其他

### 3. 资源控制

- 心跳检测保持连接
- 超时自动断开
- 内存占用监控

## 🚀 下一步

WebSocket 实时通信已完成！接下来可以：

1. ✅ **搭建前端管理后台框架** - 创建 Vue 3 管理界面
2. ✅ **实现导入进度页面** - 使用 WebSocket 显示实时进度
3. ✅ **完善其他管理页面** - 钱包管理、配置管理等

## 📝 注意事项

1. **生产环境配置**:
   - 使用 Nginx 反向代理 WebSocket
   - 配置 SSL/TLS 加密 (wss://)
   - 设置连接超时和限流

2. **监控和日志**:
   - 监控活跃连接数
   - 记录异常连接和错误
   - 定期清理旧连接

3. **扩展性**:
   - 支持 Redis 实现跨进程消息
   - 支持集群部署
   - 支持更多消息类型

## 🎉 总结

WebSocket 实时通信系统已完整实现，包括：

- ✅ 连接管理和用户识别
- ✅ 主题订阅机制
- ✅ 多种消息类型支持
- ✅ 导入进度实时推送
- ✅ 完整的测试工具
- ✅ 安全认证和权限控制

系统已准备好用于前端集成！


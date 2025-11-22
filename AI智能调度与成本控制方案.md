# AI 智能调度与成本控制方案

## 📌 核心问题

面对**数万个钱包**，如何智能地使用 AI 分析，既要**控制成本**，又要**保证效果**？

---

## 一、AI 分析触发策略

### 1.1 分层分析策略

**核心理念**：不是所有钱包都需要 AI 分析，**优先分析高价值钱包**。

#### 层级1：系统评分预筛选

**目标**：从数万个钱包中筛选出值得 AI 分析的钱包

**筛选条件**（可配置）：
```json
{
  "ai_analysis_filters": {
    "system_score_min": 60,        // 系统评分 ≥ 60 分
    "total_trades_min": 30,         // 至少 30 笔交易
    "trading_days_min": 30,         // 至少 30 天交易历史
    "roi_min": 50,                  // ROI ≥ 50%
    "exclude_liquidated": true      // 排除已爆仓钱包
  }
}
```

**预期结果**：从 10000 个钱包筛选出 500-1000 个优质钱包

---

#### 层级2：优先级排序

**目标**：确定 AI 分析的优先级

**优先级规则**（从高到低）：

1. **用户主动查看**（最高优先级）
   - 用户点击钱包详情时立即触发 AI 分析
   - 实时分析，不排队

2. **榜单钱包**（高优先级）
   - 系统榜单 Top 20
   - 用户自定义榜单 Top 20
   - 每日定时分析

3. **高分钱包**（中优先级）
   - 系统评分 ≥ 80 分
   - 每周分析一次

4. **中等钱包**（低优先级）
   - 系统评分 60-80 分
   - 每月分析一次

5. **低分钱包**（不分析）
   - 系统评分 < 60 分
   - 不进行 AI 分析

---

#### 层级3：动态调整

**目标**：根据钱包表现变化，动态调整分析频率

**触发条件**：
```python
# 需要重新分析的情况
def need_reanalysis(wallet):
    """判断是否需要重新分析"""
    
    # 1. 从未分析过
    if not wallet.ai_analysis:
        return True
    
    # 2. 距离上次分析时间超过阈值
    days_since_last_analysis = (now - wallet.last_ai_analysis_time).days
    
    if wallet.system_score >= 80:
        # 高分钱包：7天重新分析
        if days_since_last_analysis >= 7:
            return True
    elif wallet.system_score >= 60:
        # 中等钱包：30天重新分析
        if days_since_last_analysis >= 30:
            return True
    
    # 3. 系统评分显著变化（±10分）
    if abs(wallet.system_score - wallet.last_system_score) >= 10:
        return True
    
    # 4. 交易行为显著变化
    if wallet.recent_performance_change > 0.3:  # 30% 变化
        return True
    
    # 5. 出现重大事件
    if wallet.has_major_event:  # 爆仓、大额盈亏等
        return True
    
    return False
```

---

### 1.2 后台配置界面

**AI 分析策略配置**：

```json
{
  "ai_analysis_strategy": {
    "enabled": true,
    
    // 预筛选条件
    "pre_filter": {
      "system_score_min": 60,
      "total_trades_min": 30,
      "trading_days_min": 30,
      "roi_min": 50
    },
    
    // 分析频率（天）
    "analysis_frequency": {
      "high_score_wallets": 7,      // 系统评分 ≥ 80
      "medium_score_wallets": 30,   // 系统评分 60-80
      "leaderboard_wallets": 1      // 榜单钱包每天分析
    },
    
    // 重新分析触发条件
    "reanalysis_triggers": {
      "score_change_threshold": 10,     // 评分变化 ≥ 10 分
      "performance_change_threshold": 0.3,  // 表现变化 ≥ 30%
      "major_events": true              // 重大事件触发
    },
    
    // 批量分析配置
    "batch_analysis": {
      "enabled": true,
      "batch_size": 10,             // 每批 10 个钱包
      "concurrent_limit": 3,        // 最多 3 个并发
      "interval_seconds": 2         // 批次间隔 2 秒
    },
    
    // 每日配额
    "daily_quota": {
      "max_analyses": 1000,         // 每天最多 1000 次分析
      "max_cost": 10.0,             // 每天最多 $10
      "alert_threshold": 0.8        // 达到 80% 时告警
    },
    
    // 榜单 AI 分析配置
    "leaderboard_ai": {
      "enabled": true,
      "target_leaderboards": [      // 指定哪些榜单启用 AI
        "potential_stars",          // 潜力新星榜
        "all_star",                 // 全能王榜
        "dark_horse"                // 黑马榜
      ],
      "top_n": 20,                  // 每个榜单分析前 20 名
      "schedule": "0 2 * * *"       // 每天凌晨 2 点执行
    }
  }
}
```

---

## 二、AI 上下文长度管理

### 2.1 Token 限制

**DeepSeek 限制**：
- 输入：最大 32K tokens
- 输出：最大 4K tokens

**单个钱包分析**：
- 输入：约 1000-1500 tokens
- 输出：约 500-800 tokens
- **安全范围内**

---

### 2.2 批量分析优化

**问题**：批量分析时，如何控制 token 数量？

**方案1：单独分析（推荐）**

```python
async def batch_analyze_wallets(wallets: list):
    """批量分析钱包（单独分析）"""
    results = []
    
    for wallet in wallets:
        # 每个钱包单独调用 API
        analysis = await analyze_single_wallet(wallet)
        results.append(analysis)
        
        # 控制频率
        await asyncio.sleep(0.5)
    
    return results
```

**优点**：
- ✅ 每个钱包分析独立，互不影响
- ✅ Token 数量可控
- ✅ 失败不影响其他钱包

**缺点**：
- ❌ API 调用次数多
- ❌ 总耗时长

---

**方案2：分组批量分析（可选）**

```python
async def batch_analyze_wallets_grouped(wallets: list, group_size=5):
    """分组批量分析"""
    results = []
    
    # 每 5 个钱包一组
    for i in range(0, len(wallets), group_size):
        group = wallets[i:i+group_size]
        
        # 构建批量 Prompt（精简数据）
        prompt = build_batch_prompt(group)
        
        # 调用 API
        analysis = await call_ai_api(prompt)
        results.extend(analysis)
    
    return results
```

**优点**：
- ✅ API 调用次数少
- ✅ 总耗时短
- ✅ 成本更低

**缺点**：
- ❌ Token 数量较大
- ❌ 需要精简数据
- ❌ 一个失败影响整组

**推荐**：使用方案1（单独分析），简单可靠。

---

### 2.3 数据精简策略

**目标**：减少输入 token 数量，降低成本

**精简方法**：

1. **只发送关键指标**
   - 不发送完整交易记录
   - 只发送最近 20-30 笔交易
   - 只发送关键统计数据

2. **压缩交易记录**
   ```python
   # 完整版（约 500 tokens）
   {
       "timestamp": "2024-01-01 10:00:00",
       "symbol": "BTC",
       "side": "long",
       "size": 1.5,
       "entry_price": 40000,
       "exit_price": 41000,
       "pnl": 1500,
       "holding_time": 3.5,
       "fees": 10
   }
   
   # 精简版（约 100 tokens）
   "BTC long +$1500 (3.5h)"
   ```

3. **使用统计摘要**
   ```python
   # 不发送 100 笔交易记录
   # 发送统计摘要
   {
       "recent_30_trades": {
           "win_rate": 65,
           "avg_pnl": 500,
           "best_trade": 5000,
           "worst_trade": -1000,
           "avg_holding_time": 4.5
       }
   }
   ```

---

## 三、AI 分析场景设计

### 3.1 场景1：钱包画像分析

**触发时机**：
- 用户查看钱包详情
- 钱包首次进入榜单
- 钱包表现显著变化

**分析内容**：
- 交易风格识别
- 优势和风险分析
- 个性化标签
- AI 评分

**成本**：约 $0.0005 / 次

---

### 3.2 场景2：榜单 AI 排序

**触发时机**：
- 每日定时任务（凌晨 2 点）
- 用户手动刷新榜单

**分析流程**：
```
1. 系统评分筛选出候选钱包（Top 100）
2. AI 批量分析（每批 10 个）
3. 根据 AI 评分排序
4. 生成 AI 榜单（Top 20）
```

**成本**：100 个钱包 × $0.0005 = **$0.05 / 次**

**频率**：每天 1 次 = **$1.5 / 月**

---

### 3.3 场景3：市场趋势分析 ⭐

**触发时机**：
- 每小时自动分析
- Dashboard 页面加载

**分析内容**：
- 整体市场情绪（多空比、杠杆率等）
- 高分交易员行为变化
- 异常信号识别
- 趋势预测

**数据输入**：
```python
{
  "market_overview": {
    "total_wallets": 10000,
    "active_wallets_24h": 1500,
    "avg_system_score": 65,
    "long_short_ratio": 1.8,  // 多空比
    "avg_leverage": 12.5,
    "total_pnl_24h": 150000
  },
  "top_performers": [
    {
      "score": 92,
      "roi": 350,
      "recent_action": "增持 BTC 多头"
    },
    // Top 20 高分钱包的关键行为
  ],
  "anomalies": [
    "杠杆率 24h 上升 15%",
    "空头钱包数量减少 20%",
    "BTC 持仓集中度上升"
  ]
}
```

**AI 任务**：
- 分析市场整体情绪
- 识别趋势信号
- 发现异常行为
- 给出预测和建议

**成本**：约 $0.001 / 次

**频率**：每小时 1 次 = **$0.72 / 月**

---

### 3.4 场景4：钱包异常检测 ⭐

**触发时机**：
- 实时监控（每 5 分钟）
- 检测到异常时立即分析

**异常类型**：
1. **交易行为异常**
   - 交易频率突然大幅变化
   - 持仓方向突然反转
   - 杠杆率异常升高

2. **资金异常**
   - 大额存款/取款
   - 账户余额急剧变化

3. **表现异常**
   - 连续大额盈利/亏损
   - 胜率/盈亏比突变

**AI 任务**：
```python
{
  "anomaly_analysis": {
    "wallet_address": "0x1234...",
    "anomaly_type": "交易频率异常",
    "details": {
      "normal_frequency": "2-3 次/天",
      "current_frequency": "15 次/天",
      "change_percentage": "+500%"
    },
    "ai_task": "分析异常原因，评估风险"
  }
}
```

**AI 输出**：
```json
{
  "anomaly_assessment": {
    "severity": "中等",
    "possible_reasons": [
      "市场波动加剧，交易员增加操作频率",
      "可能改变了交易策略"
    ],
    "risk_level": "需关注",
    "recommendations": [
      "观察未来 3-5 天表现",
      "如持续高频交易且胜率下降，建议降低跟单仓位"
    ]
  }
}
```

**成本**：约 $0.0005 / 次

**频率**：按需触发，预计 10-20 次/天 = **$0.3 / 月**

---

### 3.5 场景5：跟单建议生成

**触发时机**：
- 用户查看钱包详情
- 用户点击"AI 建议"按钮

**AI 任务**：
- 评估当前是否适合跟单
- 分析风险和机会
- 给出具体建议

**成本**：约 $0.0005 / 次

**频率**：按需触发

---

## 四、成本估算与控制

### 4.1 月度成本估算

| 场景 | 频率 | 单次成本 | 月度成本 |
|------|------|----------|----------|
| 钱包画像分析 | 100次/天 | $0.0005 | $1.50 |
| 榜单 AI 排序 | 1次/天 | $0.05 | $1.50 |
| 市场趋势分析 | 24次/天 | $0.001 | $0.72 |
| 异常检测 | 15次/天 | $0.0005 | $0.23 |
| 跟单建议 | 50次/天 | $0.0005 | $0.75 |
| **总计** | - | - | **$4.70** |

**结论**：月度成本约 **$5**，非常可控！

---

### 4.2 成本控制措施

#### 措施1：智能缓存

```python
class AIAnalysisCache:
    """AI 分析缓存"""
    
    def get_cache_ttl(self, wallet, analysis_type):
        """根据钱包和分析类型确定缓存时间"""
        
        if analysis_type == "wallet_profile":
            # 钱包画像缓存
            if wallet.system_score >= 80:
                return 7 * 24 * 3600  # 7 天
            elif wallet.system_score >= 60:
                return 30 * 24 * 3600  # 30 天
            else:
                return 90 * 24 * 3600  # 90 天
        
        elif analysis_type == "market_insight":
            # 市场洞察缓存
            return 3600  # 1 小时
        
        elif analysis_type == "anomaly_detection":
            # 异常检测不缓存
            return 0
        
        return 24 * 3600  # 默认 24 小时
```

---

#### 措施2：配额管理

```python
class AIQuotaManager:
    """AI 配额管理"""
    
    async def check_quota(self, analysis_type):
        """检查是否还有配额"""
        today = date.today()
        
        # 获取今日使用情况
        usage = await self.get_daily_usage(today)
        
        # 检查次数配额
        if usage['count'] >= self.config['max_analyses']:
            raise QuotaExceededError("今日分析次数已达上限")
        
        # 检查成本配额
        if usage['cost'] >= self.config['max_cost']:
            raise QuotaExceededError("今日成本已达上限")
        
        # 检查是否接近阈值（发送告警）
        if usage['cost'] >= self.config['max_cost'] * 0.8:
            await self.send_alert("AI 成本接近每日上限")
        
        return True
    
    async def record_usage(self, analysis_type, tokens, cost):
        """记录使用情况"""
        await db.execute(
            "INSERT INTO ai_usage_stats (date, analysis_type, tokens, cost) "
            "VALUES (?, ?, ?, ?)",
            (date.today(), analysis_type, tokens, cost)
        )
```

---

#### 措施3：优先级队列

```python
class AIAnalysisQueue:
    """AI 分析队列"""
    
    def __init__(self):
        self.queue = PriorityQueue()
    
    async def add_task(self, wallet, analysis_type, priority):
        """添加分析任务"""
        task = {
            'wallet': wallet,
            'analysis_type': analysis_type,
            'priority': priority,  # 1-5，1 最高
            'created_at': datetime.now()
        }
        
        # 检查是否已在队列中
        if self.is_in_queue(wallet, analysis_type):
            return
        
        # 检查缓存
        cached = await self.get_cached_analysis(wallet, analysis_type)
        if cached and not self.is_expired(cached):
            return cached
        
        # 加入队列
        await self.queue.put((priority, task))
    
    async def process_queue(self):
        """处理队列"""
        while True:
            # 检查配额
            if not await quota_manager.check_quota():
                await asyncio.sleep(3600)  # 等待 1 小时
                continue
            
            # 获取最高优先级任务
            priority, task = await self.queue.get()
            
            # 执行分析
            result = await ai_service.analyze(
                task['wallet'], 
                task['analysis_type']
            )
            
            # 缓存结果
            await self.cache_result(task, result)
            
            # 记录使用
            await quota_manager.record_usage(
                task['analysis_type'],
                result['tokens'],
                result['cost']
            )
            
            # 控制频率
            await asyncio.sleep(1)
```

---

## 五、数据库设计补充

### 5.1 AI 分析缓存表

```sql
CREATE TABLE ai_analysis_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_address VARCHAR(42) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    analysis_result JSON NOT NULL,
    tokens_used INTEGER,
    cost DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    
    UNIQUE (wallet_address, analysis_type),
    INDEX idx_wallet (wallet_address),
    INDEX idx_type (analysis_type),
    INDEX idx_expires (expires_at)
);
```

---

### 5.2 AI 使用统计表（增强）

```sql
CREATE TABLE ai_usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    total_requests INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10, 4) DEFAULT 0,
    cache_hits INTEGER DEFAULT 0,
    cache_misses INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (date, analysis_type),
    INDEX idx_date (date DESC)
);
```

---

### 5.3 AI 分析队列表

```sql
CREATE TABLE ai_analysis_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_address VARCHAR(42) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'pending',  -- pending/processing/completed/failed
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_created (created_at)
);
```

---

## 六、后台管理界面

### 6.1 AI 分析策略配置

```
┌─────────────────────────────────────────┐
│ AI 分析策略配置                         │
│ ┌─────────────────────────────────┐   │
│ │ 预筛选条件:                     │   │
│ │ 系统评分 ≥ [60] 分              │   │
│ │ 交易次数 ≥ [30] 次              │   │
│ │ 交易天数 ≥ [30] 天              │   │
│ │                                 │   │
│ │ 分析频率:                       │   │
│ │ 高分钱包(≥80): [7] 天           │   │
│ │ 中等钱包(60-80): [30] 天        │   │
│ │ 榜单钱包: [1] 天                │   │
│ │                                 │   │
│ │ 榜单 AI 配置:                   │   │
│ │ [✓] 潜力新星榜                  │   │
│ │ [✓] 全能王榜                    │   │
│ │ [✓] 黑马榜                      │   │
│ │ 每个榜单分析前 [20] 名          │   │
│ │                                 │   │
│ │ 每日配额:                       │   │
│ │ 最大分析次数: [1000] 次         │   │
│ │ 最大成本: [$10.00]              │   │
│ │ 告警阈值: [80] %                │   │
│ │                                 │   │
│ │ [保存配置]                      │   │
│ └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

### 6.2 AI 使用统计

```
┌─────────────────────────────────────────┐
│ AI 使用统计                             │
│ ┌─────────────────────────────────┐   │
│ │ 今日使用情况:                   │   │
│ │ 分析次数: 150 / 1000            │   │
│ │ [━━━━━━━━━━━━━━━━] 15%         │   │
│ │                                 │   │
│ │ 成本: $2.50 / $10.00            │   │
│ │ [━━━━━━━━━━━━━━━━] 25%         │   │
│ │                                 │   │
│ │ 缓存命中率: 75%                 │   │
│ │ [━━━━━━━━━━━━━━━━] 75%         │   │
│ │                                 │   │
│ │ 分析类型分布:                   │   │
│ │ • 钱包画像: 80 次 ($1.20)      │   │
│ │ • 榜单排序: 1 次 ($0.05)       │   │
│ │ • 市场趋势: 24 次 ($0.72)      │   │
│ │ • 异常检测: 10 次 ($0.15)      │   │
│ │ • 跟单建议: 35 次 ($0.53)      │   │
│ │                                 │   │
│ │ [查看详细统计] [导出报表]      │   │
│ └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

### 6.3 AI 分析队列监控

```
┌─────────────────────────────────────────┐
│ AI 分析队列                             │
│ ┌─────────────────────────────────┐   │
│ │ 队列状态:                       │   │
│ │ 等待中: 25                      │   │
│ │ 处理中: 3                       │   │
│ │ 已完成: 150                     │   │
│ │ 失败: 2                         │   │
│ │                                 │   │
│ │ 当前任务:                       │   │
│ │ ┌─────────────────────────┐   │   │
│ │ │ 优先级1: 分析 0x1234... │   │   │
│ │ │ 优先级1: 分析 0x5678... │   │   │
│ │ │ 优先级2: 榜单排序       │   │   │
│ │ └─────────────────────────┘   │   │
│ │                                 │   │
│ │ [暂停队列] [清空队列] [刷新]   │   │
│ └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## 七、实施建议

### 7.1 分阶段实施

**第一阶段**：基础功能
- ✅ 单个钱包 AI 分析
- ✅ 简单的缓存机制
- ✅ 基础配额控制

**第二阶段**：智能调度
- ✅ 优先级队列
- ✅ 智能缓存策略
- ✅ 批量分析优化

**第三阶段**：高级功能
- ✅ 市场趋势分析
- ✅ 异常检测
- ✅ 完整的后台管理

---

### 7.2 监控与告警

**监控指标**：
- 每日分析次数
- 每日成本
- 缓存命中率
- 队列长度
- 失败率

**告警规则**：
- 成本达到 80% 阈值
- 队列长度 > 100
- 失败率 > 10%
- API 响应时间 > 10s

---

## 八、总结

### 核心策略

1. **分层筛选**：系统评分预筛选 → 优先级排序 → 动态调整
2. **智能缓存**：根据钱包评分和变化动态调整缓存时间
3. **配额控制**：每日上限 + 实时监控 + 自动告警
4. **优先级队列**：用户主动查看 > 榜单钱包 > 高分钱包
5. **场景多样化**：不只是打分，还有趋势分析、异常检测等

### 成本控制

- **预期月度成本**：$5-10（完全可控）
- **可配置上限**：灵活调整
- **智能优化**：缓存 + 批量 + 按需

### 效果预期

- ✅ 高价值钱包得到深度 AI 分析
- ✅ 低价值钱包不浪费成本
- ✅ 动态响应钱包表现变化
- ✅ 多样化的 AI 应用场景
- ✅ 成本可控，效果显著

---

**这套方案既智能又经济，完美解决了你提出的所有问题！** 🎯


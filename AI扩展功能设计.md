# AI 扩展功能设计 - DeepSeek 集成方案

## 📌 设计理念

**系统评分 + AI 分析 = 双重保障**

- **系统评分**：基于量化指标，客观、稳定、可解释
- **AI 分析**：理解交易行为，发现隐藏模式，提供洞察

**两者互补，不冲突**：
- 系统评分作为基础筛选
- AI 分析提供深度洞察
- 用户可选择性参考

---

## 一、AI 功能设计

### 1.1 核心功能

#### 功能1：AI 交易员画像生成

**输入数据**：
```json
{
  "wallet_address": "0x1234...",
  "basic_metrics": {
    "roi": 250.5,
    "win_rate": 65.2,
    "profit_loss_ratio": 2.8,
    "max_drawdown": 18.5,
    "sharpe_ratio": 2.1,
    "total_trades": 156,
    "trading_days": 120
  },
  "behavior_patterns": {
    "trading_frequency": "high",
    "avg_holding_time_hours": 4.5,
    "long_short_ratio": 0.6,
    "favorite_coins": ["BTC", "ETH", "SOL"],
    "trading_time_distribution": {...}
  },
  "recent_trades": [
    {
      "timestamp": "2024-01-01 10:00:00",
      "symbol": "BTC",
      "side": "long",
      "pnl": 1500,
      "holding_time": 3.5
    },
    // 最近 20-50 笔交易
  ],
  "equity_curve": {
    "30d": [[timestamp, balance], ...]
  }
}
```

**AI 任务**：
1. 分析交易风格（趋势跟踪/均值回归/动量交易等）
2. 识别优势和风险点
3. 生成个性化标签（如"BTC 波段高手"、"逆势交易者"）
4. 评估心理素质（是否情绪化交易）
5. 预测未来表现趋势

**输出示例**：
```json
{
  "ai_analysis": {
    "trading_style": "趋势跟踪型交易者",
    "style_confidence": 0.85,
    "strengths": [
      "擅长捕捉 BTC 中期趋势",
      "止损纪律严格，回撤控制优秀",
      "盈利交易平均持仓时间长，亏损交易快速止损"
    ],
    "weaknesses": [
      "在震荡行情中表现一般",
      "交易频率偏高，可能存在过度交易"
    ],
    "risk_warnings": [
      "近期杠杆率有上升趋势，需关注风险"
    ],
    "ai_tags": [
      "BTC 趋势猎手",
      "严格止损",
      "中线持仓",
      "震荡市弱势"
    ],
    "ai_score": 88,
    "score_reasoning": "该交易员在趋势行情中表现优异，风险控制严格，但需注意震荡市的应对策略。综合评分 88 分，属于优秀交易员。",
    "future_outlook": "看好。当前市场处于趋势行情，该交易员的风格匹配度高，预计未来 1-3 个月表现稳定。"
  }
}
```

---

#### 功能2：AI 榜单生成

**流程**：
```
系统筛选 → AI 深度分析 → AI 排序 → 生成榜单
```

**步骤1：系统预筛选**
- 使用系统评分筛选出 Top 100 钱包
- 或使用自定义条件筛选

**步骤2：AI 批量分析**
- 并发调用 AI 分析每个钱包
- 生成 AI 评分和标签

**步骤3：AI 排序**
- 根据 AI 评分排序
- 或根据特定维度排序（如"最具潜力"）

**步骤4：生成榜单**
- AI 榜单独立展示
- 可与系统榜单对比

**AI 榜单类型**：

##### 榜单1：AI 潜力新星榜

**筛选条件**：
- 钱包年龄：30-90 天
- 交易次数：> 30
- 系统评分：> 60

**AI 分析重点**：
- 学习能力（收益曲线是否向上）
- 交易策略的进化
- 风险意识的成长
- 潜力评估

**排序依据**：AI 潜力分（0-100）

---

##### 榜单2：AI 全能王榜

**筛选条件**：
- 系统评分 > 70
- 交易天数 > 60

**AI 分析重点**：
- 多市场适应能力
- 多币种盈利能力
- 多策略运用能力
- 综合素质评估

**排序依据**：AI 综合分

---

##### 榜单3：AI 黑马榜

**筛选条件**：
- 系统评分：50-70（中等）
- 但某些维度特别突出

**AI 分析重点**：
- 发现被系统低估的钱包
- 识别独特优势
- 评估爆发潜力

**排序依据**：AI 黑马指数

---

#### 功能3：AI 交易建议

**场景**：用户查看钱包详情时

**AI 任务**：
- 分析该交易员当前状态
- 评估是否适合跟单
- 给出具体建议

**输出示例**：
```json
{
  "recommendation": {
    "action": "建议跟单",
    "confidence": 0.75,
    "reasons": [
      "该交易员近 30 天表现稳定，胜率和盈亏比均优于历史平均",
      "当前持仓方向与市场趋势一致",
      "风险控制严格，最大回撤低于 15%"
    ],
    "risk_tips": [
      "建议跟单仓位不超过总资金的 20%",
      "该交易员偏好高杠杆，需注意风险"
    ],
    "best_follow_strategy": "建议跟随其 BTC 和 ETH 的交易，其他币种表现一般"
  }
}
```

---

#### 功能4：AI 市场洞察

**场景**：Dashboard 页面

**AI 任务**：
- 分析所有钱包的整体行为
- 识别市场趋势
- 发现异常信号

**输出示例**：
```json
{
  "market_insights": {
    "overall_sentiment": "偏多",
    "sentiment_score": 65,
    "key_findings": [
      "70% 的高分交易员增加了 BTC 多头持仓",
      "空头交易员数量减少 15%",
      "平均杠杆率上升 10%，市场情绪乐观"
    ],
    "warnings": [
      "杠杆率快速上升，需警惕市场过热"
    ],
    "ai_prediction": "未来 7 天市场可能继续上涨，但需注意回调风险"
  }
}
```

---

## 二、技术实现方案

### 2.1 DeepSeek API 集成

#### 配置管理

**后台配置界面**：
```json
{
  "ai_config": {
    "enabled": true,
    "provider": "deepseek",
    "api_key": "sk-xxxxxxxxxxxxx",
    "api_url": "https://api.deepseek.com/v1/chat/completions",
    "model": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout": 30,
    "retry_times": 3,
    "rate_limit": {
      "requests_per_minute": 20,
      "requests_per_day": 1000
    },
    "cost_control": {
      "max_daily_cost": 10.0,
      "alert_threshold": 8.0
    }
  }
}
```

---

#### API 客户端

```python
# backend/app/services/ai_service.py

from openai import AsyncOpenAI
from loguru import logger
from app.config import config

class AIService:
    """AI 分析服务"""
    
    def __init__(self):
        ai_config = config.get_config('ai')
        if ai_config['enabled']:
            self.client = AsyncOpenAI(
                api_key=ai_config['api_key'],
                base_url=ai_config['api_url']
            )
            self.model = ai_config['model']
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
    
    async def analyze_wallet(self, wallet_data: dict) -> dict:
        """分析单个钱包"""
        if not self.enabled:
            return {"error": "AI service is disabled"}
        
        try:
            # 构建 Prompt
            prompt = self._build_wallet_analysis_prompt(wallet_data)
            
            # 调用 API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位专业的量化交易分析师，擅长分析交易员的行为模式和风险特征。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # 解析响应
            result = json.loads(response.choices[0].message.content)
            
            # 记录使用量
            self._log_usage(response.usage)
            
            return result
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {"error": str(e)}
    
    def _build_wallet_analysis_prompt(self, wallet_data: dict) -> str:
        """构建分析 Prompt"""
        prompt = f"""
请分析以下交易员的数据，并以 JSON 格式返回分析结果。

## 交易员数据

### 基础指标
- ROI: {wallet_data['roi']}%
- 胜率: {wallet_data['win_rate']}%
- 盈亏比: {wallet_data['profit_loss_ratio']}
- 最大回撤: {wallet_data['max_drawdown']}%
- 夏普比率: {wallet_data['sharpe_ratio']}
- 总交易次数: {wallet_data['total_trades']}
- 交易天数: {wallet_data['trading_days']}

### 行为特征
- 交易频率: {wallet_data['trading_frequency']}
- 平均持仓时间: {wallet_data['avg_holding_time']} 小时
- 多空比: {wallet_data['long_short_ratio']}
- 偏好币种: {', '.join(wallet_data['favorite_coins'])}

### 最近交易记录
{self._format_recent_trades(wallet_data['recent_trades'])}

## 分析要求

请从以下维度进行分析：

1. **交易风格识别**：判断交易员属于哪种类型（趋势跟踪/均值回归/动量交易/套利等）
2. **优势分析**：列出 2-3 个核心优势
3. **风险点**：指出 1-2 个需要注意的风险
4. **AI 标签**：生成 3-5 个个性化标签
5. **AI 评分**：给出 0-100 的综合评分
6. **评分理由**：简要说明评分依据
7. **未来展望**：预测未来 1-3 个月的表现趋势

## 返回格式

请严格按照以下 JSON 格式返回：

{{
  "trading_style": "交易风格",
  "style_confidence": 0.85,
  "strengths": ["优势1", "优势2"],
  "weaknesses": ["风险点1"],
  "risk_warnings": ["警告1"],
  "ai_tags": ["标签1", "标签2", "标签3"],
  "ai_score": 88,
  "score_reasoning": "评分理由",
  "future_outlook": "未来展望"
}}
"""
        return prompt
    
    async def generate_ai_leaderboard(
        self, 
        wallets: list, 
        leaderboard_type: str
    ) -> list:
        """生成 AI 榜单"""
        if not self.enabled:
            return []
        
        # 批量分析（控制并发）
        semaphore = asyncio.Semaphore(5)
        
        async def analyze_one(wallet):
            async with semaphore:
                analysis = await self.analyze_wallet(wallet)
                return {**wallet, "ai_analysis": analysis}
        
        tasks = [analyze_one(w) for w in wallets]
        results = await asyncio.gather(*tasks)
        
        # 根据 AI 评分排序
        sorted_results = sorted(
            results, 
            key=lambda x: x.get('ai_analysis', {}).get('ai_score', 0),
            reverse=True
        )
        
        return sorted_results
    
    def _log_usage(self, usage):
        """记录 API 使用量"""
        logger.info(
            f"AI API Usage: "
            f"prompt_tokens={usage.prompt_tokens}, "
            f"completion_tokens={usage.completion_tokens}, "
            f"total_tokens={usage.total_tokens}"
        )
        
        # 记录到数据库（用于成本控制）
        # TODO: 实现成本统计
```

---

### 2.2 数据库扩展

#### 新增表：AI 分析结果表

```sql
CREATE TABLE ai_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_address VARCHAR(42) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL, -- 'wallet_profile', 'recommendation', etc.
    analysis_result JSON NOT NULL,
    ai_score DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (wallet_address) REFERENCES wallets(address),
    INDEX idx_wallet (wallet_address),
    INDEX idx_type (analysis_type),
    INDEX idx_created (created_at DESC)
);
```

#### 新增表：AI 榜单表

```sql
CREATE TABLE ai_leaderboards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    leaderboard_type VARCHAR(50) NOT NULL, -- 'potential', 'all_star', 'dark_horse'
    wallet_address VARCHAR(42) NOT NULL,
    rank INTEGER NOT NULL,
    ai_score DECIMAL(5, 2),
    ai_analysis JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (wallet_address) REFERENCES wallets(address),
    INDEX idx_type (leaderboard_type),
    INDEX idx_rank (rank),
    INDEX idx_created (created_at DESC)
);
```

#### 新增表：AI 使用统计表

```sql
CREATE TABLE ai_usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    total_requests INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10, 4) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (date),
    INDEX idx_date (date DESC)
);
```

---

### 2.3 API 设计

#### API 1：获取钱包 AI 分析

```
GET /api/wallets/{address}/ai-analysis

Query Parameters:
  - force_refresh: boolean (是否强制重新分析)

Response:
{
  "wallet_address": "0x1234...",
  "ai_analysis": {
    "trading_style": "趋势跟踪型",
    "strengths": [...],
    "ai_score": 88,
    ...
  },
  "analyzed_at": "2024-01-01T12:00:00Z",
  "cache_hit": false
}
```

---

#### API 2：获取 AI 榜单

```
GET /api/ai-leaderboards/{type}

Path Parameters:
  - type: 'potential' | 'all_star' | 'dark_horse'

Query Parameters:
  - time_period: '24h' | '7d' | '30d'
  - limit: integer (default: 20)

Response:
{
  "leaderboard_type": "potential",
  "time_period": "7d",
  "generated_at": "2024-01-01T12:00:00Z",
  "wallets": [
    {
      "rank": 1,
      "wallet_address": "0x1234...",
      "system_score": 75,
      "ai_score": 88,
      "ai_analysis": {...}
    },
    ...
  ]
}
```

---

#### API 3：触发 AI 批量分析

```
POST /api/ai/batch-analyze

Body:
{
  "wallet_addresses": ["0x1234...", "0x5678..."],
  "analysis_type": "wallet_profile"
}

Response:
{
  "task_id": "abc123",
  "status": "processing",
  "total": 10,
  "completed": 0
}
```

---

#### API 4：获取 AI 使用统计

```
GET /api/ai/usage-stats

Query Parameters:
  - start_date: date
  - end_date: date

Response:
{
  "total_requests": 1500,
  "total_tokens": 500000,
  "estimated_cost": 25.50,
  "daily_stats": [
    {
      "date": "2024-01-01",
      "requests": 150,
      "tokens": 50000,
      "cost": 2.50
    },
    ...
  ]
}
```

---

### 2.4 缓存策略

**AI 分析结果缓存**：
- 缓存时间：24 小时
- 用户可手动刷新
- 钱包数据更新时自动失效

**成本控制**：
- 同一钱包 24 小时内只分析一次（除非手动刷新）
- 设置每日 API 调用上限
- 达到成本阈值时发送告警

---

## 三、前端界面设计

### 3.1 钱包详情页 - AI 分析区

**位置**：钱包详情页底部，独立区域

**布局**：
```
┌─────────────────────────────────────────────┐
│  🤖 AI 深度分析                              │
│  ┌─────────────────────────────────────┐  │
│  │ [AI 分析开关: 已开启]  [刷新分析]   │  │
│  │                                     │  │
│  │ 📊 AI 评分: 88 分 (系统评分: 85)   │  │
│  │ [━━━━━━━━━━━━━━━━━━] 88%          │  │
│  │                                     │  │
│  │ 🎯 交易风格: 趋势跟踪型 (置信度85%)│  │
│  │                                     │  │
│  │ ✅ 核心优势:                        │  │
│  │   • 擅长捕捉 BTC 中期趋势           │  │
│  │   • 止损纪律严格，回撤控制优秀      │  │
│  │                                     │  │
│  │ ⚠️ 风险提示:                        │  │
│  │   • 在震荡行情中表现一般            │  │
│  │                                     │  │
│  │ 🏷️ AI 标签:                         │  │
│  │   [BTC趋势猎手] [严格止损] [中线]  │  │
│  │                                     │  │
│  │ 💡 AI 建议:                         │  │
│  │   建议跟单 (置信度: 75%)            │  │
│  │   • 该交易员近期表现稳定...         │  │
│  │   • 建议跟单仓位不超过 20%          │  │
│  │                                     │  │
│  │ 🔮 未来展望:                        │  │
│  │   看好。当前市场趋势匹配...         │  │
│  └─────────────────────────────────────┘  │
│  最后分析时间: 2024-01-01 12:00            │
└─────────────────────────────────────────────┘
```

---

### 3.2 AI 榜单页面

**导航栏**：
```
[系统榜单] [AI 榜单]

AI 榜单:
  [AI 潜力新星] [AI 全能王] [AI 黑马榜]
```

**榜单卡片**：
```
┌─────────────────────────────────────────┐
│ 🥇 1. 0x1234...abcd                     │
│ ┌─────────────────────────────────┐   │
│ │ 系统评分: 75  |  AI 评分: 88    │   │
│ │ AI 风格: 趋势跟踪型              │   │
│ │ AI 标签: [BTC高手][严格止损]    │   │
│ │ AI 评语: 该交易员在趋势行情...   │   │
│ │ [查看详情] [查看 AI 分析]        │   │
│ └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

### 3.3 Dashboard - AI 市场洞察

**位置**：Dashboard 页面右侧

**布局**：
```
┌─────────────────────────────────────┐
│ 🤖 AI 市场洞察                      │
│ ┌─────────────────────────────┐   │
│ │ 市场情绪: 偏多 (65分)        │   │
│ │ [━━━━━━━━━━━━━━] 65%        │   │
│ │                             │   │
│ │ 📈 关键发现:                 │   │
│ │ • 70% 高分交易员增持 BTC    │   │
│ │ • 空头交易员减少 15%        │   │
│ │ • 平均杠杆率上升 10%        │   │
│ │                             │   │
│ │ ⚠️ 风险警告:                 │   │
│ │ • 杠杆率快速上升，警惕过热  │   │
│ │                             │   │
│ │ 🔮 AI 预测:                  │   │
│ │ 未来 7 天市场可能继续上涨... │   │
│ └─────────────────────────────┘   │
│ 更新时间: 5 分钟前                 │
└─────────────────────────────────────┘
```

---

### 3.4 后台 - AI 配置页面

**布局**：
```
┌─────────────────────────────────────────┐
│ AI 功能配置                             │
│ ┌─────────────────────────────────┐   │
│ │ [✓] 启用 AI 功能                │   │
│ │                                 │   │
│ │ API 配置:                       │   │
│ │ API Key: [sk-xxxxxxxx] [测试]  │   │
│ │ API URL: [https://api...]      │   │
│ │ 模型: [deepseek-chat ▼]        │   │
│ │ Temperature: [0.7]             │   │
│ │                                 │   │
│ │ 频率限制:                       │   │
│ │ 每分钟: [20] 次                │   │
│ │ 每天: [1000] 次                │   │
│ │                                 │   │
│ │ 成本控制:                       │   │
│ │ 每日最大成本: [$10.00]         │   │
│ │ 告警阈值: [$8.00]              │   │
│ │                                 │   │
│ │ 当前使用情况:                   │   │
│ │ 今日请求: 150 / 1000           │   │
│ │ 今日成本: $2.50 / $10.00       │   │
│ │ [查看详细统计]                  │   │
│ │                                 │   │
│ │ [保存配置]                      │   │
│ └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## 四、成本控制方案

### 4.1 成本估算

**DeepSeek 定价**（参考）：
- 输入：¥0.001 / 1K tokens
- 输出：¥0.002 / 1K tokens

**单次分析成本**：
- 输入 tokens：约 1000-1500
- 输出 tokens：约 500-800
- 单次成本：约 ¥0.003-0.005（$0.0004-0.0007）

**日常使用估算**：
- 100 个钱包/天：约 $0.05-0.07
- 1000 个钱包/天：约 $0.50-0.70

**结论**：成本非常低，完全可控！

---

### 4.2 成本优化策略

1. **智能缓存**：
   - 24 小时内不重复分析
   - 只在钱包数据变化时重新分析

2. **按需分析**：
   - 用户查看详情时才触发 AI 分析
   - 榜单定时生成（每天 1-2 次）

3. **批量优化**：
   - 批量分析时复用 Prompt
   - 减少重复内容

4. **优先级控制**：
   - 高分钱包优先分析
   - 低活跃钱包降低分析频率

---

## 五、实施计划

### 阶段1：基础集成（1周）

- [ ] DeepSeek API 客户端开发
- [ ] 数据库表设计和创建
- [ ] 基础 Prompt 工程
- [ ] 单个钱包分析功能

---

### 阶段2：榜单功能（1周）

- [ ] AI 榜单生成逻辑
- [ ] 批量分析优化
- [ ] 缓存机制实现
- [ ] 成本控制实现

---

### 阶段3：前端集成（1周）

- [ ] 钱包详情页 AI 分析区
- [ ] AI 榜单页面
- [ ] Dashboard AI 洞察
- [ ] 后台 AI 配置页面

---

### 阶段4：优化测试（3-5天）

- [ ] Prompt 优化
- [ ] 性能测试
- [ ] 成本测试
- [ ] 用户体验优化

---

## 六、风险与应对

### 风险1：AI 分析质量不稳定

**应对**：
- 多次测试优化 Prompt
- 设置置信度阈值
- 提供"AI 分析仅供参考"提示

---

### 风险2：API 调用失败

**应对**：
- 完善的重试机制
- 降级策略（显示系统评分）
- 错误友好提示

---

### 风险3：成本超支

**应对**：
- 严格的成本控制
- 实时监控和告警
- 达到阈值自动停止

---

## 七、未来扩展

### 扩展1：多模型支持

- 支持 GPT-4、Claude 等
- 模型对比和切换
- 模型组合（投票机制）

---

### 扩展2：AI 训练

- 收集用户反馈
- 微调专属模型
- 提升分析准确度

---

### 扩展3：AI 对话

- 用户可与 AI 对话
- 询问交易策略
- 获取个性化建议

---

## 八、总结

### 核心优势

1. **双重评估**：系统评分 + AI 分析，互补互验
2. **深度洞察**：AI 发现人工难以识别的模式
3. **成本可控**：DeepSeek 价格低廉，日常使用成本极低
4. **灵活可控**：可随时开启/关闭，独立展示
5. **持续进化**：Prompt 可优化，模型可升级

### 实施建议

1. **先做基础**：先完成系统评分和数据库
2. **后加 AI**：作为增值功能逐步添加
3. **小步快跑**：先实现单个钱包分析，再扩展到榜单
4. **用户反馈**：根据实际使用效果迭代优化

---

**这个 AI 扩展功能将让系统更加智能和强大！** 🚀


# Phase 3-4 实现计划

## 📋 概述

本文档详细规划 Phase 3（AI 分析系统）和 Phase 4（前端完善）的实现方案。

---

## 🤖 Phase 3: AI 分析系统

### 1. DeepSeek API 服务

**文件**: `backend/app/services/ai/deepseek_service.py`

**核心功能**:
- ✅ API 连接和认证
- ✅ 请求封装和重试
- ✅ Token 计数和成本计算
- ✅ 错误处理和降级
- ✅ 响应解析

**配置项**:
```python
{
    "enabled": True,
    "api_key": "sk-xxx",
    "api_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
    "max_tokens": 2000,
    "temperature": 0.7,
    "daily_limit": 1000,  # 每日调用限制
    "cost_limit": 10.0,   # 单次费用上限（元）
    "timeout": 30
}
```

**实现要点**:
```python
class DeepSeekService:
    def __init__(self):
        self.config = self._load_config()
        self.usage_stats = {}  # 使用统计
    
    async def chat_completion(
        self,
        messages: List[Dict],
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> Dict:
        """调用 DeepSeek API"""
        # 1. 检查配置
        # 2. 检查限制（每日/成本）
        # 3. 发送请求
        # 4. 记录使用情况
        # 5. 返回结果
        pass
    
    def calculate_cost(self, tokens: int) -> float:
        """计算成本"""
        # DeepSeek 定价（示例）
        # 输入: ¥0.001/1K tokens
        # 输出: ¥0.002/1K tokens
        pass
    
    def check_daily_limit(self) -> bool:
        """检查每日限制"""
        pass
```

### 2. AI 智能分析器

**文件**: `backend/app/services/ai/ai_analyzer.py`

**分析类型**:

#### 2.1 交易风格分析
```python
async def analyze_trading_style(self, wallet_data: Dict) -> Dict:
    """
    分析交易风格
    
    输入: 钱包数据（交易历史、持仓、资金流）
    输出: {
        "style": "激进型/稳健型/保守型",
        "characteristics": ["高频交易", "短线操作"],
        "risk_preference": "高风险偏好",
        "confidence": 0.85
    }
    """
    prompt = f"""
    分析以下交易者的交易风格：
    
    基本信息：
    - 总交易次数：{wallet_data['total_trades']}
    - 平均持仓时间：{wallet_data['avg_holding_time']}
    - 胜率：{wallet_data['win_rate']}%
    - 盈亏比：{wallet_data['profit_loss_ratio']}
    
    交易记录：
    {wallet_data['recent_trades']}
    
    请分析：
    1. 交易风格类型
    2. 主要特征
    3. 风险偏好
    4. 建议
    
    以 JSON 格式返回。
    """
```

#### 2.2 策略识别
```python
async def identify_strategy(self, wallet_data: Dict) -> Dict:
    """
    识别交易策略
    
    输出: {
        "primary_strategy": "趋势跟踪",
        "secondary_strategies": ["网格交易", "套利"],
        "strategy_details": "...",
        "effectiveness": 0.78
    }
    """
```

#### 2.3 风险评估
```python
async def assess_risk(self, wallet_data: Dict) -> Dict:
    """
    风险评估
    
    输出: {
        "risk_level": "中等",
        "risk_factors": ["杠杆使用过高", "集中度风险"],
        "risk_score": 65,
        "suggestions": ["降低杠杆", "分散投资"]
    }
    """
```

#### 2.4 市场趋势分析
```python
async def analyze_market_trend(self, market_data: Dict) -> Dict:
    """
    市场趋势分析
    
    输出: {
        "trend": "上涨/下跌/震荡",
        "strength": 0.75,
        "key_factors": ["成交量增加", "多头占优"],
        "outlook": "短期看涨"
    }
    """
```

### 3. AI 调度系统

**文件**: `backend/app/services/ai/ai_scheduler.py`

**调度策略**:

#### 3.1 优先级管理
```python
class Priority(Enum):
    HIGH = 1    # 高分钱包、异常钱包
    MEDIUM = 2  # 活跃钱包
    LOW = 3     # 普通钱包
```

#### 3.2 智能调度
```python
class AIScheduler:
    def __init__(self):
        self.queue = PriorityQueue()
        self.cache = {}  # 分析结果缓存
        self.running = False
    
    async def schedule_analysis(
        self,
        wallet_address: str,
        analysis_type: str,
        priority: Priority = Priority.MEDIUM
    ):
        """调度分析任务"""
        # 1. 检查缓存
        # 2. 检查限制
        # 3. 加入队列
        pass
    
    async def _process_queue(self):
        """处理队列"""
        while self.running:
            # 1. 从队列取任务
            # 2. 执行分析
            # 3. 保存结果
            # 4. 更新缓存
            pass
    
    def should_analyze(self, wallet_address: str) -> bool:
        """判断是否需要分析"""
        # 1. 检查评分（>= 阈值）
        # 2. 检查缓存（是否过期）
        # 3. 检查成本（是否超限）
        pass
```

#### 3.3 缓存管理
```python
def cache_result(
    self,
    wallet_address: str,
    analysis_type: str,
    result: Dict,
    ttl: int = 86400  # 24小时
):
    """缓存分析结果"""
    db.execute("""
        INSERT OR REPLACE INTO ai_analysis_cache
        (wallet_address, analysis_type, result, created_at, expires_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        wallet_address,
        analysis_type,
        json.dumps(result),
        datetime.now().isoformat(),
        (datetime.now() + timedelta(seconds=ttl)).isoformat()
    ))
```

### 4. AI API

**文件**: `backend/app/api/ai.py`

**端点设计**:
```python
# 分析钱包
POST /api/ai/analyze
{
    "wallet_address": "0x...",
    "analysis_types": ["style", "strategy", "risk"]
}

# 获取分析结果
GET /api/ai/analysis/{wallet_address}

# 批量分析
POST /api/ai/batch-analyze
{
    "wallet_addresses": ["0x...", "0x..."],
    "priority": "high"
}

# AI 使用统计
GET /api/ai/statistics

# AI 配置
GET /api/ai/config
PUT /api/ai/config
```

---

## 🎨 Phase 4: 前端完善

### 1. 系统监控页面

**文件**: `frontend/src/views/admin/SystemMonitor.vue`

**页面布局**:
```
┌─────────────────────────────────────┐
│  系统监控                            │
├─────────────────────────────────────┤
│  健康状态卡片                        │
│  ┌──────┐ ┌──────┐ ┌──────┐        │
│  │ CPU  │ │ 内存 │ │ 磁盘 │        │
│  └──────┘ └──────┘ └──────┘        │
├─────────────────────────────────────┤
│  资源使用图表                        │
│  ┌─────────────────────────────┐   │
│  │   CPU 使用率趋势图           │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │   内存使用率趋势图           │   │
│  └─────────────────────────────┘   │
├─────────────────────────────────────┤
│  详细信息表格                        │
│  - 进程信息                          │
│  - 网络连接                          │
│  - 磁盘 IO                           │
└─────────────────────────────────────┘
```

**核心功能**:
- ✅ 实时数据刷新（WebSocket）
- ✅ 资源使用图表（ECharts）
- ✅ 健康状态指示
- ✅ 告警提示
- ✅ 详细信息展示

**实现要点**:
```vue
<template>
  <div class="system-monitor">
    <!-- 健康状态卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <el-statistic title="CPU 使用率" :value="cpuUsage" suffix="%">
            <template #prefix>
              <el-icon :color="getCpuColor()"><Cpu /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <!-- 更多卡片... -->
    </el-row>
    
    <!-- 图表 -->
    <el-card>
      <v-chart :option="cpuChartOption" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { wsClient } from '@/utils/websocket'
import apiClient from '@/api/auth'

const cpuUsage = ref(0)
const memoryUsage = ref(0)

// 加载数据
const loadMetrics = async () => {
  const response = await apiClient.get('/api/monitoring/system')
  if (response.success) {
    cpuUsage.value = response.data.cpu.usage_percent
    memoryUsage.value = response.data.memory.percent
  }
}

// 实时更新
onMounted(() => {
  loadMetrics()
  // 订阅实时更新
  wsClient.subscribe('system_metrics', (data) => {
    cpuUsage.value = data.cpu
    memoryUsage.value = data.memory
  })
})
</script>
```

### 2. 仪表盘优化

**文件**: `frontend/src/views/Dashboard.vue`

**优化内容**:

#### 2.1 数据概览卡片
```vue
<el-row :gutter="20">
  <el-col :span="6">
    <el-card class="stat-card">
      <el-statistic title="总钱包数" :value="totalWallets">
        <template #prefix>
          <el-icon><Wallet /></el-icon>
        </template>
      </el-statistic>
      <div class="stat-trend">
        <el-icon color="#67c23a"><CaretTop /></el-icon>
        <span>+12% 较昨日</span>
      </div>
    </el-card>
  </el-col>
  <!-- 更多卡片... -->
</el-row>
```

#### 2.2 趋势图表
```vue
<el-card>
  <template #header>
    <span>钱包增长趋势</span>
    <el-radio-group v-model="timeRange">
      <el-radio-button label="7d">7天</el-radio-button>
      <el-radio-button label="30d">30天</el-radio-button>
      <el-radio-button label="90d">90天</el-radio-button>
    </el-radio-group>
  </template>
  <v-chart :option="trendChartOption" />
</el-card>
```

#### 2.3 快捷操作
```vue
<el-card>
  <template #header>快捷操作</template>
  <el-space wrap>
    <el-button type="primary" @click="goToImport">
      <el-icon><Upload /></el-icon>
      批量导入
    </el-button>
    <el-button @click="goToMonitor">
      <el-icon><Monitor /></el-icon>
      系统监控
    </el-button>
    <!-- 更多按钮... -->
  </el-space>
</el-card>
```

### 3. AI 分析页面

**文件**: `frontend/src/views/admin/AIAnalysis.vue`

**页面功能**:
- ✅ 选择钱包进行分析
- ✅ 选择分析类型
- ✅ 显示分析进度
- ✅ 展示分析结果
- ✅ AI 使用统计

**布局**:
```vue
<template>
  <div class="ai-analysis">
    <!-- 分析配置 -->
    <el-card>
      <el-form>
        <el-form-item label="选择钱包">
          <el-select v-model="selectedWallet">
            <el-option
              v-for="wallet in wallets"
              :key="wallet.address"
              :label="wallet.address"
              :value="wallet.address"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="分析类型">
          <el-checkbox-group v-model="analysisTypes">
            <el-checkbox label="style">交易风格</el-checkbox>
            <el-checkbox label="strategy">策略识别</el-checkbox>
            <el-checkbox label="risk">风险评估</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="startAnalysis">
            开始分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 分析结果 -->
    <el-card v-if="analysisResult">
      <template #header>分析结果</template>
      <div v-for="(result, type) in analysisResult" :key="type">
        <h3>{{ getTypeName(type) }}</h3>
        <pre>{{ JSON.stringify(result, null, 2) }}</pre>
      </div>
    </el-card>
    
    <!-- AI 统计 -->
    <el-card>
      <template #header>AI 使用统计</template>
      <el-descriptions :column="3">
        <el-descriptions-item label="今日调用">
          {{ aiStats.today_calls }}
        </el-descriptions-item>
        <el-descriptions-item label="今日费用">
          ¥{{ aiStats.today_cost }}
        </el-descriptions-item>
        <el-descriptions-item label="剩余额度">
          {{ aiStats.remaining_quota }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>
```

---

## 📝 实现步骤

### 第一阶段：AI 基础服务（1-2天）
1. ✅ 创建 DeepSeek API 服务
2. ✅ 实现 API 调用和错误处理
3. ✅ 实现成本计算和限制
4. ✅ 测试 API 连接

### 第二阶段：AI 分析功能（2-3天）
1. ✅ 实现交易风格分析
2. ✅ 实现策略识别
3. ✅ 实现风险评估
4. ✅ 设计提示词模板
5. ✅ 测试分析效果

### 第三阶段：AI 调度系统（1-2天）
1. ✅ 实现任务队列
2. ✅ 实现优先级管理
3. ✅ 实现缓存机制
4. ✅ 实现成本控制
5. ✅ 测试调度逻辑

### 第四阶段：AI API（1天）
1. ✅ 创建 AI API 端点
2. ✅ 实现请求验证
3. ✅ 实现响应格式化
4. ✅ 测试 API

### 第五阶段：前端监控页面（2-3天）
1. ✅ 创建系统监控页面
2. ✅ 实现实时数据更新
3. ✅ 实现图表展示
4. ✅ 实现告警提示
5. ✅ 测试页面功能

### 第六阶段：前端仪表盘优化（1-2天）
1. ✅ 优化数据卡片
2. ✅ 添加趋势图表
3. ✅ 添加快捷操作
4. ✅ 优化布局和样式

### 第七阶段：AI 分析页面（2-3天）
1. ✅ 创建 AI 分析页面
2. ✅ 实现钱包选择
3. ✅ 实现分析配置
4. ✅ 实现结果展示
5. ✅ 实现统计展示

---

## 🧪 测试计划

### AI 系统测试
```bash
# 测试 DeepSeek API
python test_deepseek.py

# 测试 AI 分析
python test_ai_analysis.py

# 测试 AI 调度
python test_ai_scheduler.py
```

### 前端测试
```bash
# 启动开发服务器
npm run dev

# 测试页面
- 系统监控页面
- 仪表盘
- AI 分析页面
```

---

## 📊 预期成果

### AI 分析系统
- ✅ 完整的 DeepSeek API 集成
- ✅ 4 种智能分析功能
- ✅ 智能调度和缓存
- ✅ 成本控制和统计
- ✅ 完整的 API

### 前端完善
- ✅ 系统监控页面（实时监控）
- ✅ 仪表盘优化（数据可视化）
- ✅ AI 分析页面（智能分析）
- ✅ 更好的用户体验

---

## 💰 成本估算

### DeepSeek API 成本
- 输入: ¥0.001/1K tokens
- 输出: ¥0.002/1K tokens
- 单次分析: ~2000 tokens
- 单次成本: ~¥0.004
- 每日 1000 次: ~¥4

### 开发时间
- AI 系统: 5-7 天
- 前端完善: 5-7 天
- 总计: 10-14 天

---

## 🎯 下一步行动

**立即开始**:
1. 创建 DeepSeek API 服务
2. 实现基础的 AI 分析功能
3. 创建系统监控页面
4. 优化仪表盘

**需要的信息**:
- DeepSeek API Key（需要申请）
- API 定价信息（确认成本）
- 分析需求细化（具体分析什么）

**准备好开始了吗？** 🚀


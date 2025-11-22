<template>
  <div class="ai-analysis">
    <el-page-header @back="goBack" title="返回" content="AI 智能分析" />
    
    <!-- AI 配置状态 -->
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>AI 服务状态</span>
          <el-tag :type="aiConfig.enabled ? 'success' : 'danger'">
            {{ aiConfig.enabled ? '已启用' : '已禁用' }}
          </el-tag>
        </div>
      </template>
      
      <el-descriptions :column="3" border>
        <el-descriptions-item label="服务商">
          {{ aiConfig.provider || 'DeepSeek' }}
        </el-descriptions-item>
        <el-descriptions-item label="模型">
          {{ aiConfig.model || 'deepseek-chat' }}
        </el-descriptions-item>
        <el-descriptions-item label="每日限制">
          {{ aiConfig.daily_limit || 1000 }} 次
        </el-descriptions-item>
        <el-descriptions-item label="今日调用">
          {{ aiStats.today.calls }} 次
        </el-descriptions-item>
        <el-descriptions-item label="今日成本">
          ¥{{ aiStats.today.cost }}
        </el-descriptions-item>
        <el-descriptions-item label="剩余额度">
          {{ aiStats.limits.remaining }} 次
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
    
    <!-- 分析表单 -->
    <el-card class="analysis-form-card">
      <template #header>
        <span>开始分析</span>
      </template>
      
      <el-form :model="analysisForm" label-width="120px">
        <el-form-item label="选择钱包">
          <el-select
            v-model="analysisForm.wallet_address"
            filterable
            remote
            reserve-keyword
            placeholder="输入钱包地址搜索"
            :remote-method="searchWallets"
            :loading="walletLoading"
            style="width: 100%"
          >
            <el-option
              v-for="wallet in walletOptions"
              :key="wallet.address"
              :label="`${wallet.address} (评分: ${wallet.score})`"
              :value="wallet.address"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="分析类型">
          <el-checkbox-group v-model="analysisForm.analysis_types">
            <el-checkbox label="style">交易风格分析</el-checkbox>
            <el-checkbox label="strategy">策略识别</el-checkbox>
            <el-checkbox label="risk">风险评估</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="优先级">
          <el-radio-group v-model="analysisForm.priority">
            <el-radio label="high">高</el-radio>
            <el-radio label="medium">中</el-radio>
            <el-radio label="low">低</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="强制分析">
          <el-switch v-model="analysisForm.force" />
          <span class="form-tip">（忽略缓存，重新分析）</span>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="analyzing"
            :disabled="!analysisForm.wallet_address || analysisForm.analysis_types.length === 0"
            @click="startAnalysis"
          >
            开始分析
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 分析结果 -->
    <el-card v-if="analysisResult" class="result-card">
      <template #header>
        <div class="card-header">
          <span>分析结果</span>
          <el-button size="small" @click="clearResult">清除</el-button>
        </div>
      </template>
      
      <!-- 交易风格 -->
      <div v-if="analysisResult.style" class="result-section">
        <h3>
          <el-icon><TrendCharts /></el-icon>
          交易风格分析
        </h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="风格类型">
            <el-tag type="primary">{{ analysisResult.style.style }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="风险偏好">
            {{ analysisResult.style.risk_preference }}
          </el-descriptions-item>
          <el-descriptions-item label="主要特征" :span="2">
            <el-space wrap>
              <el-tag
                v-for="(char, idx) in analysisResult.style.characteristics"
                :key="idx"
                type="info"
              >
                {{ char }}
              </el-tag>
            </el-space>
          </el-descriptions-item>
          <el-descriptions-item label="详细描述" :span="2">
            {{ analysisResult.style.description }}
          </el-descriptions-item>
          <el-descriptions-item label="置信度">
            <el-progress
              :percentage="Math.round(analysisResult.style.confidence * 100)"
              :color="getConfidenceColor(analysisResult.style.confidence)"
            />
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- 策略识别 -->
      <div v-if="analysisResult.strategy" class="result-section">
        <h3>
          <el-icon><DataAnalysis /></el-icon>
          策略识别
        </h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="主要策略">
            <el-tag type="success">{{ analysisResult.strategy.primary_strategy }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="有效性">
            <el-progress
              :percentage="Math.round(analysisResult.strategy.effectiveness * 100)"
              :color="getEffectivenessColor(analysisResult.strategy.effectiveness)"
            />
          </el-descriptions-item>
          <el-descriptions-item v-if="analysisResult.strategy.secondary_strategies" label="辅助策略" :span="2">
            <el-space wrap>
              <el-tag
                v-for="(strategy, idx) in analysisResult.strategy.secondary_strategies"
                :key="idx"
                type="info"
              >
                {{ strategy }}
              </el-tag>
            </el-space>
          </el-descriptions-item>
          <el-descriptions-item label="策略说明" :span="2">
            {{ analysisResult.strategy.strategy_details }}
          </el-descriptions-item>
          <el-descriptions-item v-if="analysisResult.strategy.suggestions" label="改进建议" :span="2">
            <ul class="suggestions-list">
              <li v-for="(suggestion, idx) in analysisResult.strategy.suggestions" :key="idx">
                {{ suggestion }}
              </li>
            </ul>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- 风险评估 -->
      <div v-if="analysisResult.risk" class="result-section">
        <h3>
          <el-icon><Warning /></el-icon>
          风险评估
        </h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="风险等级">
            <el-tag :type="getRiskLevelType(analysisResult.risk.risk_level)">
              {{ analysisResult.risk.risk_level }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="风险评分">
            <el-progress
              :percentage="analysisResult.risk.risk_score"
              :color="getRiskScoreColor(analysisResult.risk.risk_score)"
            />
          </el-descriptions-item>
          <el-descriptions-item v-if="analysisResult.risk.risk_factors" label="风险因素" :span="2">
            <el-space wrap>
              <el-tag
                v-for="(factor, idx) in analysisResult.risk.risk_factors"
                :key="idx"
                type="danger"
              >
                {{ factor }}
              </el-tag>
            </el-space>
          </el-descriptions-item>
          <el-descriptions-item v-if="analysisResult.risk.strengths" label="优势" :span="2">
            <el-space wrap>
              <el-tag
                v-for="(strength, idx) in analysisResult.risk.strengths"
                :key="idx"
                type="success"
              >
                {{ strength }}
              </el-tag>
            </el-space>
          </el-descriptions-item>
          <el-descriptions-item v-if="analysisResult.risk.weaknesses" label="劣势" :span="2">
            <el-space wrap>
              <el-tag
                v-for="(weakness, idx) in analysisResult.risk.weaknesses"
                :key="idx"
                type="warning"
              >
                {{ weakness }}
              </el-tag>
            </el-space>
          </el-descriptions-item>
          <el-descriptions-item v-if="analysisResult.risk.suggestions" label="风控建议" :span="2">
            <ul class="suggestions-list">
              <li v-for="(suggestion, idx) in analysisResult.risk.suggestions" :key="idx">
                {{ suggestion }}
              </li>
            </ul>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
    
    <!-- 任务队列状态 -->
    <el-card class="queue-card">
      <template #header>
        <div class="card-header">
          <span>任务队列</span>
          <el-button size="small" @click="loadQueueStatus">刷新</el-button>
        </div>
      </template>
      
      <el-descriptions :column="3" border>
        <el-descriptions-item label="队列大小">
          {{ queueStatus.queue_size || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="已完成任务">
          {{ queueStatus.completed_tasks || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="运行状态">
          <el-tag :type="queueStatus.running ? 'success' : 'danger'">
            {{ queueStatus.running ? '运行中' : '已停止' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      
      <div v-if="queueStatus.current_task" class="current-task">
        <h4>当前任务</h4>
        <p>钱包: {{ queueStatus.current_task.wallet_address }}</p>
        <p>类型: {{ queueStatus.current_task.analysis_types.join(', ') }}</p>
        <p>优先级: {{ queueStatus.current_task.priority }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { TrendCharts, DataAnalysis, Warning } from '@element-plus/icons-vue'
import apiClient from '@/api/auth'

const router = useRouter()

// 数据
const aiConfig = ref({})
const aiStats = ref({
  today: { calls: 0, cost: 0 },
  limits: { remaining: 0 }
})

const analysisForm = ref({
  wallet_address: '',
  analysis_types: ['style', 'strategy', 'risk'],
  priority: 'medium',
  force: false
})

const walletOptions = ref([])
const walletLoading = ref(false)
const analyzing = ref(false)
const analysisResult = ref(null)
const queueStatus = ref({})

// 方法
const goBack = () => {
  router.back()
}

const loadAIConfig = async () => {
  try {
    const res = await apiClient.get('/api/ai/config')
    if (res.success) {
      aiConfig.value = res.data
    }
  } catch (error) {
    console.error('加载 AI 配置失败:', error)
  }
}

const loadAIStats = async () => {
  try {
    const res = await apiClient.get('/api/ai/statistics')
    if (res.success) {
      aiStats.value = res.data.usage
    }
  } catch (error) {
    console.error('加载 AI 统计失败:', error)
  }
}

const searchWallets = async (query) => {
  if (!query) return
  
  walletLoading.value = true
  try {
    const res = await apiClient.get('/api/wallets', {
      params: {
        search: query,
        page: 1,
        page_size: 10
      }
    })
    
    if (res.success) {
      walletOptions.value = res.data.wallets
    }
  } catch (error) {
    console.error('搜索钱包失败:', error)
  } finally {
    walletLoading.value = false
  }
}

const startAnalysis = async () => {
  analyzing.value = true
  
  try {
    const res = await apiClient.post('/api/ai/analyze', analysisForm.value)
    
    if (res.success) {
      if (res.data.status === 'cached') {
        ElMessage.info('使用缓存结果')
        // 加载缓存结果
        await loadAnalysisResult()
      } else {
        ElMessage.success('分析任务已加入队列')
        // 等待一段时间后加载结果
        setTimeout(async () => {
          await loadAnalysisResult()
        }, 10000)
      }
    }
  } catch (error) {
    ElMessage.error('分析失败: ' + error.message)
  } finally {
    analyzing.value = false
  }
}

const loadAnalysisResult = async () => {
  try {
    const res = await apiClient.get(`/api/ai/analysis/${analysisForm.value.wallet_address}`)
    
    if (res.success && res.data) {
      // 解析结果
      const result = {}
      for (const [type, data] of Object.entries(res.data)) {
        result[type] = data.result
      }
      analysisResult.value = result
    }
  } catch (error) {
    console.error('加载分析结果失败:', error)
  }
}

const loadQueueStatus = async () => {
  try {
    const res = await apiClient.get('/api/ai/queue')
    if (res.success) {
      queueStatus.value = res.data
    }
  } catch (error) {
    console.error('加载队列状态失败:', error)
  }
}

const resetForm = () => {
  analysisForm.value = {
    wallet_address: '',
    analysis_types: ['style', 'strategy', 'risk'],
    priority: 'medium',
    force: false
  }
}

const clearResult = () => {
  analysisResult.value = null
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#67c23a'
  if (confidence >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

const getEffectivenessColor = (effectiveness) => {
  if (effectiveness >= 0.7) return '#67c23a'
  if (effectiveness >= 0.5) return '#e6a23c'
  return '#f56c6c'
}

const getRiskLevelType = (level) => {
  if (level === '低' || level.includes('低')) return 'success'
  if (level === '中' || level.includes('中')) return 'warning'
  return 'danger'
}

const getRiskScoreColor = (score) => {
  if (score <= 40) return '#67c23a'
  if (score <= 70) return '#e6a23c'
  return '#f56c6c'
}

// 生命周期
onMounted(() => {
  loadAIConfig()
  loadAIStats()
  loadQueueStatus()
})
</script>

<style scoped>
.ai-analysis {
  padding: 20px;
}

.config-card,
.analysis-form-card,
.result-card,
.queue-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.result-section {
  margin-bottom: 30px;
}

.result-section:last-child {
  margin-bottom: 0;
}

.result-section h3 {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.suggestions-list {
  margin: 0;
  padding-left: 20px;
}

.suggestions-list li {
  margin-bottom: 5px;
}

.current-task {
  margin-top: 15px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.current-task h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.current-task p {
  margin: 5px 0;
  font-size: 14px;
}
</style>


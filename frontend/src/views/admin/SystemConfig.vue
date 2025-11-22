<template>
  <div class="system-config">
    <el-card>
      <template #header>
        <span>系统配置</span>
      </template>
      
      <el-tabs v-model="activeTab">
        <!-- 基础配置 -->
        <el-tab-pane label="基础配置" name="basic">
          <el-form :model="basicConfig" label-width="150px">
            <el-form-item label="系统名称">
              <el-input v-model="basicConfig.systemName" />
            </el-form-item>
            
            <el-form-item label="数据更新间隔">
              <el-input-number
                v-model="basicConfig.updateInterval"
                :min="5"
                :max="60"
              />
              <span class="form-tip">分钟</span>
            </el-form-item>
            
            <el-form-item label="启用调度器">
              <el-switch v-model="basicConfig.schedulerEnabled" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveBasicConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 评分配置 -->
        <el-tab-pane label="评分配置" name="scoring">
          <el-alert
            title="评分权重配置"
            type="info"
            :closable="false"
            style="margin-bottom: 20px"
          >
            调整各维度的权重，总和应为 100%
          </el-alert>
          
          <el-form :model="scoringConfig" label-width="150px">
            <el-form-item label="盈利能力">
              <el-slider
                v-model="scoringConfig.profitability"
                :max="100"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="风险控制">
              <el-slider
                v-model="scoringConfig.riskControl"
                :max="100"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="交易稳定性">
              <el-slider
                v-model="scoringConfig.stability"
                :max="100"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="交易活跃度">
              <el-slider
                v-model="scoringConfig.activity"
                :max="100"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="资金规模">
              <el-slider
                v-model="scoringConfig.scale"
                :max="100"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="经验水平">
              <el-slider
                v-model="scoringConfig.experience"
                :max="100"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="权重总和">
              <el-tag :type="weightSumType">{{ weightSum }}%</el-tag>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                :disabled="weightSum !== 100"
                @click="saveScoringConfig"
              >
                保存配置
              </el-button>
              <el-button @click="resetScoringConfig">重置为默认</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 通知配置 -->
        <el-tab-pane label="通知配置" name="notification">
          <el-form :model="notificationConfig" label-width="150px">
            <el-divider content-position="left">邮件通知</el-divider>
            
            <el-form-item label="启用邮件通知">
              <el-switch v-model="notificationConfig.email.enabled" />
            </el-form-item>
            
            <template v-if="notificationConfig.email.enabled">
              <el-form-item label="SMTP 服务器">
                <el-input
                  v-model="notificationConfig.email.smtpHost"
                  placeholder="smtp.163.com"
                />
              </el-form-item>
              
              <el-form-item label="SMTP 端口">
                <el-input-number
                  v-model="notificationConfig.email.smtpPort"
                  :min="1"
                  :max="65535"
                />
              </el-form-item>
              
              <el-form-item label="发件人邮箱">
                <el-input
                  v-model="notificationConfig.email.senderEmail"
                  placeholder="your@163.com"
                />
              </el-form-item>
              
              <el-form-item label="邮箱密码/授权码">
                <el-input
                  v-model="notificationConfig.email.senderPassword"
                  type="password"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="收件人邮箱">
                <el-select
                  v-model="notificationConfig.email.recipients"
                  multiple
                  filterable
                  allow-create
                  placeholder="输入邮箱地址后按回车"
                  style="width: 100%"
                />
              </el-form-item>
              
              <el-form-item label="测试邮件">
                <el-button @click="sendTestEmail">发送测试邮件</el-button>
              </el-form-item>
            </template>
            
            <el-divider content-position="left">通知规则</el-divider>
            
            <el-form-item label="导入完成通知">
              <el-switch v-model="notificationConfig.rules.importComplete" />
            </el-form-item>
            
            <el-form-item label="高分钱包通知">
              <el-switch v-model="notificationConfig.rules.highScoreWallet" />
              <el-input-number
                v-if="notificationConfig.rules.highScoreWallet"
                v-model="notificationConfig.rules.highScoreThreshold"
                :min="60"
                :max="100"
                style="margin-left: 10px"
              />
              <span v-if="notificationConfig.rules.highScoreWallet" class="form-tip">分以上</span>
            </el-form-item>
            
            <el-form-item label="异常交易预警">
              <el-switch v-model="notificationConfig.rules.abnormalTrade" />
            </el-form-item>
            
            <el-form-item label="系统错误告警">
              <el-switch v-model="notificationConfig.rules.systemError" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveNotificationConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- AI 配置 -->
        <el-tab-pane label="AI 配置" name="ai">
          <el-form :model="aiConfig" label-width="150px">
            <el-form-item label="启用 AI 分析">
              <el-switch v-model="aiConfig.enabled" />
            </el-form-item>
            
            <template v-if="aiConfig.enabled">
              <el-form-item label="API 提供商">
                <el-select v-model="aiConfig.provider">
                  <el-option label="DeepSeek" value="deepseek" />
                  <el-option label="OpenAI" value="openai" />
                  <el-option label="其他" value="other" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="API Key">
                <el-input
                  v-model="aiConfig.apiKey"
                  type="password"
                  show-password
                  placeholder="请输入 API Key"
                />
              </el-form-item>
              
              <el-form-item label="API 地址">
                <el-input
                  v-model="aiConfig.apiUrl"
                  placeholder="https://api.deepseek.com"
                />
              </el-form-item>
              
              <el-form-item label="每日调用限制">
                <el-input-number
                  v-model="aiConfig.dailyLimit"
                  :min="0"
                  :max="10000"
                />
                <span class="form-tip">次/天，0 表示不限制</span>
              </el-form-item>
              
              <el-form-item label="单次费用上限">
                <el-input-number
                  v-model="aiConfig.costLimit"
                  :min="0"
                  :max="10"
                  :step="0.1"
                  :precision="2"
                />
                <span class="form-tip">元</span>
              </el-form-item>
              
              <el-form-item label="分析阈值">
                <el-input-number
                  v-model="aiConfig.scoreThreshold"
                  :min="60"
                  :max="100"
                />
                <span class="form-tip">只分析评分高于此值的钱包</span>
              </el-form-item>
            </template>
            
            <el-form-item>
              <el-button type="primary" @click="saveAiConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '../../api/auth'

const activeTab = ref('basic')

// 基础配置
const basicConfig = reactive({
  systemName: 'HyperLiquid 钱包分析系统',
  updateInterval: 15,
  schedulerEnabled: true
})

// 评分配置
const scoringConfig = reactive({
  profitability: 30,
  riskControl: 25,
  stability: 20,
  activity: 10,
  scale: 10,
  experience: 5
})

// 通知配置
const notificationConfig = reactive({
  email: {
    enabled: false,
    smtpHost: 'smtp.163.com',
    smtpPort: 465,
    senderEmail: '',
    senderPassword: '',
    recipients: []
  },
  rules: {
    importComplete: true,
    highScoreWallet: true,
    highScoreThreshold: 80,
    abnormalTrade: true,
    systemError: true
  }
})

// AI 配置
const aiConfig = reactive({
  enabled: false,
  provider: 'deepseek',
  apiKey: '',
  apiUrl: 'https://api.deepseek.com',
  dailyLimit: 1000,
  costLimit: 1.0,
  scoreThreshold: 75
})

// 权重总和
const weightSum = computed(() => {
  return Object.values(scoringConfig).reduce((sum, val) => sum + val, 0)
})

const weightSumType = computed(() => {
  return weightSum.value === 100 ? 'success' : 'danger'
})

// 加载配置
const loadConfigs = async () => {
  try {
    const response = await apiClient.get('/api/config/all')
    
    if (response.success) {
      const configs = response.data
      
      // 更新各配置
      if (configs.system) {
        Object.assign(basicConfig, configs.system)
      }
      if (configs.scoring) {
        Object.assign(scoringConfig, configs.scoring.weights || {})
      }
      if (configs.notification) {
        Object.assign(notificationConfig, configs.notification)
      }
      if (configs.ai) {
        Object.assign(aiConfig, configs.ai)
      }
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

// 保存基础配置
const saveBasicConfig = async () => {
  try {
    const response = await apiClient.post('/api/config/system', basicConfig)
    
    if (response.success) {
      ElMessage.success('基础配置保存成功')
    } else {
      ElMessage.error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存基础配置失败:', error)
    ElMessage.error('保存失败')
  }
}

// 保存评分配置
const saveScoringConfig = async () => {
  try {
    const response = await apiClient.post('/api/config/scoring', {
      weights: scoringConfig
    })
    
    if (response.success) {
      ElMessage.success('评分配置保存成功')
    } else {
      ElMessage.error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存评分配置失败:', error)
    ElMessage.error('保存失败')
  }
}

// 重置评分配置
const resetScoringConfig = () => {
  scoringConfig.profitability = 30
  scoringConfig.riskControl = 25
  scoringConfig.stability = 20
  scoringConfig.activity = 10
  scoringConfig.scale = 10
  scoringConfig.experience = 5
  ElMessage.success('已重置为默认配置')
}

// 保存通知配置
const saveNotificationConfig = async () => {
  try {
    const response = await apiClient.post('/api/config/notification', notificationConfig)
    
    if (response.success) {
      ElMessage.success('通知配置保存成功')
    } else {
      ElMessage.error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存通知配置失败:', error)
    ElMessage.error('保存失败')
  }
}

// 发送测试邮件
const sendTestEmail = async () => {
  try {
    const response = await apiClient.post('/api/notifications/test-email', {
      config: notificationConfig.email
    })
    
    if (response.success) {
      ElMessage.success('测试邮件发送成功，请查收')
    } else {
      ElMessage.error(response.message || '发送失败')
    }
  } catch (error) {
    console.error('发送测试邮件失败:', error)
    ElMessage.error('发送失败')
  }
}

// 保存 AI 配置
const saveAiConfig = async () => {
  try {
    const response = await apiClient.post('/api/config/ai', aiConfig)
    
    if (response.success) {
      ElMessage.success('AI 配置保存成功')
    } else {
      ElMessage.error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存 AI 配置失败:', error)
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.system-config {
  padding: 20px;
}

.form-tip {
  margin-left: 10px;
  font-size: 12px;
  color: #999;
}
</style>


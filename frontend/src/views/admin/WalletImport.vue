<template>
  <div class="wallet-import">
    <el-card class="import-card">
      <template #header>
        <div class="card-header">
          <span>批量导入钱包</span>
          <el-button
            v-if="currentTask"
            type="danger"
            size="small"
            @click="cancelImport"
          >
            取消导入
          </el-button>
        </div>
      </template>
      
      <!-- 导入表单 -->
      <div v-if="!currentTask" class="import-form">
        <el-tabs v-model="importType">
          <!-- 文本输入 -->
          <el-tab-pane label="文本输入" name="text">
            <el-input
              v-model="textInput"
              type="textarea"
              :rows="10"
              placeholder="请输入钱包地址，支持多种分隔符：&#10;- 换行&#10;- 逗号&#10;- 分号&#10;- 空格&#10;&#10;示例：&#10;0x1234...abcd&#10;0x5678...efgh"
            />
          </el-tab-pane>
          
          <!-- 文件上传 -->
          <el-tab-pane label="文件上传" name="file">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :limit="1"
              accept=".csv,.txt"
              :on-change="handleFileChange"
              drag
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 CSV 和 TXT 格式，文件大小不超过 10MB
                </div>
              </template>
            </el-upload>
          </el-tab-pane>
        </el-tabs>
        
        <!-- 导入配置 -->
        <el-divider />
        
        <el-form :model="importConfig" label-width="100px">
          <el-form-item label="批次大小">
            <el-input-number
              v-model="importConfig.batchSize"
              :min="10"
              :max="200"
              :step="10"
            />
            <span class="form-tip">每批处理的钱包数量，建议 50-100</span>
          </el-form-item>
          
          <el-form-item label="更新频率">
            <el-radio-group v-model="importConfig.frequency">
              <el-radio label="high">高频（5分钟）</el-radio>
              <el-radio label="normal">普通（15分钟）</el-radio>
              <el-radio label="low">低频（1小时）</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="自动标签">
            <el-checkbox v-model="importConfig.autoTag">
              导入后自动生成系统标签
            </el-checkbox>
          </el-form-item>
        </el-form>
        
        <!-- 地址预览 -->
        <div v-if="parsedAddresses.length > 0" class="address-preview">
          <el-divider />
          <div class="preview-header">
            <span>已识别 {{ parsedAddresses.length }} 个地址</span>
            <el-button size="small" @click="clearAddresses">清空</el-button>
          </div>
          <div class="address-list">
            <el-tag
              v-for="(addr, index) in parsedAddresses.slice(0, 20)"
              :key="index"
              size="small"
              class="address-tag"
            >
              {{ addr }}
            </el-tag>
            <el-tag v-if="parsedAddresses.length > 20" type="info" size="small">
              ...还有 {{ parsedAddresses.length - 20 }} 个
            </el-tag>
          </div>
        </div>
        
        <!-- 开始导入按钮 -->
        <div class="import-actions">
          <el-button
            type="primary"
            size="large"
            :disabled="parsedAddresses.length === 0"
            @click="startImport"
          >
            开始导入 ({{ parsedAddresses.length }} 个地址)
          </el-button>
        </div>
      </div>
      
      <!-- 导入进度 -->
      <div v-else class="import-progress">
        <div class="progress-header">
          <h3>导入进度</h3>
          <el-tag :type="statusType">{{ statusText }}</el-tag>
        </div>
        
        <!-- 总体进度 -->
        <div class="progress-section">
          <div class="progress-label">
            <span>总体进度</span>
            <span class="progress-text">
              {{ currentTask.processed }} / {{ currentTask.total }}
              ({{ currentTask.progress }}%)
            </span>
          </div>
          <el-progress
            :percentage="currentTask.progress"
            :status="progressStatus"
            :stroke-width="20"
          />
        </div>
        
        <!-- 统计信息 -->
        <el-row :gutter="20" class="stats-row">
          <el-col :span="8">
            <el-statistic title="成功" :value="currentTask.success">
              <template #suffix>
                <el-icon color="#67c23a"><SuccessFilled /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="8">
            <el-statistic title="失败" :value="currentTask.failed">
              <template #suffix>
                <el-icon color="#f56c6c"><CircleCloseFilled /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="8">
            <el-statistic title="跳过" :value="currentTask.skipped">
              <template #suffix>
                <el-icon color="#e6a23c"><WarningFilled /></el-icon>
              </template>
            </el-statistic>
          </el-col>
        </el-row>
        
        <!-- 时间信息 -->
        <div class="time-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="已用时间">
              {{ formatTime(currentTask.elapsed_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="预计剩余">
              {{ currentTask.eta ? formatTime(currentTask.eta) : '--' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <!-- 完成后的操作 -->
        <div v-if="isCompleted" class="complete-actions">
          <el-alert
            :type="currentTask.failed > 0 ? 'warning' : 'success'"
            :title="completeMessage"
            :closable="false"
            show-icon
          />
          <div class="action-buttons">
            <el-button type="primary" @click="viewWallets">查看钱包列表</el-button>
            <el-button @click="resetImport">继续导入</el-button>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 导入历史 -->
    <el-card class="history-card">
      <template #header>
        <span>导入历史</span>
      </template>
      
      <el-table :data="importHistory" stripe>
        <el-table-column prop="task_id" label="任务ID" width="120">
          <template #default="{ row }">
            <el-text truncated>{{ row.task_id }}</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="total" label="总数" width="80" />
        <el-table-column prop="success" label="成功" width="80">
          <template #default="{ row }">
            <el-text type="success">{{ row.success }}</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="failed" label="失败" width="80">
          <template #default="{ row }">
            <el-text type="danger">{{ row.failed }}</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'processing'"
              type="text"
              size="small"
              @click="viewTaskProgress(row.task_id)"
            >
              查看进度
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  UploadFilled,
  SuccessFilled,
  CircleCloseFilled,
  WarningFilled
} from '@element-plus/icons-vue'
import { wsClient } from '../../utils/websocket'
import apiClient from '../../api/auth'

const router = useRouter()

// 导入类型
const importType = ref('text')

// 文本输入
const textInput = ref('')

// 文件上传
const uploadRef = ref(null)
const uploadedFile = ref(null)

// 导入配置
const importConfig = reactive({
  batchSize: 50,
  frequency: 'normal',
  autoTag: true
})

// 解析后的地址
const parsedAddresses = ref([])

// 当前导入任务
const currentTask = ref(null)

// 导入历史
const importHistory = ref([])

// 监听文本输入变化
watch(textInput, (value) => {
  if (value) {
    parseAddresses(value)
  } else {
    parsedAddresses.value = []
  }
})

// 解析地址
const parseAddresses = (text) => {
  const regex = /0x[a-fA-F0-9]{40}/g
  const matches = text.match(regex) || []
  parsedAddresses.value = [...new Set(matches)] // 去重
}

// 处理文件变化
const handleFileChange = (file) => {
  uploadedFile.value = file
  
  // 读取文件内容
  const reader = new FileReader()
  reader.onload = (e) => {
    const content = e.target.result
    parseAddresses(content)
  }
  reader.readAsText(file.raw)
}

// 清空地址
const clearAddresses = () => {
  textInput.value = ''
  parsedAddresses.value = []
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 开始导入
const startImport = async () => {
  try {
    const response = await apiClient.post('/api/import/start', {
      addresses: parsedAddresses.value,
      batch_size: importConfig.batchSize,
      frequency: importConfig.frequency,
      auto_tag: importConfig.autoTag
    })
    
    if (response.success) {
      const taskId = response.data.task_id
      currentTask.value = response.data
      
      // 订阅进度更新
      wsClient.subscribe(`import:${taskId}`, handleProgressUpdate)
      
      ElMessage.success('导入任务已启动')
    } else {
      ElMessage.error(response.message || '启动导入失败')
    }
  } catch (error) {
    console.error('启动导入失败:', error)
    ElMessage.error('启动导入失败')
  }
}

// 处理进度更新
const handleProgressUpdate = (data) => {
  if (data.type === 'import_progress') {
    currentTask.value = data.data
  }
}

// 取消导入
const cancelImport = async () => {
  if (!currentTask.value) return
  
  try {
    const response = await apiClient.post(`/api/import/cancel/${currentTask.value.task_id}`)
    
    if (response.success) {
      ElMessage.success('已取消导入')
    }
  } catch (error) {
    console.error('取消导入失败:', error)
  }
}

// 重置导入
const resetImport = () => {
  if (currentTask.value) {
    wsClient.unsubscribe(`import:${currentTask.value.task_id}`)
  }
  currentTask.value = null
  clearAddresses()
  loadImportHistory()
}

// 查看钱包列表
const viewWallets = () => {
  router.push('/wallets')
}

// 查看任务进度
const viewTaskProgress = async (taskId) => {
  try {
    const response = await apiClient.get(`/api/import/progress/${taskId}`)
    
    if (response.success) {
      currentTask.value = response.data
      wsClient.subscribe(`import:${taskId}`, handleProgressUpdate)
    }
  } catch (error) {
    console.error('获取任务进度失败:', error)
  }
}

// 加载导入历史
const loadImportHistory = async () => {
  try {
    const response = await apiClient.get('/api/import/history')
    
    if (response.success) {
      importHistory.value = response.data
    }
  } catch (error) {
    console.error('加载导入历史失败:', error)
  }
}

// 计算属性
const statusType = computed(() => {
  if (!currentTask.value) return 'info'
  
  const status = currentTask.value.status
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'danger'
  if (status === 'cancelled') return 'warning'
  return 'primary'
})

const statusText = computed(() => {
  if (!currentTask.value) return ''
  
  const status = currentTask.value.status
  const statusMap = {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return statusMap[status] || status
})

const progressStatus = computed(() => {
  if (!currentTask.value) return null
  
  const status = currentTask.value.status
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return null
})

const isCompleted = computed(() => {
  return currentTask.value &&
    ['completed', 'failed', 'cancelled'].includes(currentTask.value.status)
})

const completeMessage = computed(() => {
  if (!currentTask.value) return ''
  
  const { total, success, failed, skipped } = currentTask.value
  return `导入完成！总数: ${total}, 成功: ${success}, 失败: ${failed}, 跳过: ${skipped}`
})

// 工具函数
const formatTime = (seconds) => {
  if (!seconds) return '--'
  
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  
  if (h > 0) return `${h}时${m}分${s}秒`
  if (m > 0) return `${m}分${s}秒`
  return `${s}秒`
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '--'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    processing: 'primary',
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

// 生命周期
onMounted(() => {
  loadImportHistory()
})

onUnmounted(() => {
  if (currentTask.value) {
    wsClient.unsubscribe(`import:${currentTask.value.task_id}`)
  }
})
</script>

<style scoped>
.wallet-import {
  padding: 20px;
}

.import-card,
.history-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.import-form {
  padding: 20px 0;
}

.form-tip {
  margin-left: 10px;
  font-size: 12px;
  color: #999;
}

.address-preview {
  margin-top: 20px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.address-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.address-tag {
  font-family: monospace;
  font-size: 12px;
}

.import-actions {
  margin-top: 30px;
  text-align: center;
}

.import-progress {
  padding: 20px 0;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.progress-header h3 {
  margin: 0;
}

.progress-section {
  margin-bottom: 30px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
}

.progress-text {
  color: #606266;
  font-weight: bold;
}

.stats-row {
  margin: 30px 0;
}

.time-info {
  margin: 30px 0;
}

.complete-actions {
  margin-top: 30px;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
}
</style>


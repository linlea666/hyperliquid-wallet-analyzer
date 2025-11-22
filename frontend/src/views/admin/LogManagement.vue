<template>
  <div class="log-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>日志管理</span>
          <div class="header-actions">
            <el-button
              :icon="Refresh"
              @click="loadLogs"
            >
              刷新
            </el-button>
            <el-button
              :icon="Download"
              @click="exportLogs"
            >
              导出
            </el-button>
            <el-button
              :icon="Delete"
              type="danger"
              @click="clearLogs"
            >
              清空日志
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <el-form :model="filterForm" :inline="true" class="filter-form">
        <el-form-item label="日志级别">
          <el-select
            v-model="filterForm.level"
            placeholder="全部"
            clearable
            style="width: 120px"
          >
            <el-option label="DEBUG" value="DEBUG" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
            <el-option label="CRITICAL" value="CRITICAL" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="模块">
          <el-select
            v-model="filterForm.module"
            placeholder="全部"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="module in modules"
              :key="module"
              :label="module"
              :value="module"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="分类">
          <el-select
            v-model="filterForm.category"
            placeholder="全部"
            clearable
            style="width: 150px"
          >
            <el-option label="系统" value="system" />
            <el-option label="业务" value="business" />
            <el-option label="访问" value="access" />
            <el-option label="性能" value="performance" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            style="width: 360px"
          />
        </el-form-item>
        
        <el-form-item label="搜索">
          <el-input
            v-model="filterForm.keyword"
            placeholder="关键词搜索"
            clearable
            style="width: 200px"
            @keyup.enter="loadLogs"
          >
            <template #append>
              <el-button :icon="Search" @click="loadLogs" />
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 实时日志开关 -->
      <div class="realtime-control">
        <el-switch
          v-model="realtimeEnabled"
          active-text="实时日志"
          @change="toggleRealtime"
        />
        <el-tag v-if="realtimeEnabled" type="success" effect="dark">
          <el-icon class="is-loading"><Loading /></el-icon>
          实时更新中
        </el-tag>
      </div>
      
      <!-- 日志表格 -->
      <el-table
        v-loading="loading"
        :data="logs"
        stripe
        :height="tableHeight"
        @row-click="showLogDetail"
      >
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="module" label="模块" width="120" />
        
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag size="small" plain>{{ getCategoryText(row.category) }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="message" label="消息" min-width="300">
          <template #default="{ row }">
            <el-text truncated>{{ row.message }}</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="user_id" label="用户" width="100">
          <template #default="{ row }">
            {{ row.user_id || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="ip_address" label="IP" width="130" />
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadLogs"
        @size-change="loadLogs"
      />
    </el-card>
    
    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="日志详情"
      width="800px"
    >
      <el-descriptions v-if="selectedLog" :column="2" border>
        <el-descriptions-item label="时间">
          {{ formatDateTime(selectedLog.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="级别">
          <el-tag :type="getLevelType(selectedLog.level)">
            {{ selectedLog.level }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="模块">
          {{ selectedLog.module }}
        </el-descriptions-item>
        <el-descriptions-item label="分类">
          {{ getCategoryText(selectedLog.category) }}
        </el-descriptions-item>
        <el-descriptions-item label="用户">
          {{ selectedLog.user_id || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="IP 地址">
          {{ selectedLog.ip_address || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="消息" :span="2">
          {{ selectedLog.message }}
        </el-descriptions-item>
        <el-descriptions-item label="详细信息" :span="2">
          <pre class="log-details">{{ formatDetails(selectedLog.details) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Download,
  Delete,
  Search,
  Loading
} from '@element-plus/icons-vue'
import { wsClient } from '../../utils/websocket'
import apiClient from '../../api/auth'

// 筛选表单
const filterForm = reactive({
  level: '',
  module: '',
  category: '',
  dateRange: [],
  keyword: ''
})

// 模块列表
const modules = ref([
  'api',
  'scheduler',
  'analyzer',
  'database',
  'notification',
  'auth',
  'websocket'
])

// 日志列表
const logs = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 50,
  total: 0
})

// 实时日志
const realtimeEnabled = ref(false)

// 日志详情
const detailDialogVisible = ref(false)
const selectedLog = ref(null)

// 表格高度
const tableHeight = computed(() => {
  return window.innerHeight - 400
})

// 加载日志
const loadLogs = async () => {
  loading.value = true
  
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      level: filterForm.level || undefined,
      module: filterForm.module || undefined,
      category: filterForm.category || undefined,
      keyword: filterForm.keyword || undefined
    }
    
    // 时间范围
    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.start_time = filterForm.dateRange[0].toISOString()
      params.end_time = filterForm.dateRange[1].toISOString()
    }
    
    const response = await apiClient.get('/api/logs', { params })
    
    if (response.success) {
      logs.value = response.data.logs
      pagination.total = response.data.total
    } else {
      ElMessage.error(response.message || '加载日志失败')
    }
  } catch (error) {
    console.error('加载日志失败:', error)
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

// 重置筛选
const resetFilter = () => {
  filterForm.level = ''
  filterForm.module = ''
  filterForm.category = ''
  filterForm.dateRange = []
  filterForm.keyword = ''
  pagination.page = 1
  loadLogs()
}

// 切换实时日志
const toggleRealtime = (enabled) => {
  if (enabled) {
    // 订阅实时日志
    wsClient.subscribe('system_logs', handleRealtimeLog)
    ElMessage.success('已开启实时日志')
  } else {
    // 取消订阅
    wsClient.unsubscribe('system_logs')
    ElMessage.info('已关闭实时日志')
  }
}

// 处理实时日志
const handleRealtimeLog = (data) => {
  if (data.type === 'log') {
    // 添加到列表顶部
    logs.value.unshift(data.data)
    
    // 限制列表长度
    if (logs.value.length > pagination.pageSize) {
      logs.value.pop()
    }
  }
}

// 显示日志详情
const showLogDetail = (row) => {
  selectedLog.value = row
  detailDialogVisible.value = true
}

// 导出日志
const exportLogs = async () => {
  try {
    const params = {
      level: filterForm.level || undefined,
      module: filterForm.module || undefined,
      category: filterForm.category || undefined,
      keyword: filterForm.keyword || undefined
    }
    
    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.start_time = filterForm.dateRange[0].toISOString()
      params.end_time = filterForm.dateRange[1].toISOString()
    }
    
    const response = await apiClient.get('/api/logs/export', {
      params,
      responseType: 'blob'
    })
    
    // 下载文件
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `logs_${Date.now()}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('日志导出成功')
  } catch (error) {
    console.error('导出日志失败:', error)
    ElMessage.error('导出日志失败')
  }
}

// 清空日志
const clearLogs = () => {
  ElMessageBox.confirm(
    '确定要清空所有日志吗？此操作不可恢复！',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await apiClient.delete('/api/logs/clear')
      
      if (response.success) {
        ElMessage.success('日志已清空')
        loadLogs()
      } else {
        ElMessage.error(response.message || '清空失败')
      }
    } catch (error) {
      console.error('清空日志失败:', error)
      ElMessage.error('清空失败')
    }
  }).catch(() => {
    // 取消
  })
}

// 工具函数
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const getLevelType = (level) => {
  const typeMap = {
    DEBUG: 'info',
    INFO: 'success',
    WARNING: 'warning',
    ERROR: 'danger',
    CRITICAL: 'danger'
  }
  return typeMap[level] || 'info'
}

const getCategoryText = (category) => {
  const textMap = {
    system: '系统',
    business: '业务',
    access: '访问',
    performance: '性能'
  }
  return textMap[category] || category
}

const formatDetails = (details) => {
  if (!details) return '-'
  if (typeof details === 'string') return details
  return JSON.stringify(details, null, 2)
}

// 生命周期
onMounted(() => {
  loadLogs()
})

onUnmounted(() => {
  if (realtimeEnabled.value) {
    wsClient.unsubscribe('system_logs')
  }
})
</script>

<style scoped>
.log-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-form {
  margin-bottom: 20px;
}

.realtime-control {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.el-table {
  margin-bottom: 20px;
}

.el-pagination {
  justify-content: center;
}

.log-details {
  max-height: 300px;
  overflow-y: auto;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>


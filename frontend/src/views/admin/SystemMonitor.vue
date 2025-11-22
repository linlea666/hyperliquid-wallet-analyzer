<template>
  <div class="system-monitor">
    <el-page-header @back="goBack" title="返回" content="系统监控" />
    
    <!-- 健康状态卡片 -->
    <el-row :gutter="20" class="status-cards">
      <el-col :span="6">
        <el-card shadow="hover" :class="getCpuStatusClass()">
          <el-statistic title="CPU 使用率" :value="systemMetrics.cpu.usage_percent" suffix="%">
            <template #prefix>
              <el-icon :color="getCpuColor()"><Cpu /></el-icon>
            </template>
          </el-statistic>
          <div class="metric-detail">
            核心数: {{ systemMetrics.cpu.count }}
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" :class="getMemoryStatusClass()">
          <el-statistic title="内存使用率" :value="systemMetrics.memory.percent" suffix="%">
            <template #prefix>
              <el-icon :color="getMemoryColor()"><Memo /></el-icon>
            </template>
          </el-statistic>
          <div class="metric-detail">
            {{ formatBytes(systemMetrics.memory.used) }} / {{ formatBytes(systemMetrics.memory.total) }}
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" :class="getDiskStatusClass()">
          <el-statistic title="磁盘使用率" :value="systemMetrics.disk.percent" suffix="%">
            <template #prefix>
              <el-icon :color="getDiskColor()"><Document /></el-icon>
            </template>
          </el-statistic>
          <div class="metric-detail">
            {{ formatBytes(systemMetrics.disk.used) }} / {{ formatBytes(systemMetrics.disk.total) }}
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="网络连接数" :value="systemMetrics.network.connections">
            <template #prefix>
              <el-icon color="#409eff"><Connection /></el-icon>
            </template>
          </el-statistic>
          <div class="metric-detail">
            活跃: {{ systemMetrics.network.active_connections }}
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 资源使用趋势图表 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>CPU 使用率趋势</span>
          </template>
          <v-chart :option="cpuChartOption" style="height: 300px;" />
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>内存使用率趋势</span>
          </template>
          <v-chart :option="memoryChartOption" style="height: 300px;" />
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 进程信息 -->
    <el-card class="process-card">
      <template #header>
        <span>进程信息</span>
      </template>
      
      <el-descriptions :column="3" border>
        <el-descriptions-item label="进程 ID">
          {{ processInfo.pid }}
        </el-descriptions-item>
        <el-descriptions-item label="CPU 使用率">
          {{ processInfo.cpu_percent }}%
        </el-descriptions-item>
        <el-descriptions-item label="内存使用">
          {{ formatBytes(processInfo.memory_mb * 1024 * 1024) }}
        </el-descriptions-item>
        <el-descriptions-item label="线程数">
          {{ processInfo.threads }}
        </el-descriptions-item>
        <el-descriptions-item label="运行时间">
          {{ formatDuration(processInfo.uptime_seconds) }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag type="success">运行中</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
    
    <!-- 数据库信息 -->
    <el-card class="database-card">
      <template #header>
        <span>数据库信息</span>
      </template>
      
      <el-descriptions :column="3" border>
        <el-descriptions-item label="数据库大小">
          {{ formatBytes(databaseMetrics.size_mb * 1024 * 1024) }}
        </el-descriptions-item>
        <el-descriptions-item label="钱包数">
          {{ databaseMetrics.wallet_count }}
        </el-descriptions-item>
        <el-descriptions-item label="交易记录数">
          {{ databaseMetrics.trade_count }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
    
    <!-- 业务指标 -->
    <el-card class="business-card">
      <template #header>
        <span>业务指标</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="活跃钱包数" :value="businessMetrics.active_wallets" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="今日数据采集" :value="businessMetrics.today_collections" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="AI 调用次数" :value="businessMetrics.ai_calls" />
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Cpu, Memo, Document, Connection } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import apiClient from '@/api/auth'

const router = useRouter()

// 数据
const systemMetrics = ref({
  cpu: { usage_percent: 0, count: 0 },
  memory: { percent: 0, used: 0, total: 0 },
  disk: { percent: 0, used: 0, total: 0 },
  network: { connections: 0, active_connections: 0 }
})

const processInfo = ref({
  pid: 0,
  cpu_percent: 0,
  memory_mb: 0,
  threads: 0,
  uptime_seconds: 0
})

const databaseMetrics = ref({
  size_mb: 0,
  wallet_count: 0,
  trade_count: 0
})

const businessMetrics = ref({
  active_wallets: 0,
  today_collections: 0,
  ai_calls: 0
})

// 历史数据（用于图表）
const cpuHistory = ref([])
const memoryHistory = ref([])
const timeLabels = ref([])

// 定时器
let refreshTimer = null

// 图表配置
const cpuChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: timeLabels.value
  },
  yAxis: {
    type: 'value',
    max: 100,
    axisLabel: {
      formatter: '{value}%'
    }
  },
  series: [{
    name: 'CPU 使用率',
    type: 'line',
    smooth: true,
    data: cpuHistory.value,
    areaStyle: {
      color: {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [{
          offset: 0,
          color: 'rgba(64, 158, 255, 0.5)'
        }, {
          offset: 1,
          color: 'rgba(64, 158, 255, 0.1)'
        }]
      }
    }
  }]
}))

const memoryChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: timeLabels.value
  },
  yAxis: {
    type: 'value',
    max: 100,
    axisLabel: {
      formatter: '{value}%'
    }
  },
  series: [{
    name: '内存使用率',
    type: 'line',
    smooth: true,
    data: memoryHistory.value,
    areaStyle: {
      color: {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [{
          offset: 0,
          color: 'rgba(103, 194, 58, 0.5)'
        }, {
          offset: 1,
          color: 'rgba(103, 194, 58, 0.1)'
        }]
      }
    }
  }]
}))

// 方法
const goBack = () => {
  router.back()
}

const loadMetrics = async () => {
  try {
    // 加载系统指标
    const systemRes = await apiClient.get('/api/monitoring/system')
    if (systemRes.success) {
      systemMetrics.value = systemRes.data
      
      // 更新历史数据
      const now = new Date()
      const timeStr = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`
      
      cpuHistory.value.push(systemRes.data.cpu.usage_percent)
      memoryHistory.value.push(systemRes.data.memory.percent)
      timeLabels.value.push(timeStr)
      
      // 限制历史数据长度
      if (cpuHistory.value.length > 20) {
        cpuHistory.value.shift()
        memoryHistory.value.shift()
        timeLabels.value.shift()
      }
    }
    
    // 加载进程信息
    const processRes = await apiClient.get('/api/monitoring/process')
    if (processRes.success) {
      processInfo.value = processRes.data
    }
    
    // 加载数据库指标
    const dbRes = await apiClient.get('/api/monitoring/database')
    if (dbRes.success) {
      databaseMetrics.value = dbRes.data
    }
    
    // 加载业务指标
    const businessRes = await apiClient.get('/api/monitoring/business')
    if (businessRes.success) {
      businessMetrics.value = businessRes.data
    }
    
  } catch (error) {
    console.error('加载监控数据失败:', error)
  }
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

const formatDuration = (seconds) => {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) {
    return `${days}天 ${hours}小时`
  } else if (hours > 0) {
    return `${hours}小时 ${minutes}分钟`
  } else {
    return `${minutes}分钟`
  }
}

const getCpuColor = () => {
  const usage = systemMetrics.value.cpu.usage_percent
  if (usage >= 80) return '#f56c6c'
  if (usage >= 60) return '#e6a23c'
  return '#67c23a'
}

const getMemoryColor = () => {
  const usage = systemMetrics.value.memory.percent
  if (usage >= 80) return '#f56c6c'
  if (usage >= 60) return '#e6a23c'
  return '#67c23a'
}

const getDiskColor = () => {
  const usage = systemMetrics.value.disk.percent
  if (usage >= 80) return '#f56c6c'
  if (usage >= 60) return '#e6a23c'
  return '#67c23a'
}

const getCpuStatusClass = () => {
  const usage = systemMetrics.value.cpu.usage_percent
  if (usage >= 80) return 'status-danger'
  if (usage >= 60) return 'status-warning'
  return 'status-normal'
}

const getMemoryStatusClass = () => {
  const usage = systemMetrics.value.memory.percent
  if (usage >= 80) return 'status-danger'
  if (usage >= 60) return 'status-warning'
  return 'status-normal'
}

const getDiskStatusClass = () => {
  const usage = systemMetrics.value.disk.percent
  if (usage >= 80) return 'status-danger'
  if (usage >= 60) return 'status-warning'
  return 'status-normal'
}

// 生命周期
onMounted(() => {
  loadMetrics()
  
  // 每 5 秒刷新一次
  refreshTimer = setInterval(() => {
    loadMetrics()
  }, 5000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.system-monitor {
  padding: 20px;
}

.status-cards {
  margin-top: 20px;
}

.metric-detail {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.status-normal {
  border-left: 3px solid #67c23a;
}

.status-warning {
  border-left: 3px solid #e6a23c;
}

.status-danger {
  border-left: 3px solid #f56c6c;
}

.charts-row {
  margin-top: 20px;
}

.process-card,
.database-card,
.business-card {
  margin-top: 20px;
}

:deep(.el-statistic__head) {
  font-size: 14px;
  color: #909399;
}

:deep(.el-statistic__number) {
  font-size: 28px;
  font-weight: bold;
}
</style>


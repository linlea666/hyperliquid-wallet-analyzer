<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>多空比统计</span>
          </template>
          <div v-if="longShortRatio">
            <div>多头: {{ longShortRatio.long_ratio.toFixed(2) }}%</div>
            <div>空头: {{ longShortRatio.short_ratio.toFixed(2) }}%</div>
          </div>
          <div v-else>加载中...</div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>钱包异动</span>
          </template>
          <el-table :data="anomalies" style="width: 100%">
            <el-table-column prop="type" label="类型" width="120" />
            <el-table-column prop="wallet" label="钱包" width="150">
              <template #default="{ row }">
                {{ row.wallet.substring(0, 10) }}...
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const stats = ref([
  { label: '钱包总数', value: 0 },
  { label: '总资产', value: '$0' },
  { label: '总盈亏', value: '$0' },
  { label: '平均 ROI', value: '0%' }
])

const longShortRatio = ref(null)
const anomalies = ref([])

const loadDashboardData = async () => {
  try {
    // 加载统计数据
    const statsData = await api.get('/dashboard/stats')
    stats.value = [
      { label: '钱包总数', value: statsData.total_wallets || 0 },
      { label: '总资产', value: `$${(statsData.total_balance || 0).toFixed(2)}` },
      { label: '总盈亏', value: `$${(statsData.total_pnl || 0).toFixed(2)}` },
      { label: '平均 ROI', value: `${(statsData.avg_roi || 0).toFixed(2)}%` }
    ]

    // 加载多空比
    const ratioData = await api.get('/dashboard/long-short-ratio')
    longShortRatio.value = ratioData

    // 加载异动
    const anomalyData = await api.get('/dashboard/anomalies')
    anomalies.value = anomalyData.anomalies || []
  } catch (error) {
    console.error('加载看板数据失败:', error)
  }
}

onMounted(() => {
  loadDashboardData()
  // 每30秒刷新一次
  setInterval(loadDashboardData, 30000)
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}
</style>


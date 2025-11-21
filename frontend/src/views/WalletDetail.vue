<template>
  <div class="wallet-detail" v-if="wallet">
    <el-card>
      <template #header>
        <div class="header-content">
          <span>钱包详情</span>
          <el-button @click="refreshWallet" :loading="refreshing">刷新</el-button>
        </div>
      </template>

      <div class="wallet-info">
        <h2>{{ wallet.address }}</h2>
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="6">
            <div class="metric">
              <div class="metric-label">总盈亏</div>
              <div class="metric-value" :style="{ color: wallet.metrics.total_pnl >= 0 ? 'green' : 'red' }">
                ${{ wallet.metrics.total_pnl.toFixed(2) }}
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric">
              <div class="metric-label">ROI</div>
              <div class="metric-value" :style="{ color: wallet.metrics.roi >= 0 ? 'green' : 'red' }">
                {{ wallet.metrics.roi.toFixed(2) }}%
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric">
              <div class="metric-label">胜率</div>
              <div class="metric-value">
                {{ (wallet.metrics.win_rate * 100).toFixed(2) }}%
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric">
              <div class="metric-label">Smart Money Score</div>
              <div class="metric-value">
                {{ wallet.metrics.smart_money_score }}
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <span>交易历史</span>
      </template>
      <el-table :data="wallet.trades" style="width: 100%">
        <el-table-column prop="symbol" label="币种" width="100" />
        <el-table-column prop="side" label="方向" width="80">
          <template #default="{ row }">
            <el-tag :type="row.side === 'long' ? 'success' : 'danger'">
              {{ row.side === 'long' ? '多' : '空' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pnl" label="盈亏" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.pnl >= 0 ? 'green' : 'red' }">
              ${{ row.pnl.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="数量" width="100" />
        <el-table-column prop="entry_price" label="开仓价" width="120" />
        <el-table-column prop="exit_price" label="平仓价" width="120" />
      </el-table>
    </el-card>
  </div>
  <div v-else class="loading">
    <el-loading />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const route = useRoute()
const wallet = ref(null)
const refreshing = ref(false)

const loadWallet = async () => {
  try {
    const address = route.params.address
    wallet.value = await api.get(`/wallets/${address}`)
  } catch (error) {
    ElMessage.error('加载钱包详情失败')
    console.error(error)
  }
}

const refreshWallet = async () => {
  refreshing.value = true
  try {
    const address = route.params.address
    await api.post(`/wallets/${address}/refresh`)
    ElMessage.success('刷新成功')
    await loadWallet()
  } catch (error) {
    ElMessage.error('刷新失败')
    console.error(error)
  } finally {
    refreshing.value = false
  }
}

onMounted(() => {
  loadWallet()
})
</script>

<style scoped>
.wallet-detail {
  max-width: 1400px;
  margin: 0 auto;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.wallet-info h2 {
  font-size: 18px;
  margin-bottom: 10px;
}

.metric {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.metric-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
}
</style>


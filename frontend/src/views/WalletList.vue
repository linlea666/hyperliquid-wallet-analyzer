<template>
  <div class="wallet-list">
    <el-card>
      <template #header>
        <div class="header-actions">
          <span>钱包列表</span>
          <el-button type="primary" @click="showImportDialog = true">
            <el-icon><Plus /></el-icon>
            导入钱包
          </el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="8">
          <el-input
            v-model="search"
            placeholder="搜索钱包地址"
            clearable
            @input="loadWallets"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="sortBy" placeholder="排序" @change="loadWallets">
            <el-option label="Smart Money Score" value="score" />
            <el-option label="ROI" value="roi" />
            <el-option label="胜率" value="win_rate" />
            <el-option label="总盈亏" value="total_pnl" />
          </el-select>
        </el-col>
      </el-row>

      <!-- 钱包列表 -->
      <el-table :data="wallets" v-loading="loading" style="width: 100%">
        <el-table-column prop="address" label="钱包地址" width="200">
          <template #default="{ row }">
            {{ row.address.substring(0, 10) }}...{{ row.address.substring(row.address.length - 8) }}
          </template>
        </el-table-column>
        <el-table-column prop="metrics.roi" label="ROI" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.metrics.roi >= 0 ? 'green' : 'red' }">
              {{ row.metrics.roi.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="metrics.total_pnl" label="总盈亏" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.metrics.total_pnl >= 0 ? 'green' : 'red' }">
              ${{ row.metrics.total_pnl.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="metrics.win_rate" label="胜率" width="100">
          <template #default="{ row }">
            {{ (row.metrics.win_rate * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="metrics.smart_money_score" label="Smart Money Score" width="150" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewWallet(row.address)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadWallets"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入钱包" width="500px">
      <el-input
        v-model="importAddresses"
        type="textarea"
        :rows="5"
        placeholder="请输入钱包地址，每行一个"
      />
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="importWallets" :loading="importing">
          导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()

const wallets = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const search = ref('')
const sortBy = ref('score')

const showImportDialog = ref(false)
const importAddresses = ref('')
const importing = ref(false)

const loadWallets = async () => {
  loading.value = true
  try {
    const data = await api.get('/wallets', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        sort_by: sortBy.value,
        order: 'desc',
        search: search.value || undefined
      }
    })
    wallets.value = data.wallets || []
    total.value = data.total || 0
  } catch (error) {
    ElMessage.error('加载钱包列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const importWallets = async () => {
  if (!importAddresses.value.trim()) {
    ElMessage.warning('请输入钱包地址')
    return
  }

  importing.value = true
  try {
    const addresses = importAddresses.value
      .split('\n')
      .map(addr => addr.trim())
      .filter(addr => addr)

    const result = await api.post('/wallets/import', {
      addresses
    })

    ElMessage.success(`成功导入 ${result.success.length} 个钱包`)
    showImportDialog.value = false
    importAddresses.value = ''
    loadWallets()
  } catch (error) {
    ElMessage.error('导入钱包失败')
    console.error(error)
  } finally {
    importing.value = false
  }
}

const viewWallet = (address) => {
  router.push(`/wallets/${address}`)
}

onMounted(() => {
  loadWallets()
})
</script>

<style scoped>
.wallet-list {
  max-width: 1400px;
  margin: 0 auto;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>


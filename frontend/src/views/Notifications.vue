<template>
  <div class="notifications">
    <el-card>
      <template #header>
        <span>通知中心</span>
      </template>
      <el-table :data="notifications" style="width: 100%">
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="message" label="内容" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button
              v-if="!row.read"
              size="small"
              @click="markRead(row.id)"
            >
              标记已读
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="deleteNotification(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const notifications = ref([])

const loadNotifications = async () => {
  try {
    const data = await api.get('/notifications')
    notifications.value = data.notifications || []
  } catch (error) {
    console.error('加载通知失败:', error)
  }
}

const markRead = async (id) => {
  try {
    await api.post('/notifications/mark-read', { notification_id: id })
    ElMessage.success('已标记为已读')
    loadNotifications()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteNotification = async (id) => {
  try {
    await api.delete(`/notifications/${id}`)
    ElMessage.success('删除成功')
    loadNotifications()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadNotifications()
  // 每10秒刷新一次
  setInterval(loadNotifications, 10000)
})
</script>

<style scoped>
.notifications {
  max-width: 1400px;
  margin: 0 auto;
}
</style>


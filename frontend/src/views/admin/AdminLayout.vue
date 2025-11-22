<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
      <div class="logo">
        <h2 v-if="!isCollapse">HL 分析系统</h2>
        <h2 v-else>HL</h2>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        router
      >
        <!-- 仪表盘 -->
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        
        <!-- 钱包管理 -->
        <el-sub-menu index="wallets">
          <template #title>
            <el-icon><Wallet /></el-icon>
            <span>钱包管理</span>
          </template>
          <el-menu-item index="/wallets">钱包列表</el-menu-item>
          <el-menu-item index="/wallets/import">批量导入</el-menu-item>
          <el-menu-item index="/wallets/tags">标签管理</el-menu-item>
        </el-sub-menu>
        
        <!-- 排行榜 -->
        <el-menu-item index="/leaderboard">
          <el-icon><TrophyBase /></el-icon>
          <template #title>排行榜</template>
        </el-menu-item>
        
        <!-- 通知管理 -->
        <el-menu-item index="/notifications">
          <el-icon><Bell /></el-icon>
          <template #title>通知中心</template>
        </el-menu-item>
        
        <!-- 系统管理 -->
        <el-sub-menu index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/config">系统配置</el-menu-item>
          <el-menu-item index="/system/logs">日志管理</el-menu-item>
          <el-menu-item index="/system/monitor">系统监控</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-icon" @click="toggleCollapse">
            <Expand v-if="isCollapse" />
            <Fold v-else />
          </el-icon>
          
          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="item in breadcrumbs"
              :key="item.path"
              :to="item.path"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <!-- WebSocket 连接状态 -->
          <el-tooltip :content="wsStatus.text" placement="bottom">
            <el-icon :class="['ws-status', wsStatus.class]">
              <Connection />
            </el-icon>
          </el-tooltip>
          
          <!-- 通知 -->
          <el-badge :value="unreadCount" :hidden="unreadCount === 0">
            <el-icon class="header-icon" @click="showNotifications">
              <Bell />
            </el-icon>
          </el-badge>
          
          <!-- 用户菜单 -->
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32">{{ username.charAt(0).toUpperCase() }}</el-avatar>
              <span class="username">{{ username }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item command="changePassword">
                  <el-icon><Lock /></el-icon>
                  修改密码
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 内容区 -->
      <el-main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
    
    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="400px"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="80px"
      >
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  DataAnalysis,
  Wallet,
  TrophyBase,
  Bell,
  Setting,
  Expand,
  Fold,
  Connection,
  User,
  Lock,
  SwitchButton
} from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'
import { wsClient } from '../../utils/websocket'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 侧边栏折叠状态
const isCollapse = ref(false)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 面包屑
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    path: item.path,
    title: item.meta.title
  }))
})

// 用户信息
const username = computed(() => authStore.username)

// WebSocket 状态
const wsConnected = ref(false)
const wsStatus = computed(() => {
  if (wsConnected.value) {
    return { text: 'WebSocket 已连接', class: 'connected' }
  } else {
    return { text: 'WebSocket 未连接', class: 'disconnected' }
  }
})

// 未读通知数
const unreadCount = ref(0)

// 修改密码对话框
const passwordDialogVisible = ref(false)
const passwordFormRef = ref(null)
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 切换侧边栏折叠
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 显示通知
const showNotifications = () => {
  router.push('/notifications')
}

// 处理用户菜单命令
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人信息功能开发中')
      break
    case 'changePassword':
      passwordDialogVisible.value = true
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 修改密码
const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    
    const result = await authStore.changePassword(
      passwordForm.oldPassword,
      passwordForm.newPassword
    )
    
    if (result.success) {
      ElMessage.success(result.message)
      passwordDialogVisible.value = false
      
      // 清空表单
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
      
      // 跳转到登录页
      setTimeout(() => {
        router.push('/login')
      }, 1000)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('修改密码失败:', error)
  }
}

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }).catch(() => {
    // 取消
  })
}

// 初始化 WebSocket
const initWebSocket = () => {
  const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/ws'
  const token = authStore.accessToken
  
  // 连接 WebSocket
  wsClient.connect(wsUrl, token)
  
  // 监听连接状态
  wsClient.onConnect(() => {
    wsConnected.value = true
    console.log('WebSocket 连接成功')
  })
  
  wsClient.onDisconnect(() => {
    wsConnected.value = false
    console.log('WebSocket 连接断开')
  })
  
  // 监听通知消息
  wsClient.on('notification', (data) => {
    ElMessage({
      message: data.data.content,
      type: data.data.level || 'info',
      duration: 3000
    })
    
    // 更新未读数
    unreadCount.value++
  })
}

// 组件挂载
onMounted(() => {
  initWebSocket()
})

// 组件卸载
onUnmounted(() => {
  wsClient.disconnect()
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow-x: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4a;
}

.logo h2 {
  color: white;
  margin: 0;
  font-size: 18px;
  font-weight: bold;
}

.el-menu {
  border-right: none;
  background-color: #304156;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  color: #bfcbd9;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background-color: #263445 !important;
  color: #fff;
}

:deep(.el-menu-item.is-active) {
  background-color: #409eff !important;
  color: #fff;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.collapse-icon {
  font-size: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.collapse-icon:hover {
  transform: scale(1.1);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.ws-status {
  font-size: 18px;
  cursor: pointer;
}

.ws-status.connected {
  color: #67c23a;
}

.ws-status.disconnected {
  color: #f56c6c;
}

.header-icon {
  font-size: 20px;
  cursor: pointer;
  transition: color 0.3s;
}

.header-icon:hover {
  color: #409eff;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #333;
}

.content {
  background-color: #f0f2f5;
  overflow-y: auto;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>


import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// 页面组件
import Login from '../views/Login.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import WalletList from '../views/WalletList.vue'
import WalletDetail from '../views/WalletDetail.vue'
import WalletImport from '../views/admin/WalletImport.vue'
import Notifications from '../views/Notifications.vue'
import SystemConfig from '../views/admin/SystemConfig.vue'
import LogManagement from '../views/admin/LogManagement.vue'
import SystemMonitor from '../views/admin/SystemMonitor.vue'
import AIAnalysis from '../views/admin/AIAnalysis.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '仪表盘' }
      },
      {
        path: 'wallets',
        name: 'WalletList',
        component: WalletList,
        meta: { title: '钱包列表' }
      },
      {
        path: 'wallets/import',
        name: 'WalletImport',
        component: WalletImport,
        meta: { title: '批量导入' }
      },
      {
        path: 'wallets/:address',
        name: 'WalletDetail',
        component: WalletDetail,
        meta: { title: '钱包详情' }
      },
      {
        path: 'notifications',
        name: 'Notifications',
        component: Notifications,
        meta: { title: '通知中心' }
      },
      {
        path: 'system/config',
        name: 'SystemConfig',
        component: SystemConfig,
        meta: { title: '系统配置' }
      },
      {
        path: 'system/logs',
        name: 'LogManagement',
        component: LogManagement,
        meta: { title: '日志管理' }
      },
      {
        path: 'system/monitor',
        name: 'SystemMonitor',
        component: SystemMonitor,
        meta: { title: '系统监控' }
      },
      {
        path: 'ai/analysis',
        name: 'AIAnalysis',
        component: AIAnalysis,
        meta: { title: 'AI 分析' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  
  if (requiresAuth && !authStore.isAuthenticated) {
    // 需要认证但未登录，跳转到登录页
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    // 已登录但访问登录页，跳转到首页
    next('/')
  } else {
    next()
  }
})

export default router

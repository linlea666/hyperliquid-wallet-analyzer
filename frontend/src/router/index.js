import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import WalletList from '../views/WalletList.vue'
import WalletDetail from '../views/WalletDetail.vue'
import Notifications from '../views/Notifications.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/wallets',
    name: 'WalletList',
    component: WalletList
  },
  {
    path: '/wallets/:address',
    name: 'WalletDetail',
    component: WalletDetail
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: Notifications
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router


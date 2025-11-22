/**
 * 认证 Store
 * 管理用户登录状态、Token、用户信息
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  
  // 计算属性
  const isAuthenticated = computed(() => !!accessToken.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const username = computed(() => user.value?.username || '')
  
  // 登录
  const login = async (username, password) => {
    try {
      const response = await authApi.login(username, password)
      
      if (response.success) {
        const { access_token, refresh_token, user: userData } = response.data
        
        // 保存 Token
        accessToken.value = access_token
        refreshToken.value = refresh_token
        user.value = userData
        
        // 持久化到 localStorage
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        localStorage.setItem('user', JSON.stringify(userData))
        
        return { success: true }
      } else {
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, message: error.message || '登录失败' }
    }
  }
  
  // 登出
  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      // 清除本地数据
      accessToken.value = ''
      refreshToken.value = ''
      user.value = null
      
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }
  
  // 刷新 Token
  const refreshAccessToken = async () => {
    try {
      const response = await authApi.refreshToken(refreshToken.value)
      
      if (response.success) {
        const { access_token } = response.data
        accessToken.value = access_token
        localStorage.setItem('access_token', access_token)
        return true
      } else {
        // 刷新失败，清除登录状态
        await logout()
        return false
      }
    } catch (error) {
      console.error('刷新 Token 失败:', error)
      await logout()
      return false
    }
  }
  
  // 修改密码
  const changePassword = async (oldPassword, newPassword) => {
    try {
      const response = await authApi.changePassword(oldPassword, newPassword)
      
      if (response.success) {
        // 修改密码后需要重新登录
        await logout()
        return { success: true, message: '密码修改成功，请重新登录' }
      } else {
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('修改密码失败:', error)
      return { success: false, message: error.message || '修改密码失败' }
    }
  }
  
  // 获取当前用户信息
  const fetchUserInfo = async () => {
    try {
      const response = await authApi.getCurrentUser()
      
      if (response.success) {
        user.value = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
        return true
      } else {
        return false
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return false
    }
  }
  
  // 检查是否需要修改密码
  const mustChangePassword = computed(() => user.value?.must_change_password || false)
  
  return {
    // 状态
    accessToken,
    refreshToken,
    user,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    username,
    mustChangePassword,
    
    // 方法
    login,
    logout,
    refreshAccessToken,
    changePassword,
    fetchUserInfo
  }
})


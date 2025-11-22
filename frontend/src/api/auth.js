/**
 * 认证 API
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加 Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理 Token 过期
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const originalRequest = error.config
    
    // Token 过期，尝试刷新
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(
            `${API_BASE_URL}/api/auth/refresh`,
            {},
            {
              headers: {
                Authorization: `Bearer ${refreshToken}`
              }
            }
          )
          
          if (response.data.success) {
            const { access_token } = response.data.data
            localStorage.setItem('access_token', access_token)
            
            // 重试原请求
            originalRequest.headers.Authorization = `Bearer ${access_token}`
            return apiClient(originalRequest)
          }
        }
      } catch (refreshError) {
        // 刷新失败，跳转到登录页
        localStorage.clear()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

export const authApi = {
  /**
   * 登录
   */
  login: (username, password) => {
    return apiClient.post('/api/auth/login', { username, password })
  },
  
  /**
   * 登出
   */
  logout: () => {
    return apiClient.post('/api/auth/logout')
  },
  
  /**
   * 刷新 Token
   */
  refreshToken: (refreshToken) => {
    return axios.post(
      `${API_BASE_URL}/api/auth/refresh`,
      {},
      {
        headers: {
          Authorization: `Bearer ${refreshToken}`
        }
      }
    ).then(res => res.data)
  },
  
  /**
   * 获取当前用户信息
   */
  getCurrentUser: () => {
    return apiClient.get('/api/auth/me')
  },
  
  /**
   * 修改密码
   */
  changePassword: (oldPassword, newPassword) => {
    return apiClient.post('/api/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    })
  }
}

export default apiClient


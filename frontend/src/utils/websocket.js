/**
 * WebSocket 工具类
 * 管理 WebSocket 连接、消息订阅、自动重连
 */

class WebSocketClient {
  constructor() {
    this.ws = null
    this.url = ''
    this.token = ''
    this.clientId = null
    this.isConnected = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 3000
    this.heartbeatInterval = null
    this.heartbeatTimer = 30000
    
    // 消息处理器
    this.messageHandlers = new Map()
    this.topicHandlers = new Map()
    
    // 连接状态回调
    this.onConnectCallbacks = []
    this.onDisconnectCallbacks = []
    this.onErrorCallbacks = []
  }
  
  /**
   * 连接 WebSocket
   */
  connect(url, token = '') {
    if (this.ws && this.isConnected) {
      console.log('WebSocket 已连接')
      return
    }
    
    this.url = url
    this.token = token
    
    // 构建连接 URL
    let wsUrl = url
    if (token) {
      wsUrl += `?token=${token}`
    }
    
    console.log('正在连接 WebSocket:', wsUrl)
    
    try {
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = this._handleOpen.bind(this)
      this.ws.onmessage = this._handleMessage.bind(this)
      this.ws.onclose = this._handleClose.bind(this)
      this.ws.onerror = this._handleError.bind(this)
    } catch (error) {
      console.error('WebSocket 连接失败:', error)
      this._scheduleReconnect()
    }
  }
  
  /**
   * 断开连接
   */
  disconnect() {
    console.log('断开 WebSocket 连接')
    
    // 停止心跳
    this._stopHeartbeat()
    
    // 关闭连接
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    this.isConnected = false
    this.reconnectAttempts = 0
  }
  
  /**
   * 发送消息
   */
  send(message) {
    if (!this.isConnected || !this.ws) {
      console.warn('WebSocket 未连接，无法发送消息')
      return false
    }
    
    try {
      const data = typeof message === 'string' ? message : JSON.stringify(message)
      this.ws.send(data)
      return true
    } catch (error) {
      console.error('发送消息失败:', error)
      return false
    }
  }
  
  /**
   * 订阅主题
   */
  subscribe(topic, handler) {
    // 保存处理器
    if (!this.topicHandlers.has(topic)) {
      this.topicHandlers.set(topic, new Set())
    }
    this.topicHandlers.get(topic).add(handler)
    
    // 发送订阅消息
    this.send({
      type: 'subscribe',
      topic: topic
    })
    
    console.log('订阅主题:', topic)
  }
  
  /**
   * 取消订阅
   */
  unsubscribe(topic, handler = null) {
    if (handler) {
      // 移除特定处理器
      const handlers = this.topicHandlers.get(topic)
      if (handlers) {
        handlers.delete(handler)
        if (handlers.size === 0) {
          this.topicHandlers.delete(topic)
        }
      }
    } else {
      // 移除所有处理器
      this.topicHandlers.delete(topic)
    }
    
    // 发送取消订阅消息
    this.send({
      type: 'unsubscribe',
      topic: topic
    })
    
    console.log('取消订阅主题:', topic)
  }
  
  /**
   * 注册消息类型处理器
   */
  on(messageType, handler) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, new Set())
    }
    this.messageHandlers.get(messageType).add(handler)
  }
  
  /**
   * 移除消息类型处理器
   */
  off(messageType, handler = null) {
    if (handler) {
      const handlers = this.messageHandlers.get(messageType)
      if (handlers) {
        handlers.delete(handler)
      }
    } else {
      this.messageHandlers.delete(messageType)
    }
  }
  
  /**
   * 注册连接成功回调
   */
  onConnect(callback) {
    this.onConnectCallbacks.push(callback)
  }
  
  /**
   * 注册断开连接回调
   */
  onDisconnect(callback) {
    this.onDisconnectCallbacks.push(callback)
  }
  
  /**
   * 注册错误回调
   */
  onError(callback) {
    this.onErrorCallbacks.push(callback)
  }
  
  /**
   * 处理连接打开
   */
  _handleOpen(event) {
    console.log('✅ WebSocket 连接成功')
    this.isConnected = true
    this.reconnectAttempts = 0
    
    // 启动心跳
    this._startHeartbeat()
    
    // 触发回调
    this.onConnectCallbacks.forEach(callback => {
      try {
        callback(event)
      } catch (error) {
        console.error('连接回调错误:', error)
      }
    })
  }
  
  /**
   * 处理消息
   */
  _handleMessage(event) {
    try {
      const data = JSON.parse(event.data)
      
      // 保存客户端 ID
      if (data.type === 'connection' && data.client_id) {
        this.clientId = data.client_id
        console.log('客户端 ID:', this.clientId)
      }
      
      // 处理 pong
      if (data.type === 'pong') {
        // 心跳响应，不需要特殊处理
        return
      }
      
      // 调用消息类型处理器
      const handlers = this.messageHandlers.get(data.type)
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(data)
          } catch (error) {
            console.error('消息处理器错误:', error)
          }
        })
      }
      
      // 调用主题处理器
      if (data.topic) {
        const topicHandlers = this.topicHandlers.get(data.topic)
        if (topicHandlers) {
          topicHandlers.forEach(handler => {
            try {
              handler(data)
            } catch (error) {
              console.error('主题处理器错误:', error)
            }
          })
        }
      }
    } catch (error) {
      console.error('处理消息失败:', error)
    }
  }
  
  /**
   * 处理连接关闭
   */
  _handleClose(event) {
    console.log('WebSocket 连接关闭:', event.code, event.reason)
    this.isConnected = false
    
    // 停止心跳
    this._stopHeartbeat()
    
    // 触发回调
    this.onDisconnectCallbacks.forEach(callback => {
      try {
        callback(event)
      } catch (error) {
        console.error('断开回调错误:', error)
      }
    })
    
    // 自动重连
    if (event.code !== 1000) { // 1000 = 正常关闭
      this._scheduleReconnect()
    }
  }
  
  /**
   * 处理错误
   */
  _handleError(event) {
    console.error('WebSocket 错误:', event)
    
    // 触发回调
    this.onErrorCallbacks.forEach(callback => {
      try {
        callback(event)
      } catch (error) {
        console.error('错误回调错误:', error)
      }
    })
  }
  
  /**
   * 启动心跳
   */
  _startHeartbeat() {
    this._stopHeartbeat()
    
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.send({ type: 'ping' })
      }
    }, this.heartbeatTimer)
  }
  
  /**
   * 停止心跳
   */
  _stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }
  
  /**
   * 计划重连
   */
  _scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('达到最大重连次数，停止重连')
      return
    }
    
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    
    console.log(`${delay / 1000} 秒后尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
    
    setTimeout(() => {
      this.connect(this.url, this.token)
    }, delay)
  }
}

// 创建全局实例
export const wsClient = new WebSocketClient()

export default WebSocketClient


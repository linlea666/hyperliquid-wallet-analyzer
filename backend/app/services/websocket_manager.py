"""
WebSocket 管理器
处理实时通信、进度推送、通知推送等
"""
from typing import Dict, Set, List, Optional
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 存储所有活跃连接: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # 订阅管理: {topic: Set[client_id]}
        self.subscriptions: Dict[str, Set[str]] = {}
        
        # 用户连接映射: {username: Set[client_id]}
        self.user_connections: Dict[str, Set[str]] = {}
        
        logger.info("WebSocket 连接管理器初始化完成")
    
    async def connect(self, websocket: WebSocket, client_id: str, username: Optional[str] = None):
        """
        接受新的 WebSocket 连接
        
        Args:
            websocket: WebSocket 连接对象
            client_id: 客户端唯一标识
            username: 用户名（可选）
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        # 记录用户连接
        if username:
            if username not in self.user_connections:
                self.user_connections[username] = set()
            self.user_connections[username].add(client_id)
        
        logger.info(f"WebSocket 连接建立: {client_id} (用户: {username or '未认证'})")
        logger.info(f"当前活跃连接数: {len(self.active_connections)}")
        
        # 发送欢迎消息
        await self.send_personal_message(client_id, {
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, client_id: str):
        """
        断开连接
        
        Args:
            client_id: 客户端唯一标识
        """
        # 移除连接
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # 移除所有订阅
        for topic in self.subscriptions:
            self.subscriptions[topic].discard(client_id)
        
        # 移除用户连接映射
        for username in list(self.user_connections.keys()):
            self.user_connections[username].discard(client_id)
            if not self.user_connections[username]:
                del self.user_connections[username]
        
        logger.info(f"WebSocket 连接断开: {client_id}")
        logger.info(f"当前活跃连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, client_id: str, message: dict):
        """
        发送消息给指定客户端
        
        Args:
            client_id: 客户端唯一标识
            message: 消息内容（字典）
        """
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败 ({client_id}): {e}")
                self.disconnect(client_id)
    
    async def send_to_user(self, username: str, message: dict):
        """
        发送消息给指定用户的所有连接
        
        Args:
            username: 用户名
            message: 消息内容（字典）
        """
        if username in self.user_connections:
            client_ids = list(self.user_connections[username])
            for client_id in client_ids:
                await self.send_personal_message(client_id, message)
    
    async def broadcast(self, message: dict, exclude: Optional[Set[str]] = None):
        """
        广播消息给所有连接
        
        Args:
            message: 消息内容（字典）
            exclude: 排除的客户端 ID 集合
        """
        exclude = exclude or set()
        disconnected = []
        
        for client_id, websocket in self.active_connections.items():
            if client_id not in exclude:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"广播消息失败 ({client_id}): {e}")
                    disconnected.append(client_id)
        
        # 清理断开的连接
        for client_id in disconnected:
            self.disconnect(client_id)
    
    def subscribe(self, client_id: str, topic: str):
        """
        订阅主题
        
        Args:
            client_id: 客户端唯一标识
            topic: 主题名称
        """
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        
        self.subscriptions[topic].add(client_id)
        logger.info(f"客户端 {client_id} 订阅主题: {topic}")
    
    def unsubscribe(self, client_id: str, topic: str):
        """
        取消订阅主题
        
        Args:
            client_id: 客户端唯一标识
            topic: 主题名称
        """
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(client_id)
            logger.info(f"客户端 {client_id} 取消订阅主题: {topic}")
    
    async def publish(self, topic: str, message: dict):
        """
        发布消息到主题
        
        Args:
            topic: 主题名称
            message: 消息内容（字典）
        """
        if topic in self.subscriptions:
            client_ids = list(self.subscriptions[topic])
            
            # 添加主题信息
            message["topic"] = topic
            message["timestamp"] = datetime.now().isoformat()
            
            for client_id in client_ids:
                await self.send_personal_message(client_id, message)
            
            logger.debug(f"发布消息到主题 {topic}: {len(client_ids)} 个订阅者")
    
    async def send_import_progress(self, task_id: str, progress: dict):
        """
        发送导入进度更新
        
        Args:
            task_id: 任务 ID
            progress: 进度信息
        """
        message = {
            "type": "import_progress",
            "task_id": task_id,
            "data": progress,
            "timestamp": datetime.now().isoformat()
        }
        
        # 发布到导入进度主题
        await self.publish(f"import:{task_id}", message)
    
    async def send_wallet_update(self, wallet_address: str, data: dict):
        """
        发送钱包数据更新
        
        Args:
            wallet_address: 钱包地址
            data: 更新数据
        """
        message = {
            "type": "wallet_update",
            "wallet_address": wallet_address,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # 发布到钱包更新主题
        await self.publish("wallet_updates", message)
    
    async def send_notification(self, notification: dict, target_users: Optional[List[str]] = None):
        """
        发送通知
        
        Args:
            notification: 通知内容
            target_users: 目标用户列表（None 表示广播给所有用户）
        """
        message = {
            "type": "notification",
            "data": notification,
            "timestamp": datetime.now().isoformat()
        }
        
        if target_users:
            # 发送给指定用户
            for username in target_users:
                await self.send_to_user(username, message)
        else:
            # 广播给所有用户
            await self.broadcast(message)
    
    async def send_system_status(self, status: dict):
        """
        发送系统状态更新
        
        Args:
            status: 系统状态信息
        """
        message = {
            "type": "system_status",
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
        
        # 发布到系统状态主题
        await self.publish("system_status", message)
    
    def get_stats(self) -> dict:
        """
        获取连接统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "total_connections": len(self.active_connections),
            "total_users": len(self.user_connections),
            "total_subscriptions": sum(len(subs) for subs in self.subscriptions.values()),
            "topics": list(self.subscriptions.keys()),
            "users": list(self.user_connections.keys())
        }


# 全局连接管理器实例
ws_manager = ConnectionManager()


class WebSocketHandler:
    """WebSocket 消息处理器"""
    
    @staticmethod
    async def handle_message(client_id: str, message: dict):
        """
        处理客户端消息
        
        Args:
            client_id: 客户端 ID
            message: 消息内容
        """
        try:
            msg_type = message.get("type")
            
            if msg_type == "subscribe":
                # 订阅主题
                topic = message.get("topic")
                if topic:
                    ws_manager.subscribe(client_id, topic)
                    await ws_manager.send_personal_message(client_id, {
                        "type": "subscribed",
                        "topic": topic,
                        "success": True
                    })
            
            elif msg_type == "unsubscribe":
                # 取消订阅
                topic = message.get("topic")
                if topic:
                    ws_manager.unsubscribe(client_id, topic)
                    await ws_manager.send_personal_message(client_id, {
                        "type": "unsubscribed",
                        "topic": topic,
                        "success": True
                    })
            
            elif msg_type == "ping":
                # 心跳检测
                await ws_manager.send_personal_message(client_id, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif msg_type == "get_stats":
                # 获取统计信息
                stats = ws_manager.get_stats()
                await ws_manager.send_personal_message(client_id, {
                    "type": "stats",
                    "data": stats
                })
            
            else:
                logger.warning(f"未知消息类型: {msg_type}")
                await ws_manager.send_personal_message(client_id, {
                    "type": "error",
                    "message": f"未知消息类型: {msg_type}"
                })
        
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            await ws_manager.send_personal_message(client_id, {
                "type": "error",
                "message": str(e)
            })


# 导出
__all__ = ["ws_manager", "ConnectionManager", "WebSocketHandler"]


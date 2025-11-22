"""
WebSocket API
提供实时通信接口
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional
import uuid
from loguru import logger

from app.services.websocket_manager import ws_manager, WebSocketHandler
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None)
):
    """
    WebSocket 连接端点
    
    Query 参数:
        - token: 认证 Token（可选，用于识别用户身份）
        - client_id: 客户端 ID（可选，如果不提供则自动生成）
    
    消息格式:
        客户端发送:
        {
            "type": "subscribe|unsubscribe|ping|get_stats",
            "topic": "主题名称（订阅/取消订阅时需要）",
            ...其他参数
        }
        
        服务端发送:
        {
            "type": "消息类型",
            "data": {...},
            "timestamp": "ISO 格式时间戳"
        }
    
    支持的主题:
        - import:{task_id} - 导入进度更新
        - wallet_updates - 钱包数据更新
        - system_status - 系统状态更新
        - notifications - 通知消息
    """
    # 生成或使用提供的客户端 ID
    if not client_id:
        client_id = str(uuid.uuid4())
    
    # 验证 Token（如果提供）
    username = None
    if token:
        try:
            from app.services.auth_service import auth_service
            token_data = auth_service.verify_token(token)
            if token_data:
                username = token_data.username
                logger.info(f"WebSocket 认证成功: {username}")
        except Exception as e:
            logger.warning(f"WebSocket Token 验证失败: {e}")
    
    # 建立连接
    await ws_manager.connect(websocket, client_id, username)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()
            
            # 处理消息
            await WebSocketHandler.handle_message(client_id, data)
    
    except WebSocketDisconnect:
        logger.info(f"客户端主动断开连接: {client_id}")
        ws_manager.disconnect(client_id)
    
    except Exception as e:
        logger.error(f"WebSocket 错误 ({client_id}): {e}")
        ws_manager.disconnect(client_id)


@router.get("/ws/stats")
async def get_websocket_stats(current_user: User = Depends(get_current_user)):
    """
    获取 WebSocket 连接统计信息
    
    需要管理员权限
    """
    try:
        stats = ws_manager.get_stats()
        
        return {
            "success": True,
            "data": stats
        }
    
    except Exception as e:
        logger.error(f"获取 WebSocket 统计失败: {e}")
        return {
            "success": False,
            "message": str(e)
        }


@router.post("/ws/broadcast")
async def broadcast_message(
    message: dict,
    current_user: User = Depends(get_current_user)
):
    """
    广播消息给所有连接
    
    需要管理员权限
    """
    try:
        await ws_manager.broadcast({
            "type": "admin_broadcast",
            "data": message,
            "sender": current_user.username
        })
        
        return {
            "success": True,
            "message": "广播成功"
        }
    
    except Exception as e:
        logger.error(f"广播消息失败: {e}")
        return {
            "success": False,
            "message": str(e)
        }


@router.post("/ws/notify")
async def send_notification(
    notification: dict,
    target_users: Optional[list] = None,
    current_user: User = Depends(get_current_user)
):
    """
    发送通知
    
    Body 参数:
        - notification: 通知内容
        - target_users: 目标用户列表（None 表示广播）
    
    需要管理员权限
    """
    try:
        await ws_manager.send_notification(notification, target_users)
        
        return {
            "success": True,
            "message": "通知发送成功"
        }
    
    except Exception as e:
        logger.error(f"发送通知失败: {e}")
        return {
            "success": False,
            "message": str(e)
        }


# 导出
__all__ = ["router"]


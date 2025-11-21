"""通知相关 API"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger

from app.services.storage import StorageService
from app.services.notifier import NotificationService

router = APIRouter()

storage = StorageService()
notifier = NotificationService()


@router.get("")
async def get_notifications():
    """获取通知列表"""
    try:
        notifications = storage.get_notifications()
        return {"notifications": notifications}
    except Exception as e:
        logger.error(f"获取通知列表失败: {e}")
        return {"notifications": []}


@router.post("/mark-read")
async def mark_notification_read(request: dict):
    """标记通知已读"""
    try:
        notification_id = request.get("notification_id")
        if not notification_id:
            raise HTTPException(status_code=400, detail="缺少 notification_id")
        storage.mark_notification_read(notification_id)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记通知已读失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notification_id}")
async def delete_notification(notification_id: str):
    """删除通知"""
    try:
        storage.delete_notification(notification_id)
        return {"success": True}
    except Exception as e:
        logger.error(f"删除通知失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings")
async def get_notification_settings():
    """获取通知设置"""
    try:
        from app.config import config
        settings = config.get_config("notifications")
        return settings
    except Exception as e:
        logger.error(f"获取通知设置失败: {e}")
        return {}


@router.put("/settings")
async def update_notification_settings(settings: dict):
    """更新通知设置"""
    try:
        from app.config import config
        config.update_config("notifications", settings)
        return {"success": True}
    except Exception as e:
        logger.error(f"更新通知设置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


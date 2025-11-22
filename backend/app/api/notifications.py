"""通知相关 API"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger

from app.services.notification import email_service, notification_manager
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter()


class EmailTestRequest(BaseModel):
    """测试邮件请求"""
    config: dict


@router.get("")
async def get_notifications(
    limit: int = 50,
    offset: int = 0,
    is_read: Optional[bool] = None,
    level: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """获取通知列表"""
    try:
        notifications = notification_manager.get_notifications(
            limit=limit,
            offset=offset,
            is_read=is_read,
            level=level
        )
        
        return {
            "success": True,
            "data": notifications
        }
    except Exception as e:
        logger.error(f"获取通知列表失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": []
        }


@router.get("/unread-count")
async def get_unread_count(current_user: User = Depends(get_current_user)):
    """获取未读通知数量"""
    try:
        count = notification_manager.get_unread_count()
        return {
            "success": True,
            "data": {"count": count}
        }
    except Exception as e:
        logger.error(f"获取未读数量失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {"count": 0}
        }


@router.post("/mark-read")
async def mark_notification_read(
    notification_ids: List[int],
    current_user: User = Depends(get_current_user)
):
    """标记通知已读"""
    try:
        success = notification_manager.mark_as_read(notification_ids)
        return {
            "success": success,
            "message": "标记成功" if success else "标记失败"
        }
    except Exception as e:
        logger.error(f"标记通知已读失败: {e}")
        return {
            "success": False,
            "message": str(e)
        }


@router.post("/delete")
async def delete_notifications(
    notification_ids: List[int],
    current_user: User = Depends(get_current_user)
):
    """删除通知"""
    try:
        success = notification_manager.delete_notifications(notification_ids)
        return {
            "success": success,
            "message": "删除成功" if success else "删除失败"
        }
    except Exception as e:
        logger.error(f"删除通知失败: {e}")
        return {
            "success": False,
            "message": str(e)
        }


@router.post("/test-email")
async def send_test_email(
    request: EmailTestRequest,
    current_user: User = Depends(get_current_user)
):
    """发送测试邮件"""
    try:
        success = email_service.send_test_email(request.config)
        
        return {
            "success": success,
            "message": "测试邮件发送成功" if success else "测试邮件发送失败"
        }
    except Exception as e:
        logger.error(f"发送测试邮件失败: {e}")
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/email/history")
async def get_email_history(
    limit: int = 100,
    offset: int = 0,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """获取邮件发送历史"""
    try:
        history = email_service.get_history(limit, offset, status)
        
        return {
            "success": True,
            "data": history
        }
    except Exception as e:
        logger.error(f"获取邮件历史失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": []
        }


@router.get("/email/statistics")
async def get_email_statistics(current_user: User = Depends(get_current_user)):
    """获取邮件统计信息"""
    try:
        stats = email_service.get_statistics()
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取邮件统计失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


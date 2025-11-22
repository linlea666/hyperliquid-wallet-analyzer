"""
通知服务模块
"""
from .email_service import email_service, EmailService
from .notification_manager import notification_manager, NotificationManager

__all__ = [
    'email_service',
    'EmailService',
    'notification_manager',
    'NotificationManager'
]


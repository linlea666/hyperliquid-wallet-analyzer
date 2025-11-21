"""通知服务"""
from typing import Dict, Any
from datetime import datetime
import uuid
from loguru import logger

from app.services.storage import StorageService
from app.config import config


class NotificationService:
    """通知服务"""
    
    def __init__(self):
        self.storage = StorageService()
        self.config = config.get_config("notifications")
    
    def create_notification(
        self,
        notification_type: str,
        wallet_address: str,
        title: str,
        message: str,
        data: Dict[str, Any] = None
    ):
        """创建通知"""
        notification = {
            "id": str(uuid.uuid4()),
            "type": notification_type,
            "wallet_address": wallet_address,
            "title": title,
            "message": message,
            "data": data or {},
            "read": False,
            "created_at": datetime.now().isoformat()
        }
        
        self.storage.save_notification(notification)
        
        # 发送浏览器通知（如果启用）
        if self.config.get("browser", {}).get("enabled", False):
            self._send_browser_notification(notification)
        
        # 发送邮件通知（如果启用）
        if self.config.get("email", {}).get("enabled", False):
            self._send_email_notification(notification)
        
        logger.info(f"📢 创建通知: {title}")
    
    def _send_browser_notification(self, notification: Dict[str, Any]):
        """发送浏览器通知（通过 WebSocket，前端处理）"""
        # TODO: 实现 WebSocket 推送
        pass
    
    def _send_email_notification(self, notification: Dict[str, Any]):
        """发送邮件通知"""
        # TODO: 实现邮件发送
        pass
    
    def check_wallet_anomalies(self, wallet: Dict[str, Any], previous_state: Dict[str, Any] = None):
        """检查钱包异动"""
        thresholds = self.config.get("thresholds", {})
        metrics = wallet.get("metrics", {})
        
        # 检查收益阈值
        total_pnl = metrics.get("total_pnl", 0)
        if total_pnl > thresholds.get("profit_threshold", 5000):
            self.create_notification(
                "profit",
                wallet.get("address", ""),
                "收益达到阈值",
                f"钱包 {wallet.get('address', '')[:10]}... 收益达到 ${total_pnl:.2f}",
                {"pnl": total_pnl}
            )
        
        # 检查 ROI 阈值
        roi = metrics.get("roi", 0)
        if roi > thresholds.get("roi_threshold", 200):
            self.create_notification(
                "roi",
                wallet.get("address", ""),
                "ROI 达到阈值",
                f"钱包 {wallet.get('address', '')[:10]}... ROI 达到 {roi:.2f}%",
                {"roi": roi}
            )
        
        # 检查回撤阈值
        max_drawdown = wallet.get("risk_metrics", {}).get("max_drawdown", 0) * 100
        if max_drawdown > thresholds.get("drawdown_threshold", 50):
            self.create_notification(
                "risk",
                wallet.get("address", ""),
                "最大回撤超过阈值",
                f"钱包 {wallet.get('address', '')[:10]}... 最大回撤达到 {max_drawdown:.2f}%",
                {"max_drawdown": max_drawdown}
            )


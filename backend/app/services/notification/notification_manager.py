"""
通知管理器
处理通知规则、通知发送、通知历史等
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import json

from app.database import db
from app.services.notification.email_service import email_service
from app.services.websocket_manager import ws_manager


class NotificationManager:
    """通知管理器"""
    
    def __init__(self):
        self.rules = self._load_rules()
        # 通知频率限制缓存 {rule_id: last_sent_time}
        self.rate_limit_cache = {}
    
    def _load_rules(self) -> Dict[str, Any]:
        """加载通知规则"""
        try:
            config_row = db.fetch_one(
                "SELECT config_value FROM system_configs WHERE config_key = ?",
                ("notification",)
            )
            
            if config_row:
                config = json.loads(config_row['config_value'])
                return config.get('rules', {})
            
            return {}
        except Exception as e:
            logger.error(f"加载通知规则失败: {e}")
            return {}
    
    def reload_rules(self):
        """重新加载规则"""
        self.rules = self._load_rules()
    
    async def send_notification(
        self,
        event_type: str,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]] = None,
        level: str = 'info',
        target_users: Optional[List[str]] = None
    ) -> bool:
        """
        发送通知
        
        Args:
            event_type: 事件类型
            title: 通知标题
            content: 通知内容
            data: 附加数据
            level: 通知级别 (info/success/warning/error)
            target_users: 目标用户列表
            
        Returns:
            是否发送成功
        """
        try:
            # 检查规则是否启用
            if not self._check_rule_enabled(event_type):
                logger.debug(f"通知规则未启用: {event_type}")
                return False
            
            # 检查频率限制
            if not self._check_rate_limit(event_type):
                logger.debug(f"通知频率受限: {event_type}")
                return False
            
            # 获取通知渠道
            channels = self._get_channels(event_type)
            
            success = False
            
            # 发送到各个渠道
            if 'websocket' in channels:
                await self._send_websocket(title, content, data, level, target_users)
                success = True
            
            if 'email' in channels:
                if self._send_email(event_type, title, content, data):
                    success = True
            
            if 'database' in channels:
                self._save_to_database(event_type, title, content, data, level)
                success = True
            
            # 更新频率限制缓存
            if success:
                self.rate_limit_cache[event_type] = datetime.now()
            
            return success
            
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
            return False
    
    def _check_rule_enabled(self, event_type: str) -> bool:
        """检查规则是否启用"""
        # 特殊事件类型映射
        event_map = {
            'import_complete': 'importComplete',
            'high_score_wallet': 'highScoreWallet',
            'abnormal_trade': 'abnormalTrade',
            'system_error': 'systemError'
        }
        
        rule_key = event_map.get(event_type, event_type)
        return self.rules.get(rule_key, True)
    
    def _check_rate_limit(self, event_type: str) -> bool:
        """检查频率限制"""
        if event_type not in self.rate_limit_cache:
            return True
        
        last_sent = self.rate_limit_cache[event_type]
        
        # 根据事件类型设置不同的限制时间
        limit_minutes = {
            'import_complete': 5,      # 导入完成：5分钟
            'high_score_wallet': 30,   # 高分钱包：30分钟
            'abnormal_trade': 10,      # 异常交易：10分钟
            'system_error': 5          # 系统错误：5分钟
        }
        
        limit = limit_minutes.get(event_type, 10)
        
        if datetime.now() - last_sent < timedelta(minutes=limit):
            return False
        
        return True
    
    def _get_channels(self, event_type: str) -> List[str]:
        """获取通知渠道"""
        # 默认渠道
        default_channels = ['websocket', 'database']
        
        # 重要事件添加邮件通知
        important_events = [
            'import_complete',
            'high_score_wallet',
            'system_error'
        ]
        
        if event_type in important_events and email_service.is_enabled():
            default_channels.append('email')
        
        return default_channels
    
    async def _send_websocket(
        self,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]],
        level: str,
        target_users: Optional[List[str]]
    ):
        """通过 WebSocket 发送通知"""
        try:
            notification = {
                'title': title,
                'content': content,
                'level': level,
                'data': data or {},
                'timestamp': datetime.now().isoformat()
            }
            
            await ws_manager.send_notification(notification, target_users)
            
        except Exception as e:
            logger.error(f"WebSocket 通知发送失败: {e}")
    
    def _send_email(
        self,
        event_type: str,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]]
    ) -> bool:
        """通过邮件发送通知"""
        try:
            # 获取收件人
            config_row = db.fetch_one(
                "SELECT config_value FROM system_configs WHERE config_key = ?",
                ("notification",)
            )
            
            if not config_row:
                return False
            
            config = json.loads(config_row['config_value'])
            recipients = config.get('email', {}).get('recipients', [])
            
            if not recipients:
                logger.warning("邮件收件人列表为空")
                return False
            
            # 构建邮件内容
            html_content = self._build_email_content(event_type, title, content, data)
            
            # 发送邮件
            return email_service.send_email(
                subject=f"[HyperLiquid] {title}",
                content=html_content,
                recipients=recipients,
                content_type='html'
            )
            
        except Exception as e:
            logger.error(f"邮件通知发送失败: {e}")
            return False
    
    def _build_email_content(
        self,
        event_type: str,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]]
    ) -> str:
        """构建邮件内容"""
        # 根据事件类型选择模板
        templates = {
            'import_complete': self._template_import_complete,
            'high_score_wallet': self._template_high_score_wallet,
            'abnormal_trade': self._template_abnormal_trade,
            'system_error': self._template_system_error
        }
        
        template_func = templates.get(event_type, self._template_default)
        return template_func(title, content, data)
    
    def _template_default(
        self,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]]
    ) -> str:
        """默认邮件模板"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; }}
                .footer {{ background: #333; color: #999; padding: 10px; text-align: center; 
                          font-size: 12px; border-radius: 0 0 5px 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{title}</h2>
                </div>
                <div class="content">
                    <p>{content}</p>
                    {self._format_data(data)}
                </div>
                <div class="footer">
                    <p>此邮件由 HyperLiquid 钱包分析系统自动发送，请勿回复。</p>
                    <p>发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _template_import_complete(
        self,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]]
    ) -> str:
        """导入完成邮件模板"""
        stats = data or {}
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-item {{ text-align: center; }}
                .stat-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
                .stat-label {{ font-size: 14px; color: #666; }}
                .footer {{ background: #333; color: #999; padding: 10px; text-align: center; 
                          font-size: 12px; border-radius: 0 0 5px 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>✅ {title}</h2>
                </div>
                <div class="content">
                    <p>{content}</p>
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-value">{stats.get('total', 0)}</div>
                            <div class="stat-label">总数</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" style="color: #67c23a;">{stats.get('success', 0)}</div>
                            <div class="stat-label">成功</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" style="color: #f56c6c;">{stats.get('failed', 0)}</div>
                            <div class="stat-label">失败</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" style="color: #e6a23c;">{stats.get('skipped', 0)}</div>
                            <div class="stat-label">跳过</div>
                        </div>
                    </div>
                </div>
                <div class="footer">
                    <p>此邮件由 HyperLiquid 钱包分析系统自动发送，请勿回复。</p>
                    <p>发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _template_high_score_wallet(
        self,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]]
    ) -> str:
        """高分钱包邮件模板"""
        wallet = data or {}
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; }}
                .wallet-info {{ background: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .score {{ font-size: 48px; font-weight: bold; color: #f39c12; text-align: center; }}
                .footer {{ background: #333; color: #999; padding: 10px; text-align: center; 
                          font-size: 12px; border-radius: 0 0 5px 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🏆 {title}</h2>
                </div>
                <div class="content">
                    <p>{content}</p>
                    <div class="wallet-info">
                        <div class="score">{wallet.get('score', 0)}</div>
                        <p><strong>钱包地址:</strong> {wallet.get('address', 'N/A')}</p>
                        <p><strong>评分等级:</strong> {wallet.get('grade', 'N/A')}</p>
                        <p><strong>标签:</strong> {', '.join(wallet.get('tags', []))}</p>
                    </div>
                </div>
                <div class="footer">
                    <p>此邮件由 HyperLiquid 钱包分析系统自动发送，请勿回复。</p>
                    <p>发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _template_abnormal_trade(
        self,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]]
    ) -> str:
        """异常交易邮件模板"""
        return self._template_default(title, f"⚠️ {content}", data)
    
    def _template_system_error(
        self,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]]
    ) -> str:
        """系统错误邮件模板"""
        return self._template_default(title, f"❌ {content}", data)
    
    def _format_data(self, data: Optional[Dict[str, Any]]) -> str:
        """格式化附加数据"""
        if not data:
            return ""
        
        html = "<hr><h4>详细信息:</h4><ul>"
        for key, value in data.items():
            html += f"<li><strong>{key}:</strong> {value}</li>"
        html += "</ul>"
        
        return html
    
    def _save_to_database(
        self,
        event_type: str,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]],
        level: str
    ):
        """保存通知到数据库"""
        try:
            db.execute("""
                INSERT INTO notifications 
                (type, title, content, level, data, created_at, is_read)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event_type,
                title,
                content,
                level,
                json.dumps(data) if data else None,
                datetime.now().isoformat(),
                False
            ))
        except Exception as e:
            logger.error(f"保存通知到数据库失败: {e}")
    
    def get_notifications(
        self,
        limit: int = 50,
        offset: int = 0,
        is_read: Optional[bool] = None,
        level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取通知列表"""
        try:
            sql = "SELECT * FROM notifications WHERE 1=1"
            params = []
            
            if is_read is not None:
                sql += " AND is_read = ?"
                params.append(is_read)
            
            if level:
                sql += " AND level = ?"
                params.append(level)
            
            sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            rows = db.fetch_all(sql, tuple(params))
            
            notifications = []
            for row in rows:
                notification = dict(row)
                if notification.get('data'):
                    notification['data'] = json.loads(notification['data'])
                notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            logger.error(f"获取通知列表失败: {e}")
            return []
    
    def mark_as_read(self, notification_ids: List[int]) -> bool:
        """标记通知为已读"""
        try:
            placeholders = ','.join(['?' for _ in notification_ids])
            db.execute(
                f"UPDATE notifications SET is_read = ? WHERE id IN ({placeholders})",
                tuple([True] + notification_ids)
            )
            return True
        except Exception as e:
            logger.error(f"标记通知已读失败: {e}")
            return False
    
    def delete_notifications(self, notification_ids: List[int]) -> bool:
        """删除通知"""
        try:
            placeholders = ','.join(['?' for _ in notification_ids])
            db.execute(
                f"DELETE FROM notifications WHERE id IN ({placeholders})",
                tuple(notification_ids)
            )
            return True
        except Exception as e:
            logger.error(f"删除通知失败: {e}")
            return False
    
    def get_unread_count(self) -> int:
        """获取未读通知数量"""
        try:
            result = db.fetch_one(
                "SELECT COUNT(*) as count FROM notifications WHERE is_read = ?",
                (False,)
            )
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"获取未读数量失败: {e}")
            return 0


# 全局通知管理器实例
notification_manager = NotificationManager()


# 导出
__all__ = ['NotificationManager', 'notification_manager']


"""
邮件通知服务
支持 163 邮箱、QQ 邮箱、Gmail 等
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from app.database import db


class EmailService:
    """邮件服务"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载邮件配置"""
        try:
            config_row = db.fetch_one(
                "SELECT config_value FROM system_configs WHERE config_key = ?",
                ("notification",)
            )
            
            if config_row:
                import json
                config = json.loads(config_row['config_value'])
                return config.get('email', {})
            
            return {}
        except Exception as e:
            logger.error(f"加载邮件配置失败: {e}")
            return {}
    
    def reload_config(self):
        """重新加载配置"""
        self.config = self._load_config()
    
    def is_enabled(self) -> bool:
        """检查邮件服务是否启用"""
        return self.config.get('enabled', False)
    
    def send_email(
        self,
        subject: str,
        content: str,
        recipients: List[str],
        content_type: str = 'plain',
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            subject: 邮件主题
            content: 邮件内容
            recipients: 收件人列表
            content_type: 内容类型 ('plain' 或 'html')
            attachments: 附件列表
            
        Returns:
            是否发送成功
        """
        if not self.is_enabled():
            logger.warning("邮件服务未启用")
            return False
        
        if not recipients:
            logger.warning("收件人列表为空")
            return False
        
        try:
            # 创建邮件对象
            message = MIMEMultipart()
            message['From'] = Header(
                f"HyperLiquid 分析系统 <{self.config.get('sender_email')}>",
                'utf-8'
            )
            message['To'] = Header(', '.join(recipients), 'utf-8')
            message['Subject'] = Header(subject, 'utf-8')
            
            # 添加邮件内容
            if content_type == 'html':
                message.attach(MIMEText(content, 'html', 'utf-8'))
            else:
                message.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 添加附件（如果有）
            if attachments:
                for attachment in attachments:
                    self._add_attachment(message, attachment)
            
            # 连接 SMTP 服务器
            smtp_host = self.config.get('smtp_host', 'smtp.163.com')
            smtp_port = self.config.get('smtp_port', 465)
            use_ssl = self.config.get('use_ssl', True)
            
            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port)
                server.starttls()
            
            # 登录
            sender_email = self.config.get('sender_email')
            sender_password = self.config.get('sender_password')
            
            if not sender_email or not sender_password:
                logger.error("邮箱账号或密码未配置")
                return False
            
            server.login(sender_email, sender_password)
            
            # 发送邮件
            server.sendmail(sender_email, recipients, message.as_string())
            server.quit()
            
            logger.info(f"邮件发送成功: {subject} -> {recipients}")
            
            # 记录发送历史
            self._save_history(subject, content, recipients, 'sent')
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"邮箱认证失败: {e}")
            self._save_history(subject, content, recipients, 'failed', str(e))
            return False
        
        except smtplib.SMTPException as e:
            logger.error(f"邮件发送失败: {e}")
            self._save_history(subject, content, recipients, 'failed', str(e))
            return False
        
        except Exception as e:
            logger.error(f"发送邮件时发生错误: {e}")
            self._save_history(subject, content, recipients, 'failed', str(e))
            return False
    
    def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, Any]):
        """添加附件"""
        try:
            from email.mime.base import MIMEBase
            from email import encoders
            
            filename = attachment.get('filename')
            content = attachment.get('content')
            
            if not filename or not content:
                return
            
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={filename}'
            )
            message.attach(part)
            
        except Exception as e:
            logger.error(f"添加附件失败: {e}")
    
    def _save_history(
        self,
        subject: str,
        content: str,
        recipients: List[str],
        status: str,
        error_message: Optional[str] = None
    ):
        """保存发送历史"""
        try:
            db.execute("""
                INSERT INTO notification_history 
                (channel, recipient, title, content, status, sent_at, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'email',
                ', '.join(recipients),
                subject,
                content,
                status,
                datetime.now().isoformat(),
                error_message
            ))
        except Exception as e:
            logger.error(f"保存邮件历史失败: {e}")
    
    def send_test_email(self, test_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        发送测试邮件
        
        Args:
            test_config: 测试配置（如果提供则使用，否则使用当前配置）
            
        Returns:
            是否发送成功
        """
        # 临时使用测试配置
        original_config = self.config
        if test_config:
            self.config = test_config
        
        try:
            recipients = self.config.get('recipients', [])
            if not recipients:
                logger.warning("测试邮件：收件人列表为空")
                return False
            
            subject = "HyperLiquid 钱包分析系统 - 测试邮件"
            content = f"""
            <html>
            <body>
                <h2>测试邮件</h2>
                <p>这是一封来自 HyperLiquid 钱包分析系统的测试邮件。</p>
                <p>如果您收到这封邮件，说明邮件服务配置正确。</p>
                <hr>
                <p><strong>配置信息：</strong></p>
                <ul>
                    <li>SMTP 服务器: {self.config.get('smtp_host')}</li>
                    <li>SMTP 端口: {self.config.get('smtp_port')}</li>
                    <li>发件人: {self.config.get('sender_email')}</li>
                    <li>发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                </ul>
                <hr>
                <p style="color: #999; font-size: 12px;">
                    此邮件由系统自动发送，请勿回复。
                </p>
            </body>
            </html>
            """
            
            result = self.send_email(
                subject=subject,
                content=content,
                recipients=recipients,
                content_type='html'
            )
            
            return result
            
        finally:
            # 恢复原配置
            self.config = original_config
    
    def get_history(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取发送历史
        
        Args:
            limit: 返回数量
            offset: 偏移量
            status: 状态筛选
            
        Returns:
            历史记录列表
        """
        try:
            sql = """
                SELECT * FROM notification_history 
                WHERE channel = 'email'
            """
            params = []
            
            if status:
                sql += " AND status = ?"
                params.append(status)
            
            sql += " ORDER BY sent_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            rows = db.fetch_all(sql, tuple(params))
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"获取邮件历史失败: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取发送统计"""
        try:
            # 总发送数
            total = db.fetch_one(
                "SELECT COUNT(*) as count FROM notification_history WHERE channel = 'email'"
            )
            
            # 成功数
            success = db.fetch_one(
                "SELECT COUNT(*) as count FROM notification_history WHERE channel = 'email' AND status = 'sent'"
            )
            
            # 失败数
            failed = db.fetch_one(
                "SELECT COUNT(*) as count FROM notification_history WHERE channel = 'email' AND status = 'failed'"
            )
            
            # 今日发送数
            today = db.fetch_one("""
                SELECT COUNT(*) as count FROM notification_history 
                WHERE channel = 'email' AND DATE(sent_at) = DATE('now')
            """)
            
            return {
                'total': total['count'] if total else 0,
                'success': success['count'] if success else 0,
                'failed': failed['count'] if failed else 0,
                'today': today['count'] if today else 0,
                'success_rate': round(
                    (success['count'] / total['count'] * 100) if total and total['count'] > 0 else 0,
                    2
                )
            }
            
        except Exception as e:
            logger.error(f"获取邮件统计失败: {e}")
            return {
                'total': 0,
                'success': 0,
                'failed': 0,
                'today': 0,
                'success_rate': 0
            }


# 全局邮件服务实例
email_service = EmailService()


# 导出
__all__ = ['EmailService', 'email_service']


"""
日志收集器
收集、分类和存储系统日志
"""
import sys
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger as loguru_logger
import json

from app.database import db


class LogCollector:
    """日志收集器"""
    
    def __init__(self):
        self.enabled = True
        self._setup_loguru_handler()
    
    def _setup_loguru_handler(self):
        """设置 Loguru 处理器，自动收集日志到数据库"""
        
        def database_sink(message):
            """数据库日志接收器"""
            if not self.enabled:
                return
            
            try:
                record = message.record
                
                # 提取日志信息
                level = record["level"].name
                module = record["name"]
                msg = record["message"]
                
                # 提取额外信息
                extra = record.get("extra", {})
                category = extra.get("category", "system")
                user_id = extra.get("user_id")
                ip_address = extra.get("ip_address")
                
                # 提取详细信息
                details = {}
                if record["exception"]:
                    details["exception"] = {
                        "type": record["exception"].type.__name__,
                        "value": str(record["exception"].value),
                        "traceback": record["exception"].traceback
                    }
                
                # 保存到数据库
                self.save_log(
                    level=level,
                    module=module,
                    category=category,
                    message=msg,
                    details=details if details else None,
                    user_id=user_id,
                    ip_address=ip_address
                )
                
            except Exception as e:
                # 避免日志收集失败影响主程序
                print(f"日志收集失败: {e}", file=sys.stderr)
        
        # 添加数据库处理器
        loguru_logger.add(
            database_sink,
            level="INFO",
            format="{message}",
            filter=lambda record: record["extra"].get("to_db", True)
        )
    
    def save_log(
        self,
        level: str,
        module: str,
        category: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """
        保存日志到数据库
        
        Args:
            level: 日志级别
            module: 模块名称
            category: 分类
            message: 日志消息
            details: 详细信息
            user_id: 用户 ID
            ip_address: IP 地址
        """
        try:
            db.execute("""
                INSERT INTO system_logs 
                (level, module, category, message, details, user_id, ip_address, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                level,
                module,
                category,
                message,
                json.dumps(details) if details else None,
                user_id,
                ip_address,
                datetime.now().isoformat()
            ))
        except Exception as e:
            print(f"保存日志失败: {e}", file=sys.stderr)
    
    def log(
        self,
        level: str,
        message: str,
        module: str = "app",
        category: str = "system",
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
            message: 日志消息
            module: 模块名称
            category: 分类 (system/business/access/performance)
            details: 详细信息
            user_id: 用户 ID
            ip_address: IP 地址
        """
        # 构建 extra 数据
        extra = {
            "category": category,
            "user_id": user_id,
            "ip_address": ip_address,
            "to_db": True
        }
        
        # 使用 Loguru 记录日志
        log_func = getattr(loguru_logger.bind(**extra), level.lower())
        log_func(message)
    
    def log_api_access(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """
        记录 API 访问日志
        
        Args:
            method: HTTP 方法
            path: 请求路径
            status_code: 状态码
            duration: 请求耗时（秒）
            user_id: 用户 ID
            ip_address: IP 地址
        """
        message = f"{method} {path} - {status_code} ({duration:.3f}s)"
        
        self.log(
            level="INFO",
            message=message,
            module="api",
            category="access",
            details={
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration": duration
            },
            user_id=user_id,
            ip_address=ip_address
        )
    
    def log_performance(
        self,
        operation: str,
        duration: float,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        记录性能日志
        
        Args:
            operation: 操作名称
            duration: 耗时（秒）
            details: 详细信息
        """
        message = f"{operation} - {duration:.3f}s"
        
        perf_details = {
            "operation": operation,
            "duration": duration
        }
        if details:
            perf_details.update(details)
        
        self.log(
            level="INFO",
            message=message,
            module="performance",
            category="performance",
            details=perf_details
        )
    
    def log_business(
        self,
        event: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ):
        """
        记录业务日志
        
        Args:
            event: 事件类型
            message: 日志消息
            details: 详细信息
            user_id: 用户 ID
        """
        business_details = {
            "event": event
        }
        if details:
            business_details.update(details)
        
        self.log(
            level="INFO",
            message=message,
            module="business",
            category="business",
            details=business_details,
            user_id=user_id
        )
    
    def log_error(
        self,
        error: Exception,
        module: str = "app",
        context: Optional[Dict[str, Any]] = None
    ):
        """
        记录错误日志
        
        Args:
            error: 异常对象
            module: 模块名称
            context: 上下文信息
        """
        message = f"{type(error).__name__}: {str(error)}"
        
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        if context:
            error_details["context"] = context
        
        self.log(
            level="ERROR",
            message=message,
            module=module,
            category="system",
            details=error_details
        )
    
    def enable(self):
        """启用日志收集"""
        self.enabled = True
    
    def disable(self):
        """禁用日志收集"""
        self.enabled = False


# 全局日志收集器实例
log_collector = LogCollector()


# 导出
__all__ = ['LogCollector', 'log_collector']


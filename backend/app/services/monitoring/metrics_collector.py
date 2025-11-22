"""
指标收集器
定期收集和存储系统指标
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
import json

from app.database import db
from app.services.monitoring.system_monitor import system_monitor


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.enabled = False
        self.collection_task = None
        self.interval = 60  # 收集间隔（秒）
    
    def start(self, interval: int = 60):
        """
        启动指标收集
        
        Args:
            interval: 收集间隔（秒）
        """
        if self.enabled:
            logger.warning("指标收集器已在运行")
            return
        
        self.interval = interval
        self.enabled = True
        
        # 创建收集任务
        self.collection_task = asyncio.create_task(self._collection_loop())
        
        logger.info(f"指标收集器已启动，间隔: {interval} 秒")
    
    def stop(self):
        """停止指标收集"""
        self.enabled = False
        
        if self.collection_task:
            self.collection_task.cancel()
            self.collection_task = None
        
        logger.info("指标收集器已停止")
    
    async def _collection_loop(self):
        """收集循环"""
        while self.enabled:
            try:
                # 收集指标
                await self.collect_metrics()
                
                # 等待下次收集
                await asyncio.sleep(self.interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"收集指标失败: {e}")
                await asyncio.sleep(self.interval)
    
    async def collect_metrics(self):
        """收集当前指标"""
        try:
            # 获取所有指标
            metrics = system_monitor.get_all_metrics()
            
            # 保存到数据库（可选，用于历史趋势分析）
            # 这里简化处理，只保存关键指标
            key_metrics = {
                'cpu_percent': metrics['cpu']['usage_percent'],
                'memory_percent': metrics['memory']['percent'],
                'disk_percent': max([p['percent'] for p in metrics['disk']['partitions']], default=0),
                'process_memory_mb': round(metrics['process']['memory_info']['rss'] / 1024 / 1024, 2),
                'database_size_mb': metrics['database']['size_mb']
            }
            
            # 可以保存到时间序列数据库或文件
            # 这里简化为只在内存中保持最近的数据
            
            logger.debug(f"收集指标完成: CPU {key_metrics['cpu_percent']}%, "
                        f"内存 {key_metrics['memory_percent']}%")
            
        except Exception as e:
            logger.error(f"收集指标失败: {e}")
    
    def get_business_metrics(self) -> Dict[str, Any]:
        """
        获取业务指标
        
        Returns:
            业务指标字典
        """
        try:
            # 钱包统计
            wallets_total = db.fetch_one("SELECT COUNT(*) as count FROM wallets")
            wallets_active = db.fetch_one("""
                SELECT COUNT(*) as count FROM wallets 
                WHERE last_updated > datetime('now', '-1 day')
            """)
            
            # 交易统计
            trades_total = db.fetch_one("SELECT COUNT(*) as count FROM trades")
            trades_today = db.fetch_one("""
                SELECT COUNT(*) as count FROM trades 
                WHERE DATE(timestamp) = DATE('now')
            """)
            
            # 通知统计
            notifications_total = db.fetch_one("SELECT COUNT(*) as count FROM notifications")
            notifications_unread = db.fetch_one("""
                SELECT COUNT(*) as count FROM notifications WHERE is_read = 0
            """)
            
            # 用户统计
            users_total = db.fetch_one("SELECT COUNT(*) as count FROM users")
            users_active = db.fetch_one("""
                SELECT COUNT(*) as count FROM users 
                WHERE last_login > datetime('now', '-7 day')
            """)
            
            return {
                'wallets': {
                    'total': wallets_total['count'] if wallets_total else 0,
                    'active': wallets_active['count'] if wallets_active else 0
                },
                'trades': {
                    'total': trades_total['count'] if trades_total else 0,
                    'today': trades_today['count'] if trades_today else 0
                },
                'notifications': {
                    'total': notifications_total['count'] if notifications_total else 0,
                    'unread': notifications_unread['count'] if notifications_unread else 0
                },
                'users': {
                    'total': users_total['count'] if users_total else 0,
                    'active': users_active['count'] if users_active else 0
                }
            }
            
        except Exception as e:
            logger.error(f"获取业务指标失败: {e}")
            return {}
    
    def get_api_metrics(self) -> Dict[str, Any]:
        """
        获取 API 指标
        
        Returns:
            API 指标字典
        """
        try:
            # 从日志中统计 API 调用
            today = datetime.now().date().isoformat()
            
            # 总请求数
            total_requests = db.fetch_one("""
                SELECT COUNT(*) as count FROM system_logs 
                WHERE category = 'access' AND DATE(created_at) = ?
            """, (today,))
            
            # 错误请求数
            error_requests = db.fetch_one("""
                SELECT COUNT(*) as count FROM system_logs 
                WHERE category = 'access' AND level = 'ERROR' AND DATE(created_at) = ?
            """, (today,))
            
            # 平均响应时间（从 details 中提取）
            # 这里简化处理
            
            return {
                'total_requests': total_requests['count'] if total_requests else 0,
                'error_requests': error_requests['count'] if error_requests else 0,
                'success_rate': round(
                    ((total_requests['count'] - error_requests['count']) / total_requests['count'] * 100)
                    if total_requests and total_requests['count'] > 0 else 100,
                    2
                )
            }
            
        except Exception as e:
            logger.error(f"获取 API 指标失败: {e}")
            return {}


# 全局指标收集器实例
metrics_collector = MetricsCollector()


# 导出
__all__ = ['MetricsCollector', 'metrics_collector']


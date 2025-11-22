"""
系统监控器
监控系统资源使用情况、性能指标等
"""
import psutil
import platform
from typing import Dict, Any, List
from datetime import datetime
from loguru import logger

from app.database import db


class SystemMonitor:
    """系统监控器"""
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统基本信息
        
        Returns:
            系统信息字典
        """
        try:
            return {
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'hostname': platform.node(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {}
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """
        获取 CPU 信息
        
        Returns:
            CPU 信息字典
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            return {
                'usage_percent': cpu_percent,
                'count': cpu_count,
                'frequency': {
                    'current': cpu_freq.current if cpu_freq else 0,
                    'min': cpu_freq.min if cpu_freq else 0,
                    'max': cpu_freq.max if cpu_freq else 0
                },
                'per_cpu': psutil.cpu_percent(interval=1, percpu=True)
            }
        except Exception as e:
            logger.error(f"获取 CPU 信息失败: {e}")
            return {}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        获取内存信息
        
        Returns:
            内存信息字典
        """
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                }
            }
        except Exception as e:
            logger.error(f"获取内存信息失败: {e}")
            return {}
    
    def get_disk_info(self) -> Dict[str, Any]:
        """
        获取磁盘信息
        
        Returns:
            磁盘信息字典
        """
        try:
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except PermissionError:
                    continue
            
            # 磁盘 IO
            disk_io = psutil.disk_io_counters()
            
            return {
                'partitions': partitions,
                'io': {
                    'read_count': disk_io.read_count,
                    'write_count': disk_io.write_count,
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes
                } if disk_io else {}
            }
        except Exception as e:
            logger.error(f"获取磁盘信息失败: {e}")
            return {}
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        获取网络信息
        
        Returns:
            网络信息字典
        """
        try:
            # 网络 IO
            net_io = psutil.net_io_counters()
            
            # 网络连接
            connections = psutil.net_connections()
            
            return {
                'io': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv,
                    'errin': net_io.errin,
                    'errout': net_io.errout,
                    'dropin': net_io.dropin,
                    'dropout': net_io.dropout
                },
                'connections': {
                    'total': len(connections),
                    'established': len([c for c in connections if c.status == 'ESTABLISHED']),
                    'listen': len([c for c in connections if c.status == 'LISTEN'])
                }
            }
        except Exception as e:
            logger.error(f"获取网络信息失败: {e}")
            return {}
    
    def get_process_info(self) -> Dict[str, Any]:
        """
        获取进程信息
        
        Returns:
            进程信息字典
        """
        try:
            process = psutil.Process()
            
            return {
                'pid': process.pid,
                'name': process.name(),
                'status': process.status(),
                'cpu_percent': process.cpu_percent(interval=1),
                'memory_info': {
                    'rss': process.memory_info().rss,
                    'vms': process.memory_info().vms,
                    'percent': process.memory_percent()
                },
                'num_threads': process.num_threads(),
                'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0,
                'create_time': process.create_time()
            }
        except Exception as e:
            logger.error(f"获取进程信息失败: {e}")
            return {}
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        获取数据库信息
        
        Returns:
            数据库信息字典
        """
        try:
            # 数据库文件大小
            import os
            from app.config import DATA_DIR
            
            db_path = DATA_DIR / "hyperliquid_analyzer.db"
            db_size = os.path.getsize(db_path) if db_path.exists() else 0
            
            # 表统计
            tables = {}
            table_names = [
                'wallets', 'trades', 'positions', 'transfers',
                'leaderboards', 'system_configs', 'notifications',
                'ai_analysis_cache', 'users', 'system_logs'
            ]
            
            for table in table_names:
                try:
                    result = db.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                    tables[table] = result['count'] if result else 0
                except:
                    tables[table] = 0
            
            return {
                'size': db_size,
                'size_mb': round(db_size / 1024 / 1024, 2),
                'tables': tables,
                'total_records': sum(tables.values())
            }
        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            return {}
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        获取所有监控指标
        
        Returns:
            完整的监控指标字典
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'process': self.get_process_info(),
            'database': self.get_database_info()
        }
    
    def check_health(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态字典
        """
        try:
            issues = []
            warnings = []
            
            # 检查 CPU
            cpu_info = self.get_cpu_info()
            cpu_usage = cpu_info.get('usage_percent', 0)
            if cpu_usage > 90:
                issues.append(f"CPU 使用率过高: {cpu_usage}%")
            elif cpu_usage > 70:
                warnings.append(f"CPU 使用率较高: {cpu_usage}%")
            
            # 检查内存
            memory_info = self.get_memory_info()
            memory_percent = memory_info.get('percent', 0)
            if memory_percent > 90:
                issues.append(f"内存使用率过高: {memory_percent}%")
            elif memory_percent > 70:
                warnings.append(f"内存使用率较高: {memory_percent}%")
            
            # 检查磁盘
            disk_info = self.get_disk_info()
            for partition in disk_info.get('partitions', []):
                if partition['percent'] > 90:
                    issues.append(f"磁盘 {partition['mountpoint']} 使用率过高: {partition['percent']}%")
                elif partition['percent'] > 80:
                    warnings.append(f"磁盘 {partition['mountpoint']} 使用率较高: {partition['percent']}%")
            
            # 检查数据库
            db_info = self.get_database_info()
            db_size_mb = db_info.get('size_mb', 0)
            if db_size_mb > 1000:  # 超过 1GB
                warnings.append(f"数据库文件较大: {db_size_mb} MB")
            
            # 确定健康状态
            if issues:
                status = 'unhealthy'
                level = 'error'
            elif warnings:
                status = 'warning'
                level = 'warning'
            else:
                status = 'healthy'
                level = 'success'
            
            return {
                'status': status,
                'level': level,
                'issues': issues,
                'warnings': warnings,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                'status': 'error',
                'level': 'error',
                'issues': [f"健康检查失败: {str(e)}"],
                'warnings': [],
                'timestamp': datetime.now().isoformat()
            }
    
    def get_uptime(self) -> Dict[str, Any]:
        """
        获取系统运行时间
        
        Returns:
            运行时间信息
        """
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time
            
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return {
                'boot_time': datetime.fromtimestamp(boot_time).isoformat(),
                'uptime_seconds': int(uptime_seconds),
                'uptime_text': f"{days}天 {hours}小时 {minutes}分钟"
            }
        except Exception as e:
            logger.error(f"获取运行时间失败: {e}")
            return {}


# 全局系统监控器实例
system_monitor = SystemMonitor()


# 导出
__all__ = ['SystemMonitor', 'system_monitor']


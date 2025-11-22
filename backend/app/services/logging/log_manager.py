"""
日志管理器
提供日志查询、分析、归档等功能
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger
import json

from app.database import db


class LogManager:
    """日志管理器"""
    
    def query_logs(
        self,
        level: Optional[str] = None,
        module: Optional[str] = None,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        查询日志
        
        Args:
            level: 日志级别
            module: 模块名称
            category: 分类
            keyword: 关键词搜索
            start_time: 开始时间
            end_time: 结束时间
            user_id: 用户 ID
            limit: 返回数量
            offset: 偏移量
            
        Returns:
            (日志列表, 总数)
        """
        try:
            # 构建查询条件
            conditions = []
            params = []
            
            if level:
                conditions.append("level = ?")
                params.append(level)
            
            if module:
                conditions.append("module = ?")
                params.append(module)
            
            if category:
                conditions.append("category = ?")
                params.append(category)
            
            if keyword:
                conditions.append("message LIKE ?")
                params.append(f"%{keyword}%")
            
            if start_time:
                conditions.append("created_at >= ?")
                params.append(start_time)
            
            if end_time:
                conditions.append("created_at <= ?")
                params.append(end_time)
            
            if user_id:
                conditions.append("user_id = ?")
                params.append(user_id)
            
            # 构建 WHERE 子句
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # 查询总数
            count_sql = f"SELECT COUNT(*) as count FROM system_logs WHERE {where_clause}"
            count_result = db.fetch_one(count_sql, tuple(params))
            total = count_result['count'] if count_result else 0
            
            # 查询日志
            sql = f"""
                SELECT * FROM system_logs 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            rows = db.fetch_all(sql, tuple(params))
            
            # 处理结果
            logs = []
            for row in rows:
                log = dict(row)
                if log.get('details'):
                    try:
                        log['details'] = json.loads(log['details'])
                    except:
                        pass
                logs.append(log)
            
            return logs, total
            
        except Exception as e:
            logger.error(f"查询日志失败: {e}")
            return [], 0
    
    def get_log_statistics(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取日志统计信息
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            统计信息
        """
        try:
            # 时间条件
            time_condition = "1=1"
            params = []
            
            if start_time:
                time_condition += " AND created_at >= ?"
                params.append(start_time)
            
            if end_time:
                time_condition += " AND created_at <= ?"
                params.append(end_time)
            
            # 按级别统计
            level_stats = {}
            level_sql = f"""
                SELECT level, COUNT(*) as count 
                FROM system_logs 
                WHERE {time_condition}
                GROUP BY level
            """
            level_rows = db.fetch_all(level_sql, tuple(params))
            for row in level_rows:
                level_stats[row['level']] = row['count']
            
            # 按分类统计
            category_stats = {}
            category_sql = f"""
                SELECT category, COUNT(*) as count 
                FROM system_logs 
                WHERE {time_condition}
                GROUP BY category
            """
            category_rows = db.fetch_all(category_sql, tuple(params))
            for row in category_rows:
                category_stats[row['category']] = row['count']
            
            # 按模块统计
            module_stats = {}
            module_sql = f"""
                SELECT module, COUNT(*) as count 
                FROM system_logs 
                WHERE {time_condition}
                GROUP BY module
                ORDER BY count DESC
                LIMIT 10
            """
            module_rows = db.fetch_all(module_sql, tuple(params))
            for row in module_rows:
                module_stats[row['module']] = row['count']
            
            # 总数
            total_sql = f"SELECT COUNT(*) as count FROM system_logs WHERE {time_condition}"
            total_result = db.fetch_one(total_sql, tuple(params))
            total = total_result['count'] if total_result else 0
            
            # 错误数
            error_sql = f"""
                SELECT COUNT(*) as count FROM system_logs 
                WHERE {time_condition} AND level IN ('ERROR', 'CRITICAL')
            """
            error_result = db.fetch_one(error_sql, tuple(params))
            error_count = error_result['count'] if error_result else 0
            
            return {
                'total': total,
                'error_count': error_count,
                'level_stats': level_stats,
                'category_stats': category_stats,
                'module_stats': module_stats
            }
            
        except Exception as e:
            logger.error(f"获取日志统计失败: {e}")
            return {
                'total': 0,
                'error_count': 0,
                'level_stats': {},
                'category_stats': {},
                'module_stats': {}
            }
    
    def get_error_logs(
        self,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取最近的错误日志
        
        Args:
            hours: 最近几小时
            limit: 返回数量
            
        Returns:
            错误日志列表
        """
        try:
            start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            sql = """
                SELECT * FROM system_logs 
                WHERE level IN ('ERROR', 'CRITICAL') 
                AND created_at >= ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            
            rows = db.fetch_all(sql, (start_time, limit))
            
            logs = []
            for row in rows:
                log = dict(row)
                if log.get('details'):
                    try:
                        log['details'] = json.loads(log['details'])
                    except:
                        pass
                logs.append(log)
            
            return logs
            
        except Exception as e:
            logger.error(f"获取错误日志失败: {e}")
            return []
    
    def clear_old_logs(self, days: int = 30) -> int:
        """
        清理旧日志
        
        Args:
            days: 保留天数
            
        Returns:
            删除的日志数量
        """
        try:
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 查询要删除的数量
            count_sql = "SELECT COUNT(*) as count FROM system_logs WHERE created_at < ?"
            count_result = db.fetch_one(count_sql, (cutoff_time,))
            count = count_result['count'] if count_result else 0
            
            # 删除
            db.execute("DELETE FROM system_logs WHERE created_at < ?", (cutoff_time,))
            
            logger.info(f"清理了 {count} 条旧日志（{days} 天前）")
            
            return count
            
        except Exception as e:
            logger.error(f"清理旧日志失败: {e}")
            return 0
    
    def clear_all_logs(self) -> int:
        """
        清空所有日志
        
        Returns:
            删除的日志数量
        """
        try:
            # 查询总数
            count_sql = "SELECT COUNT(*) as count FROM system_logs"
            count_result = db.fetch_one(count_sql)
            count = count_result['count'] if count_result else 0
            
            # 删除
            db.execute("DELETE FROM system_logs")
            
            logger.info(f"清空了所有日志，共 {count} 条")
            
            return count
            
        except Exception as e:
            logger.error(f"清空日志失败: {e}")
            return 0
    
    def export_logs(
        self,
        level: Optional[str] = None,
        module: Optional[str] = None,
        category: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        format: str = 'csv'
    ) -> str:
        """
        导出日志
        
        Args:
            level: 日志级别
            module: 模块名称
            category: 分类
            start_time: 开始时间
            end_time: 结束时间
            format: 导出格式 (csv/json)
            
        Returns:
            导出的文件内容
        """
        try:
            # 查询日志
            logs, _ = self.query_logs(
                level=level,
                module=module,
                category=category,
                start_time=start_time,
                end_time=end_time,
                limit=10000  # 最多导出 10000 条
            )
            
            if format == 'csv':
                return self._export_csv(logs)
            elif format == 'json':
                return self._export_json(logs)
            else:
                raise ValueError(f"不支持的导出格式: {format}")
                
        except Exception as e:
            logger.error(f"导出日志失败: {e}")
            return ""
    
    def _export_csv(self, logs: List[Dict[str, Any]]) -> str:
        """导出为 CSV 格式"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow([
            'ID', '时间', '级别', '模块', '分类', '消息', '用户ID', 'IP地址'
        ])
        
        # 写入数据
        for log in logs:
            writer.writerow([
                log.get('id', ''),
                log.get('created_at', ''),
                log.get('level', ''),
                log.get('module', ''),
                log.get('category', ''),
                log.get('message', ''),
                log.get('user_id', ''),
                log.get('ip_address', '')
            ])
        
        return output.getvalue()
    
    def _export_json(self, logs: List[Dict[str, Any]]) -> str:
        """导出为 JSON 格式"""
        return json.dumps(logs, ensure_ascii=False, indent=2)
    
    def get_modules(self) -> List[str]:
        """获取所有模块列表"""
        try:
            sql = "SELECT DISTINCT module FROM system_logs ORDER BY module"
            rows = db.fetch_all(sql)
            return [row['module'] for row in rows]
        except Exception as e:
            logger.error(f"获取模块列表失败: {e}")
            return []


# 全局日志管理器实例
log_manager = LogManager()


# 导出
__all__ = ['LogManager', 'log_manager']


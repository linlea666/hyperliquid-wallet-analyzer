"""
AI 调度系统
智能管理 AI 分析任务的调度、优先级和缓存
"""
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger

from app.database import db
from .ai_analyzer import ai_analyzer
from .deepseek_service import deepseek_service


class Priority(Enum):
    """任务优先级"""
    HIGH = 1    # 高分钱包、异常钱包
    MEDIUM = 2  # 活跃钱包
    LOW = 3     # 普通钱包


class AnalysisTask:
    """分析任务"""
    
    def __init__(
        self,
        wallet_address: str,
        analysis_types: List[str],
        priority: Priority = Priority.MEDIUM,
        force: bool = False
    ):
        self.wallet_address = wallet_address
        self.analysis_types = analysis_types
        self.priority = priority
        self.force = force  # 是否强制分析（忽略缓存）
        self.created_at = datetime.now()
    
    def __lt__(self, other):
        """用于优先级队列排序"""
        return self.priority.value < other.priority.value


class AIScheduler:
    """AI 调度器"""
    
    def __init__(self):
        self.queue = asyncio.PriorityQueue()
        self.running = False
        self.current_task = None
        self.task_history = []
        
        # 缓存配置
        self.cache_ttl = {
            'style': 86400 * 7,      # 7天
            'strategy': 86400 * 7,   # 7天
            'risk': 86400 * 3,       # 3天
            'market': 3600           # 1小时
        }
    
    async def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("AI 调度器已在运行")
            return
        
        self.running = True
        logger.info("🤖 AI 调度器启动")
        
        # 启动后台任务处理
        asyncio.create_task(self._process_queue())
    
    def stop(self):
        """停止调度器"""
        self.running = False
        logger.info("AI 调度器停止")
    
    async def schedule_analysis(
        self,
        wallet_address: str,
        analysis_types: Optional[List[str]] = None,
        priority: Priority = Priority.MEDIUM,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        调度分析任务
        
        Args:
            wallet_address: 钱包地址
            analysis_types: 分析类型列表
            priority: 优先级
            force: 是否强制分析
            
        Returns:
            任务信息
        """
        if analysis_types is None:
            analysis_types = ['style', 'strategy', 'risk']
        
        # 检查是否需要分析
        if not force:
            needs_analysis = []
            for analysis_type in analysis_types:
                if self._should_analyze(wallet_address, analysis_type):
                    needs_analysis.append(analysis_type)
            
            if not needs_analysis:
                logger.info(f"钱包 {wallet_address} 的分析结果仍有效，使用缓存")
                return {
                    'status': 'cached',
                    'message': '使用缓存结果',
                    'wallet_address': wallet_address
                }
            
            analysis_types = needs_analysis
        
        # 创建任务
        task = AnalysisTask(wallet_address, analysis_types, priority, force)
        
        # 加入队列
        await self.queue.put((priority.value, task))
        
        logger.info(
            f"已调度分析任务: {wallet_address}, "
            f"类型: {analysis_types}, 优先级: {priority.name}"
        )
        
        return {
            'status': 'scheduled',
            'message': '任务已加入队列',
            'wallet_address': wallet_address,
            'analysis_types': analysis_types,
            'priority': priority.name,
            'queue_size': self.queue.qsize()
        }
    
    async def batch_schedule(
        self,
        wallet_addresses: List[str],
        analysis_types: Optional[List[str]] = None,
        priority: Priority = Priority.MEDIUM
    ) -> Dict[str, Any]:
        """
        批量调度分析任务
        
        Args:
            wallet_addresses: 钱包地址列表
            analysis_types: 分析类型列表
            priority: 优先级
            
        Returns:
            批量任务信息
        """
        scheduled = []
        cached = []
        
        for address in wallet_addresses:
            result = await self.schedule_analysis(
                address,
                analysis_types,
                priority,
                force=False
            )
            
            if result['status'] == 'scheduled':
                scheduled.append(address)
            else:
                cached.append(address)
        
        return {
            'total': len(wallet_addresses),
            'scheduled': len(scheduled),
            'cached': len(cached),
            'queue_size': self.queue.qsize()
        }
    
    async def _process_queue(self):
        """处理任务队列"""
        logger.info("AI 任务处理器启动")
        
        while self.running:
            try:
                # 检查是否启用
                if not deepseek_service.is_enabled():
                    await asyncio.sleep(60)
                    continue
                
                # 从队列获取任务（超时 1 秒）
                try:
                    priority, task = await asyncio.wait_for(
                        self.queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # 处理任务
                self.current_task = task
                await self._execute_task(task)
                self.current_task = None
                
                # 记录历史
                self.task_history.append({
                    'wallet_address': task.wallet_address,
                    'analysis_types': task.analysis_types,
                    'priority': task.priority.name,
                    'completed_at': datetime.now().isoformat()
                })
                
                # 限制历史记录数量
                if len(self.task_history) > 1000:
                    self.task_history = self.task_history[-1000:]
                
                # 任务间隔（避免过于频繁）
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"任务处理失败: {e}")
                await asyncio.sleep(5)
        
        logger.info("AI 任务处理器停止")
    
    async def _execute_task(self, task: AnalysisTask):
        """执行分析任务"""
        try:
            logger.info(f"开始执行任务: {task.wallet_address}")
            
            # 获取钱包数据
            wallet_data = self._get_wallet_data(task.wallet_address)
            
            if not wallet_data:
                logger.warning(f"钱包数据不存在: {task.wallet_address}")
                return
            
            # 执行分析
            results = {}
            
            for analysis_type in task.analysis_types:
                try:
                    if analysis_type == 'style':
                        result = await ai_analyzer.analyze_trading_style(wallet_data)
                    elif analysis_type == 'strategy':
                        result = await ai_analyzer.identify_strategy(wallet_data)
                    elif analysis_type == 'risk':
                        result = await ai_analyzer.assess_risk(wallet_data)
                    else:
                        logger.warning(f"未知的分析类型: {analysis_type}")
                        continue
                    
                    results[analysis_type] = result
                    
                    # 缓存结果
                    self._cache_result(task.wallet_address, analysis_type, result)
                    
                    logger.info(f"完成 {analysis_type} 分析: {task.wallet_address}")
                    
                except Exception as e:
                    logger.error(f"{analysis_type} 分析失败: {e}")
                    results[analysis_type] = {'error': str(e)}
            
            # 保存综合分析结果
            self._save_analysis(task.wallet_address, results)
            
            logger.info(f"任务执行完成: {task.wallet_address}")
            
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
    
    def _get_wallet_data(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """获取钱包数据"""
        try:
            # 从数据库获取钱包信息
            wallet = db.fetch_one(
                "SELECT * FROM wallets WHERE address = ?",
                (wallet_address,)
            )
            
            if not wallet:
                return None
            
            # 获取交易数据
            trades = db.fetch_all(
                "SELECT * FROM trades WHERE wallet_address = ? ORDER BY timestamp DESC LIMIT 100",
                (wallet_address,)
            )
            
            # 构建分析数据
            wallet_data = {
                'address': wallet_address,
                'score': wallet.get('score', 0),
                'metrics': json.loads(wallet.get('metrics', '{}')),
                'tags': json.loads(wallet.get('tags', '[]')),
                'trades': [dict(trade) for trade in trades] if trades else []
            }
            
            return wallet_data
            
        except Exception as e:
            logger.error(f"获取钱包数据失败: {e}")
            return None
    
    def _should_analyze(self, wallet_address: str, analysis_type: str) -> bool:
        """判断是否需要分析"""
        try:
            # 检查缓存
            cache = db.fetch_one("""
                SELECT * FROM ai_analysis_cache
                WHERE wallet_address = ? AND analysis_type = ?
            """, (wallet_address, analysis_type))
            
            if not cache:
                return True
            
            # 检查是否过期
            expires_at = datetime.fromisoformat(cache['expires_at'])
            if datetime.now() >= expires_at:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查分析需求失败: {e}")
            return True  # 出错时执行分析
    
    def _cache_result(
        self,
        wallet_address: str,
        analysis_type: str,
        result: Dict[str, Any]
    ):
        """缓存分析结果"""
        try:
            ttl = self.cache_ttl.get(analysis_type, 86400)
            expires_at = datetime.now() + timedelta(seconds=ttl)
            
            db.execute("""
                INSERT OR REPLACE INTO ai_analysis_cache
                (wallet_address, analysis_type, result, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                wallet_address,
                analysis_type,
                json.dumps(result, ensure_ascii=False),
                datetime.now().isoformat(),
                expires_at.isoformat()
            ))
            
            logger.debug(f"缓存分析结果: {wallet_address} - {analysis_type}")
            
        except Exception as e:
            logger.error(f"缓存结果失败: {e}")
    
    def _save_analysis(self, wallet_address: str, results: Dict[str, Any]):
        """保存综合分析结果"""
        try:
            # 更新钱包的 AI 标签
            ai_tags = self._extract_ai_tags(results)
            
            if ai_tags:
                # 获取现有标签
                wallet = db.fetch_one(
                    "SELECT tags FROM wallets WHERE address = ?",
                    (wallet_address,)
                )
                
                if wallet:
                    existing_tags = json.loads(wallet.get('tags', '[]'))
                    
                    # 移除旧的 AI 标签
                    existing_tags = [
                        tag for tag in existing_tags
                        if not tag.startswith('AI:')
                    ]
                    
                    # 添加新的 AI 标签
                    existing_tags.extend(ai_tags)
                    
                    # 更新数据库
                    db.execute(
                        "UPDATE wallets SET tags = ?, updated_at = ? WHERE address = ?",
                        (json.dumps(existing_tags, ensure_ascii=False), datetime.now().isoformat(), wallet_address)
                    )
                    
                    logger.info(f"更新 AI 标签: {wallet_address}, 标签: {ai_tags}")
            
        except Exception as e:
            logger.error(f"保存分析结果失败: {e}")
    
    def _extract_ai_tags(self, results: Dict[str, Any]) -> List[str]:
        """从分析结果中提取 AI 标签"""
        tags = []
        
        try:
            # 从交易风格提取
            if 'style' in results and 'style' in results['style']:
                tags.append(f"AI:{results['style']['style']}")
            
            # 从策略识别提取
            if 'strategy' in results and 'primary_strategy' in results['strategy']:
                tags.append(f"AI:{results['strategy']['primary_strategy']}")
            
            # 从风险评估提取
            if 'risk' in results and 'risk_level' in results['risk']:
                tags.append(f"AI:风险{results['risk']['risk_level']}")
            
        except Exception as e:
            logger.error(f"提取 AI 标签失败: {e}")
        
        return tags
    
    def get_cached_analysis(
        self,
        wallet_address: str,
        analysis_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取缓存的分析结果"""
        try:
            if analysis_type:
                # 获取特定类型的分析
                cache = db.fetch_one("""
                    SELECT * FROM ai_analysis_cache
                    WHERE wallet_address = ? AND analysis_type = ?
                    AND expires_at > ?
                """, (wallet_address, analysis_type, datetime.now().isoformat()))
                
                if cache:
                    return {
                        'analysis_type': analysis_type,
                        'result': json.loads(cache['result']),
                        'created_at': cache['created_at'],
                        'expires_at': cache['expires_at']
                    }
                
                return None
            
            else:
                # 获取所有类型的分析
                caches = db.fetch_all("""
                    SELECT * FROM ai_analysis_cache
                    WHERE wallet_address = ? AND expires_at > ?
                """, (wallet_address, datetime.now().isoformat()))
                
                if not caches:
                    return None
                
                results = {}
                for cache in caches:
                    results[cache['analysis_type']] = {
                        'result': json.loads(cache['result']),
                        'created_at': cache['created_at'],
                        'expires_at': cache['expires_at']
                    }
                
                return results
            
        except Exception as e:
            logger.error(f"获取缓存分析失败: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        return {
            'running': self.running,
            'queue_size': self.queue.qsize(),
            'current_task': {
                'wallet_address': self.current_task.wallet_address,
                'analysis_types': self.current_task.analysis_types,
                'priority': self.current_task.priority.name
            } if self.current_task else None,
            'completed_tasks': len(self.task_history),
            'recent_tasks': self.task_history[-10:] if self.task_history else []
        }


# 全局 AI 调度器实例
ai_scheduler = AIScheduler()


# 导出
__all__ = ['AIScheduler', 'ai_scheduler', 'Priority']


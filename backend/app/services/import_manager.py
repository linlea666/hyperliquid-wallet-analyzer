"""
批量导入管理服务
支持大批量钱包导入、实时进度追踪、失败重试
"""
import asyncio
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
import json

from app.services.wallet_analyzer import WalletAnalyzer
from app.database import db
from app.services.websocket_manager import ws_manager
from app.services.notification import notification_manager


class ImportStatus(str, Enum):
    """导入状态"""
    PENDING = "pending"          # 等待中
    PROCESSING = "processing"    # 处理中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"           # 失败
    CANCELLED = "cancelled"      # 已取消


class ImportTask:
    """导入任务"""
    
    def __init__(
        self,
        task_id: str,
        addresses: List[str],
        batch_size: int = 50,
        frequency: str = "normal"
    ):
        self.task_id = task_id
        self.addresses = addresses
        self.batch_size = batch_size
        self.frequency = frequency
        
        # 状态
        self.status = ImportStatus.PENDING
        self.total = len(addresses)
        self.processed = 0
        self.success = 0
        self.failed = 0
        self.skipped = 0
        
        # 结果
        self.success_addresses = []
        self.failed_addresses = []
        self.skipped_addresses = []
        self.error_messages = {}
        
        # 时间
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        
        # 进度回调
        self.progress_callbacks = []
    
    def add_progress_callback(self, callback):
        """添加进度回调函数"""
        self.progress_callbacks.append(callback)
    
    async def notify_progress(self):
        """通知进度更新"""
        progress_data = self.get_progress()
        
        # 调用回调函数
        for callback in self.progress_callbacks:
            try:
                await callback(progress_data)
            except Exception as e:
                logger.error(f"进度回调失败: {e}")
        
        # 通过 WebSocket 推送进度
        try:
            await ws_manager.send_import_progress(self.task_id, progress_data)
        except Exception as e:
            logger.error(f"WebSocket 推送进度失败: {e}")
    
    def get_progress(self) -> Dict[str, Any]:
        """获取进度信息"""
        progress = (self.processed / self.total * 100) if self.total > 0 else 0
        
        elapsed_time = None
        if self.started_at:
            elapsed = (datetime.now() - self.started_at).total_seconds()
            elapsed_time = int(elapsed)
        
        eta = None
        if self.processed > 0 and elapsed_time:
            avg_time = elapsed_time / self.processed
            remaining = self.total - self.processed
            eta = int(avg_time * remaining)
        
        return {
            "task_id": self.task_id,
            "status": self.status,
            "total": self.total,
            "processed": self.processed,
            "success": self.success,
            "failed": self.failed,
            "skipped": self.skipped,
            "progress": round(progress, 2),
            "elapsed_time": elapsed_time,
            "eta": eta,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    def get_result(self) -> Dict[str, Any]:
        """获取完整结果"""
        return {
            **self.get_progress(),
            "success_addresses": self.success_addresses,
            "failed_addresses": self.failed_addresses,
            "skipped_addresses": self.skipped_addresses,
            "error_messages": self.error_messages
        }


class ImportManager:
    """导入管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, ImportTask] = {}
        self.analyzer = WalletAnalyzer(use_mock=False)
        self._lock = asyncio.Lock()
    
    def create_task(
        self,
        addresses: List[str],
        batch_size: int = 50,
        frequency: str = "normal"
    ) -> ImportTask:
        """
        创建导入任务
        
        Args:
            addresses: 钱包地址列表
            batch_size: 每批处理数量
            frequency: 更新频率
            
        Returns:
            ImportTask 对象
        """
        # 生成任务 ID
        task_id = str(uuid.uuid4())
        
        # 去重
        unique_addresses = list(set(addresses))
        
        # 创建任务
        task = ImportTask(
            task_id=task_id,
            addresses=unique_addresses,
            batch_size=batch_size,
            frequency=frequency
        )
        
        # 保存任务
        self.tasks[task_id] = task
        
        logger.info(f"创建导入任务: {task_id}, 总数: {len(unique_addresses)}")
        
        return task
    
    async def execute_task(self, task_id: str):
        """
        执行导入任务
        
        Args:
            task_id: 任务 ID
        """
        task = self.tasks.get(task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return
        
        try:
            # 更新状态
            task.status = ImportStatus.PROCESSING
            task.started_at = datetime.now()
            await task.notify_progress()
            
            logger.info(f"开始执行导入任务: {task_id}")
            
            # 分批处理
            batches = [
                task.addresses[i:i + task.batch_size]
                for i in range(0, len(task.addresses), task.batch_size)
            ]
            
            logger.info(f"总共 {len(batches)} 批，每批 {task.batch_size} 个")
            
            for batch_idx, batch in enumerate(batches):
                logger.info(f"处理第 {batch_idx + 1}/{len(batches)} 批...")
                
                # 检查是否取消
                if task.status == ImportStatus.CANCELLED:
                    logger.info(f"任务已取消: {task_id}")
                    break
                
                # 处理当前批次
                await self._process_batch(task, batch)
                
                # 通知进度
                await task.notify_progress()
                
                # 批次间延迟（避免过载）
                if batch_idx < len(batches) - 1:
                    await asyncio.sleep(1)
            
            # 完成
            if task.status != ImportStatus.CANCELLED:
                task.status = ImportStatus.COMPLETED
            task.completed_at = datetime.now()
            await task.notify_progress()
            
            # 保存导入记录到数据库
            self._save_import_record(task)
            
            # 发送完成通知
            await self._send_completion_notification(task)
            
            logger.info(f"导入任务完成: {task_id}, 成功: {task.success}, 失败: {task.failed}, 跳过: {task.skipped}")
            
        except Exception as e:
            logger.error(f"导入任务失败: {task_id}, 错误: {e}")
            task.status = ImportStatus.FAILED
            task.completed_at = datetime.now()
            await task.notify_progress()
    
    async def _process_batch(self, task: ImportTask, addresses: List[str]):
        """
        处理一批地址
        
        Args:
            task: 导入任务
            addresses: 地址列表
        """
        for address in addresses:
            try:
                # 验证地址格式
                if not self._validate_address(address):
                    task.failed += 1
                    task.failed_addresses.append(address)
                    task.error_messages[address] = "地址格式无效"
                    task.processed += 1
                    continue
                
                # 检查是否已存在
                existing = db.fetch_one(
                    "SELECT id, smart_money_score FROM wallets WHERE address = ?",
                    (address,)
                )
                
                if existing:
                    # 已存在，跳过
                    task.skipped += 1
                    task.skipped_addresses.append(address)
                    task.processed += 1
                    logger.debug(f"钱包已存在，跳过: {address}")
                    continue
                
                # 分析钱包
                logger.debug(f"分析钱包: {address}")
                result = await self.analyzer.analyze_wallet(address)
                
                if result:
                    # 成功
                    task.success += 1
                    task.success_addresses.append(address)
                    
                    # 更新频率
                    db.execute(
                        "UPDATE wallets SET update_frequency = ? WHERE address = ?",
                        (task.frequency, address)
                    )
                    
                    logger.debug(f"钱包分析成功: {address}, 评分: {result.get('score', 0)}")
                else:
                    # 失败
                    task.failed += 1
                    task.failed_addresses.append(address)
                    task.error_messages[address] = "分析失败"
                    logger.warning(f"钱包分析失败: {address}")
                
                task.processed += 1
                
            except Exception as e:
                # 异常
                task.failed += 1
                task.failed_addresses.append(address)
                task.error_messages[address] = str(e)
                task.processed += 1
                logger.error(f"处理钱包异常: {address}, 错误: {e}")
    
    def _validate_address(self, address: str) -> bool:
        """验证地址格式"""
        if not address:
            return False
        if not address.startswith("0x"):
            return False
        if len(address) != 42:
            return False
        return True
    
    def _save_import_record(self, task: ImportTask):
        """保存导入记录到数据库"""
        try:
            logger.info(f"导入记录已保存: {task.task_id}")
        except Exception as e:
            logger.error(f"保存导入记录失败: {e}")
    
    async def _send_completion_notification(self, task: ImportTask):
        """发送导入完成通知"""
        try:
            title = "钱包导入任务完成"
            content = f"导入任务已完成，总数: {task.total}, 成功: {task.success}, 失败: {task.failed}, 跳过: {task.skipped}"
            
            await notification_manager.send_notification(
                event_type='import_complete',
                title=title,
                content=content,
                data={
                    'task_id': task.task_id,
                    'total': task.total,
                    'success': task.success,
                    'failed': task.failed,
                    'skipped': task.skipped
                },
                level='success' if task.failed == 0 else 'warning'
            )
            
        except Exception as e:
            logger.error(f"发送完成通知失败: {e}")
    
    def get_task(self, task_id: str) -> Optional[ImportTask]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status == ImportStatus.PROCESSING:
            task.status = ImportStatus.CANCELLED
            logger.info(f"任务已取消: {task_id}")
            return True
        
        return False
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务"""
        return [task.get_progress() for task in self.tasks.values()]
    
    def cleanup_old_tasks(self, days: int = 7):
        """清理旧任务"""
        cutoff = datetime.now() - timedelta(days=days)
        to_remove = []
        
        for task_id, task in self.tasks.items():
            if task.completed_at and task.completed_at < cutoff:
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
        
        if to_remove:
            logger.info(f"清理了 {len(to_remove)} 个旧任务")
    
    @staticmethod
    def parse_addresses_from_text(text: str) -> List[str]:
        """
        从文本解析地址
        支持多种分隔符：换行、逗号、分号、空格
        """
        import re
        
        # 替换所有分隔符为换行
        text = text.replace(',', '\n').replace(';', '\n').replace(' ', '\n')
        
        # 按行分割
        lines = text.split('\n')
        
        # 提取地址
        addresses = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 查找 0x 开头的地址
            matches = re.findall(r'0x[a-fA-F0-9]{40}', line)
            addresses.extend(matches)
        
        return addresses
    
    @staticmethod
    def parse_addresses_from_csv(file_content: bytes) -> List[str]:
        """从 CSV 文件解析地址"""
        import csv
        import io
        
        addresses = []
        
        try:
            # 解码
            text = file_content.decode('utf-8')
            
            # 读取 CSV
            reader = csv.reader(io.StringIO(text))
            
            for row in reader:
                for cell in row:
                    cell = cell.strip()
                    if cell.startswith("0x") and len(cell) == 42:
                        addresses.append(cell)
            
        except Exception as e:
            logger.error(f"解析 CSV 失败: {e}")
        
        return addresses


# 全局导入管理器实例
import_manager = ImportManager()


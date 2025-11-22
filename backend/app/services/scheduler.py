"""
数据采集调度服务
定时更新钱包数据
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from app.services.wallet_analyzer import WalletAnalyzer
from app.database import db
from app.config import config


class DataScheduler:
    """数据采集调度器"""
    
    def __init__(self):
        """初始化调度器"""
        self.scheduler = AsyncIOScheduler()
        self.analyzer = WalletAnalyzer(use_mock=False)
        self.is_running = False
        
        # 从配置读取更新频率
        scheduler_config = config.get_config("system").get("scheduler", {})
        self.update_intervals = scheduler_config.get("update_intervals", {
            "active": 300,      # 活跃钱包：5 分钟
            "normal": 1800,     # 普通钱包：30 分钟
            "inactive": 3600    # 不活跃钱包：1 小时
        })
        
        self.batch_size = scheduler_config.get("batch_size", 10)
        self.max_concurrent = scheduler_config.get("max_concurrent", 5)
    
    def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已在运行")
            return
        
        logger.info("=" * 60)
        logger.info("启动数据采集调度器...")
        logger.info("=" * 60)
        
        # 添加定时任务
        
        # 1. 活跃钱包更新（每 5 分钟）
        self.scheduler.add_job(
            self.update_active_wallets,
            trigger=IntervalTrigger(seconds=self.update_intervals["active"]),
            id="update_active_wallets",
            name="更新活跃钱包",
            max_instances=1,
            coalesce=True
        )
        
        # 2. 普通钱包更新（每 30 分钟）
        self.scheduler.add_job(
            self.update_normal_wallets,
            trigger=IntervalTrigger(seconds=self.update_intervals["normal"]),
            id="update_normal_wallets",
            name="更新普通钱包",
            max_instances=1,
            coalesce=True
        )
        
        # 3. 不活跃钱包更新（每 1 小时）
        self.scheduler.add_job(
            self.update_inactive_wallets,
            trigger=IntervalTrigger(seconds=self.update_intervals["inactive"]),
            id="update_inactive_wallets",
            name="更新不活跃钱包",
            max_instances=1,
            coalesce=True
        )
        
        # 4. 清理过期数据（每天凌晨 3 点）
        self.scheduler.add_job(
            self.cleanup_old_data,
            trigger=CronTrigger(hour=3, minute=0),
            id="cleanup_old_data",
            name="清理过期数据",
            max_instances=1
        )
        
        # 5. 统计报告（每天早上 9 点）
        self.scheduler.add_job(
            self.generate_daily_report,
            trigger=CronTrigger(hour=9, minute=0),
            id="generate_daily_report",
            name="生成每日报告",
            max_instances=1
        )
        
        self.scheduler.start()
        self.is_running = True
        
        logger.info("✅ 调度器启动成功")
        logger.info(f"活跃钱包更新间隔: {self.update_intervals['active']} 秒")
        logger.info(f"普通钱包更新间隔: {self.update_intervals['normal']} 秒")
        logger.info(f"不活跃钱包更新间隔: {self.update_intervals['inactive']} 秒")
        logger.info("=" * 60)
    
    def stop(self):
        """停止调度器"""
        if not self.is_running:
            return
        
        logger.info("停止数据采集调度器...")
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("✅ 调度器已停止")
    
    async def update_active_wallets(self):
        """更新活跃钱包"""
        try:
            logger.info("🔄 开始更新活跃钱包...")
            
            # 获取需要更新的活跃钱包
            wallets = db.fetch_all("""
                SELECT address, last_updated 
                FROM wallets 
                WHERE update_frequency = 'active'
                ORDER BY last_updated ASC NULLS FIRST
                LIMIT ?
            """, (self.batch_size,))
            
            if not wallets:
                logger.info("没有需要更新的活跃钱包")
                return
            
            addresses = [w["address"] for w in wallets]
            logger.info(f"准备更新 {len(addresses)} 个活跃钱包")
            
            # 批量更新
            results = await self.analyzer.batch_analyze_wallets(
                addresses,
                max_concurrent=self.max_concurrent
            )
            
            success_count = len([r for r in results if r])
            logger.info(f"✅ 活跃钱包更新完成: {success_count}/{len(addresses)}")
            
        except Exception as e:
            logger.error(f"❌ 更新活跃钱包失败: {e}")
    
    async def update_normal_wallets(self):
        """更新普通钱包"""
        try:
            logger.info("🔄 开始更新普通钱包...")
            
            wallets = db.fetch_all("""
                SELECT address, last_updated 
                FROM wallets 
                WHERE update_frequency = 'normal'
                ORDER BY last_updated ASC NULLS FIRST
                LIMIT ?
            """, (self.batch_size,))
            
            if not wallets:
                logger.info("没有需要更新的普通钱包")
                return
            
            addresses = [w["address"] for w in wallets]
            logger.info(f"准备更新 {len(addresses)} 个普通钱包")
            
            results = await self.analyzer.batch_analyze_wallets(
                addresses,
                max_concurrent=self.max_concurrent
            )
            
            success_count = len([r for r in results if r])
            logger.info(f"✅ 普通钱包更新完成: {success_count}/{len(addresses)}")
            
        except Exception as e:
            logger.error(f"❌ 更新普通钱包失败: {e}")
    
    async def update_inactive_wallets(self):
        """更新不活跃钱包"""
        try:
            logger.info("🔄 开始更新不活跃钱包...")
            
            wallets = db.fetch_all("""
                SELECT address, last_updated 
                FROM wallets 
                WHERE update_frequency = 'inactive'
                ORDER BY last_updated ASC NULLS FIRST
                LIMIT ?
            """, (self.batch_size // 2,))  # 不活跃钱包更新数量减半
            
            if not wallets:
                logger.info("没有需要更新的不活跃钱包")
                return
            
            addresses = [w["address"] for w in wallets]
            logger.info(f"准备更新 {len(addresses)} 个不活跃钱包")
            
            results = await self.analyzer.batch_analyze_wallets(
                addresses,
                max_concurrent=self.max_concurrent
            )
            
            success_count = len([r for r in results if r])
            logger.info(f"✅ 不活跃钱包更新完成: {success_count}/{len(addresses)}")
            
        except Exception as e:
            logger.error(f"❌ 更新不活跃钱包失败: {e}")
    
    async def update_wallet_frequency(self):
        """
        根据钱包活跃度自动调整更新频率
        - 高评分且最近有交易 -> active
        - 中等评分或有一定交易 -> normal
        - 低评分或长时间无交易 -> inactive
        """
        try:
            logger.info("🔄 调整钱包更新频率...")
            
            # 活跃钱包：评分 > 80 且最近 24 小时有交易
            db.execute("""
                UPDATE wallets 
                SET update_frequency = 'active'
                WHERE smart_money_score >= 80
                AND (julianday('now') - julianday(last_updated)) < 1
            """)
            
            # 普通钱包：评分 60-80 或最近 7 天有交易
            db.execute("""
                UPDATE wallets 
                SET update_frequency = 'normal'
                WHERE (smart_money_score >= 60 AND smart_money_score < 80)
                OR (julianday('now') - julianday(last_updated)) < 7
            """)
            
            # 不活跃钱包：评分 < 60 且超过 7 天无更新
            db.execute("""
                UPDATE wallets 
                SET update_frequency = 'inactive'
                WHERE smart_money_score < 60
                AND (julianday('now') - julianday(last_updated)) >= 7
            """)
            
            logger.info("✅ 钱包更新频率调整完成")
            
        except Exception as e:
            logger.error(f"❌ 调整更新频率失败: {e}")
    
    async def cleanup_old_data(self):
        """清理过期数据"""
        try:
            logger.info("🧹 开始清理过期数据...")
            
            # 清理 30 天前的通知
            result = db.execute("""
                DELETE FROM notifications 
                WHERE created_at < datetime('now', '-30 days')
            """)
            logger.info(f"清理了 {result.rowcount} 条过期通知")
            
            # 清理过期的 AI 缓存
            result = db.execute("""
                DELETE FROM ai_analysis_cache 
                WHERE expires_at < datetime('now')
            """)
            logger.info(f"清理了 {result.rowcount} 条过期 AI 缓存")
            
            logger.info("✅ 数据清理完成")
            
        except Exception as e:
            logger.error(f"❌ 数据清理失败: {e}")
    
    async def generate_daily_report(self):
        """生成每日统计报告"""
        try:
            logger.info("📊 生成每日统计报告...")
            
            # 统计总钱包数
            total_wallets = db.fetch_one("SELECT COUNT(*) as count FROM wallets")
            total_count = total_wallets["count"] if total_wallets else 0
            
            # 统计各等级钱包数
            grade_stats = db.fetch_all("""
                SELECT score_grade, COUNT(*) as count 
                FROM wallets 
                GROUP BY score_grade 
                ORDER BY score_grade
            """)
            
            # 统计今日更新数
            today_updates = db.fetch_one("""
                SELECT COUNT(*) as count 
                FROM wallets 
                WHERE date(last_updated) = date('now')
            """)
            today_count = today_updates["count"] if today_updates else 0
            
            # 统计平均评分
            avg_score = db.fetch_one("""
                SELECT AVG(smart_money_score) as avg_score 
                FROM wallets 
                WHERE smart_money_score > 0
            """)
            avg = avg_score["avg_score"] if avg_score and avg_score["avg_score"] else 0
            
            # 输出报告
            logger.info("=" * 60)
            logger.info("📊 每日统计报告")
            logger.info("=" * 60)
            logger.info(f"总钱包数: {total_count}")
            logger.info(f"今日更新: {today_count}")
            logger.info(f"平均评分: {avg:.2f}")
            logger.info("\n等级分布:")
            for stat in grade_stats:
                logger.info(f"  {stat['score_grade']} 级: {stat['count']} 个")
            logger.info("=" * 60)
            
            # 创建系统通知
            db.execute("""
                INSERT INTO notifications 
                (type, title, content, level, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "system_report",
                "每日统计报告",
                f"总钱包数: {total_count}, 今日更新: {today_count}, 平均评分: {avg:.2f}",
                "info",
                datetime.now().isoformat()
            ))
            
        except Exception as e:
            logger.error(f"❌ 生成报告失败: {e}")
    
    async def add_wallet(self, address: str, frequency: str = "normal"):
        """
        添加新钱包到监控列表
        
        Args:
            address: 钱包地址
            frequency: 更新频率 (active/normal/inactive)
        """
        try:
            # 检查是否已存在
            existing = db.fetch_one(
                "SELECT id FROM wallets WHERE address = ?",
                (address,)
            )
            
            if existing:
                logger.info(f"钱包已存在: {address}")
                return
            
            # 立即分析钱包
            logger.info(f"添加新钱包: {address}")
            result = await self.analyzer.analyze_wallet(address)
            
            if result:
                # 更新频率
                db.execute(
                    "UPDATE wallets SET update_frequency = ? WHERE address = ?",
                    (frequency, address)
                )
                logger.info(f"✅ 钱包添加成功: {address}, 评分: {result['score']}")
            else:
                logger.error(f"❌ 钱包分析失败: {address}")
            
        except Exception as e:
            logger.error(f"❌ 添加钱包失败 {address}: {e}")
    
    async def remove_wallet(self, address: str):
        """从监控列表移除钱包"""
        try:
            db.execute("DELETE FROM wallets WHERE address = ?", (address,))
            logger.info(f"✅ 钱包已移除: {address}")
        except Exception as e:
            logger.error(f"❌ 移除钱包失败 {address}: {e}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "is_running": self.is_running,
            "jobs": jobs,
            "update_intervals": self.update_intervals,
            "batch_size": self.batch_size,
            "max_concurrent": self.max_concurrent
        }


# 全局调度器实例
scheduler = DataScheduler()


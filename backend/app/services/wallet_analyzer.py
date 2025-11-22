"""
钱包分析服务
整合 API 数据采集、指标计算、评分等功能
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import json

from app.services.hyperliquid import HyperLiquidClient
from app.services.scoring import TradingScorer, MetricsCalculator
from app.database import db
from loguru import logger


class WalletAnalyzer:
    """钱包分析器 - 核心业务逻辑"""
    
    def __init__(self, use_mock: bool = False):
        """
        初始化分析器
        
        Args:
            use_mock: 是否使用模拟数据
        """
        self.hl_client = HyperLiquidClient(use_mock=use_mock)
        self.scorer = TradingScorer()
        self.metrics_calc = MetricsCalculator()
    
    async def analyze_wallet(
        self, 
        address: str,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        分析钱包并存入数据库
        
        Args:
            address: 钱包地址
            force_update: 是否强制更新（忽略缓存）
            
        Returns:
            分析结果字典
        """
        try:
            logger.info(f"开始分析钱包: {address}")
            
            # 1. 检查数据库中是否已存在
            existing_wallet = db.fetch_one(
                "SELECT * FROM wallets WHERE address = ?",
                (address,)
            )
            
            # 如果存在且不强制更新，检查更新时间
            if existing_wallet and not force_update:
                last_updated = existing_wallet.get("last_updated")
                if last_updated:
                    # 如果最近 1 小时内更新过，直接返回
                    # TODO: 根据 update_frequency 动态调整
                    pass
            
            # 2. 从 HyperLiquid API 获取数据
            logger.info("获取钱包数据...")
            wallet_data = await self.hl_client.get_wallet_data(address)
            
            if not wallet_data:
                logger.error(f"无法获取钱包数据: {address}")
                return None
            
            # 3. 计算所有指标
            logger.info("计算交易指标...")
            metrics = self._calculate_all_metrics(wallet_data)
            
            # 4. 计算综合评分
            logger.info("计算综合评分...")
            score_result = self.scorer.calculate_comprehensive_score(
                metrics,
                wallet_data.get("trades", []),
                wallet_data.get("positions", [])
            )
            
            # 5. 合并数据
            final_data = {
                **metrics,
                "smart_money_score": score_result["total_score"],
                "score_grade": score_result["grade"],
                "tags": json.dumps(score_result["tags"]),
                "style": score_result["style"],
                "last_updated": datetime.now().isoformat()
            }
            
            # 6. 存入数据库
            logger.info("保存到数据库...")
            self._save_to_database(address, final_data, wallet_data)
            
            logger.info(f"✅ 钱包分析完成: {address}, 评分: {score_result['total_score']}, 等级: {score_result['grade']}")
            
            return {
                "address": address,
                "score": score_result["total_score"],
                "grade": score_result["grade"],
                "tags": score_result["tags"],
                "style": score_result["style"],
                "metrics": metrics,
                "dimension_scores": score_result["dimension_scores"]
            }
            
        except Exception as e:
            logger.error(f"分析钱包失败 {address}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _calculate_all_metrics(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算所有交易指标
        
        Args:
            wallet_data: 从 API 获取的原始钱包数据
            
        Returns:
            包含所有指标的字典
        """
        metrics = {}
        
        # 基础信息
        metrics["address"] = wallet_data.get("address")
        metrics["current_balance"] = wallet_data.get("account_value", 0)
        metrics["initial_capital"] = wallet_data.get("initial_capital", 0)
        metrics["total_deposits"] = wallet_data.get("total_deposits", 0)
        metrics["total_withdrawals"] = wallet_data.get("total_withdrawals", 0)
        metrics["net_deposits"] = metrics["total_deposits"] - metrics["total_withdrawals"]
        
        # 交易统计
        trades = wallet_data.get("trades", [])
        metrics["closed_trades_count"] = len(trades)
        
        # 盈亏统计
        metrics["total_pnl"] = wallet_data.get("total_pnl", 0)
        
        # ROI
        if metrics["initial_capital"] > 0:
            metrics["roi"] = self.metrics_calc.calculate_roi(
                metrics["total_pnl"],
                metrics["initial_capital"]
            )
        else:
            metrics["roi"] = 0
        
        # 胜率和盈亏比
        if trades:
            winning_trades = [t for t in trades if float(t.get("pnl", 0)) > 0]
            losing_trades = [t for t in trades if float(t.get("pnl", 0)) < 0]
            
            metrics["win_rate"] = self.metrics_calc.calculate_win_rate(
                len(winning_trades),
                len(trades)
            )
            
            # 计算平均盈利和平均亏损
            if winning_trades:
                avg_win = sum(float(t.get("pnl", 0)) for t in winning_trades) / len(winning_trades)
            else:
                avg_win = 0
            
            if losing_trades:
                avg_loss = sum(abs(float(t.get("pnl", 0))) for t in losing_trades) / len(losing_trades)
            else:
                avg_loss = 0
            
            metrics["profit_loss_ratio"] = self.metrics_calc.calculate_profit_loss_ratio(
                avg_win, avg_loss
            )
        else:
            metrics["win_rate"] = 0
            metrics["profit_loss_ratio"] = 0
        
        # 最大回撤
        equity_curve = wallet_data.get("equity_curve", [])
        if equity_curve:
            metrics["max_drawdown"] = self.metrics_calc.calculate_max_drawdown(equity_curve)
            # 保存不同时间周期的资金曲线
            metrics["equity_curve_all"] = json.dumps(equity_curve[-1000:])  # 最多保存 1000 个点
        else:
            metrics["max_drawdown"] = 0
            metrics["equity_curve_all"] = json.dumps([])
        
        # 高级指标
        returns = self._calculate_returns(trades)
        if returns:
            metrics["sharpe_ratio"] = self.metrics_calc.calculate_sharpe_ratio(returns)
            metrics["sortino_ratio"] = self.metrics_calc.calculate_sortino_ratio(returns)
            metrics["volatility"] = self.metrics_calc.calculate_volatility(returns)
        else:
            metrics["sharpe_ratio"] = 0
            metrics["sortino_ratio"] = 0
            metrics["volatility"] = 0
        
        # 钱包年龄
        first_trade_time = wallet_data.get("first_trade_time")
        if first_trade_time:
            if isinstance(first_trade_time, str):
                first_trade_time = datetime.fromisoformat(first_trade_time.replace('Z', '+00:00'))
            metrics["first_trade_time"] = first_trade_time.isoformat()
            metrics["wallet_age_days"] = (datetime.now() - first_trade_time.replace(tzinfo=None)).days
        else:
            metrics["first_trade_time"] = None
            metrics["wallet_age_days"] = 0
        
        # 年化收益
        if metrics["wallet_age_days"] > 0:
            metrics["annual_return"] = self.metrics_calc.calculate_annual_return(
                metrics["roi"],
                metrics["wallet_age_days"]
            )
            
            # 卡玛比率
            if metrics["max_drawdown"] > 0:
                metrics["calmar_ratio"] = self.metrics_calc.calculate_calmar_ratio(
                    metrics["annual_return"],
                    metrics["max_drawdown"]
                )
            else:
                metrics["calmar_ratio"] = 0
        else:
            metrics["annual_return"] = 0
            metrics["calmar_ratio"] = 0
        
        # 交易行为特征
        if metrics["wallet_age_days"] > 0:
            metrics["trading_frequency"] = self.metrics_calc.identify_trading_frequency(
                metrics["closed_trades_count"],
                metrics["wallet_age_days"]
            )
        else:
            metrics["trading_frequency"] = "unknown"
        
        # 平均持仓时间
        if trades:
            holding_times = [
                float(t.get("holding_time_minutes", 0)) 
                for t in trades 
                if t.get("holding_time_minutes")
            ]
            if holding_times:
                avg_holding = sum(holding_times) / len(holding_times)
                metrics["holding_period"] = self.metrics_calc.identify_holding_period(avg_holding)
            else:
                metrics["holding_period"] = "unknown"
        else:
            metrics["holding_period"] = "unknown"
        
        # 多空偏好
        if trades:
            long_trades = [t for t in trades if t.get("side", "").lower() in ["buy", "long"]]
            short_trades = [t for t in trades if t.get("side", "").lower() in ["sell", "short"]]
            metrics["long_short_preference"] = self.metrics_calc.identify_long_short_preference(
                len(long_trades),
                len(short_trades)
            )
        else:
            metrics["long_short_preference"] = "unknown"
        
        # 偏好币种（交易最多的前 5 个）
        if trades:
            coin_counts = {}
            for trade in trades:
                coin = trade.get("symbol", "")
                if coin:
                    coin_counts[coin] = coin_counts.get(coin, 0) + 1
            
            favorite_coins = sorted(coin_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            metrics["favorite_coins"] = json.dumps([coin for coin, _ in favorite_coins])
        else:
            metrics["favorite_coins"] = json.dumps([])
        
        # 清算次数（从交易记录或其他数据源获取）
        metrics["liquidation_count"] = wallet_data.get("liquidation_count", 0)
        
        # 保证金比率（从持仓数据获取）
        positions = wallet_data.get("positions", [])
        if positions and metrics["current_balance"] > 0:
            total_margin_used = sum(float(p.get("margin_used", 0)) for p in positions)
            metrics["margin_ratio"] = total_margin_used / metrics["current_balance"]
        else:
            metrics["margin_ratio"] = 0
        
        return metrics
    
    def _calculate_returns(self, trades: List[Dict[str, Any]]) -> List[float]:
        """
        从交易记录计算收益率序列
        
        Args:
            trades: 交易记录列表
            
        Returns:
            收益率列表
        """
        if not trades:
            return []
        
        returns = []
        cumulative_capital = 0
        
        for trade in trades:
            pnl = float(trade.get("pnl", 0))
            # 简化计算：假设每笔交易的收益率 = pnl / (累计资金 + 初始资金的一部分)
            # 实际应该基于每笔交易的投入资金
            if cumulative_capital > 0:
                ret = pnl / cumulative_capital
                returns.append(ret)
            cumulative_capital += pnl
        
        return returns
    
    def _save_to_database(
        self, 
        address: str, 
        metrics: Dict[str, Any],
        wallet_data: Dict[str, Any]
    ):
        """
        保存钱包数据到数据库
        
        Args:
            address: 钱包地址
            metrics: 计算好的指标
            wallet_data: 原始钱包数据
        """
        # 1. 保存/更新钱包基础信息
        existing = db.fetch_one("SELECT id FROM wallets WHERE address = ?", (address,))
        
        if existing:
            # 更新
            update_fields = []
            update_values = []
            for key, value in metrics.items():
                if key != "address":
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            update_values.append(address)
            sql = f"UPDATE wallets SET {', '.join(update_fields)} WHERE address = ?"
            db.execute(sql, tuple(update_values))
            logger.info(f"更新钱包记录: {address}")
        else:
            # 插入
            fields = list(metrics.keys())
            placeholders = ", ".join(["?" for _ in fields])
            values = [metrics[f] for f in fields]
            
            sql = f"INSERT INTO wallets ({', '.join(fields)}) VALUES ({placeholders})"
            db.execute(sql, tuple(values))
            logger.info(f"创建钱包记录: {address}")
        
        # 2. 保存交易记录
        trades = wallet_data.get("trades", [])
        if trades:
            self._save_trades(address, trades)
        
        # 3. 保存持仓
        positions = wallet_data.get("positions", [])
        if positions:
            self._save_positions(address, positions)
        
        # 4. 保存资金流水
        transfers = wallet_data.get("transfers", [])
        if transfers:
            self._save_transfers(address, transfers)
    
    def _save_trades(self, address: str, trades: List[Dict[str, Any]]):
        """保存交易记录"""
        # 清空旧记录（或者只保存新的）
        # db.execute("DELETE FROM trades WHERE wallet_address = ?", (address,))
        
        for trade in trades:
            # 检查是否已存在（基于 hash 或 tid）
            trade_hash = trade.get("hash")
            if trade_hash:
                existing = db.fetch_one(
                    "SELECT id FROM trades WHERE wallet_address = ? AND hash = ?",
                    (address, trade_hash)
                )
                if existing:
                    continue  # 跳过已存在的
            
            # 插入新交易
            db.execute("""
                INSERT INTO trades 
                (wallet_address, timestamp, symbol, side, size, entry_price, exit_price, 
                 pnl, pnl_percentage, holding_time_minutes, fees, hash, oid, tid, 
                 direction, start_position, closed_pnl, fee_token)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                address,
                trade.get("timestamp"),
                trade.get("symbol"),
                trade.get("side"),
                trade.get("size"),
                trade.get("entry_price"),
                trade.get("exit_price"),
                trade.get("pnl"),
                trade.get("pnl_percentage"),
                trade.get("holding_time_minutes"),
                trade.get("fees"),
                trade.get("hash"),
                trade.get("oid"),
                trade.get("tid"),
                trade.get("direction"),
                trade.get("start_position"),
                trade.get("closed_pnl"),
                trade.get("fee_token")
            ))
    
    def _save_positions(self, address: str, positions: List[Dict[str, Any]]):
        """保存持仓"""
        # 清空旧持仓
        db.execute("DELETE FROM positions WHERE wallet_address = ?", (address,))
        
        for pos in positions:
            db.execute("""
                INSERT INTO positions 
                (wallet_address, symbol, side, size, entry_price, mark_price, 
                 unrealized_pnl, leverage, margin_used, liquidation_price, 
                 position_value, return_on_equity, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                address,
                pos.get("symbol"),
                pos.get("side"),
                pos.get("size"),
                pos.get("entry_price"),
                pos.get("mark_price"),
                pos.get("unrealized_pnl"),
                pos.get("leverage"),
                pos.get("margin_used"),
                pos.get("liquidation_price"),
                pos.get("position_value"),
                pos.get("return_on_equity"),
                datetime.now().isoformat()
            ))
    
    def _save_transfers(self, address: str, transfers: List[Dict[str, Any]]):
        """保存资金流水"""
        for transfer in transfers:
            # 检查是否已存在
            tx_hash = transfer.get("tx_hash")
            if tx_hash:
                existing = db.fetch_one(
                    "SELECT id FROM transfers WHERE wallet_address = ? AND tx_hash = ?",
                    (address, tx_hash)
                )
                if existing:
                    continue
            
            db.execute("""
                INSERT INTO transfers 
                (wallet_address, timestamp, type, amount, tx_hash, status, fee)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                address,
                transfer.get("timestamp"),
                transfer.get("type"),
                transfer.get("amount"),
                transfer.get("tx_hash"),
                transfer.get("status", "confirmed"),
                transfer.get("fee", 0)
            ))
    
    async def batch_analyze_wallets(
        self, 
        addresses: List[str],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        批量分析钱包
        
        Args:
            addresses: 钱包地址列表
            max_concurrent: 最大并发数
            
        Returns:
            分析结果列表
        """
        import asyncio
        
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_semaphore(addr):
            async with semaphore:
                return await self.analyze_wallet(addr)
        
        tasks = [analyze_with_semaphore(addr) for addr in addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤掉异常
        valid_results = [r for r in results if r and not isinstance(r, Exception)]
        
        logger.info(f"批量分析完成: {len(valid_results)}/{len(addresses)} 成功")
        
        return valid_results
    
    def get_wallet_from_db(self, address: str) -> Optional[Dict[str, Any]]:
        """从数据库获取钱包信息"""
        wallet = db.fetch_one(
            "SELECT * FROM wallets WHERE address = ?",
            (address,)
        )
        
        if wallet:
            # 解析 JSON 字段
            if wallet.get("tags"):
                try:
                    wallet["tags"] = json.loads(wallet["tags"])
                except:
                    wallet["tags"] = []
            
            if wallet.get("favorite_coins"):
                try:
                    wallet["favorite_coins"] = json.loads(wallet["favorite_coins"])
                except:
                    wallet["favorite_coins"] = []
        
        return wallet
    
    def get_top_wallets(
        self, 
        limit: int = 20,
        sort_by: str = "smart_money_score",
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        获取排名靠前的钱包
        
        Args:
            limit: 返回数量
            sort_by: 排序字段
            filters: 筛选条件
            
        Returns:
            钱包列表
        """
        # 构建 SQL
        sql = "SELECT * FROM wallets WHERE 1=1"
        params = []
        
        # 应用筛选条件
        if filters:
            for key, value in filters.items():
                if isinstance(value, dict):
                    if "min" in value:
                        sql += f" AND {key} >= ?"
                        params.append(value["min"])
                    if "max" in value:
                        sql += f" AND {key} <= ?"
                        params.append(value["max"])
                else:
                    sql += f" AND {key} = ?"
                    params.append(value)
        
        # 排序
        sql += f" ORDER BY {sort_by} DESC LIMIT ?"
        params.append(limit)
        
        wallets = db.fetch_all(sql, tuple(params))
        
        # 解析 JSON 字段
        for wallet in wallets:
            if wallet.get("tags"):
                try:
                    wallet["tags"] = json.loads(wallet["tags"])
                except:
                    wallet["tags"] = []
        
        return wallets


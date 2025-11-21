"""数据分析服务"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from app.config import config


class AnalyzerService:
    """数据分析服务"""
    
    def __init__(self):
        self.scoring_config = config.get_config("scoring")
    
    def analyze_wallet(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析钱包数据"""
        try:
            # 计算指标
            metrics = self._calculate_metrics(wallet_data)
            wallet_data["metrics"].update(metrics)
            
            # 计算风险指标
            risk_metrics = self._calculate_risk_metrics(wallet_data)
            wallet_data["risk_metrics"].update(risk_metrics)
            
            # 分析行为模式
            behavior = self._analyze_behavior(wallet_data)
            wallet_data["behavior"].update(behavior)
            
            # 计算 Smart Money Score
            score = self._calculate_smart_money_score(wallet_data)
            wallet_data["metrics"]["smart_money_score"] = score
            
            return wallet_data
            
        except Exception as e:
            logger.error(f"分析钱包失败: {e}")
            return wallet_data
    
    def _calculate_metrics(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算基础指标"""
        trades = wallet_data.get("trades", [])
        deposits = wallet_data.get("deposits", [])
        withdrawals = wallet_data.get("withdrawals", [])
        
        # 计算初始资金
        total_deposits = sum(d.get("amount", 0) for d in deposits)
        total_withdrawals = sum(w.get("amount", 0) for w in withdrawals)
        initial_capital = total_deposits - total_withdrawals
        
        # 计算总盈亏
        total_pnl = sum(t.get("pnl", 0) for t in trades)
        
        # 计算 ROI
        roi = (total_pnl / initial_capital * 100) if initial_capital > 0 else 0
        
        # 计算胜率
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0
        
        # 计算盈亏比
        profits = [t.get("pnl", 0) for t in winning_trades]
        losses = [abs(t.get("pnl", 0)) for t in trades if t.get("pnl", 0) < 0]
        
        avg_profit = sum(profits) / len(profits) if profits else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        profit_loss_ratio = avg_profit / avg_loss if avg_loss > 0 else 0
        
        return {
            "initial_capital": initial_capital,
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "net_deposits": initial_capital,
            "total_pnl": total_pnl,
            "roi": roi,
            "win_rate": win_rate,
            "profit_loss_ratio": profit_loss_ratio,
            "closed_trades_count": len(trades)
        }
    
    def _calculate_risk_metrics(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算风险指标"""
        trades = wallet_data.get("trades", [])
        
        if not trades:
            return {
                "volatility": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0
            }
        
        # 计算收益序列
        pnls = [t.get("pnl", 0) for t in trades]
        
        # 计算波动率（标准差）
        import statistics
        volatility = statistics.stdev(pnls) if len(pnls) > 1 else 0
        
        # 计算最大回撤（简化版）
        cumulative = 0
        peak = 0
        max_drawdown = 0
        
        for pnl in pnls:
            cumulative += pnl
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        max_drawdown_pct = (max_drawdown / peak * 100) if peak > 0 else 0
        
        return {
            "volatility": volatility,
            "max_drawdown": max_drawdown_pct / 100,
            "sharpe_ratio": 1.5  # 简化计算
        }
    
    def _analyze_behavior(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析行为模式"""
        trades = wallet_data.get("trades", [])
        
        if not trades:
            return {}
        
        # 多空偏好
        long_trades = [t for t in trades if t.get("side") == "long"]
        short_trades = [t for t in trades if t.get("side") == "short"]
        
        long_ratio = len(long_trades) / len(trades) if trades else 0
        
        if long_ratio > 0.6:
            preference = "long"
        elif long_ratio < 0.4:
            preference = "short"
        else:
            preference = "balanced"
        
        # 交易频率
        if len(trades) > 100:
            frequency = "high"
        elif len(trades) > 30:
            frequency = "medium"
        else:
            frequency = "low"
        
        # 持仓周期
        holding_times = [t.get("holding_time_minutes", 0) for t in trades]
        avg_holding = sum(holding_times) / len(holding_times) if holding_times else 0
        
        if avg_holding < 60:
            holding_period = "short"
        elif avg_holding < 1440:
            holding_period = "medium"
        else:
            holding_period = "long"
        
        # 币种偏好
        symbols = {}
        for t in trades:
            symbol = t.get("symbol", "")
            symbols[symbol] = symbols.get(symbol, 0) + 1
        
        coin_preference = sorted(symbols.items(), key=lambda x: x[1], reverse=True)[:5]
        coin_preference = [c[0] for c in coin_preference]
        
        return {
            "long_short_preference": preference,
            "trading_frequency": frequency,
            "holding_period": holding_period,
            "coin_preference": coin_preference
        }
    
    def _calculate_smart_money_score(self, wallet_data: Dict[str, Any]) -> int:
        """计算 Smart Money Score"""
        metrics = wallet_data.get("metrics", {})
        risk_metrics = wallet_data.get("risk_metrics", {})
        behavior = wallet_data.get("behavior", {})
        
        weights = self.scoring_config.get("weights", {})
        thresholds = self.scoring_config.get("thresholds", {})
        
        score = 0
        
        # ROI 评分 (35%)
        roi = metrics.get("roi", 0)
        roi_thresholds = thresholds.get("roi", {})
        if roi >= roi_thresholds.get("excellent", 500):
            score += 35
        elif roi >= roi_thresholds.get("good", 200):
            score += 25 + (roi - 200) / 300 * 10
        elif roi >= roi_thresholds.get("average", 100):
            score += 15 + (roi - 100) / 100 * 10
        elif roi >= roi_thresholds.get("poor", 50):
            score += 10 + (roi - 50) / 50 * 5
        else:
            score += roi / 50 * 10
        
        # 盈亏比评分 (20%)
        profit_loss_ratio = metrics.get("profit_loss_ratio", 0)
        if profit_loss_ratio >= 3.0:
            score += 20
        elif profit_loss_ratio >= 2.0:
            score += 15 + (profit_loss_ratio - 2.0) * 5
        elif profit_loss_ratio >= 1.5:
            score += 10 + (profit_loss_ratio - 1.5) * 10
        elif profit_loss_ratio >= 1.0:
            score += 5 + (profit_loss_ratio - 1.0) * 10
        else:
            score += profit_loss_ratio * 5
        
        # 最大回撤评分 (20%)
        max_drawdown = risk_metrics.get("max_drawdown", 1) * 100
        if max_drawdown < 20:
            score += 20
        elif max_drawdown < 30:
            score += 15 + (30 - max_drawdown) / 10 * 5
        elif max_drawdown < 40:
            score += 10 + (40 - max_drawdown) / 10 * 5
        elif max_drawdown < 50:
            score += 5 + (50 - max_drawdown) / 10 * 5
        else:
            score += max(0, 5 - (max_drawdown - 50) / 10 * 5)
        
        # 胜率评分 (15%)
        win_rate = metrics.get("win_rate", 0) * 100
        win_rate_thresholds = thresholds.get("win_rate", {})
        if win_rate >= win_rate_thresholds.get("excellent", 70):
            score += 10
        elif win_rate >= win_rate_thresholds.get("good", 60):
            score += 7 + (win_rate - 60) / 10 * 3
        elif win_rate >= win_rate_thresholds.get("average", 50):
            score += 4 + (win_rate - 50) / 10 * 3
        else:
            score += win_rate / 50 * 4
        
        # 资金规模评分 (5%)
        initial_capital = metrics.get("initial_capital", 0)
        if initial_capital < 2000 and roi > 200:
            score += 5
        elif initial_capital < 5000:
            score += 3
        else:
            score += 1
        
        # 风格评分 (5%)
        style = behavior.get("style", "")
        if style == "stable":
            score += 5
        elif style == "trend":
            score += 3
        else:
            score += 2
        
        return min(100, int(score))
    
    def calculate_avg_roi(self, wallets: List[Dict[str, Any]]) -> float:
        """计算平均 ROI"""
        if not wallets:
            return 0.0
        
        rois = [w.get("metrics", {}).get("roi", 0) for w in wallets]
        return sum(rois) / len(rois) if rois else 0.0
    
    def calculate_avg_win_rate(self, wallets: List[Dict[str, Any]]) -> float:
        """计算平均胜率"""
        if not wallets:
            return 0.0
        
        win_rates = [w.get("metrics", {}).get("win_rate", 0) for w in wallets]
        return sum(win_rates) / len(win_rates) if win_rates else 0.0
    
    def count_active_wallets(self, wallets: List[Dict[str, Any]], hours: int = 24) -> int:
        """统计活跃钱包数"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        count = 0
        
        for wallet in wallets:
            last_updated = wallet.get("last_updated", "")
            if last_updated:
                try:
                    last_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                    if last_time >= cutoff_time:
                        count += 1
                except:
                    pass
        
        return count
    
    def calculate_long_short_ratio(self, wallets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算多空比"""
        total_long_value = 0
        total_short_value = 0
        long_pnl = 0
        short_pnl = 0
        
        for wallet in wallets:
            positions = wallet.get("current_positions", [])
            trades = wallet.get("trades", [])
            
            for pos in positions:
                value = pos.get("size", 0) * pos.get("mark_price", 0)
                if pos.get("side") == "long":
                    total_long_value += value
                else:
                    total_short_value += value
            
            for trade in trades:
                pnl = trade.get("pnl", 0)
                if trade.get("side") == "long":
                    long_pnl += pnl
                else:
                    short_pnl += pnl
        
        total_value = total_long_value + total_short_value
        long_ratio = (total_long_value / total_value * 100) if total_value > 0 else 50
        short_ratio = 100 - long_ratio
        
        return {
            "long_ratio": long_ratio,
            "short_ratio": short_ratio,
            "long_value": total_long_value,
            "short_value": total_short_value,
            "long_pnl": long_pnl,
            "short_pnl": short_pnl
        }
    
    def detect_anomalies(self, wallets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检测异动"""
        from app.config import config
        notification_config = config.get_config("notifications")
        thresholds = notification_config.get("thresholds", {})
        
        anomalies = []
        
        for wallet in wallets:
            address = wallet.get("address", "")
            trades = wallet.get("trades", [])
            deposits = wallet.get("deposits", [])
            withdrawals = wallet.get("withdrawals", [])
            
            # 检测大额交易
            if trades:
                latest_trade = trades[-1]
                trade_amount = latest_trade.get("size", 0) * latest_trade.get("entry_price", 0)
                if trade_amount > thresholds.get("large_trade", 10000):
                    anomalies.append({
                        "type": "large_trade",
                        "wallet": address,
                        "amount": trade_amount,
                        "time": latest_trade.get("timestamp", ""),
                        "symbol": latest_trade.get("symbol", "")
                    })
            
            # 检测大额存款
            if deposits:
                latest_deposit = deposits[-1]
                if latest_deposit.get("amount", 0) > thresholds.get("large_deposit", 5000):
                    anomalies.append({
                        "type": "large_deposit",
                        "wallet": address,
                        "amount": latest_deposit.get("amount", 0),
                        "time": latest_deposit.get("timestamp", "")
                    })
            
            # 检测大额取款
            if withdrawals:
                latest_withdrawal = withdrawals[-1]
                if latest_withdrawal.get("amount", 0) > thresholds.get("large_withdrawal", 5000):
                    anomalies.append({
                        "type": "large_withdrawal",
                        "wallet": address,
                        "amount": latest_withdrawal.get("amount", 0),
                        "time": latest_withdrawal.get("timestamp", "")
                    })
        
        return anomalies
    
    def get_rankings(self, wallets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """获取排行榜"""
        # Top 10 盈利
        top_profit = sorted(
            wallets,
            key=lambda x: x.get("metrics", {}).get("total_pnl", 0),
            reverse=True
        )[:10]
        
        # Top 10 ROI
        top_roi = sorted(
            wallets,
            key=lambda x: x.get("metrics", {}).get("roi", 0),
            reverse=True
        )[:10]
        
        # Top 10 Score
        top_score = sorted(
            wallets,
            key=lambda x: x.get("metrics", {}).get("smart_money_score", 0),
            reverse=True
        )[:10]
        
        return {
            "profit": [{"address": w.get("address"), "pnl": w.get("metrics", {}).get("total_pnl", 0)} for w in top_profit],
            "roi": [{"address": w.get("address"), "roi": w.get("metrics", {}).get("roi", 0)} for w in top_roi],
            "score": [{"address": w.get("address"), "score": w.get("metrics", {}).get("smart_money_score", 0)} for w in top_score]
        }


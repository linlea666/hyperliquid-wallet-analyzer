"""
交易者综合评分模型
实现 6 大维度、20+ 指标的智能评分系统
"""
import math
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import statistics

class TradingScorer:
    """交易者评分器"""
    
    # 默认权重配置（6 大维度）
    DEFAULT_WEIGHTS = {
        "profitability": 0.30,      # 盈利能力 30%
        "risk_control": 0.25,        # 风险控制 25%
        "stability": 0.20,           # 稳定性 20%
        "efficiency": 0.15,          # 交易效率 15%
        "experience": 0.05,          # 经验水平 5%
        "growth": 0.05               # 成长性 5%
    }
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        初始化评分器
        
        Args:
            weights: 自定义权重配置
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
        
    def calculate_comprehensive_score(
        self, 
        wallet_data: Dict[str, Any],
        trades: List[Dict[str, Any]] = None,
        positions: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        计算综合评分
        
        Args:
            wallet_data: 钱包基础数据
            trades: 交易记录列表
            positions: 持仓列表
            
        Returns:
            包含各维度得分和综合得分的字典
        """
        scores = {}
        
        # 1. 盈利能力维度 (30%)
        scores["profitability"] = self._score_profitability(wallet_data, trades)
        
        # 2. 风险控制维度 (25%)
        scores["risk_control"] = self._score_risk_control(wallet_data, trades)
        
        # 3. 稳定性维度 (20%)
        scores["stability"] = self._score_stability(wallet_data, trades)
        
        # 4. 交易效率维度 (15%)
        scores["efficiency"] = self._score_efficiency(wallet_data, trades)
        
        # 5. 经验水平维度 (5%)
        scores["experience"] = self._score_experience(wallet_data, trades)
        
        # 6. 成长性维度 (5%)
        scores["growth"] = self._score_growth(wallet_data, trades)
        
        # 计算加权总分
        total_score = sum(
            scores[dim] * self.weights[dim] 
            for dim in self.weights.keys()
        )
        
        # 确保分数在 0-100 之间
        total_score = max(0, min(100, total_score))
        
        # 计算等级
        grade = self._calculate_grade(total_score)
        
        # 生成标签
        tags = self._generate_tags(wallet_data, scores)
        
        # 识别交易风格
        style = self._identify_trading_style(wallet_data, trades)
        
        return {
            "total_score": round(total_score, 2),
            "grade": grade,
            "dimension_scores": {k: round(v, 2) for k, v in scores.items()},
            "tags": tags,
            "style": style,
            "evaluated_at": datetime.now().isoformat()
        }
    
    def _score_profitability(
        self, 
        wallet_data: Dict[str, Any],
        trades: List[Dict[str, Any]] = None
    ) -> float:
        """
        盈利能力评分 (0-100)
        
        指标：
        - ROI (投资回报率) - 40%
        - 总盈亏 - 30%
        - 年化收益率 - 30%
        """
        score = 0.0
        
        # ROI 评分 (40%)
        roi = float(wallet_data.get("roi", 0))
        if roi >= 500:
            roi_score = 100
        elif roi >= 300:
            roi_score = 90
        elif roi >= 200:
            roi_score = 80
        elif roi >= 100:
            roi_score = 70
        elif roi >= 50:
            roi_score = 60
        elif roi >= 20:
            roi_score = 50
        elif roi >= 0:
            roi_score = 40
        elif roi >= -20:
            roi_score = 30
        elif roi >= -50:
            roi_score = 20
        else:
            roi_score = 10
        score += roi_score * 0.4
        
        # 总盈亏评分 (30%)
        total_pnl = float(wallet_data.get("total_pnl", 0))
        if total_pnl >= 50000:
            pnl_score = 100
        elif total_pnl >= 20000:
            pnl_score = 90
        elif total_pnl >= 10000:
            pnl_score = 80
        elif total_pnl >= 5000:
            pnl_score = 70
        elif total_pnl >= 2000:
            pnl_score = 60
        elif total_pnl >= 1000:
            pnl_score = 50
        elif total_pnl >= 0:
            pnl_score = 40
        elif total_pnl >= -1000:
            pnl_score = 30
        elif total_pnl >= -5000:
            pnl_score = 20
        else:
            pnl_score = 10
        score += pnl_score * 0.3
        
        # 年化收益率评分 (30%)
        annual_return = float(wallet_data.get("annual_return", 0))
        if annual_return >= 300:
            annual_score = 100
        elif annual_return >= 200:
            annual_score = 90
        elif annual_return >= 150:
            annual_score = 80
        elif annual_return >= 100:
            annual_score = 70
        elif annual_return >= 50:
            annual_score = 60
        elif annual_return >= 20:
            annual_score = 50
        elif annual_return >= 0:
            annual_score = 40
        else:
            annual_score = 20
        score += annual_score * 0.3
        
        return score
    
    def _score_risk_control(
        self, 
        wallet_data: Dict[str, Any],
        trades: List[Dict[str, Any]] = None
    ) -> float:
        """
        风险控制评分 (0-100)
        
        指标：
        - 最大回撤 - 40%
        - 盈亏比 - 30%
        - 清算次数 - 20%
        - 夏普比率 - 10%
        """
        score = 0.0
        
        # 最大回撤评分 (40%) - 越小越好
        max_drawdown = float(wallet_data.get("max_drawdown", 0))
        if max_drawdown <= 5:
            dd_score = 100
        elif max_drawdown <= 10:
            dd_score = 90
        elif max_drawdown <= 15:
            dd_score = 80
        elif max_drawdown <= 20:
            dd_score = 70
        elif max_drawdown <= 30:
            dd_score = 60
        elif max_drawdown <= 40:
            dd_score = 50
        elif max_drawdown <= 50:
            dd_score = 40
        elif max_drawdown <= 60:
            dd_score = 30
        elif max_drawdown <= 70:
            dd_score = 20
        else:
            dd_score = 10
        score += dd_score * 0.4
        
        # 盈亏比评分 (30%) - 越大越好
        profit_loss_ratio = float(wallet_data.get("profit_loss_ratio", 0))
        if profit_loss_ratio >= 5:
            plr_score = 100
        elif profit_loss_ratio >= 4:
            plr_score = 95
        elif profit_loss_ratio >= 3:
            plr_score = 90
        elif profit_loss_ratio >= 2.5:
            plr_score = 85
        elif profit_loss_ratio >= 2:
            plr_score = 80
        elif profit_loss_ratio >= 1.5:
            plr_score = 70
        elif profit_loss_ratio >= 1.2:
            plr_score = 60
        elif profit_loss_ratio >= 1:
            plr_score = 50
        elif profit_loss_ratio >= 0.8:
            plr_score = 40
        else:
            plr_score = 20
        score += plr_score * 0.3
        
        # 清算次数评分 (20%) - 越少越好
        liquidation_count = int(wallet_data.get("liquidation_count", 0))
        if liquidation_count == 0:
            liq_score = 100
        elif liquidation_count == 1:
            liq_score = 70
        elif liquidation_count == 2:
            liq_score = 50
        elif liquidation_count == 3:
            liq_score = 30
        else:
            liq_score = 10
        score += liq_score * 0.2
        
        # 夏普比率评分 (10%)
        sharpe_ratio = float(wallet_data.get("sharpe_ratio", 0))
        if sharpe_ratio >= 3:
            sharpe_score = 100
        elif sharpe_ratio >= 2:
            sharpe_score = 90
        elif sharpe_ratio >= 1.5:
            sharpe_score = 80
        elif sharpe_ratio >= 1:
            sharpe_score = 70
        elif sharpe_ratio >= 0.5:
            sharpe_score = 60
        elif sharpe_ratio >= 0:
            sharpe_score = 50
        else:
            sharpe_score = 30
        score += sharpe_score * 0.1
        
        return score
    
    def _score_stability(
        self, 
        wallet_data: Dict[str, Any],
        trades: List[Dict[str, Any]] = None
    ) -> float:
        """
        稳定性评分 (0-100)
        
        指标：
        - 胜率 - 50%
        - 波动率 - 30%
        - 交易一致性 - 20%
        """
        score = 0.0
        
        # 胜率评分 (50%)
        win_rate = float(wallet_data.get("win_rate", 0)) * 100  # 转为百分比
        if win_rate >= 80:
            wr_score = 100
        elif win_rate >= 70:
            wr_score = 95
        elif win_rate >= 65:
            wr_score = 90
        elif win_rate >= 60:
            wr_score = 85
        elif win_rate >= 55:
            wr_score = 80
        elif win_rate >= 50:
            wr_score = 75
        elif win_rate >= 45:
            wr_score = 65
        elif win_rate >= 40:
            wr_score = 55
        elif win_rate >= 35:
            wr_score = 45
        else:
            wr_score = 30
        score += wr_score * 0.5
        
        # 波动率评分 (30%) - 越小越稳定
        volatility = float(wallet_data.get("volatility", 0)) * 100
        if volatility <= 5:
            vol_score = 100
        elif volatility <= 10:
            vol_score = 90
        elif volatility <= 15:
            vol_score = 80
        elif volatility <= 20:
            vol_score = 70
        elif volatility <= 30:
            vol_score = 60
        elif volatility <= 40:
            vol_score = 50
        elif volatility <= 50:
            vol_score = 40
        else:
            vol_score = 30
        score += vol_score * 0.3
        
        # 交易一致性评分 (20%)
        # 基于交易频率的规律性
        trading_freq = wallet_data.get("trading_frequency", "unknown")
        if trading_freq in ["high", "medium", "low"]:
            consistency_score = 80  # 有明确的交易模式
        else:
            consistency_score = 50  # 交易模式不明确
        score += consistency_score * 0.2
        
        return score
    
    def _score_efficiency(
        self, 
        wallet_data: Dict[str, Any],
        trades: List[Dict[str, Any]] = None
    ) -> float:
        """
        交易效率评分 (0-100)
        
        指标：
        - 资金利用率 - 40%
        - 交易频率 - 30%
        - 平均持仓时间 - 30%
        """
        score = 0.0
        
        # 资金利用率评分 (40%)
        # ROI / 时间 = 效率
        roi = float(wallet_data.get("roi", 0))
        wallet_age_days = int(wallet_data.get("wallet_age_days", 1))
        if wallet_age_days > 0:
            daily_roi = roi / wallet_age_days
            if daily_roi >= 5:
                util_score = 100
            elif daily_roi >= 3:
                util_score = 90
            elif daily_roi >= 2:
                util_score = 80
            elif daily_roi >= 1:
                util_score = 70
            elif daily_roi >= 0.5:
                util_score = 60
            elif daily_roi >= 0:
                util_score = 50
            else:
                util_score = 30
        else:
            util_score = 50
        score += util_score * 0.4
        
        # 交易频率评分 (30%)
        closed_trades = int(wallet_data.get("closed_trades_count", 0))
        if wallet_age_days > 0:
            trades_per_day = closed_trades / wallet_age_days
            if 1 <= trades_per_day <= 10:  # 适中的交易频率
                freq_score = 90
            elif 0.5 <= trades_per_day < 1:
                freq_score = 80
            elif 10 < trades_per_day <= 20:
                freq_score = 85
            elif 0.2 <= trades_per_day < 0.5:
                freq_score = 70
            elif trades_per_day > 20:
                freq_score = 75  # 过于频繁
            else:
                freq_score = 60  # 交易太少
        else:
            freq_score = 50
        score += freq_score * 0.3
        
        # 平均持仓时间评分 (30%)
        holding_period = wallet_data.get("holding_period", "unknown")
        if holding_period == "short":  # 短线
            hold_score = 85
        elif holding_period == "medium":  # 中线
            hold_score = 90
        elif holding_period == "long":  # 长线
            hold_score = 80
        else:
            hold_score = 60
        score += hold_score * 0.3
        
        return score
    
    def _score_experience(
        self, 
        wallet_data: Dict[str, Any],
        trades: List[Dict[str, Any]] = None
    ) -> float:
        """
        经验水平评分 (0-100)
        
        指标：
        - 钱包年龄 - 40%
        - 交易笔数 - 40%
        - 交易品种多样性 - 20%
        """
        score = 0.0
        
        # 钱包年龄评分 (40%)
        wallet_age_days = int(wallet_data.get("wallet_age_days", 0))
        if wallet_age_days >= 365:
            age_score = 100
        elif wallet_age_days >= 180:
            age_score = 90
        elif wallet_age_days >= 90:
            age_score = 80
        elif wallet_age_days >= 60:
            age_score = 70
        elif wallet_age_days >= 30:
            age_score = 60
        elif wallet_age_days >= 14:
            age_score = 50
        elif wallet_age_days >= 7:
            age_score = 40
        else:
            age_score = 30
        score += age_score * 0.4
        
        # 交易笔数评分 (40%)
        closed_trades = int(wallet_data.get("closed_trades_count", 0))
        if closed_trades >= 1000:
            trades_score = 100
        elif closed_trades >= 500:
            trades_score = 95
        elif closed_trades >= 300:
            trades_score = 90
        elif closed_trades >= 200:
            trades_score = 85
        elif closed_trades >= 100:
            trades_score = 80
        elif closed_trades >= 50:
            trades_score = 70
        elif closed_trades >= 30:
            trades_score = 60
        elif closed_trades >= 10:
            trades_score = 50
        else:
            trades_score = 40
        score += trades_score * 0.4
        
        # 交易品种多样性评分 (20%)
        # 从 favorite_coins 获取
        favorite_coins = wallet_data.get("favorite_coins", [])
        if isinstance(favorite_coins, str):
            import json
            try:
                favorite_coins = json.loads(favorite_coins)
            except:
                favorite_coins = []
        
        coin_count = len(favorite_coins) if favorite_coins else 0
        if coin_count >= 10:
            diversity_score = 100
        elif coin_count >= 7:
            diversity_score = 90
        elif coin_count >= 5:
            diversity_score = 80
        elif coin_count >= 3:
            diversity_score = 70
        elif coin_count >= 2:
            diversity_score = 60
        else:
            diversity_score = 50
        score += diversity_score * 0.2
        
        return score
    
    def _score_growth(
        self, 
        wallet_data: Dict[str, Any],
        trades: List[Dict[str, Any]] = None
    ) -> float:
        """
        成长性评分 (0-100)
        
        指标：
        - 近期表现趋势 - 60%
        - 资金增长率 - 40%
        """
        score = 0.0
        
        # 近期表现趋势 (60%)
        # 基于 ROI 和钱包年龄
        roi = float(wallet_data.get("roi", 0))
        wallet_age_days = int(wallet_data.get("wallet_age_days", 1))
        
        if wallet_age_days <= 90 and roi >= 100:
            trend_score = 100  # 新手高手，成长性极强
        elif wallet_age_days <= 180 and roi >= 150:
            trend_score = 95
        elif wallet_age_days <= 365 and roi >= 200:
            trend_score = 90
        elif roi >= 100:
            trend_score = 80
        elif roi >= 50:
            trend_score = 70
        elif roi >= 20:
            trend_score = 60
        elif roi >= 0:
            trend_score = 50
        else:
            trend_score = 30
        score += trend_score * 0.6
        
        # 资金增长率 (40%)
        initial_capital = float(wallet_data.get("initial_capital", 0))
        current_balance = float(wallet_data.get("current_balance", 0))
        
        if initial_capital > 0:
            growth_rate = ((current_balance - initial_capital) / initial_capital) * 100
            if growth_rate >= 500:
                growth_score = 100
            elif growth_rate >= 300:
                growth_score = 95
            elif growth_rate >= 200:
                growth_score = 90
            elif growth_rate >= 100:
                growth_score = 85
            elif growth_rate >= 50:
                growth_score = 75
            elif growth_rate >= 0:
                growth_score = 60
            else:
                growth_score = 40
        else:
            growth_score = 50
        score += growth_score * 0.4
        
        return score
    
    def _calculate_grade(self, score: float) -> str:
        """
        根据分数计算等级
        
        S: 95-100 (传奇)
        A+: 90-94 (卓越)
        A: 85-89 (优秀)
        B+: 80-84 (良好+)
        B: 75-79 (良好)
        C+: 70-74 (中等+)
        C: 60-69 (中等)
        D: 50-59 (及格)
        E: 0-49 (不及格)
        """
        if score >= 95:
            return "S"
        elif score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "E"
    
    def _generate_tags(
        self, 
        wallet_data: Dict[str, Any],
        scores: Dict[str, float]
    ) -> List[str]:
        """生成标签"""
        tags = []
        
        # 基于综合评分
        total_score = sum(scores[dim] * self.weights[dim] for dim in self.weights.keys())
        if total_score >= 90:
            tags.append("顶级交易者")
        elif total_score >= 80:
            tags.append("优秀交易者")
        
        # 基于盈利能力
        if scores["profitability"] >= 85:
            tags.append("高盈利")
        
        # 基于风险控制
        if scores["risk_control"] >= 85:
            tags.append("风控大师")
        max_drawdown = float(wallet_data.get("max_drawdown", 100))
        if max_drawdown <= 15:
            tags.append("低回撤")
        
        # 基于稳定性
        win_rate = float(wallet_data.get("win_rate", 0))
        if win_rate >= 0.7:
            tags.append("高胜率")
        if scores["stability"] >= 85:
            tags.append("稳定盈利")
        
        # 基于盈亏比
        plr = float(wallet_data.get("profit_loss_ratio", 0))
        if plr >= 3:
            tags.append("小亏大赚")
        
        # 基于交易风格
        style = wallet_data.get("style", "")
        if style:
            tags.append(style)
        
        # 基于经验
        closed_trades = int(wallet_data.get("closed_trades_count", 0))
        if closed_trades >= 500:
            tags.append("资深交易者")
        
        # 基于成长性
        wallet_age_days = int(wallet_data.get("wallet_age_days", 999))
        roi = float(wallet_data.get("roi", 0))
        if wallet_age_days <= 90 and roi >= 100:
            tags.append("潜力新星")
        
        # 基于资金规模
        initial_capital = float(wallet_data.get("initial_capital", 0))
        if initial_capital <= 2000 and roi >= 200:
            tags.append("小资金高手")
        
        # 清算情况
        liquidation_count = int(wallet_data.get("liquidation_count", 0))
        if liquidation_count == 0:
            tags.append("零清算")
        
        return tags[:8]  # 最多返回 8 个标签
    
    def _identify_trading_style(
        self, 
        wallet_data: Dict[str, Any],
        trades: List[Dict[str, Any]] = None
    ) -> str:
        """
        识别交易风格
        
        返回：trend（趋势）、scalping（短线）、swing（波段）、mixed（混合）
        """
        holding_period = wallet_data.get("holding_period", "")
        trading_freq = wallet_data.get("trading_frequency", "")
        
        # 基于持仓周期和交易频率判断
        if holding_period == "short" and trading_freq == "high":
            return "scalping"  # 短线/剥头皮
        elif holding_period == "long" and trading_freq == "low":
            return "trend"  # 趋势交易
        elif holding_period == "medium":
            return "swing"  # 波段交易
        else:
            return "mixed"  # 混合风格


class MetricsCalculator:
    """指标计算器 - 计算各种交易指标"""
    
    @staticmethod
    def calculate_roi(
        total_pnl: float,
        initial_capital: float
    ) -> float:
        """计算 ROI (投资回报率) %"""
        if initial_capital <= 0:
            return 0.0
        return (total_pnl / initial_capital) * 100
    
    @staticmethod
    def calculate_win_rate(
        winning_trades: int,
        total_trades: int
    ) -> float:
        """计算胜率 (0-1)"""
        if total_trades <= 0:
            return 0.0
        return winning_trades / total_trades
    
    @staticmethod
    def calculate_profit_loss_ratio(
        avg_win: float,
        avg_loss: float
    ) -> float:
        """计算盈亏比"""
        if avg_loss <= 0:
            return 0.0
        return abs(avg_win / avg_loss)
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: List[float]) -> float:
        """
        计算最大回撤 %
        
        Args:
            equity_curve: 资金曲线数组
        """
        if not equity_curve or len(equity_curve) < 2:
            return 0.0
        
        max_dd = 0.0
        peak = equity_curve[0]
        
        for value in equity_curve:
            if value > peak:
                peak = value
            
            if peak > 0:
                dd = ((peak - value) / peak) * 100
                max_dd = max(max_dd, dd)
        
        return max_dd
    
    @staticmethod
    def calculate_sharpe_ratio(
        returns: List[float],
        risk_free_rate: float = 0.0
    ) -> float:
        """
        计算夏普比率
        
        Args:
            returns: 收益率列表
            risk_free_rate: 无风险利率
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        avg_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        
        if std_return == 0:
            return 0.0
        
        return (avg_return - risk_free_rate) / std_return
    
    @staticmethod
    def calculate_sortino_ratio(
        returns: List[float],
        risk_free_rate: float = 0.0
    ) -> float:
        """
        计算索提诺比率（只考虑下行波动）
        
        Args:
            returns: 收益率列表
            risk_free_rate: 无风险利率
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        avg_return = statistics.mean(returns)
        
        # 只计算负收益的标准差
        downside_returns = [r for r in returns if r < risk_free_rate]
        if not downside_returns:
            return float('inf') if avg_return > risk_free_rate else 0.0
        
        downside_std = statistics.stdev(downside_returns)
        
        if downside_std == 0:
            return 0.0
        
        return (avg_return - risk_free_rate) / downside_std
    
    @staticmethod
    def calculate_calmar_ratio(
        annual_return: float,
        max_drawdown: float
    ) -> float:
        """
        计算卡玛比率
        
        Args:
            annual_return: 年化收益率 %
            max_drawdown: 最大回撤 %
        """
        if max_drawdown <= 0:
            return 0.0
        return annual_return / max_drawdown
    
    @staticmethod
    def calculate_volatility(returns: List[float]) -> float:
        """
        计算波动率（收益率标准差）
        
        Args:
            returns: 收益率列表
        """
        if not returns or len(returns) < 2:
            return 0.0
        return statistics.stdev(returns)
    
    @staticmethod
    def calculate_annual_return(
        total_return: float,
        days: int
    ) -> float:
        """
        计算年化收益率
        
        Args:
            total_return: 总收益率 %
            days: 天数
        """
        if days <= 0:
            return 0.0
        
        years = days / 365.0
        if years <= 0:
            return 0.0
        
        # 年化收益 = (1 + 总收益率)^(1/年数) - 1
        annual = ((1 + total_return / 100) ** (1 / years) - 1) * 100
        return annual
    
    @staticmethod
    def identify_trading_frequency(
        trades_count: int,
        days: int
    ) -> str:
        """
        识别交易频率
        
        Returns:
            "high" (高频), "medium" (中频), "low" (低频)
        """
        if days <= 0:
            return "unknown"
        
        trades_per_day = trades_count / days
        
        if trades_per_day >= 5:
            return "high"
        elif trades_per_day >= 1:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def identify_holding_period(
        avg_holding_minutes: float
    ) -> str:
        """
        识别持仓周期
        
        Returns:
            "short" (短线), "medium" (中线), "long" (长线)
        """
        if avg_holding_minutes < 60:  # < 1 小时
            return "short"
        elif avg_holding_minutes < 1440:  # < 1 天
            return "medium"
        else:
            return "long"
    
    @staticmethod
    def identify_long_short_preference(
        long_count: int,
        short_count: int
    ) -> str:
        """
        识别多空偏好
        
        Returns:
            "long" (偏多), "short" (偏空), "balanced" (均衡)
        """
        total = long_count + short_count
        if total == 0:
            return "unknown"
        
        long_ratio = long_count / total
        
        if long_ratio >= 0.7:
            return "long"
        elif long_ratio <= 0.3:
            return "short"
        else:
            return "balanced"


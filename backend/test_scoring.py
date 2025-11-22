"""
测试评分模型
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.scoring import TradingScorer, MetricsCalculator

def test_scoring():
    """测试评分功能"""
    print("=" * 80)
    print("测试交易者评分模型")
    print("=" * 80)
    
    # 创建评分器
    scorer = TradingScorer()
    
    # 测试案例 1: 优秀交易者
    print("\n【测试案例 1: 优秀交易者】")
    wallet_data_1 = {
        "address": "0x1111111111111111111111111111111111111111",
        "roi": 250.0,  # 250% ROI
        "total_pnl": 15000,  # 盈利 15000
        "annual_return": 180.0,  # 年化 180%
        "max_drawdown": 12.0,  # 最大回撤 12%
        "profit_loss_ratio": 3.5,  # 盈亏比 3.5
        "liquidation_count": 0,  # 零清算
        "sharpe_ratio": 2.1,  # 夏普比率 2.1
        "win_rate": 0.68,  # 胜率 68%
        "volatility": 0.15,  # 波动率 15%
        "trading_frequency": "medium",
        "wallet_age_days": 120,
        "closed_trades_count": 180,
        "holding_period": "medium",
        "initial_capital": 6000,
        "current_balance": 21000,
        "favorite_coins": ["BTC", "ETH", "SOL", "ARB", "OP"]
    }
    
    result_1 = scorer.calculate_comprehensive_score(wallet_data_1)
    print(f"\n总分: {result_1['total_score']} / 100")
    print(f"等级: {result_1['grade']}")
    print(f"交易风格: {result_1['style']}")
    print(f"标签: {', '.join(result_1['tags'])}")
    print(f"\n各维度得分:")
    for dim, score in result_1['dimension_scores'].items():
        print(f"  - {dim}: {score:.2f}")
    
    # 测试案例 2: 高风险交易者
    print("\n" + "=" * 80)
    print("【测试案例 2: 高风险交易者】")
    wallet_data_2 = {
        "address": "0x2222222222222222222222222222222222222222",
        "roi": 80.0,
        "total_pnl": 2000,
        "annual_return": 90.0,
        "max_drawdown": 45.0,  # 高回撤
        "profit_loss_ratio": 1.2,  # 低盈亏比
        "liquidation_count": 2,  # 有清算
        "sharpe_ratio": 0.5,
        "win_rate": 0.42,  # 低胜率
        "volatility": 0.38,  # 高波动
        "trading_frequency": "high",
        "wallet_age_days": 60,
        "closed_trades_count": 450,
        "holding_period": "short",
        "initial_capital": 2500,
        "current_balance": 4500,
        "favorite_coins": ["DOGE", "SHIB"]
    }
    
    result_2 = scorer.calculate_comprehensive_score(wallet_data_2)
    print(f"\n总分: {result_2['total_score']} / 100")
    print(f"等级: {result_2['grade']}")
    print(f"交易风格: {result_2['style']}")
    print(f"标签: {', '.join(result_2['tags'])}")
    print(f"\n各维度得分:")
    for dim, score in result_2['dimension_scores'].items():
        print(f"  - {dim}: {score:.2f}")
    
    # 测试案例 3: 潜力新星
    print("\n" + "=" * 80)
    print("【测试案例 3: 潜力新星】")
    wallet_data_3 = {
        "address": "0x3333333333333333333333333333333333333333",
        "roi": 320.0,  # 超高 ROI
        "total_pnl": 3200,
        "annual_return": 450.0,  # 超高年化
        "max_drawdown": 18.0,
        "profit_loss_ratio": 4.2,
        "liquidation_count": 0,
        "sharpe_ratio": 2.8,
        "win_rate": 0.72,
        "volatility": 0.12,
        "trading_frequency": "medium",
        "wallet_age_days": 45,  # 新钱包
        "closed_trades_count": 85,
        "holding_period": "medium",
        "initial_capital": 1000,  # 小资金
        "current_balance": 4200,
        "favorite_coins": ["BTC", "ETH", "SOL"]
    }
    
    result_3 = scorer.calculate_comprehensive_score(wallet_data_3)
    print(f"\n总分: {result_3['total_score']} / 100")
    print(f"等级: {result_3['grade']}")
    print(f"交易风格: {result_3['style']}")
    print(f"标签: {', '.join(result_3['tags'])}")
    print(f"\n各维度得分:")
    for dim, score in result_3['dimension_scores'].items():
        print(f"  - {dim}: {score:.2f}")
    
    # 测试指标计算器
    print("\n" + "=" * 80)
    print("【测试指标计算器】")
    
    calc = MetricsCalculator()
    
    # 测试 ROI
    roi = calc.calculate_roi(total_pnl=5000, initial_capital=2000)
    print(f"\nROI: {roi:.2f}%")
    
    # 测试胜率
    win_rate = calc.calculate_win_rate(winning_trades=70, total_trades=100)
    print(f"胜率: {win_rate * 100:.2f}%")
    
    # 测试盈亏比
    plr = calc.calculate_profit_loss_ratio(avg_win=500, avg_loss=150)
    print(f"盈亏比: {plr:.2f}")
    
    # 测试最大回撤
    equity_curve = [10000, 11000, 10500, 12000, 9500, 11500, 13000]
    max_dd = calc.calculate_max_drawdown(equity_curve)
    print(f"最大回撤: {max_dd:.2f}%")
    
    # 测试夏普比率
    returns = [0.05, 0.03, -0.02, 0.08, 0.04, -0.01, 0.06]
    sharpe = calc.calculate_sharpe_ratio(returns)
    print(f"夏普比率: {sharpe:.2f}")
    
    # 测试年化收益
    annual = calc.calculate_annual_return(total_return=150, days=180)
    print(f"年化收益: {annual:.2f}%")
    
    # 测试交易频率识别
    freq = calc.identify_trading_frequency(trades_count=300, days=100)
    print(f"交易频率: {freq}")
    
    # 测试持仓周期识别
    holding = calc.identify_holding_period(avg_holding_minutes=720)
    print(f"持仓周期: {holding}")
    
    # 测试多空偏好
    preference = calc.identify_long_short_preference(long_count=60, short_count=40)
    print(f"多空偏好: {preference}")
    
    print("\n" + "=" * 80)
    print("✅ 所有测试完成！")
    print("=" * 80)

if __name__ == "__main__":
    test_scoring()


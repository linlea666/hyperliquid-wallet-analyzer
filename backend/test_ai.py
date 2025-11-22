"""
测试 AI 系统
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai.deepseek_service import deepseek_service
from app.services.ai.ai_analyzer import ai_analyzer
from app.services.ai.ai_scheduler import ai_scheduler, Priority


async def test_deepseek_api():
    """测试 DeepSeek API"""
    print("\n" + "="*60)
    print("测试 1: DeepSeek API 连接")
    print("="*60)
    
    try:
        # 检查配置
        print(f"✓ API 启用状态: {deepseek_service.is_enabled()}")
        print(f"✓ API URL: {deepseek_service.config.get('api_url')}")
        print(f"✓ 模型: {deepseek_service.config.get('model')}")
        
        # 发送测试请求
        print("\n发送测试请求...")
        messages = [
            {
                "role": "user",
                "content": "请用一句话介绍你自己。"
            }
        ]
        
        response = await deepseek_service.chat_completion(messages, max_tokens=100)
        
        print(f"✓ API 调用成功")
        print(f"✓ 响应内容: {response['choices'][0]['message']['content']}")
        print(f"✓ Token 使用: {response['usage']}")
        
        # 获取使用统计
        stats = deepseek_service.get_usage_stats()
        print(f"\n使用统计:")
        print(f"  今日调用: {stats['today']['calls']}")
        print(f"  今日 Token: {stats['today']['tokens']}")
        print(f"  今日成本: ¥{stats['today']['cost']}")
        print(f"  剩余额度: {stats['limits']['remaining']}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


async def test_ai_analyzer():
    """测试 AI 分析器"""
    print("\n" + "="*60)
    print("测试 2: AI 分析器")
    print("="*60)
    
    # 模拟钱包数据
    wallet_data = {
        'address': '0x1234567890abcdef',
        'score': 85,
        'metrics': {
            'total_trades': 150,
            'trading_days': 30,
            'total_pnl': 5000.0,
            'win_rate': 65.5,
            'profit_loss_ratio': 2.5,
            'avg_holding_time': 4.5,
            'max_drawdown': 15.2,
            'sharpe_ratio': 1.8,
            'avg_position_size': 25.0,
            'max_position_size': 50.0,
            'avg_leverage': 3.0,
            'trades_per_day': 5.0,
            'most_active_hour': '14:00',
            'traded_symbols': 8,
            'long_trades': 90,
            'short_trades': 60,
            'avg_trade_interval': 4.8,
            'max_profit': 800.0,
            'max_loss': -300.0,
            'avg_profit': 150.0,
            'avg_loss': -80.0,
            'max_consecutive_wins': 8,
            'max_consecutive_losses': 4,
            'volatility': 12.5,
            'sortino_ratio': 2.1,
            'max_leverage': 5.0,
            'stop_loss_rate': 85.0,
            'max_symbol_ratio': 30.0
        }
    }
    
    try:
        # 测试交易风格分析
        print("\n2.1 测试交易风格分析...")
        style_result = await ai_analyzer.analyze_trading_style(wallet_data)
        print(f"✓ 交易风格: {style_result.get('style', 'N/A')}")
        print(f"✓ 特征: {style_result.get('characteristics', [])}")
        print(f"✓ 风险偏好: {style_result.get('risk_preference', 'N/A')}")
        print(f"✓ 置信度: {style_result.get('confidence', 0)}")
        
        # 测试策略识别
        print("\n2.2 测试策略识别...")
        strategy_result = await ai_analyzer.identify_strategy(wallet_data)
        print(f"✓ 主要策略: {strategy_result.get('primary_strategy', 'N/A')}")
        print(f"✓ 辅助策略: {strategy_result.get('secondary_strategies', [])}")
        print(f"✓ 有效性: {strategy_result.get('effectiveness', 0)}")
        
        # 测试风险评估
        print("\n2.3 测试风险评估...")
        risk_result = await ai_analyzer.assess_risk(wallet_data)
        print(f"✓ 风险等级: {risk_result.get('risk_level', 'N/A')}")
        print(f"✓ 风险评分: {risk_result.get('risk_score', 0)}")
        print(f"✓ 风险因素: {risk_result.get('risk_factors', [])}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ai_scheduler():
    """测试 AI 调度器"""
    print("\n" + "="*60)
    print("测试 3: AI 调度器")
    print("="*60)
    
    try:
        # 启动调度器
        print("\n启动调度器...")
        await ai_scheduler.start()
        print("✓ 调度器已启动")
        
        # 调度测试任务
        print("\n调度测试任务...")
        result = await ai_scheduler.schedule_analysis(
            wallet_address='0xtest123',
            analysis_types=['style'],
            priority=Priority.HIGH
        )
        print(f"✓ 任务状态: {result['status']}")
        print(f"✓ 队列大小: {result.get('queue_size', 0)}")
        
        # 等待任务处理
        print("\n等待任务处理（10秒）...")
        await asyncio.sleep(10)
        
        # 获取调度器状态
        status = ai_scheduler.get_status()
        print(f"\n调度器状态:")
        print(f"  运行中: {status['running']}")
        print(f"  队列大小: {status['queue_size']}")
        print(f"  已完成任务: {status['completed_tasks']}")
        
        # 停止调度器
        ai_scheduler.stop()
        print("\n✓ 调度器已停止")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("AI 系统测试")
    print("="*60)
    
    results = []
    
    # 测试 1: DeepSeek API
    result1 = await test_deepseek_api()
    results.append(("DeepSeek API", result1))
    
    # 测试 2: AI 分析器
    if result1:  # 只有 API 正常才测试分析器
        result2 = await test_ai_analyzer()
        results.append(("AI 分析器", result2))
    else:
        print("\n⚠️  跳过 AI 分析器测试（API 连接失败）")
        results.append(("AI 分析器", False))
    
    # 测试 3: AI 调度器
    # result3 = await test_ai_scheduler()
    # results.append(("AI 调度器", result3))
    print("\n⚠️  跳过 AI 调度器测试（需要完整数据库）")
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    # 关闭客户端
    await deepseek_service.close()
    
    print("\n测试完成！")


if __name__ == "__main__":
    asyncio.run(main())


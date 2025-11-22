#!/usr/bin/env python3
"""
HyperLiquid API 测试脚本
用于验证 API 返回的数据格式和内容
"""

import httpx
import json
from datetime import datetime
from typing import Dict, Any

# 测试钱包地址
TEST_WALLET = "0x34827044cbd4b808fc1b189fce9f50e6dafae7c9"

# API 基础 URL
API_BASE_URL = "https://api.hyperliquid.xyz/info"


def print_section(title: str):
    """打印分隔线"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def save_response(filename: str, data: Any):
    """保存响应数据到文件"""
    with open(f"api_test_results/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ 已保存到: api_test_results/{filename}")


async def test_clearinghouse_state(wallet: str):
    """测试 clearinghouseState - 获取账户状态、持仓、资产"""
    print_section("测试 1: clearinghouseState - 账户状态和持仓")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                API_BASE_URL,
                json={
                    "type": "clearinghouseState",
                    "user": wallet
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API 调用成功")
                print(f"\n📊 返回数据结构:")
                print(f"  - marginSummary: {list(data.get('marginSummary', {}).keys())}")
                print(f"  - assetPositions: {len(data.get('assetPositions', []))} 个持仓")
                
                # 打印关键信息
                margin = data.get('marginSummary', {})
                print(f"\n💰 账户信息:")
                print(f"  - 账户总价值: ${float(margin.get('accountValue', 0)):,.2f}")
                print(f"  - 总持仓价值: ${float(margin.get('totalNtlPos', 0)):,.2f}")
                print(f"  - 已用保证金: ${float(margin.get('totalMarginUsed', 0)):,.2f}")
                print(f"  - 可提现金额: ${float(data.get('withdrawable', 0)):,.2f}")
                
                # 打印持仓信息
                positions = data.get('assetPositions', [])
                if positions:
                    print(f"\n📈 当前持仓:")
                    for pos in positions:
                        p = pos.get('position', {})
                        print(f"  - {p.get('coin')}: {p.get('szi')} (杠杆: {p.get('leverage', {}).get('value')}x)")
                        print(f"    未实现盈亏: ${float(p.get('unrealizedPnl', 0)):,.2f}")
                
                # 保存完整响应
                save_response("clearinghouse_state.json", data)
                return data
            else:
                print(f"❌ API 调用失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None


async def test_user_fills(wallet: str):
    """测试 userFillsByTime - 获取交易历史"""
    print_section("测试 2: userFillsByTime - 交易历史")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 获取最近 30 天的交易
            start_time = int((datetime.now().timestamp() - 30 * 24 * 3600) * 1000)
            
            response = await client.post(
                API_BASE_URL,
                json={
                    "type": "userFillsByTime",
                    "user": wallet,
                    "startTime": start_time
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API 调用成功")
                print(f"\n📊 返回数据:")
                print(f"  - 交易记录数: {len(data)} 笔")
                
                if data:
                    # 分析交易数据
                    total_pnl = sum(float(trade.get('closedPnl', 0)) for trade in data)
                    long_trades = [t for t in data if t.get('side') == 'B']
                    short_trades = [t for t in data if t.get('side') == 'A']
                    
                    print(f"\n📈 交易统计:")
                    print(f"  - 总盈亏: ${total_pnl:,.2f}")
                    print(f"  - 多单: {len(long_trades)} 笔")
                    print(f"  - 空单: {len(short_trades)} 笔")
                    
                    # 打印最近 5 笔交易
                    print(f"\n🔄 最近 5 笔交易:")
                    for trade in data[:5]:
                        time_str = datetime.fromtimestamp(trade['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        side = "多单" if trade['side'] == 'B' else "空单"
                        print(f"  - {time_str} | {trade['coin']} | {side} | "
                              f"盈亏: ${float(trade.get('closedPnl', 0)):,.2f}")
                    
                    # 打印第一笔交易的完整结构
                    print(f"\n📋 单笔交易数据结构:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
                
                # 保存完整响应
                save_response("user_fills.json", data)
                return data
            else:
                print(f"❌ API 调用失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None


async def test_user_transfers(wallet: str):
    """测试 userNonFundingLedgerUpdates - 获取存取款记录"""
    print_section("测试 3: userNonFundingLedgerUpdates - 存取款记录")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 获取最近 90 天的记录
            start_time = int((datetime.now().timestamp() - 90 * 24 * 3600) * 1000)
            
            response = await client.post(
                API_BASE_URL,
                json={
                    "type": "userNonFundingLedgerUpdates",
                    "user": wallet,
                    "startTime": start_time
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API 调用成功")
                print(f"\n📊 返回数据:")
                print(f"  - 记录数: {len(data)} 条")
                
                if data:
                    # 分类统计
                    deposits = []
                    withdrawals = []
                    
                    for record in data:
                        delta = record.get('delta', {})
                        if 'type' in delta:
                            if delta['type'] == 'deposit':
                                deposits.append(record)
                            elif delta['type'] == 'withdraw':
                                withdrawals.append(record)
                    
                    total_deposits = sum(float(r['delta'].get('amount', 0)) for r in deposits)
                    total_withdrawals = sum(float(r['delta'].get('amount', 0)) for r in withdrawals)
                    
                    print(f"\n💰 资金流水统计:")
                    print(f"  - 存款: {len(deposits)} 笔, 总额: ${total_deposits:,.2f}")
                    print(f"  - 取款: {len(withdrawals)} 笔, 总额: ${total_withdrawals:,.2f}")
                    print(f"  - 净流入: ${total_deposits - total_withdrawals:,.2f}")
                    
                    # 打印最近 5 条记录
                    print(f"\n🔄 最近 5 条记录:")
                    for record in data[:5]:
                        time_str = datetime.fromtimestamp(record['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        delta = record.get('delta', {})
                        print(f"  - {time_str} | {delta.get('type', 'unknown')} | "
                              f"金额: ${float(delta.get('amount', 0)):,.2f}")
                    
                    # 打印第一条记录的完整结构
                    if data:
                        print(f"\n📋 单条记录数据结构:")
                        print(json.dumps(data[0], indent=2, ensure_ascii=False))
                
                # 保存完整响应
                save_response("user_transfers.json", data)
                return data
            else:
                print(f"❌ API 调用失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None


async def test_open_orders(wallet: str):
    """测试 frontendOpenOrders - 获取当前挂单"""
    print_section("测试 4: frontendOpenOrders - 当前挂单")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                API_BASE_URL,
                json={
                    "type": "frontendOpenOrders",
                    "user": wallet
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API 调用成功")
                print(f"\n📊 返回数据:")
                print(f"  - 挂单数: {len(data)} 个")
                
                if data:
                    print(f"\n📋 当前挂单:")
                    for order in data:
                        print(f"  - {order.get('coin')} | "
                              f"方向: {order.get('side')} | "
                              f"价格: ${float(order.get('limitPx', 0)):,.2f} | "
                              f"数量: {order.get('sz')}")
                    
                    # 打印第一个挂单的完整结构
                    print(f"\n📋 单个挂单数据结构:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
                else:
                    print("  - 当前无挂单")
                
                # 保存完整响应
                save_response("open_orders.json", data)
                return data
            else:
                print(f"❌ API 调用失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None


async def analyze_data_for_scoring(clearinghouse: Dict, fills: list, transfers: list):
    """分析数据，为评分模型提供参考"""
    print_section("数据分析 - 评分模型参考")
    
    if not clearinghouse or not fills:
        print("❌ 缺少必要数据，无法分析")
        return
    
    print("📊 可用于评分的数据:")
    
    # 1. 账户信息
    margin = clearinghouse.get('marginSummary', {})
    account_value = float(margin.get('accountValue', 0))
    print(f"\n1️⃣ 账户信息:")
    print(f"  ✅ 账户总价值: ${account_value:,.2f}")
    print(f"  ✅ 可提现金额: ${float(clearinghouse.get('withdrawable', 0)):,.2f}")
    
    # 2. 初始资金（从存取款计算）
    if transfers:
        deposits = [r for r in transfers if r.get('delta', {}).get('type') == 'deposit']
        withdrawals = [r for r in transfers if r.get('delta', {}).get('type') == 'withdraw']
        
        total_deposits = sum(float(r['delta'].get('amount', 0)) for r in deposits)
        total_withdrawals = sum(float(r['delta'].get('amount', 0)) for r in withdrawals)
        initial_capital = total_deposits - total_withdrawals
        
        print(f"\n2️⃣ 初始资金:")
        print(f"  ✅ 累计存款: ${total_deposits:,.2f}")
        print(f"  ✅ 累计取款: ${total_withdrawals:,.2f}")
        print(f"  ✅ 初始资金: ${initial_capital:,.2f}")
        
        # 计算 ROI
        if initial_capital > 0:
            total_pnl = account_value - initial_capital
            roi = (total_pnl / initial_capital) * 100
            print(f"  ✅ 总盈亏: ${total_pnl:,.2f}")
            print(f"  ✅ ROI: {roi:.2f}%")
    
    # 3. 交易统计
    if fills:
        total_trades = len(fills)
        winning_trades = [t for t in fills if float(t.get('closedPnl', 0)) > 0]
        losing_trades = [t for t in fills if float(t.get('closedPnl', 0)) < 0]
        
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum(float(t.get('closedPnl', 0)) for t in winning_trades)
        total_loss = abs(sum(float(t.get('closedPnl', 0)) for t in losing_trades))
        profit_loss_ratio = (total_profit / total_loss) if total_loss > 0 else 0
        
        print(f"\n3️⃣ 交易统计:")
        print(f"  ✅ 总交易次数: {total_trades}")
        print(f"  ✅ 盈利交易: {len(winning_trades)} 笔")
        print(f"  ✅ 亏损交易: {len(losing_trades)} 笔")
        print(f"  ✅ 胜率: {win_rate:.2f}%")
        print(f"  ✅ 盈亏比: {profit_loss_ratio:.2f}")
    
    # 4. 持仓信息
    positions = clearinghouse.get('assetPositions', [])
    if positions:
        print(f"\n4️⃣ 持仓信息:")
        print(f"  ✅ 持仓数量: {len(positions)}")
        
        long_positions = [p for p in positions if float(p['position']['szi']) > 0]
        short_positions = [p for p in positions if float(p['position']['szi']) < 0]
        
        print(f"  ✅ 多头持仓: {len(long_positions)}")
        print(f"  ✅ 空头持仓: {len(short_positions)}")
        
        total_unrealized_pnl = sum(float(p['position'].get('unrealizedPnl', 0)) for p in positions)
        print(f"  ✅ 未实现盈亏: ${total_unrealized_pnl:,.2f}")
    
    # 5. 钱包年龄
    if fills:
        first_trade_time = min(t['time'] for t in fills)
        first_trade_date = datetime.fromtimestamp(first_trade_time / 1000)
        wallet_age_days = (datetime.now() - first_trade_date).days
        
        print(f"\n5️⃣ 钱包年龄:")
        print(f"  ✅ 第一笔交易时间: {first_trade_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  ✅ 钱包年龄: {wallet_age_days} 天")
    
    print("\n✅ 数据分析完成！所有必要数据都可以从 API 获取。")


async def main():
    """主函数"""
    import os
    
    # 创建结果目录
    os.makedirs("api_test_results", exist_ok=True)
    
    print("\n" + "=" * 80)
    print("  HyperLiquid API 测试")
    print("  测试钱包: " + TEST_WALLET)
    print("=" * 80)
    
    # 测试各个 API
    clearinghouse = await test_clearinghouse_state(TEST_WALLET)
    fills = await test_user_fills(TEST_WALLET)
    transfers = await test_user_transfers(TEST_WALLET)
    orders = await test_open_orders(TEST_WALLET)
    
    # 分析数据
    if clearinghouse and fills:
        await analyze_data_for_scoring(clearinghouse, fills, transfers or [])
    
    print("\n" + "=" * 80)
    print("  测试完成！")
    print("  结果已保存到: api_test_results/")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


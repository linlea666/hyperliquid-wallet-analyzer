#!/usr/bin/env python3
"""
HyperLiquid API 测试脚本
测试钱包：0x34827044cbd4b808fc1b189fce9f50e6dafae7c9
"""

import httpx
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

# API 配置
API_URL = "https://api.hyperliquid.xyz/info"
TEST_WALLET = "0x34827044cbd4b808fc1b189fce9f50e6dafae7c9"


async def test_api(endpoint_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """测试 API 调用"""
    print(f"\n{'='*80}")
    print(f"测试 API: {endpoint_type}")
    print(f"参数: {json.dumps(params, indent=2)}")
    print(f"{'='*80}")
    
    try:
        # 禁用代理
        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            response = await client.post(
                API_URL,
                json=params,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功！返回数据类型: {type(data)}")
                
                # 美化输出
                if isinstance(data, list):
                    print(f"返回列表长度: {len(data)}")
                    if len(data) > 0:
                        print(f"\n第一条数据示例:")
                        print(json.dumps(data[0], indent=2, ensure_ascii=False))
                        if len(data) > 1:
                            print(f"\n最后一条数据示例:")
                            print(json.dumps(data[-1], indent=2, ensure_ascii=False))
                elif isinstance(data, dict):
                    print(f"\n返回数据:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                
                return {"success": True, "data": data}
            else:
                print(f"❌ 失败！状态码: {response.status_code}")
                print(f"响应: {response.text}")
                return {"success": False, "error": response.text}
                
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return {"success": False, "error": str(e)}


async def main():
    """主测试函数"""
    print(f"\n{'#'*80}")
    print(f"# HyperLiquid API 测试")
    print(f"# 测试钱包: {TEST_WALLET}")
    print(f"# 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}")
    
    results = {}
    
    # 测试1: 获取账户状态和持仓信息
    print("\n\n" + "="*80)
    print("测试 1: clearinghouseState - 账户状态、持仓、资产信息")
    print("="*80)
    results['clearinghouseState'] = await test_api(
        "clearinghouseState",
        {
            "type": "clearinghouseState",
            "user": TEST_WALLET
        }
    )
    
    # 测试2: 获取交易历史（分页）
    print("\n\n" + "="*80)
    print("测试 2: userFillsByTime - 交易历史（最近100笔）")
    print("="*80)
    results['userFillsByTime'] = await test_api(
        "userFillsByTime",
        {
            "type": "userFillsByTime",
            "user": TEST_WALLET,
            "startTime": 0  # 从最早开始
        }
    )
    
    # 测试3: 获取存取款记录
    print("\n\n" + "="*80)
    print("测试 3: userNonFundingLedgerUpdates - 存取款记录")
    print("="*80)
    results['userNonFundingLedgerUpdates'] = await test_api(
        "userNonFundingLedgerUpdates",
        {
            "type": "userNonFundingLedgerUpdates",
            "user": TEST_WALLET,
            "startTime": 0
        }
    )
    
    # 测试4: 获取当前挂单
    print("\n\n" + "="*80)
    print("测试 4: frontendOpenOrders - 当前挂单")
    print("="*80)
    results['frontendOpenOrders'] = await test_api(
        "frontendOpenOrders",
        {
            "type": "frontendOpenOrders",
            "user": TEST_WALLET
        }
    )
    
    # 测试5: 获取账户价值历史
    print("\n\n" + "="*80)
    print("测试 5: userFunding - 账户价值历史")
    print("="*80)
    results['userFunding'] = await test_api(
        "userFunding",
        {
            "type": "userFunding",
            "user": TEST_WALLET,
            "startTime": 0
        }
    )
    
    # 汇总结果
    print("\n\n" + "#"*80)
    print("# 测试结果汇总")
    print("#"*80)
    
    for api_name, result in results.items():
        status = "✅ 成功" if result.get("success") else "❌ 失败"
        print(f"{api_name}: {status}")
        
        if result.get("success"):
            data = result.get("data")
            if isinstance(data, list):
                print(f"  - 返回列表长度: {len(data)}")
            elif isinstance(data, dict):
                print(f"  - 返回字典，键: {list(data.keys())}")
    
    # 保存测试结果到文件
    output_file = "api_test_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 测试结果已保存到: {output_file}")
    
    # 数据结构分析
    print("\n\n" + "#"*80)
    print("# 数据结构分析")
    print("#"*80)
    
    if results['clearinghouseState'].get('success'):
        data = results['clearinghouseState']['data']
        print("\n【clearinghouseState 数据结构】")
        print("- marginSummary: 账户摘要")
        print("  - accountValue: 账户总价值")
        print("  - totalNtlPos: 总持仓价值")
        print("  - totalMarginUsed: 已用保证金")
        print("- assetPositions: 持仓列表")
        if 'assetPositions' in data and len(data['assetPositions']) > 0:
            pos = data['assetPositions'][0]
            print(f"  示例持仓字段: {list(pos.keys())}")
    
    if results['userFillsByTime'].get('success'):
        data = results['userFillsByTime']['data']
        print("\n【userFillsByTime 数据结构】")
        print(f"- 返回列表长度: {len(data)}")
        if len(data) > 0:
            print(f"- 单条交易字段: {list(data[0].keys())}")
    
    if results['userNonFundingLedgerUpdates'].get('success'):
        data = results['userNonFundingLedgerUpdates']['data']
        print("\n【userNonFundingLedgerUpdates 数据结构】")
        print(f"- 返回列表长度: {len(data)}")
        if len(data) > 0:
            print(f"- 单条记录字段: {list(data[0].keys())}")
    
    print("\n\n" + "#"*80)
    print("# 测试完成！")
    print("#"*80)


if __name__ == "__main__":
    asyncio.run(main())


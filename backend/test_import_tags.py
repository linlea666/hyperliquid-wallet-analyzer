"""
测试批量导入和标签系统
"""
import asyncio
import time
from app.services.import_manager import import_manager
from app.services.tag_manager import tag_manager, Tag, TagSource, TagCategory

async def test_import():
    """测试批量导入"""
    print("=" * 80)
    print("测试批量导入功能")
    print("=" * 80)
    
    # 模拟 100 个地址
    test_addresses = [
        f"0x{i:040x}" for i in range(1, 101)
    ]
    
    print(f"\n创建导入任务: {len(test_addresses)} 个地址")
    
    # 创建任务
    task = import_manager.create_task(
        addresses=test_addresses,
        batch_size=20,
        frequency="normal"
    )
    
    print(f"任务 ID: {task.task_id}")
    print(f"批次大小: {task.batch_size}")
    print(f"总批次: {len(test_addresses) // task.batch_size + 1}")
    
    # 执行任务（模拟）
    print("\n开始执行任务...")
    
    # 注意：这里只是演示，实际会调用 API
    # await import_manager.execute_task(task.task_id)
    
    # 模拟进度
    for i in range(0, 101, 10):
        task.processed = i
        task.success = int(i * 0.9)
        task.failed = int(i * 0.05)
        task.skipped = int(i * 0.05)
        
        progress = task.get_progress()
        print(f"\n进度: {progress['progress']:.1f}%")
        print(f"已处理: {progress['processed']}/{progress['total']}")
        print(f"成功: {task.success}, 失败: {task.failed}, 跳过: {task.skipped}")
        
        time.sleep(0.5)
    
    print("\n✅ 导入任务完成！")
    print(f"总数: {task.total}")
    print(f"成功: {task.success}")
    print(f"失败: {task.failed}")
    print(f"跳过: {task.skipped}")

def test_tags():
    """测试标签系统"""
    print("\n" + "=" * 80)
    print("测试标签系统")
    print("=" * 80)
    
    # 模拟钱包数据
    wallet_data = {
        "smart_money_score": 88.5,
        "roi": 250.0,
        "win_rate": 0.72,
        "max_drawdown": 12.0,
        "profit_loss_ratio": 3.8,
        "liquidation_count": 0,
        "sharpe_ratio": 2.1,
        "closed_trades_count": 350,
        "wallet_age_days": 120,
        "initial_capital": 1500,
        "style": "swing"
    }
    
    print("\n钱包数据:")
    print(f"  评分: {wallet_data['smart_money_score']}")
    print(f"  ROI: {wallet_data['roi']}%")
    print(f"  胜率: {wallet_data['win_rate'] * 100}%")
    print(f"  回撤: {wallet_data['max_drawdown']}%")
    print(f"  盈亏比: {wallet_data['profit_loss_ratio']}")
    
    # 生成系统标签
    print("\n生成系统标签...")
    system_tags = tag_manager.generate_system_tags(wallet_data)
    
    print(f"\n✅ 生成了 {len(system_tags)} 个系统标签:")
    for tag in system_tags:
        print(f"  - {tag.name} ({tag.category.value}, 权重: {tag.weight})")
    
    # 模拟 AI 标签
    print("\n模拟 AI 标签...")
    ai_tags = [
        Tag(
            name="逆势高手",
            source=TagSource.AI,
            category=TagCategory.SKILL,
            weight=0.9,
            confidence=0.85,
            metadata={"reason": "在市场下跌时仍能保持盈利"}
        ),
        Tag(
            name="纪律性强",
            source=TagSource.AI,
            category=TagCategory.SPECIAL,
            weight=0.88,
            confidence=0.9,
            metadata={"reason": "严格止损，从不追涨杀跌"}
        )
    ]
    
    print(f"✅ 生成了 {len(ai_tags)} 个 AI 标签:")
    for tag in ai_tags:
        print(f"  - {tag.name} ({tag.category.value}, 权重: {tag.weight}, 置信度: {tag.confidence})")
    
    # 模拟用户标签
    print("\n模拟用户标签...")
    user_tags = [
        Tag(
            name="值得跟单",
            source=TagSource.USER,
            category=TagCategory.SPECIAL,
            weight=0.7,
            confidence=1.0
        )
    ]
    
    print(f"✅ 添加了 {len(user_tags)} 个用户标签:")
    for tag in user_tags:
        print(f"  - {tag.name} ({tag.category.value})")
    
    # 合并标签
    print("\n合并所有标签...")
    merged_tags = tag_manager.merge_tags(system_tags, ai_tags, user_tags)
    
    print(f"\n✅ 最终标签列表（共 {len(merged_tags)} 个）:")
    for i, tag in enumerate(merged_tags, 1):
        print(f"  {i}. {tag.name}")
        print(f"     来源: {tag.source.value}")
        print(f"     分类: {tag.category.value}")
        print(f"     权重: {tag.weight}")
        print(f"     置信度: {tag.confidence}")
    
    # 测试标签规则
    print("\n" + "=" * 80)
    print("系统标签规则列表")
    print("=" * 80)
    
    for tag_name, rule in tag_manager.SYSTEM_TAG_RULES.items():
        print(f"\n标签: {tag_name}")
        print(f"  分类: {rule['category'].value}")
        print(f"  权重: {rule['weight']}")
        print(f"  条件: {rule['conditions']}")

def test_text_parsing():
    """测试文本解析"""
    print("\n" + "=" * 80)
    print("测试地址解析")
    print("=" * 80)
    
    # 测试不同格式的文本
    test_texts = [
        # 换行分隔
        """
        0x1111111111111111111111111111111111111111
        0x2222222222222222222222222222222222222222
        0x3333333333333333333333333333333333333333
        """,
        
        # 逗号分隔
        "0x1111111111111111111111111111111111111111,0x2222222222222222222222222222222222222222,0x3333333333333333333333333333333333333333",
        
        # 混合分隔
        "0x1111111111111111111111111111111111111111; 0x2222222222222222222222222222222222222222, 0x3333333333333333333333333333333333333333",
        
        # 带说明文本
        """
        钱包1: 0x1111111111111111111111111111111111111111
        钱包2: 0x2222222222222222222222222222222222222222
        钱包3: 0x3333333333333333333333333333333333333333
        """
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n测试 {i}:")
        print(f"输入文本: {text[:50]}...")
        
        addresses = import_manager.parse_addresses_from_text(text)
        print(f"✅ 解析出 {len(addresses)} 个地址:")
        for addr in addresses:
            print(f"  - {addr}")

if __name__ == "__main__":
    print("\n🚀 开始测试批量导入和标签系统\n")
    
    # 测试导入
    asyncio.run(test_import())
    
    # 测试标签
    test_tags()
    
    # 测试解析
    test_text_parsing()
    
    print("\n" + "=" * 80)
    print("✅ 所有测试完成！")
    print("=" * 80)


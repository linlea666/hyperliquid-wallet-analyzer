"""
通知系统测试脚本
测试邮件服务、通知规则、模板等功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.notification import email_service, notification_manager
from app.database import db


def print_section(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_email_config():
    """测试邮件配置"""
    print_section("1. 测试邮件配置")
    
    config = email_service.config
    
    print(f"✓ 邮件服务启用: {email_service.is_enabled()}")
    print(f"✓ SMTP 服务器: {config.get('smtp_host', '未配置')}")
    print(f"✓ SMTP 端口: {config.get('smtp_port', '未配置')}")
    print(f"✓ 发件人: {config.get('sender_email', '未配置')}")
    print(f"✓ 收件人数量: {len(config.get('recipients', []))}")
    
    if not email_service.is_enabled():
        print("\n⚠️  邮件服务未启用，请在系统配置中启用并配置")
        print("\n配置步骤：")
        print("1. 登录系统 (admin/admin888)")
        print("2. 进入 系统管理 → 系统配置 → 通知配置")
        print("3. 启用邮件通知并填写配置")
        print("4. 发送测试邮件验证")
        return False
    
    return True


def test_email_send():
    """测试邮件发送"""
    print_section("2. 测试邮件发送")
    
    if not email_service.is_enabled():
        print("❌ 邮件服务未启用，跳过测试")
        return
    
    print("📧 准备发送测试邮件...")
    
    try:
        success = email_service.send_test_email()
        
        if success:
            print("✅ 测试邮件发送成功！")
            print("   请检查收件箱（包括垃圾邮件）")
        else:
            print("❌ 测试邮件发送失败")
            print("   请检查配置是否正确")
            
    except Exception as e:
        print(f"❌ 发送失败: {e}")


def test_email_history():
    """测试邮件历史"""
    print_section("3. 测试邮件历史")
    
    history = email_service.get_history(limit=5)
    
    print(f"✓ 历史记录数量: {len(history)}")
    
    if history:
        print("\n最近 5 条记录:")
        for i, record in enumerate(history, 1):
            status_icon = "✅" if record['status'] == 'sent' else "❌"
            print(f"\n{i}. {status_icon} {record['title']}")
            print(f"   收件人: {record['recipient']}")
            print(f"   时间: {record['sent_at']}")
            print(f"   状态: {record['status']}")
            if record.get('error_message'):
                print(f"   错误: {record['error_message']}")
    else:
        print("暂无历史记录")


def test_email_statistics():
    """测试邮件统计"""
    print_section("4. 测试邮件统计")
    
    stats = email_service.get_statistics()
    
    print(f"✓ 总发送数: {stats['total']}")
    print(f"✓ 成功数: {stats['success']}")
    print(f"✓ 失败数: {stats['failed']}")
    print(f"✓ 今日发送: {stats['today']}")
    print(f"✓ 成功率: {stats['success_rate']}%")


async def test_notification_send():
    """测试通知发送"""
    print_section("5. 测试通知发送")
    
    print("📢 测试发送导入完成通知...")
    
    try:
        success = await notification_manager.send_notification(
            event_type='import_complete',
            title='测试：钱包导入任务完成',
            content='这是一条测试通知，用于验证通知系统功能',
            data={
                'total': 100,
                'success': 95,
                'failed': 3,
                'skipped': 2
            },
            level='success'
        )
        
        if success:
            print("✅ 通知发送成功")
            print("   - WebSocket 推送: ✓")
            print("   - 数据库存储: ✓")
            if email_service.is_enabled():
                print("   - 邮件发送: ✓")
        else:
            print("❌ 通知发送失败")
            
    except Exception as e:
        print(f"❌ 发送失败: {e}")


async def test_notification_rules():
    """测试通知规则"""
    print_section("6. 测试通知规则")
    
    rules = notification_manager.rules
    
    print("当前规则配置:")
    print(f"✓ 导入完成通知: {rules.get('importComplete', False)}")
    print(f"✓ 高分钱包通知: {rules.get('highScoreWallet', False)}")
    print(f"  - 阈值: {rules.get('highScoreThreshold', 80)} 分")
    print(f"✓ 异常交易通知: {rules.get('abnormalTrade', False)}")
    print(f"✓ 系统错误通知: {rules.get('systemError', False)}")


def test_notification_list():
    """测试通知列表"""
    print_section("7. 测试通知列表")
    
    notifications = notification_manager.get_notifications(limit=5)
    
    print(f"✓ 通知数量: {len(notifications)}")
    print(f"✓ 未读数量: {notification_manager.get_unread_count()}")
    
    if notifications:
        print("\n最近 5 条通知:")
        for i, notif in enumerate(notifications, 1):
            read_icon = "📖" if notif['is_read'] else "📩"
            level_icon = {
                'success': '✅',
                'info': 'ℹ️',
                'warning': '⚠️',
                'error': '❌'
            }.get(notif['level'], '📢')
            
            print(f"\n{i}. {read_icon} {level_icon} {notif['title']}")
            print(f"   内容: {notif['content']}")
            print(f"   时间: {notif['created_at']}")
            print(f"   级别: {notif['level']}")
    else:
        print("暂无通知")


async def test_all_notification_types():
    """测试所有通知类型"""
    print_section("8. 测试所有通知类型")
    
    test_cases = [
        {
            'type': 'import_complete',
            'title': '测试：导入任务完成',
            'content': '批量导入任务已完成',
            'data': {'total': 50, 'success': 48, 'failed': 2, 'skipped': 0},
            'level': 'success'
        },
        {
            'type': 'high_score_wallet',
            'title': '测试：发现高分钱包',
            'content': '发现一个高评分钱包',
            'data': {
                'address': '0x1234567890abcdef1234567890abcdef12345678',
                'score': 92,
                'grade': 'S',
                'tags': ['稳定盈利', '风险控制优秀', '高频交易']
            },
            'level': 'success'
        },
        {
            'type': 'abnormal_trade',
            'title': '测试：异常交易预警',
            'content': '检测到异常交易行为',
            'data': {'wallet': '0xabcd...', 'reason': '单笔交易金额异常'},
            'level': 'warning'
        },
        {
            'type': 'system_error',
            'title': '测试：系统错误',
            'content': '系统发生错误',
            'data': {'error': 'Test error', 'module': 'test'},
            'level': 'error'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试 {test_case['type']}...")
        
        try:
            success = await notification_manager.send_notification(
                event_type=test_case['type'],
                title=test_case['title'],
                content=test_case['content'],
                data=test_case['data'],
                level=test_case['level']
            )
            
            if success:
                print(f"   ✅ 发送成功")
            else:
                print(f"   ❌ 发送失败")
                
        except Exception as e:
            print(f"   ❌ 错误: {e}")


def print_menu():
    """打印测试菜单"""
    print("\n" + "="*60)
    print("  通知系统测试菜单")
    print("="*60)
    print("1. 测试邮件配置")
    print("2. 发送测试邮件")
    print("3. 查看邮件历史")
    print("4. 查看邮件统计")
    print("5. 测试通知发送")
    print("6. 查看通知规则")
    print("7. 查看通知列表")
    print("8. 测试所有通知类型")
    print("9. 运行完整测试")
    print("0. 退出")
    print("="*60)


async def run_full_test():
    """运行完整测试"""
    print("\n🚀 开始完整测试...\n")
    
    # 1. 测试配置
    if not test_email_config():
        return
    
    # 2. 测试邮件发送
    test_email_send()
    
    # 3. 测试历史
    test_email_history()
    
    # 4. 测试统计
    test_email_statistics()
    
    # 5. 测试通知发送
    await test_notification_send()
    
    # 6. 测试规则
    await test_notification_rules()
    
    # 7. 测试列表
    test_notification_list()
    
    # 8. 测试所有类型
    await test_all_notification_types()
    
    print("\n" + "="*60)
    print("  ✅ 完整测试完成！")
    print("="*60)


async def main():
    """主函数"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║         通知系统测试工具                                ║
    ║         HyperLiquid 钱包分析系统 V2.0                  ║
    ╚════════════════════════════════════════════════════════╝
    
    ⚠️  测试前请确保：
    1. 后端服务已启动
    2. 数据库已初始化
    3. 邮件服务已配置（如需测试邮件功能）
    """)
    
    while True:
        print_menu()
        choice = input("\n请选择测试项 (0-9): ").strip()
        
        if choice == "0":
            print("\n👋 测试结束，再见！")
            break
        
        elif choice == "1":
            test_email_config()
        
        elif choice == "2":
            test_email_send()
        
        elif choice == "3":
            test_email_history()
        
        elif choice == "4":
            test_email_statistics()
        
        elif choice == "5":
            await test_notification_send()
        
        elif choice == "6":
            await test_notification_rules()
        
        elif choice == "7":
            test_notification_list()
        
        elif choice == "8":
            await test_all_notification_types()
        
        elif choice == "9":
            await run_full_test()
        
        else:
            print("❌ 无效选择，请重试")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试已中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


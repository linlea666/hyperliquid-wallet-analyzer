"""
WebSocket 功能测试
测试实时通信、进度推送等功能
"""
import asyncio
import websockets
import json
from datetime import datetime


async def test_websocket_connection():
    """测试 WebSocket 连接"""
    uri = "ws://localhost:8000/api/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket 连接成功")
            
            # 接收欢迎消息
            welcome = await websocket.recv()
            print(f"📨 收到欢迎消息: {welcome}")
            
            # 测试 ping-pong
            print("\n🏓 测试心跳...")
            await websocket.send(json.dumps({"type": "ping"}))
            pong = await websocket.recv()
            print(f"📨 收到 pong: {pong}")
            
            # 订阅主题
            print("\n📢 订阅主题...")
            await websocket.send(json.dumps({
                "type": "subscribe",
                "topic": "wallet_updates"
            }))
            sub_response = await websocket.recv()
            print(f"📨 订阅响应: {sub_response}")
            
            # 获取统计信息
            print("\n📊 获取统计信息...")
            await websocket.send(json.dumps({"type": "get_stats"}))
            stats = await websocket.recv()
            print(f"📨 统计信息: {stats}")
            
            # 取消订阅
            print("\n🚫 取消订阅...")
            await websocket.send(json.dumps({
                "type": "unsubscribe",
                "topic": "wallet_updates"
            }))
            unsub_response = await websocket.recv()
            print(f"📨 取消订阅响应: {unsub_response}")
            
            print("\n✅ 所有测试通过！")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")


async def test_import_progress():
    """测试导入进度推送"""
    uri = "ws://localhost:8000/api/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket 连接成功")
            
            # 接收欢迎消息
            await websocket.recv()
            
            # 订阅导入进度（假设任务 ID 为 test-task-123）
            task_id = "test-task-123"
            print(f"\n📢 订阅导入进度: {task_id}")
            await websocket.send(json.dumps({
                "type": "subscribe",
                "topic": f"import:{task_id}"
            }))
            
            # 接收订阅响应
            await websocket.recv()
            
            print("\n⏳ 等待进度更新（10秒）...")
            print("提示：在另一个终端运行导入任务来测试进度推送")
            
            # 监听进度更新
            try:
                for i in range(10):
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    if data.get("type") == "import_progress":
                        print(f"📊 进度更新: {data['data']['progress']}%")
            except asyncio.TimeoutError:
                pass
            
            print("\n✅ 测试完成")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")


async def test_multiple_clients():
    """测试多客户端连接"""
    uri = "ws://localhost:8000/api/ws"
    
    async def client(client_id: int):
        try:
            async with websockets.connect(uri) as websocket:
                print(f"✅ 客户端 {client_id} 连接成功")
                
                # 接收欢迎消息
                await websocket.recv()
                
                # 订阅系统状态
                await websocket.send(json.dumps({
                    "type": "subscribe",
                    "topic": "system_status"
                }))
                await websocket.recv()
                
                # 保持连接 5 秒
                await asyncio.sleep(5)
                
                print(f"👋 客户端 {client_id} 断开连接")
        
        except Exception as e:
            print(f"❌ 客户端 {client_id} 失败: {e}")
    
    # 创建 3 个客户端
    print("🚀 创建 3 个客户端...")
    await asyncio.gather(
        client(1),
        client(2),
        client(3)
    )
    
    print("\n✅ 多客户端测试完成")


def print_menu():
    """打印测试菜单"""
    print("\n" + "="*50)
    print("WebSocket 功能测试")
    print("="*50)
    print("1. 测试基本连接和消息")
    print("2. 测试导入进度推送")
    print("3. 测试多客户端连接")
    print("4. 运行所有测试")
    print("0. 退出")
    print("="*50)


async def main():
    """主函数"""
    while True:
        print_menu()
        choice = input("\n请选择测试项 (0-4): ").strip()
        
        if choice == "0":
            print("👋 再见！")
            break
        
        elif choice == "1":
            print("\n🧪 开始测试基本连接...")
            await test_websocket_connection()
        
        elif choice == "2":
            print("\n🧪 开始测试导入进度...")
            await test_import_progress()
        
        elif choice == "3":
            print("\n🧪 开始测试多客户端...")
            await test_multiple_clients()
        
        elif choice == "4":
            print("\n🧪 运行所有测试...")
            await test_websocket_connection()
            await asyncio.sleep(1)
            await test_multiple_clients()
            print("\n✅ 所有测试完成！")
        
        else:
            print("❌ 无效选择，请重试")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════╗
    ║   WebSocket 功能测试工具               ║
    ║   HyperLiquid 钱包分析系统 V2.0       ║
    ╚════════════════════════════════════════╝
    
    ⚠️  请确保后端服务已启动 (http://localhost:8000)
    """)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试已中断")


"""
简单测试数据库初始化（不依赖其他包）
"""
import sqlite3
import json
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent / "data" / "hyperliquid_analyzer.db"

def test_database():
    """测试数据库功能"""
    try:
        print("=" * 60)
        print("测试数据库功能...")
        print("=" * 60)
        
        # 确保目录存在
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # 连接数据库
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. 创建钱包表
        print("\n1. 创建钱包表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address VARCHAR(42) UNIQUE NOT NULL,
                smart_money_score DECIMAL(5, 2) DEFAULT 0,
                roi DECIMAL(10, 4) DEFAULT 0,
                win_rate DECIMAL(5, 4) DEFAULT 0
            )
        """)
        conn.commit()
        print("✅ 钱包表创建成功")
        
        # 2. 查询表
        print("\n2. 查询所有表...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = cursor.fetchall()
        print(f"✅ 找到 {len(tables)} 张表:")
        for table in tables:
            print(f"   - {table['name']}")
        
        # 3. 测试插入
        print("\n3. 测试插入数据...")
        test_address = "0x0000000000000000000000000000000000000000"
        cursor.execute("""
            INSERT OR REPLACE INTO wallets (address, smart_money_score, roi, win_rate)
            VALUES (?, ?, ?, ?)
        """, (test_address, 85.5, 150.0, 0.65))
        conn.commit()
        print("✅ 数据插入成功")
        
        # 4. 测试查询
        print("\n4. 测试查询数据...")
        cursor.execute("SELECT * FROM wallets WHERE address = ?", (test_address,))
        row = cursor.fetchone()
        if row:
            print(f"✅ 查询成功:")
            print(f"   地址: {row['address']}")
            print(f"   评分: {row['smart_money_score']}")
            print(f"   ROI: {row['roi']}")
            print(f"   胜率: {row['win_rate']}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print(f"数据库文件: {DB_PATH}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_database()
    sys.exit(0 if success else 1)


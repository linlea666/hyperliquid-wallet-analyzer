"""
测试数据库初始化
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import db
from loguru import logger

def test_database():
    """测试数据库功能"""
    try:
        logger.info("=" * 60)
        logger.info("测试数据库功能...")
        logger.info("=" * 60)
        
        # 1. 测试表创建
        logger.info("\n1. 测试表创建...")
        db.create_tables()
        logger.info("✅ 表创建成功")
        
        # 2. 测试查询表结构
        logger.info("\n2. 测试查询表结构...")
        tables = db.fetch_all("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        logger.info(f"✅ 找到 {len(tables)} 张表:")
        for table in tables:
            logger.info(f"   - {table['name']}")
        
        # 3. 测试预设榜单
        logger.info("\n3. 测试预设榜单...")
        leaderboards = db.fetch_all("SELECT name, display_name FROM leaderboards")
        logger.info(f"✅ 找到 {len(leaderboards)} 个预设榜单:")
        for lb in leaderboards:
            logger.info(f"   - {lb['display_name']} ({lb['name']})")
        
        # 4. 测试钱包表结构
        logger.info("\n4. 测试钱包表结构...")
        columns = db.fetch_all("PRAGMA table_info(wallets)")
        logger.info(f"✅ 钱包表有 {len(columns)} 个字段")
        
        # 5. 测试插入和查询
        logger.info("\n5. 测试插入和查询...")
        test_address = "0x0000000000000000000000000000000000000000"
        
        # 检查是否已存在
        existing = db.fetch_one(
            "SELECT id FROM wallets WHERE address = ?",
            (test_address,)
        )
        
        if not existing:
            db.execute("""
                INSERT INTO wallets (address, smart_money_score, roi, win_rate)
                VALUES (?, ?, ?, ?)
            """, (test_address, 85.5, 150.0, 0.65))
            logger.info("✅ 测试数据插入成功")
        else:
            logger.info("ℹ️  测试数据已存在，跳过插入")
        
        # 查询测试数据
        wallet = db.fetch_one(
            "SELECT address, smart_money_score, roi, win_rate FROM wallets WHERE address = ?",
            (test_address,)
        )
        if wallet:
            logger.info(f"✅ 查询成功: {wallet}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 所有测试通过！")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)



"""
数据库初始化脚本
用于创建数据库表和初始化预设数据
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.database import db
from loguru import logger

def init_database():
    """初始化数据库"""
    try:
        logger.info("=" * 60)
        logger.info("开始初始化数据库...")
        logger.info("=" * 60)
        
        # 创建所有表
        db.create_tables()
        
        logger.info("=" * 60)
        logger.info("✅ 数据库初始化完成！")
        logger.info(f"数据库文件位置: {db.db_path}")
        logger.info("=" * 60)
        
        return True
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)



"""
数据库备份脚本
定期备份数据库文件
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.config import DATA_DIR


def backup_database():
    """备份数据库"""
    try:
        # 数据库文件
        db_file = DATA_DIR / "hyperliquid_analyzer.db"
        
        if not db_file.exists():
            print(f"❌ 数据库文件不存在: {db_file}")
            return False
        
        # 备份目录
        backup_dir = DATA_DIR / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"db_backup_{timestamp}.db"
        
        # 复制数据库文件
        print(f"📦 开始备份数据库...")
        print(f"   源文件: {db_file}")
        print(f"   目标文件: {backup_file}")
        
        shutil.copy2(db_file, backup_file)
        
        # 获取文件大小
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        
        print(f"✅ 数据库备份成功!")
        print(f"   文件大小: {size_mb:.2f} MB")
        print(f"   备份位置: {backup_file}")
        
        # 清理旧备份（保留最近 7 个）
        cleanup_old_backups(backup_dir, keep=7)
        
        return True
        
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False


def cleanup_old_backups(backup_dir: Path, keep: int = 7):
    """清理旧备份文件"""
    try:
        # 获取所有备份文件
        backup_files = sorted(
            backup_dir.glob("db_backup_*.db"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # 删除多余的备份
        if len(backup_files) > keep:
            print(f"\n🧹 清理旧备份（保留最近 {keep} 个）...")
            for old_backup in backup_files[keep:]:
                old_backup.unlink()
                print(f"   已删除: {old_backup.name}")
            print(f"✅ 清理完成")
        
    except Exception as e:
        print(f"⚠️  清理旧备份失败: {e}")


def list_backups():
    """列出所有备份"""
    try:
        backup_dir = DATA_DIR / "backups"
        
        if not backup_dir.exists():
            print("📁 备份目录不存在")
            return
        
        backup_files = sorted(
            backup_dir.glob("db_backup_*.db"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not backup_files:
            print("📁 没有找到备份文件")
            return
        
        print(f"\n📋 备份文件列表（共 {len(backup_files)} 个）:")
        print("-" * 80)
        print(f"{'序号':<6} {'文件名':<30} {'大小':<12} {'创建时间':<20}")
        print("-" * 80)
        
        for idx, backup_file in enumerate(backup_files, 1):
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            print(f"{idx:<6} {backup_file.name:<30} {size_mb:>8.2f} MB  {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("-" * 80)
        
    except Exception as e:
        print(f"❌ 列出备份失败: {e}")


def restore_backup(backup_file: str):
    """恢复备份"""
    try:
        backup_dir = DATA_DIR / "backups"
        backup_path = backup_dir / backup_file
        
        if not backup_path.exists():
            print(f"❌ 备份文件不存在: {backup_path}")
            return False
        
        db_file = DATA_DIR / "hyperliquid_analyzer.db"
        
        # 备份当前数据库
        if db_file.exists():
            current_backup = DATA_DIR / f"hyperliquid_analyzer_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(db_file, current_backup)
            print(f"📦 当前数据库已备份到: {current_backup}")
        
        # 恢复备份
        print(f"🔄 开始恢复备份...")
        print(f"   备份文件: {backup_path}")
        print(f"   目标文件: {db_file}")
        
        shutil.copy2(backup_path, db_file)
        
        print(f"✅ 数据库恢复成功!")
        
        return True
        
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库备份管理工具")
    parser.add_argument(
        "action",
        choices=["backup", "list", "restore"],
        help="操作类型: backup(备份), list(列出), restore(恢复)"
    )
    parser.add_argument(
        "--file",
        help="恢复时指定备份文件名"
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("数据库备份管理工具")
    print("="*80)
    
    if args.action == "backup":
        backup_database()
    
    elif args.action == "list":
        list_backups()
    
    elif args.action == "restore":
        if not args.file:
            print("❌ 请使用 --file 参数指定备份文件名")
            list_backups()
            return
        restore_backup(args.file)
    
    print("\n" + "="*80)
    print("操作完成")
    print("="*80)


if __name__ == "__main__":
    main()


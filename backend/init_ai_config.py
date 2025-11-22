"""
初始化 AI 配置
"""
import json
from datetime import datetime
from app.database import db


def init_ai_config():
    """初始化 AI 配置"""
    
    # AI 配置
    ai_config = {
        'enabled': True,
        'provider': 'deepseek',
        'api_key': 'sk-95468bc93340462e81772278f0ae6058',
        'api_url': 'https://api.deepseek.com/v1',
        'model': 'deepseek-chat',
        'max_tokens': 2000,
        'temperature': 0.7,
        'daily_limit': 1000,
        'cost_limit': 10.0,
        'score_threshold': 75
    }
    
    try:
        # 检查是否已存在
        existing = db.fetch_one(
            "SELECT * FROM system_configs WHERE config_key = ?",
            ("ai",)
        )
        
        if existing:
            print("AI 配置已存在，更新中...")
            db.execute("""
                UPDATE system_configs
                SET config_value = ?, updated_at = ?
                WHERE config_key = ?
            """, (
                json.dumps(ai_config, ensure_ascii=False),
                datetime.now().isoformat(),
                'ai'
            ))
            print("✓ AI 配置已更新")
        else:
            print("创建 AI 配置...")
            db.execute("""
                INSERT INTO system_configs (config_key, config_value, updated_at)
                VALUES (?, ?, ?)
            """, (
                'ai',
                json.dumps(ai_config, ensure_ascii=False),
                datetime.now().isoformat()
            ))
            print("✓ AI 配置已创建")
        
        # 显示配置
        print("\n当前 AI 配置:")
        print(json.dumps(ai_config, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        raise


if __name__ == "__main__":
    print("="*60)
    print("初始化 AI 配置")
    print("="*60)
    
    init_ai_config()
    
    print("\n完成！")


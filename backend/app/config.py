"""配置管理模块（SQLite 持久化）"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any

from loguru import logger

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = DATA_DIR / "config"
WALLETS_DIR = DATA_DIR / "wallets"
CACHE_DIR = DATA_DIR / "cache"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = DATA_DIR / "hyperliquid_analyzer.db"

# 创建必要的目录
for dir_path in [DATA_DIR, CONFIG_DIR, WALLETS_DIR, CACHE_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


def _deep_merge(original: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """递归合并配置，避免浅拷贝覆盖嵌套字段。"""

    merged = original.copy()
    for key, value in updates.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class Config:
    """配置管理类，使用 SQLite 存储，启动时自动填充默认值。"""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or DB_PATH
        self.conn = sqlite3.connect(
            str(self.db_path), check_same_thread=False, timeout=30.0
        )
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()
        self._configs: Dict[str, Dict[str, Any]] = {}
        self.load_all_configs()

    def _ensure_table(self):
        """确保系统配置表存在并具备必要字段。"""

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS system_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key VARCHAR(100) UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                description TEXT,
                version INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # 补充缺失字段（兼容旧表结构）
        columns = {
            row[1]: row[2]
            for row in self.conn.execute("PRAGMA table_info(system_configs)").fetchall()
        }
        if "version" not in columns:
            self.conn.execute("ALTER TABLE system_configs ADD COLUMN version INTEGER DEFAULT 1")
        if "updated_at" not in columns:
            self.conn.execute(
                "ALTER TABLE system_configs ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            )
        self.conn.commit()

    def _load_config_from_db(self, name: str) -> Dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT config_value FROM system_configs WHERE config_key = ?", (name,)
        ).fetchone()
        if not row:
            return None
        try:
            return json.loads(row[0])
        except json.JSONDecodeError as exc:
            logger.error(f"配置 {name} JSON 解析失败，使用默认值: {exc}")
            return None

    def _save_config_to_db(self, name: str, value: Dict[str, Any], description: str | None = None):
        existing = self.conn.execute(
            "SELECT version FROM system_configs WHERE config_key = ?", (name,)
        ).fetchone()
        next_version = (existing[0] + 1) if existing else 1

        self.conn.execute(
            """
            INSERT INTO system_configs (config_key, config_value, description, version)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(config_key) DO UPDATE SET
                config_value = excluded.config_value,
                description = COALESCE(excluded.description, system_configs.description),
                version = excluded.version,
                updated_at = CURRENT_TIMESTAMP
            """,
            (name, json.dumps(value, ensure_ascii=False), description, next_version),
        )
        self.conn.commit()

    def load_all_configs(self):
        """从数据库加载配置，缺失时写入默认值。"""

        config_names = [
            "system",
            "scoring",
            "recommendation",
            "filters",
            "notifications",
            "ai",
        ]

        # 预加载数据库中已有的配置
        existing_rows = self.conn.execute(
            "SELECT config_key, config_value FROM system_configs"
        ).fetchall()
        for row in existing_rows:
            try:
                self._configs[row[0]] = json.loads(row[1])
            except json.JSONDecodeError as exc:
                logger.error(f"配置 {row[0]} JSON 解析失败: {exc}")

        # 填充默认值并写入数据库
        for name in config_names:
            default_config = self._get_default_config(name)
            if name not in self._configs or not self._configs[name]:
                self._configs[name] = default_config
                self._save_config_to_db(name, default_config)
            else:
                # 合并默认值缺失字段
                merged = _deep_merge(default_config, self._configs[name])
                if merged != self._configs[name]:
                    self._configs[name] = merged
                    self._save_config_to_db(name, merged)

    def _get_default_config(self, name: str) -> Dict[str, Any]:
        """获取默认配置"""
        defaults = {
            'system': {
                "api": {
                    "base_url": "https://api.hyperliquid.xyz/info",
                    "timeout": 30,
                    "retry_times": 3,
                    "retry_delay": 1,
                    "use_mock": True  # 设置为 False 使用真实 API
                },
                "update": {
                    "active_interval": 3600,
                    "normal_interval": 21600,
                    "dormant_interval": 86400,
                    "batch_size": 100,
                    "concurrent_limit": 10
                },
                "cache": {
                    "api_cache_ttl": 300,
                    "calculation_cache_ttl": 3600
                },
                "pagination": {
                    "default_page_size": 20,
                    "max_page_size": 100
                },
                "scheduler": {
                    "enabled": True  # 调度器开关，便于灰度控制
                }
            },
            'scoring': {
                "weights": {
                    "roi": 0.35,
                    "profit_loss_ratio": 0.20,
                    "max_drawdown": 0.20,
                    "win_rate_stability": 0.15,
                    "capital_size": 0.05,
                    "style": 0.05
                },
                "thresholds": {
                    "roi": {
                        "excellent": 500,
                        "good": 200,
                        "average": 100,
                        "poor": 50
                    },
                    "profit_loss_ratio": {
                        "excellent": 3.0,
                        "good": 2.0,
                        "average": 1.5,
                        "poor": 1.0
                    },
                    "max_drawdown": {
                        "excellent": 20,
                        "good": 30,
                        "average": 40,
                        "poor": 50
                    },
                    "win_rate": {
                        "excellent": 70,
                        "good": 60,
                        "average": 50
                    }
                }
            },
            'recommendation': {
                "filters": {
                    "wallet_age_min_days": 30,
                    "wallet_age_max_days": 180,
                    "min_roi": 200,
                    "min_profit_loss_ratio": 2.0,
                    "max_drawdown": 40,
                    "max_capital": 2000,
                    "min_win_rate": 55,
                    "min_smart_money_score": 70
                },
                "top_n": 20
            },
            'filters': {
                "default_filters": {
                    "wallet_age": {
                        "min": 30,
                        "max": 180
                    }
                },
                "filter_options": {
                    "roi_range": [-100, 1000],
                    "profit_loss_ratio_range": [0, 10],
                    "win_rate_range": [0, 100],
                    "max_drawdown_range": [0, 100],
                    "capital_range": [0, 10000]
                }
            },
            'notifications': {
                "enabled": True,
                "browser": {
                    "enabled": True,
                    "sound": True,
                    "duration": 5000
                },
                "email": {
                    "enabled": False,
                    "smtp": {
                        "host": "smtp.gmail.com",
                        "port": 587,
                        "username": "",
                        "password": "",
                        "from_email": "",
                        "to_emails": []
                    },
                    "frequency": "immediate"
                },
                "thresholds": {
                    "large_trade": 10000,
                    "large_deposit": 5000,
                    "large_withdrawal": 5000,
                    "profit_threshold": 5000,
                    "roi_threshold": 200,
                    "drawdown_threshold": 50
                }
            },
            'ai': {
                "enabled": False,
                "api_url": "https://api.deepseek.com",
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 2000,
                "daily_limit": 1000,
                "cost_limit": 1.0,
                "timeout": 30
            }
        }
        return defaults.get(name, {})

    def get_config(self, name: str) -> Dict[str, Any]:
        """获取配置"""
        return json.loads(json.dumps(self._configs.get(name, {})))

    def update_config(self, name: str, updates: Dict[str, Any]):
        """更新配置并持久化到数据库。"""

        if name not in self._configs:
            logger.warning(f"Config {name} not found，写入默认值后再更新")
            self._configs[name] = self._get_default_config(name)

        merged_config = _deep_merge(self._configs[name], updates)
        self._configs[name] = merged_config
        self._save_config_to_db(name, merged_config)

    def reload(self):
        """重新加载数据库中的配置。"""

        self._configs.clear()
        self.load_all_configs()


# 全局配置实例
config = Config()


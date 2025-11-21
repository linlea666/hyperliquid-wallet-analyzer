"""配置管理模块"""
import json
import os
from pathlib import Path
from typing import Dict, Any
from loguru import logger

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = DATA_DIR / "config"
WALLETS_DIR = DATA_DIR / "wallets"
CACHE_DIR = DATA_DIR / "cache"
LOGS_DIR = BASE_DIR / "logs"

# 创建必要的目录
for dir_path in [DATA_DIR, CONFIG_DIR, WALLETS_DIR, CACHE_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


class Config:
    """配置管理类"""
    
    def __init__(self):
        self._configs: Dict[str, Dict[str, Any]] = {}
        self.load_all_configs()
    
    def load_all_configs(self):
        """加载所有配置文件"""
        config_files = {
            'system': 'system.json',
            'scoring': 'scoring.json',
            'recommendation': 'recommendation.json',
            'filters': 'filters.json',
            'notifications': 'notifications.json'
        }
        
        for name, filename in config_files.items():
            config_path = CONFIG_DIR / filename
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        self._configs[name] = json.load(f)
                    logger.info(f"Loaded config: {name}")
                except Exception as e:
                    logger.error(f"Failed to load config {name}: {e}")
                    self._configs[name] = self._get_default_config(name)
            else:
                self._configs[name] = self._get_default_config(name)
                self.save_config(name)
    
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
            }
        }
        return defaults.get(name, {})
    
    def get_config(self, name: str) -> Dict[str, Any]:
        """获取配置"""
        return self._configs.get(name, {})
    
    def save_config(self, name: str):
        """保存配置"""
        config_path = CONFIG_DIR / f"{name}.json"
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._configs[name], f, indent=2, ensure_ascii=False)
            logger.info(f"Saved config: {name}")
        except Exception as e:
            logger.error(f"Failed to save config {name}: {e}")
    
    def update_config(self, name: str, updates: Dict[str, Any]):
        """更新配置"""
        if name in self._configs:
            self._configs[name].update(updates)
            self.save_config(name)
        else:
            logger.warning(f"Config {name} not found")


# 全局配置实例
config = Config()


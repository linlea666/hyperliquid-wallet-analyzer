"""配置服务：封装配置的读取、更新与校验逻辑。

该服务结合 `config.Config` 的 SQLite 持久化能力，通过 Pydantic 模型对
不同配置段进行结构化校验，避免随意写入导致的 JSON 污染，同时提供
带版本号的更新结果，便于前端即时刷新。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator

from app.config import config


class SystemAPIConfig(BaseModel):
    """API 相关配置。"""

    base_url: str = Field(..., description="基础请求地址")
    timeout: int = Field(ge=1, le=120, description="请求超时时间，秒")
    retry_times: int = Field(ge=0, le=10, description="重试次数")
    retry_delay: int = Field(ge=0, le=30, description="重试间隔，秒")
    use_mock: bool = Field(False, description="是否使用 Mock 数据")


class SystemUpdateConfig(BaseModel):
    """数据更新调度配置。"""

    active_interval: int = Field(ge=60, description="活跃钱包更新间隔，秒")
    normal_interval: int = Field(ge=300, description="普通钱包更新间隔，秒")
    dormant_interval: int = Field(ge=600, description="沉睡钱包更新间隔，秒")
    batch_size: int = Field(ge=1, le=500, description="单批处理的钱包数量")
    concurrent_limit: int = Field(ge=1, le=50, description="并发上限")


class SystemCacheConfig(BaseModel):
    """缓存 TTL 配置。"""

    api_cache_ttl: int = Field(ge=30, le=3600, description="API 缓存时间，秒")
    calculation_cache_ttl: int = Field(ge=60, le=7200, description="指标计算缓存时间，秒")


class SystemPaginationConfig(BaseModel):
    """分页配置。"""

    default_page_size: int = Field(ge=5, le=200, description="默认分页大小")
    max_page_size: int = Field(ge=20, le=500, description="最大分页大小")


class SystemSchedulerConfig(BaseModel):
    """调度器开关配置。"""

    enabled: bool = Field(True, description="是否启用调度器")


class SystemConfig(BaseModel):
    """系统配置根模型。"""

    api: SystemAPIConfig
    update: SystemUpdateConfig
    cache: SystemCacheConfig
    pagination: SystemPaginationConfig
    scheduler: SystemSchedulerConfig = Field(default_factory=SystemSchedulerConfig)


class NotificationSMTP(BaseModel):
    host: str = Field(..., description="SMTP 服务器地址")
    port: int = Field(ge=1, le=65535, description="SMTP 端口")
    username: str = Field("", description="SMTP 用户名")
    password: str = Field("", description="SMTP 密码")
    from_email: str = Field("", description="发件人邮箱")
    to_emails: list[str] = Field(default_factory=list, description="收件人列表")


class NotificationEmail(BaseModel):
    enabled: bool = Field(False, description="是否启用邮件通知")
    smtp: NotificationSMTP
    frequency: str = Field("immediate", description="通知频率")


class NotificationBrowser(BaseModel):
    enabled: bool = Field(True, description="是否启用浏览器通知")
    sound: bool = Field(True, description="是否播放声音")
    duration: int = Field(ge=1000, le=20000, description="通知停留时间，毫秒")


class NotificationThresholds(BaseModel):
    large_trade: float = Field(ge=0)
    large_deposit: float = Field(ge=0)
    large_withdrawal: float = Field(ge=0)
    profit_threshold: float = Field(ge=0)
    roi_threshold: float = Field(ge=0)
    drawdown_threshold: float = Field(ge=0)


class NotificationConfig(BaseModel):
    enabled: bool = Field(True, description="通知总开关")
    browser: NotificationBrowser
    email: NotificationEmail
    thresholds: NotificationThresholds


class ScoringWeights(BaseModel):
    roi: float = Field(ge=0, le=1)
    profit_loss_ratio: float = Field(ge=0, le=1)
    max_drawdown: float = Field(ge=0, le=1)
    win_rate_stability: float = Field(ge=0, le=1)
    capital_size: float = Field(ge=0, le=1)
    style: float = Field(ge=0, le=1)

    @validator("style")
    def validate_sum(cls, v, values):
        """保证权重总和为 1。"""
        if "roi" in values:
            total = v + sum(values.values())
            if abs(total - 1.0) > 1e-6:
                raise ValueError("评分权重之和必须为 1")
        return v


class ScoringThresholds(BaseModel):
    roi: Dict[str, float]
    profit_loss_ratio: Dict[str, float]
    max_drawdown: Dict[str, float]
    win_rate: Dict[str, float]


class ScoringConfig(BaseModel):
    weights: ScoringWeights
    thresholds: ScoringThresholds


class AIConfig(BaseModel):
    enabled: bool
    api_url: str
    model: str
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(ge=1, le=8000)
    daily_limit: int = Field(ge=0)
    cost_limit: float = Field(ge=0.0)
    timeout: int = Field(ge=1, le=120)


class RecommendationFilters(BaseModel):
    wallet_age_min_days: int
    wallet_age_max_days: int
    min_roi: float
    min_profit_loss_ratio: float
    max_drawdown: float
    max_capital: float
    min_win_rate: float
    min_smart_money_score: float


class RecommendationConfig(BaseModel):
    filters: RecommendationFilters
    top_n: int = Field(ge=1, le=200)


class ConfigService:
    """提供配置的读取和更新接口，并保证结构化校验。"""

    def get(self, name: str) -> Dict[str, Any]:
        """获取指定配置的安全副本。"""
        return config.get_config(name)

    def update(self, name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """校验并更新配置，返回最新快照。"""

        validator_model = self._get_model(name)
        if validator_model:
            # 使用 Pydantic 进行结构化校验
            current = config.get_config(name)
            merged = self._deep_merge(current, updates)
            validator_model(**merged)  # 校验失败会抛出异常
        config.update_config(name, updates)
        return config.get_config(name)

    def _get_model(self, name: str) -> Optional[type[BaseModel]]:
        """根据配置名称返回对应的校验模型。"""
        return {
            "system": SystemConfig,
            "notifications": NotificationConfig,
            "scoring": ScoringConfig,
            "ai": AIConfig,
            "recommendation": RecommendationConfig,
        }.get(name)

    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并字典，用于校验前保留未修改的默认值。"""

        merged: Dict[str, Any] = base.copy()
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged


config_service = ConfigService()

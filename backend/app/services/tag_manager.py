"""
标签管理系统
支持系统标签、AI 标签、用户自定义标签
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
from loguru import logger

from app.database import db


class TagSource(str, Enum):
    """标签来源"""
    SYSTEM = "system"      # 系统自动生成
    AI = "ai"             # AI 分析生成
    USER = "user"         # 用户手动添加
    BEHAVIOR = "behavior"  # 行为分析生成
    STYLE = "style"       # 交易风格


class TagCategory(str, Enum):
    """标签分类"""
    PERFORMANCE = "performance"    # 表现类：高盈利、稳定盈利
    RISK = "risk"                 # 风险类：低回撤、风控大师
    SKILL = "skill"               # 技能类：高胜率、小亏大赚
    EXPERIENCE = "experience"      # 经验类：资深交易者、潜力新星
    STYLE = "style"               # 风格类：趋势、短线、波段
    CAPITAL = "capital"           # 资金类：小资金高手、大资金
    SPECIAL = "special"           # 特殊类：零清算、传奇交易者


class Tag:
    """标签对象"""
    
    def __init__(
        self,
        name: str,
        source: TagSource,
        category: TagCategory,
        weight: float = 1.0,
        confidence: float = 1.0,
        metadata: Dict[str, Any] = None
    ):
        self.name = name
        self.source = source
        self.category = category
        self.weight = weight  # 权重：0-1
        self.confidence = confidence  # 置信度：0-1
        self.metadata = metadata or {}
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        return {
            "name": self.name,
            "source": self.source,
            "category": self.category,
            "weight": self.weight,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tag':
        """从字典创建"""
        tag = cls(
            name=data["name"],
            source=TagSource(data["source"]),
            category=TagCategory(data["category"]),
            weight=data.get("weight", 1.0),
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {})
        )
        if "created_at" in data:
            tag.created_at = datetime.fromisoformat(data["created_at"])
        return tag


class TagManager:
    """标签管理器"""
    
    # 系统预定义标签配置
    SYSTEM_TAG_RULES = {
        # 表现类
        "顶级交易者": {
            "category": TagCategory.PERFORMANCE,
            "conditions": {"smart_money_score": {"min": 90}},
            "weight": 1.0
        },
        "优秀交易者": {
            "category": TagCategory.PERFORMANCE,
            "conditions": {"smart_money_score": {"min": 80, "max": 90}},
            "weight": 0.9
        },
        "高盈利": {
            "category": TagCategory.PERFORMANCE,
            "conditions": {"roi": {"min": 200}},
            "weight": 0.9
        },
        "稳定盈利": {
            "category": TagCategory.PERFORMANCE,
            "conditions": {"win_rate": {"min": 0.6}, "volatility": {"max": 0.2}},
            "weight": 0.85
        },
        
        # 风险类
        "风控大师": {
            "category": TagCategory.RISK,
            "conditions": {"max_drawdown": {"max": 15}, "sharpe_ratio": {"min": 1.5}},
            "weight": 0.95
        },
        "低回撤": {
            "category": TagCategory.RISK,
            "conditions": {"max_drawdown": {"max": 20}},
            "weight": 0.85
        },
        "零清算": {
            "category": TagCategory.RISK,
            "conditions": {"liquidation_count": {"max": 0}},
            "weight": 0.9
        },
        
        # 技能类
        "高胜率": {
            "category": TagCategory.SKILL,
            "conditions": {"win_rate": {"min": 0.7}},
            "weight": 0.9
        },
        "小亏大赚": {
            "category": TagCategory.SKILL,
            "conditions": {"profit_loss_ratio": {"min": 3.0}},
            "weight": 0.95
        },
        
        # 经验类
        "资深交易者": {
            "category": TagCategory.EXPERIENCE,
            "conditions": {"closed_trades_count": {"min": 500}, "wallet_age_days": {"min": 180}},
            "weight": 0.8
        },
        "潜力新星": {
            "category": TagCategory.EXPERIENCE,
            "conditions": {
                "wallet_age_days": {"min": 30, "max": 90},
                "roi": {"min": 100},
                "win_rate": {"min": 0.5}
            },
            "weight": 0.9
        },
        
        # 资金类
        "小资金高手": {
            "category": TagCategory.CAPITAL,
            "conditions": {"initial_capital": {"max": 2000}, "roi": {"min": 200}},
            "weight": 0.95
        },
        
        # 风格类（由交易行为决定）
        "趋势交易": {
            "category": TagCategory.STYLE,
            "conditions": {"style": "trend"},
            "weight": 0.8
        },
        "短线交易": {
            "category": TagCategory.STYLE,
            "conditions": {"style": "scalping"},
            "weight": 0.8
        },
        "波段交易": {
            "category": TagCategory.STYLE,
            "conditions": {"style": "swing"},
            "weight": 0.8
        }
    }
    
    def __init__(self):
        pass
    
    def generate_system_tags(self, wallet_data: Dict[str, Any]) -> List[Tag]:
        """
        生成系统标签
        
        Args:
            wallet_data: 钱包数据
            
        Returns:
            标签列表
        """
        tags = []
        
        for tag_name, rule in self.SYSTEM_TAG_RULES.items():
            if self._check_conditions(wallet_data, rule["conditions"]):
                tag = Tag(
                    name=tag_name,
                    source=TagSource.SYSTEM,
                    category=rule["category"],
                    weight=rule["weight"],
                    confidence=1.0,
                    metadata={"rule": rule["conditions"]}
                )
                tags.append(tag)
        
        # 限制数量（最多 8 个）
        tags.sort(key=lambda t: t.weight, reverse=True)
        return tags[:8]
    
    def _check_conditions(
        self,
        wallet_data: Dict[str, Any],
        conditions: Dict[str, Any]
    ) -> bool:
        """检查条件是否满足"""
        for field, condition in conditions.items():
            value = wallet_data.get(field)
            
            if value is None:
                return False
            
            # 字符串相等
            if isinstance(condition, str):
                if value != condition:
                    return False
            
            # 数值范围
            elif isinstance(condition, dict):
                if "min" in condition:
                    if value < condition["min"]:
                        return False
                if "max" in condition:
                    if value > condition["max"]:
                        return False
        
        return True
    
    def add_user_tag(
        self,
        address: str,
        tag_name: str,
        category: TagCategory = TagCategory.SPECIAL
    ) -> bool:
        """
        添加用户自定义标签
        
        Args:
            address: 钱包地址
            tag_name: 标签名称
            category: 标签分类
            
        Returns:
            是否成功
        """
        try:
            # 获取现有标签
            wallet = db.fetch_one(
                "SELECT tags FROM wallets WHERE address = ?",
                (address,)
            )
            
            if not wallet:
                return False
            
            # 解析标签
            tags_data = json.loads(wallet["tags"]) if wallet["tags"] else []
            
            # 检查是否已存在
            if tag_name in [t if isinstance(t, str) else t.get("name") for t in tags_data]:
                logger.info(f"标签已存在: {tag_name}")
                return True
            
            # 添加新标签
            new_tag = Tag(
                name=tag_name,
                source=TagSource.USER,
                category=category,
                weight=0.7,  # 用户标签权重较低
                confidence=1.0
            )
            
            tags_data.append(new_tag.to_dict())
            
            # 更新数据库
            db.execute(
                "UPDATE wallets SET tags = ? WHERE address = ?",
                (json.dumps(tags_data), address)
            )
            
            logger.info(f"添加用户标签成功: {address} - {tag_name}")
            return True
            
        except Exception as e:
            logger.error(f"添加用户标签失败: {e}")
            return False
    
    def remove_tag(self, address: str, tag_name: str) -> bool:
        """
        移除标签
        
        Args:
            address: 钱包地址
            tag_name: 标签名称
            
        Returns:
            是否成功
        """
        try:
            wallet = db.fetch_one(
                "SELECT tags FROM wallets WHERE address = ?",
                (address,)
            )
            
            if not wallet:
                return False
            
            tags_data = json.loads(wallet["tags"]) if wallet["tags"] else []
            
            # 过滤掉指定标签
            new_tags = [
                t for t in tags_data
                if (t if isinstance(t, str) else t.get("name")) != tag_name
            ]
            
            # 更新数据库
            db.execute(
                "UPDATE wallets SET tags = ? WHERE address = ?",
                (json.dumps(new_tags), address)
            )
            
            logger.info(f"移除标签成功: {address} - {tag_name}")
            return True
            
        except Exception as e:
            logger.error(f"移除标签失败: {e}")
            return False
    
    def get_tags(self, address: str) -> List[Dict[str, Any]]:
        """
        获取钱包的所有标签
        
        Args:
            address: 钱包地址
            
        Returns:
            标签列表
        """
        try:
            wallet = db.fetch_one(
                "SELECT tags FROM wallets WHERE address = ?",
                (address,)
            )
            
            if not wallet or not wallet["tags"]:
                return []
            
            tags_data = json.loads(wallet["tags"])
            
            # 兼容旧格式（纯字符串列表）
            result = []
            for tag in tags_data:
                if isinstance(tag, str):
                    # 旧格式：转换为新格式
                    result.append({
                        "name": tag,
                        "source": TagSource.SYSTEM,
                        "category": TagCategory.SPECIAL,
                        "weight": 1.0,
                        "confidence": 1.0
                    })
                else:
                    result.append(tag)
            
            return result
            
        except Exception as e:
            logger.error(f"获取标签失败: {e}")
            return []
    
    def update_tags(self, address: str, tags: List[Tag]):
        """
        更新钱包标签
        
        Args:
            address: 钱包地址
            tags: 新标签列表
        """
        try:
            tags_data = [tag.to_dict() for tag in tags]
            
            db.execute(
                "UPDATE wallets SET tags = ? WHERE address = ?",
                (json.dumps(tags_data), address)
            )
            
            logger.info(f"更新标签成功: {address}, 数量: {len(tags)}")
            
        except Exception as e:
            logger.error(f"更新标签失败: {e}")
    
    def merge_tags(
        self,
        system_tags: List[Tag],
        ai_tags: List[Tag] = None,
        user_tags: List[Tag] = None
    ) -> List[Tag]:
        """
        合并不同来源的标签
        
        优先级：用户标签 > AI 标签 > 系统标签
        
        Args:
            system_tags: 系统标签
            ai_tags: AI 标签
            user_tags: 用户标签
            
        Returns:
            合并后的标签列表
        """
        all_tags = {}
        
        # 添加系统标签
        for tag in system_tags:
            all_tags[tag.name] = tag
        
        # 添加 AI 标签（覆盖同名系统标签）
        if ai_tags:
            for tag in ai_tags:
                if tag.name in all_tags:
                    # 如果已存在，提高权重
                    all_tags[tag.name].weight = max(all_tags[tag.name].weight, tag.weight)
                else:
                    all_tags[tag.name] = tag
        
        # 添加用户标签（优先级最高）
        if user_tags:
            for tag in user_tags:
                all_tags[tag.name] = tag
        
        # 按权重排序
        merged = list(all_tags.values())
        merged.sort(key=lambda t: (t.weight, t.confidence), reverse=True)
        
        # 限制数量
        return merged[:12]  # 最多 12 个标签
    
    def get_popular_tags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取热门标签
        
        Args:
            limit: 返回数量
            
        Returns:
            标签统计列表
        """
        try:
            # 获取所有钱包的标签
            wallets = db.fetch_all("SELECT tags FROM wallets WHERE tags IS NOT NULL")
            
            tag_counts = {}
            
            for wallet in wallets:
                if not wallet["tags"]:
                    continue
                
                tags_data = json.loads(wallet["tags"])
                
                for tag in tags_data:
                    tag_name = tag if isinstance(tag, str) else tag.get("name")
                    if tag_name:
                        tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
            
            # 排序
            popular = [
                {"name": name, "count": count}
                for name, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            ]
            
            return popular[:limit]
            
        except Exception as e:
            logger.error(f"获取热门标签失败: {e}")
            return []
    
    def search_by_tags(
        self,
        tags: List[str],
        match_all: bool = False
    ) -> List[str]:
        """
        根据标签搜索钱包
        
        Args:
            tags: 标签列表
            match_all: 是否匹配所有标签（True=AND, False=OR）
            
        Returns:
            钱包地址列表
        """
        try:
            wallets = db.fetch_all(
                "SELECT address, tags FROM wallets WHERE tags IS NOT NULL"
            )
            
            result = []
            
            for wallet in wallets:
                if not wallet["tags"]:
                    continue
                
                tags_data = json.loads(wallet["tags"])
                wallet_tags = [
                    t if isinstance(t, str) else t.get("name")
                    for t in tags_data
                ]
                
                if match_all:
                    # 匹配所有标签
                    if all(tag in wallet_tags for tag in tags):
                        result.append(wallet["address"])
                else:
                    # 匹配任意标签
                    if any(tag in wallet_tags for tag in tags):
                        result.append(wallet["address"])
            
            return result
            
        except Exception as e:
            logger.error(f"标签搜索失败: {e}")
            return []


# 全局标签管理器实例
tag_manager = TagManager()


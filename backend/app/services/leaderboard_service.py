"""排行榜管理服务（SQLite 持久化）。

该服务提供榜单的增删改查以及榜单预览查询能力，供后台配置和公开榜单展示使用。
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from app.database import db

# 可用于排序/过滤的允许字段，避免 SQL 注入
ALLOWED_SORT_FIELDS = {
    "roi",
    "win_rate",
    "profit_loss_ratio",
    "max_drawdown",
    "smart_money_score",
    "total_pnl",
    "sharpe_ratio",
    "annual_return",
    "closed_trades_count",
    "last_updated",
    "liquidation_count",
}

ALLOWED_FILTER_FIELDS = ALLOWED_SORT_FIELDS | {
    "wallet_age_days",
    "initial_capital",
    "trading_frequency",
    "style",
    "net_deposits",
}


class LeaderboardService:
    """封装榜单的存储与查询逻辑。"""

    def list_leaderboards(self, include_disabled: bool = False) -> List[Dict[str, Any]]:
        """返回榜单列表，支持是否包含已禁用项。"""
        where_clause = "" if include_disabled else "WHERE enabled = 1"
        sql = f"SELECT * FROM leaderboards {where_clause} ORDER BY updated_at DESC NULLS LAST, id DESC"
        rows = db.fetch_all(sql)
        return [self._deserialize(row) for row in rows]

    def get_leaderboard(self, name: str) -> Optional[Dict[str, Any]]:
        """按名称获取榜单配置。"""
        row = db.fetch_one("SELECT * FROM leaderboards WHERE name = ?", (name,))
        return self._deserialize(row) if row else None

    def create_leaderboard(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的榜单配置。"""
        filters_json = json.dumps(payload["filters"], ensure_ascii=False)
        db.execute(
            """
            INSERT INTO leaderboards (name, display_name, description, filters, sort_by, sort_order, top_n, enabled, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                payload["name"],
                payload.get("display_name", payload["name"]),
                payload.get("description", ""),
                filters_json,
                payload.get("sort_by"),
                payload.get("sort_order", "DESC"),
                payload.get("top_n", 20),
                payload.get("enabled", True),
            ),
        )
        logger.info(f"创建榜单: {payload['name']}")
        return self.get_leaderboard(payload["name"])  # 返回持久化后的结果

    def update_leaderboard(self, name: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新榜单配置，若不存在则返回 None。"""
        existing = self.get_leaderboard(name)
        if not existing:
            return None

        merged = {**existing, **updates}
        filters_json = json.dumps(merged.get("filters", {}), ensure_ascii=False)
        db.execute(
            """
            UPDATE leaderboards
            SET display_name = ?, description = ?, filters = ?, sort_by = ?, sort_order = ?, top_n = ?, enabled = ?, updated_at = CURRENT_TIMESTAMP
            WHERE name = ?
            """,
            (
                merged.get("display_name", name),
                merged.get("description", existing.get("description", "")),
                filters_json,
                merged.get("sort_by"),
                merged.get("sort_order", "DESC"),
                merged.get("top_n", 20),
                merged.get("enabled", True),
                name,
            ),
        )
        logger.info(f"更新榜单: {name}")
        return self.get_leaderboard(name)

    def delete_leaderboard(self, name: str) -> bool:
        """删除榜单，返回是否删除成功。"""
        result = db.execute("DELETE FROM leaderboards WHERE name = ?", (name,))
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"删除榜单: {name}")
        return deleted

    def toggle_leaderboard(self, name: str, enabled: bool) -> Optional[Dict[str, Any]]:
        """启用/禁用榜单。"""
        result = db.execute(
            "UPDATE leaderboards SET enabled = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
            (enabled, name),
        )
        if result.rowcount == 0:
            return None
        state = "启用" if enabled else "禁用"
        logger.info(f"{state}榜单: {name}")
        return self.get_leaderboard(name)

    def preview_leaderboard(self, name: str) -> Optional[Dict[str, Any]]:
        """按榜单配置返回榜单的最新数据预览。"""
        leaderboard = self.get_leaderboard(name)
        if not leaderboard:
            return None

        where_clause, params = self._build_filters(leaderboard.get("filters", {}))
        sort_by = leaderboard.get("sort_by") or "smart_money_score"
        sort_order = leaderboard.get("sort_order", "DESC").upper()
        top_n = leaderboard.get("top_n", 20)

        if sort_by not in ALLOWED_SORT_FIELDS:
            sort_by = "smart_money_score"
        sort_order = "DESC" if sort_order not in {"ASC", "DESC"} else sort_order

        sql = (
            "SELECT address, roi, win_rate, profit_loss_ratio, max_drawdown, smart_money_score, total_pnl, sharpe_ratio, "
            "annual_return, closed_trades_count, liquidation_count, last_updated "
            "FROM wallets "
            f"{where_clause} "
            f"ORDER BY {sort_by} {sort_order} "
            "LIMIT ?"
        )
        params.append(top_n)
        wallets = db.fetch_all(sql, tuple(params))
        return {"leaderboard": leaderboard, "wallets": wallets}

    def _build_filters(self, filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """将过滤条件转换成 SQL WHERE 子句和参数列表。"""
        clauses: List[str] = []
        params: List[Any] = []
        for key, condition in filters.items():
            if key not in ALLOWED_FILTER_FIELDS:
                logger.warning(f"忽略未允许的过滤字段: {key}")
                continue

            if isinstance(condition, dict):
                if "min" in condition:
                    clauses.append(f"{key} >= ?")
                    params.append(condition["min"])
                if "max" in condition:
                    clauses.append(f"{key} <= ?")
                    params.append(condition["max"])
            else:
                clauses.append(f"{key} = ?")
                params.append(condition)

        if clauses:
            return "WHERE " + " AND ".join(clauses), params
        return "", params

    def _deserialize(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """将数据库行转换为 Python 对象并解析 JSON 字段。"""
        leaderboard = dict(row)
        filters_raw = leaderboard.get("filters") or "{}"
        try:
            leaderboard["filters"] = json.loads(filters_raw)
        except json.JSONDecodeError:
            logger.warning(f"榜单过滤条件解析失败，使用空对象: {filters_raw}")
            leaderboard["filters"] = {}
        return leaderboard


leaderboard_service = LeaderboardService()

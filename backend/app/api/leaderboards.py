"""榜单管理 API，供后台和公开页调用。

提供榜单 CRUD、启用/禁用、预览功能，配合 SQLite 存储落地。"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, validator

from app.services.leaderboard_service import leaderboard_service, ALLOWED_SORT_FIELDS

router = APIRouter()


class FilterField(BaseModel):
    """单个过滤字段定义。"""

    min: Optional[float] = Field(None, description="最小值过滤")
    max: Optional[float] = Field(None, description="最大值过滤")


class LeaderboardPayload(BaseModel):
    """榜单创建/更新请求体。"""

    name: str = Field(..., description="榜单唯一名称")
    display_name: Optional[str] = Field(None, description="榜单显示名称")
    description: Optional[str] = Field("", description="榜单描述")
    filters: Dict[str, Any] = Field(default_factory=dict, description="过滤条件，键值需与钱包字段匹配")
    sort_by: Optional[str] = Field("smart_money_score", description="排序字段")
    sort_order: Optional[str] = Field("DESC", description="排序方向 ASC/DESC")
    top_n: Optional[int] = Field(20, ge=1, le=200, description="榜单数量")
    enabled: Optional[bool] = Field(True, description="是否启用")

    @validator("sort_by")
    def validate_sort_by(cls, value: Optional[str]) -> Optional[str]:
        """校验排序字段避免 SQL 注入。"""
        if value is None:
            return value
        if value not in ALLOWED_SORT_FIELDS:
            raise ValueError(f"排序字段 {value} 不被允许")
        return value

    @validator("sort_order")
    def validate_sort_order(cls, value: Optional[str]) -> Optional[str]:
        """校验排序方向。"""
        if value is None:
            return value
        normalized = value.upper()
        if normalized not in {"ASC", "DESC"}:
            raise ValueError("sort_order 只能为 ASC 或 DESC")
        return normalized


@router.get("")
async def list_leaderboards(include_disabled: bool = Query(False, description="是否包含禁用的榜单")):
    """返回所有榜单配置。"""
    return leaderboard_service.list_leaderboards(include_disabled=include_disabled)


@router.get("/{name}")
async def get_leaderboard(name: str):
    """获取单个榜单详情。"""
    leaderboard = leaderboard_service.get_leaderboard(name)
    if not leaderboard:
        raise HTTPException(status_code=404, detail="榜单不存在")
    return leaderboard


@router.post("")
async def create_leaderboard(payload: LeaderboardPayload):
    """创建新榜单。"""
    if leaderboard_service.get_leaderboard(payload.name):
        raise HTTPException(status_code=400, detail="榜单名称已存在")
    return leaderboard_service.create_leaderboard(payload.dict())


@router.put("/{name}")
async def update_leaderboard(name: str, payload: LeaderboardPayload):
    """更新指定榜单。"""
    updated = leaderboard_service.update_leaderboard(name, payload.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="榜单不存在")
    return updated


@router.patch("/{name}/toggle")
async def toggle_leaderboard(name: str, enabled: bool):
    """启用或禁用榜单。"""
    updated = leaderboard_service.toggle_leaderboard(name, enabled)
    if not updated:
        raise HTTPException(status_code=404, detail="榜单不存在")
    return updated


@router.delete("/{name}")
async def delete_leaderboard(name: str):
    """删除榜单。"""
    deleted = leaderboard_service.delete_leaderboard(name)
    if not deleted:
        raise HTTPException(status_code=404, detail="榜单不存在")
    return {"deleted": True}


@router.get("/{name}/preview")
async def preview_leaderboard(name: str):
    """预览榜单对应的钱包排名数据。"""
    preview = leaderboard_service.preview_leaderboard(name)
    if not preview:
        raise HTTPException(status_code=404, detail="榜单不存在或无数据")
    return preview

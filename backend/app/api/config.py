"""配置管理 API，提供带校验的配置读取与更新能力。"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from app.services.config_service import config_service

router = APIRouter()


class UpdateRequest(BaseModel):
    """配置更新请求体，接受任意键值对并依靠服务层做细粒度校验。"""

    updates: dict = Field(default_factory=dict, description="要更新的配置内容")


@router.get("/{config_name}")
async def get_config(config_name: str):
    """获取指定配置的当前值。"""
    try:
        return {"config": config_service.get(config_name)}
    except Exception as e:  # pragma: no cover - FastAPI 自动捕获
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{config_name}")
async def update_config(config_name: str, payload: UpdateRequest):
    """更新配置并返回最新快照。"""
    try:
        updated = config_service.update(config_name, payload.updates)
        return {"config": updated}
    except ValueError as e:
        # Pydantic 校验失败时返回 400，错误信息便于前端提示
        logger.warning(f"配置校验失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # pragma: no cover
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

"""配置相关 API"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from app.config import config

router = APIRouter()


@router.get("/{config_name}")
async def get_config(config_name: str):
    """获取配置"""
    try:
        config_data = config.get_config(config_name)
        return {"config": config_data}
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{config_name}")
async def update_config(config_name: str, updates: dict):
    """更新配置"""
    try:
        config.update_config(config_name, updates)
        return {"success": True}
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


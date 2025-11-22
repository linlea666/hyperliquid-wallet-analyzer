"""
日志管理 API
提供日志查询、统计、导出等功能
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from typing import Optional
from pydantic import BaseModel
from loguru import logger

from app.services.logging import log_manager
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter()


class LogQuery(BaseModel):
    """日志查询请求"""
    level: Optional[str] = None
    module: Optional[str] = None
    category: Optional[str] = None
    keyword: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    user_id: Optional[int] = None
    limit: int = 100
    offset: int = 0


@router.get("")
async def get_logs(
    level: Optional[str] = None,
    module: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    user_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    查询日志
    
    参数:
        - level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        - module: 模块名称
        - category: 分类 (system/business/access/performance)
        - keyword: 关键词搜索
        - start_time: 开始时间 (ISO 格式)
        - end_time: 结束时间 (ISO 格式)
        - user_id: 用户 ID
        - limit: 返回数量
        - offset: 偏移量
    """
    try:
        logs, total = log_manager.query_logs(
            level=level,
            module=module,
            category=category,
            keyword=keyword,
            start_time=start_time,
            end_time=end_time,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "data": {
                "logs": logs,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
    except Exception as e:
        logger.error(f"查询日志失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {
                "logs": [],
                "total": 0
            }
        }


@router.get("/statistics")
async def get_log_statistics(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    获取日志统计信息
    
    参数:
        - start_time: 开始时间
        - end_time: 结束时间
    """
    try:
        stats = log_manager.get_log_statistics(
            start_time=start_time,
            end_time=end_time
        )
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取日志统计失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


@router.get("/errors")
async def get_error_logs(
    hours: int = 24,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    获取最近的错误日志
    
    参数:
        - hours: 最近几小时
        - limit: 返回数量
    """
    try:
        errors = log_manager.get_error_logs(hours=hours, limit=limit)
        
        return {
            "success": True,
            "data": errors
        }
    except Exception as e:
        logger.error(f"获取错误日志失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": []
        }


@router.get("/modules")
async def get_modules(current_user: User = Depends(get_current_user)):
    """获取所有模块列表"""
    try:
        modules = log_manager.get_modules()
        
        return {
            "success": True,
            "data": modules
        }
    except Exception as e:
        logger.error(f"获取模块列表失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": []
        }


@router.get("/export")
async def export_logs(
    level: Optional[str] = None,
    module: Optional[str] = None,
    category: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    format: str = 'csv',
    current_user: User = Depends(get_current_user)
):
    """
    导出日志
    
    参数:
        - level: 日志级别
        - module: 模块名称
        - category: 分类
        - start_time: 开始时间
        - end_time: 结束时间
        - format: 导出格式 (csv/json)
    """
    try:
        content = log_manager.export_logs(
            level=level,
            module=module,
            category=category,
            start_time=start_time,
            end_time=end_time,
            format=format
        )
        
        if not content:
            raise HTTPException(status_code=404, detail="没有找到日志")
        
        # 设置响应头
        media_type = "text/csv" if format == "csv" else "application/json"
        filename = f"logs_{format}.{format}"
        
        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_logs(
    days: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """
    清理日志
    
    参数:
        - days: 保留天数（不提供则清空所有）
    """
    try:
        if days:
            count = log_manager.clear_old_logs(days=days)
            message = f"清理了 {count} 条旧日志（{days} 天前）"
        else:
            count = log_manager.clear_all_logs()
            message = f"清空了所有日志，共 {count} 条"
        
        return {
            "success": True,
            "message": message,
            "data": {"count": count}
        }
    except Exception as e:
        logger.error(f"清理日志失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {"count": 0}
        }


# 导出
__all__ = ["router"]


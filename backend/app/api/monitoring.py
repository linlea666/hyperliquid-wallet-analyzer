"""
系统监控 API
提供系统资源、性能指标、健康检查等接口
"""
from fastapi import APIRouter, Depends
from loguru import logger

from app.services.monitoring import system_monitor, metrics_collector
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/system")
async def get_system_metrics(current_user: User = Depends(get_current_user)):
    """
    获取系统监控指标
    
    返回 CPU、内存、磁盘、网络等系统资源使用情况
    """
    try:
        metrics = system_monitor.get_all_metrics()
        
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        logger.error(f"获取系统指标失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


@router.get("/health")
async def health_check(current_user: User = Depends(get_current_user)):
    """
    健康检查
    
    检查系统资源使用情况，返回健康状态
    """
    try:
        health = system_monitor.check_health()
        
        return {
            "success": True,
            "data": health
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {
                "status": "error",
                "level": "error",
                "issues": [str(e)],
                "warnings": []
            }
        }


@router.get("/cpu")
async def get_cpu_info(current_user: User = Depends(get_current_user)):
    """获取 CPU 信息"""
    try:
        cpu_info = system_monitor.get_cpu_info()
        
        return {
            "success": True,
            "data": cpu_info
        }
    except Exception as e:
        logger.error(f"获取 CPU 信息失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


@router.get("/memory")
async def get_memory_info(current_user: User = Depends(get_current_user)):
    """获取内存信息"""
    try:
        memory_info = system_monitor.get_memory_info()
        
        return {
            "success": True,
            "data": memory_info
        }
    except Exception as e:
        logger.error(f"获取内存信息失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


@router.get("/disk")
async def get_disk_info(current_user: User = Depends(get_current_user)):
    """获取磁盘信息"""
    try:
        disk_info = system_monitor.get_disk_info()
        
        return {
            "success": True,
            "data": disk_info
        }
    except Exception as e:
        logger.error(f"获取磁盘信息失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


@router.get("/network")
async def get_network_info(current_user: User = Depends(get_current_user)):
    """获取网络信息"""
    try:
        network_info = system_monitor.get_network_info()
        
        return {
            "success": True,
            "data": network_info
        }
    except Exception as e:
        logger.error(f"获取网络信息失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


@router.get("/process")
async def get_process_info(current_user: User = Depends(get_current_user)):
    """获取进程信息"""
    try:
        process_info = system_monitor.get_process_info()
        
        return {
            "success": True,
            "data": process_info
        }
    except Exception as e:
        logger.error(f"获取进程信息失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


@router.get("/database")
async def get_database_info(current_user: User = Depends(get_current_user)):
    """获取数据库信息"""
    try:
        db_info = system_monitor.get_database_info()
        
        return {
            "success": True,
            "data": db_info
        }
    except Exception as e:
        logger.error(f"获取数据库信息失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


@router.get("/uptime")
async def get_uptime(current_user: User = Depends(get_current_user)):
    """获取系统运行时间"""
    try:
        uptime = system_monitor.get_uptime()
        
        return {
            "success": True,
            "data": uptime
        }
    except Exception as e:
        logger.error(f"获取运行时间失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


@router.get("/business")
async def get_business_metrics(current_user: User = Depends(get_current_user)):
    """获取业务指标"""
    try:
        metrics = metrics_collector.get_business_metrics()
        
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        logger.error(f"获取业务指标失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


@router.get("/api")
async def get_api_metrics(current_user: User = Depends(get_current_user)):
    """获取 API 指标"""
    try:
        metrics = metrics_collector.get_api_metrics()
        
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        logger.error(f"获取 API 指标失败: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


# 导出
__all__ = ["router"]


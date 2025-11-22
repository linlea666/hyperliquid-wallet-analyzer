"""
批量导入 API
支持多种导入方式、实时进度追踪
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional
from loguru import logger

from app.services.import_manager import import_manager, ImportStatus

router = APIRouter()


class CreateImportTaskRequest(BaseModel):
    """创建导入任务请求"""
    addresses: List[str] = Field(..., description="钱包地址列表")
    batch_size: int = Field(50, ge=10, le=100, description="每批处理数量")
    frequency: str = Field("normal", description="更新频率: active/normal/inactive")


class ImportFromTextRequest(BaseModel):
    """从文本导入请求"""
    text: str = Field(..., description="包含地址的文本")
    batch_size: int = Field(50, ge=10, le=100, description="每批处理数量")
    frequency: str = Field("normal", description="更新频率")


@router.post("/create-task")
async def create_import_task(
    request: CreateImportTaskRequest,
    background_tasks: BackgroundTasks
):
    """
    创建导入任务
    
    - 支持批量导入钱包
    - 自动分批处理
    - 后台异步执行
    """
    try:
        if not request.addresses:
            raise HTTPException(status_code=400, detail="地址列表不能为空")
        
        if len(request.addresses) > 10000:
            raise HTTPException(status_code=400, detail="单次最多导入 10000 个地址")
        
        # 创建任务
        task = import_manager.create_task(
            addresses=request.addresses,
            batch_size=request.batch_size,
            frequency=request.frequency
        )
        
        # 后台执行
        background_tasks.add_task(import_manager.execute_task, task.task_id)
        
        return {
            "success": True,
            "message": "导入任务已创建",
            "data": task.get_progress()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建导入任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.post("/from-text")
async def import_from_text(
    request: ImportFromTextRequest,
    background_tasks: BackgroundTasks
):
    """
    从文本导入
    
    - 支持多种分隔符（换行、逗号、分号、空格）
    - 自动提取地址
    """
    try:
        # 解析地址
        addresses = import_manager.parse_addresses_from_text(request.text)
        
        if not addresses:
            raise HTTPException(status_code=400, detail="未找到有效的钱包地址")
        
        # 创建任务
        task = import_manager.create_task(
            addresses=addresses,
            batch_size=request.batch_size,
            frequency=request.frequency
        )
        
        # 后台执行
        background_tasks.add_task(import_manager.execute_task, task.task_id)
        
        return {
            "success": True,
            "message": f"已识别 {len(addresses)} 个地址，导入任务已创建",
            "data": task.get_progress()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"从文本导入失败: {e}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.post("/from-file")
async def import_from_file(
    file: UploadFile = File(...),
    batch_size: int = 50,
    frequency: str = "normal",
    background_tasks: BackgroundTasks = None
):
    """
    从文件导入
    
    - 支持 CSV、TXT 文件
    - 自动解析地址
    """
    try:
        # 检查文件类型
        if not file.filename.endswith(('.csv', '.txt')):
            raise HTTPException(status_code=400, detail="只支持 CSV 和 TXT 文件")
        
        # 读取文件内容
        content = await file.read()
        
        # 解析地址
        if file.filename.endswith('.csv'):
            addresses = import_manager.parse_addresses_from_csv(content)
        else:
            # TXT 文件
            text = content.decode('utf-8')
            addresses = import_manager.parse_addresses_from_text(text)
        
        if not addresses:
            raise HTTPException(status_code=400, detail="文件中未找到有效的钱包地址")
        
        # 创建任务
        task = import_manager.create_task(
            addresses=addresses,
            batch_size=batch_size,
            frequency=frequency
        )
        
        # 后台执行
        background_tasks.add_task(import_manager.execute_task, task.task_id)
        
        return {
            "success": True,
            "message": f"已从文件中识别 {len(addresses)} 个地址，导入任务已创建",
            "data": task.get_progress()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"从文件导入失败: {e}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/task/{task_id}")
async def get_task_progress(task_id: str):
    """
    获取任务进度
    
    - 实时进度
    - 处理状态
    - 预计剩余时间
    """
    try:
        task = import_manager.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return {
            "success": True,
            "data": task.get_progress()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务进度失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取进度失败: {str(e)}")


@router.get("/task/{task_id}/result")
async def get_task_result(task_id: str):
    """
    获取任务完整结果
    
    - 成功列表
    - 失败列表
    - 跳过列表
    - 错误信息
    """
    try:
        task = import_manager.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task.status not in [ImportStatus.COMPLETED, ImportStatus.FAILED, ImportStatus.CANCELLED]:
            raise HTTPException(status_code=400, detail="任务尚未完成")
        
        return {
            "success": True,
            "data": task.get_result()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取结果失败: {str(e)}")


@router.post("/task/{task_id}/cancel")
async def cancel_task(task_id: str):
    """
    取消任务
    
    - 停止正在执行的任务
    """
    try:
        success = import_manager.cancel_task(task_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="无法取消任务（任务不存在或已完成）")
        
        return {
            "success": True,
            "message": "任务已取消"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"取消失败: {str(e)}")


@router.get("/tasks")
async def get_all_tasks():
    """
    获取所有任务
    
    - 任务列表
    - 状态概览
    """
    try:
        tasks = import_manager.get_all_tasks()
        
        return {
            "success": True,
            "data": {
                "tasks": tasks,
                "total": len(tasks)
            }
        }
        
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取列表失败: {str(e)}")


@router.delete("/tasks/cleanup")
async def cleanup_old_tasks(days: int = 7):
    """
    清理旧任务
    
    - 删除指定天数前的已完成任务
    """
    try:
        import_manager.cleanup_old_tasks(days=days)
        
        return {
            "success": True,
            "message": f"已清理 {days} 天前的旧任务"
        }
        
    except Exception as e:
        logger.error(f"清理任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理失败: {str(e)}")


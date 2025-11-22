"""
AI 分析 API
提供 AI 智能分析相关的 API 端点
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from loguru import logger

from app.services.ai.ai_scheduler import ai_scheduler, Priority
from app.services.ai.deepseek_service import deepseek_service
from app.api.auth import get_current_user


router = APIRouter()


# 请求模型
class AnalyzeRequest(BaseModel):
    """分析请求"""
    wallet_address: str = Field(..., description="钱包地址")
    analysis_types: Optional[List[str]] = Field(
        default=['style', 'strategy', 'risk'],
        description="分析类型列表"
    )
    priority: Optional[str] = Field(default='medium', description="优先级: high/medium/low")
    force: Optional[bool] = Field(default=False, description="是否强制分析（忽略缓存）")


class BatchAnalyzeRequest(BaseModel):
    """批量分析请求"""
    wallet_addresses: List[str] = Field(..., description="钱包地址列表")
    analysis_types: Optional[List[str]] = Field(
        default=['style', 'strategy', 'risk'],
        description="分析类型列表"
    )
    priority: Optional[str] = Field(default='medium', description="优先级")


class AIConfigUpdate(BaseModel):
    """AI 配置更新"""
    enabled: Optional[bool] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    daily_limit: Optional[int] = None
    cost_limit: Optional[float] = None
    score_threshold: Optional[int] = None


# API 端点
@router.post("/analyze")
async def analyze_wallet(
    request: AnalyzeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    分析钱包
    
    对指定钱包进行 AI 智能分析
    """
    try:
        # 转换优先级
        priority_map = {
            'high': Priority.HIGH,
            'medium': Priority.MEDIUM,
            'low': Priority.LOW
        }
        priority = priority_map.get(request.priority.lower(), Priority.MEDIUM)
        
        # 调度分析任务
        result = await ai_scheduler.schedule_analysis(
            wallet_address=request.wallet_address,
            analysis_types=request.analysis_types,
            priority=priority,
            force=request.force
        )
        
        return {
            'success': True,
            'data': result
        }
        
    except Exception as e:
        logger.error(f"分析钱包失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-analyze")
async def batch_analyze_wallets(
    request: BatchAnalyzeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    批量分析钱包
    
    对多个钱包进行批量 AI 分析
    """
    try:
        # 转换优先级
        priority_map = {
            'high': Priority.HIGH,
            'medium': Priority.MEDIUM,
            'low': Priority.LOW
        }
        priority = priority_map.get(request.priority.lower(), Priority.MEDIUM)
        
        # 批量调度
        result = await ai_scheduler.batch_schedule(
            wallet_addresses=request.wallet_addresses,
            analysis_types=request.analysis_types,
            priority=priority
        )
        
        return {
            'success': True,
            'data': result
        }
        
    except Exception as e:
        logger.error(f"批量分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{wallet_address}")
async def get_analysis(
    wallet_address: str,
    analysis_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    获取分析结果
    
    获取指定钱包的 AI 分析结果（从缓存）
    """
    try:
        result = ai_scheduler.get_cached_analysis(wallet_address, analysis_type)
        
        if not result:
            return {
                'success': False,
                'message': '未找到分析结果',
                'data': None
            }
        
        return {
            'success': True,
            'data': result
        }
        
    except Exception as e:
        logger.error(f"获取分析结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics(current_user: dict = Depends(get_current_user)):
    """
    获取 AI 使用统计
    
    返回 AI 调用次数、Token 使用量、成本等统计信息
    """
    try:
        # 获取使用统计
        usage_stats = deepseek_service.get_usage_stats()
        
        # 获取调度器状态
        scheduler_status = ai_scheduler.get_status()
        
        return {
            'success': True,
            'data': {
                'usage': usage_stats,
                'scheduler': scheduler_status
            }
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_config(current_user: dict = Depends(get_current_user)):
    """
    获取 AI 配置
    
    返回当前 AI 系统配置
    """
    try:
        config = deepseek_service.config.copy()
        
        # 隐藏敏感信息
        if 'api_key' in config and config['api_key']:
            config['api_key'] = config['api_key'][:10] + '...'
        
        return {
            'success': True,
            'data': config
        }
        
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config")
async def update_config(
    config_update: AIConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新 AI 配置
    
    更新 AI 系统配置（需要管理员权限）
    """
    try:
        # 检查权限
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="需要管理员权限")
        
        # 获取当前配置
        from app.database import db
        import json
        
        config_row = db.fetch_one(
            "SELECT config_value FROM system_configs WHERE config_key = ?",
            ("ai",)
        )
        
        if config_row:
            config = json.loads(config_row['config_value'])
        else:
            config = deepseek_service.config.copy()
        
        # 更新配置
        update_data = config_update.dict(exclude_unset=True)
        config.update(update_data)
        
        # 保存到数据库
        from datetime import datetime
        db.execute("""
            INSERT OR REPLACE INTO system_configs
            (config_key, config_value, updated_at)
            VALUES (?, ?, ?)
        """, (
            'ai',
            json.dumps(config, ensure_ascii=False),
            datetime.now().isoformat()
        ))
        
        # 重新加载配置
        deepseek_service.reload_config()
        
        logger.info(f"AI 配置已更新: {update_data}")
        
        return {
            'success': True,
            'message': '配置更新成功',
            'data': config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_ai(current_user: dict = Depends(get_current_user)):
    """
    测试 AI 连接
    
    测试 DeepSeek API 是否正常工作
    """
    try:
        # 发送测试请求
        messages = [
            {
                "role": "user",
                "content": "请用一句话介绍你自己。"
            }
        ]
        
        response = await deepseek_service.chat_completion(
            messages=messages,
            max_tokens=100
        )
        
        content = response['choices'][0]['message']['content']
        
        return {
            'success': True,
            'message': 'AI 连接正常',
            'data': {
                'response': content,
                'usage': response.get('usage', {})
            }
        }
        
    except Exception as e:
        logger.error(f"AI 测试失败: {e}")
        return {
            'success': False,
            'message': f'AI 连接失败: {str(e)}',
            'data': None
        }


@router.get("/queue")
async def get_queue_status(current_user: dict = Depends(get_current_user)):
    """
    获取任务队列状态
    
    返回当前 AI 分析任务队列的状态
    """
    try:
        status = ai_scheduler.get_status()
        
        return {
            'success': True,
            'data': status
        }
        
    except Exception as e:
        logger.error(f"获取队列状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache/{wallet_address}")
async def clear_cache(
    wallet_address: str,
    analysis_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    清除分析缓存
    
    清除指定钱包的 AI 分析缓存
    """
    try:
        from app.database import db
        
        if analysis_type:
            # 清除特定类型的缓存
            db.execute("""
                DELETE FROM ai_analysis_cache
                WHERE wallet_address = ? AND analysis_type = ?
            """, (wallet_address, analysis_type))
        else:
            # 清除所有缓存
            db.execute("""
                DELETE FROM ai_analysis_cache
                WHERE wallet_address = ?
            """, (wallet_address,))
        
        logger.info(f"清除缓存: {wallet_address}, 类型: {analysis_type or '全部'}")
        
        return {
            'success': True,
            'message': '缓存已清除'
        }
        
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


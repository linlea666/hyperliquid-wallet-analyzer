"""
钱包管理 API
提供钱包的添加、删除、更新、查询等功能
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from loguru import logger

from app.services.scheduler import scheduler
from app.services.wallet_analyzer import WalletAnalyzer
from app.database import db

router = APIRouter()


class AddWalletRequest(BaseModel):
    """添加钱包请求"""
    address: str = Field(..., description="钱包地址")
    frequency: str = Field("normal", description="更新频率: active/normal/inactive")
    force_update: bool = Field(False, description="是否强制更新")


class BatchAddWalletsRequest(BaseModel):
    """批量添加钱包请求"""
    addresses: List[str] = Field(..., description="钱包地址列表")
    frequency: str = Field("normal", description="更新频率")


class UpdateWalletRequest(BaseModel):
    """更新钱包请求"""
    address: str = Field(..., description="钱包地址")
    force: bool = Field(False, description="是否强制更新")


class WalletQueryRequest(BaseModel):
    """钱包查询请求"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    sort_by: str = Field("smart_money_score", description="排序字段")
    sort_order: str = Field("DESC", description="排序方向: ASC/DESC")
    filters: Optional[Dict[str, Any]] = Field(None, description="筛选条件")


@router.post("/add")
async def add_wallet(
    request: AddWalletRequest,
    background_tasks: BackgroundTasks
):
    """
    添加钱包到监控列表
    
    - 立即分析钱包数据
    - 计算评分
    - 加入定时更新队列
    """
    try:
        # 检查地址格式
        if not request.address.startswith("0x") or len(request.address) != 42:
            raise HTTPException(status_code=400, detail="无效的钱包地址格式")
        
        # 检查是否已存在
        existing = db.fetch_one(
            "SELECT id, smart_money_score, score_grade FROM wallets WHERE address = ?",
            (request.address,)
        )
        
        if existing and not request.force_update:
            return {
                "success": True,
                "message": "钱包已存在",
                "data": {
                    "address": request.address,
                    "score": existing["smart_money_score"],
                    "grade": existing["score_grade"],
                    "is_new": False
                }
            }
        
        # 后台任务：添加钱包
        background_tasks.add_task(
            scheduler.add_wallet,
            request.address,
            request.frequency
        )
        
        return {
            "success": True,
            "message": "钱包添加成功，正在后台分析...",
            "data": {
                "address": request.address,
                "frequency": request.frequency,
                "is_new": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加钱包失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加钱包失败: {str(e)}")


@router.post("/batch-add")
async def batch_add_wallets(
    request: BatchAddWalletsRequest,
    background_tasks: BackgroundTasks
):
    """
    批量添加钱包
    
    - 支持一次添加多个钱包
    - 后台异步处理
    """
    try:
        if not request.addresses:
            raise HTTPException(status_code=400, detail="钱包地址列表不能为空")
        
        if len(request.addresses) > 100:
            raise HTTPException(status_code=400, detail="一次最多添加 100 个钱包")
        
        # 验证地址格式
        invalid_addresses = [
            addr for addr in request.addresses 
            if not addr.startswith("0x") or len(addr) != 42
        ]
        
        if invalid_addresses:
            raise HTTPException(
                status_code=400,
                detail=f"以下地址格式无效: {', '.join(invalid_addresses[:5])}"
            )
        
        # 后台任务：批量添加
        for address in request.addresses:
            background_tasks.add_task(
                scheduler.add_wallet,
                address,
                request.frequency
            )
        
        return {
            "success": True,
            "message": f"已提交 {len(request.addresses)} 个钱包，正在后台处理...",
            "data": {
                "count": len(request.addresses),
                "frequency": request.frequency
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量添加钱包失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量添加失败: {str(e)}")


@router.delete("/{address}")
async def remove_wallet(address: str):
    """
    从监控列表移除钱包
    
    - 删除钱包及相关数据
    """
    try:
        # 检查是否存在
        existing = db.fetch_one(
            "SELECT id FROM wallets WHERE address = ?",
            (address,)
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="钱包不存在")
        
        # 删除钱包
        await scheduler.remove_wallet(address)
        
        return {
            "success": True,
            "message": "钱包已移除",
            "data": {
                "address": address
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"移除钱包失败: {e}")
        raise HTTPException(status_code=500, detail=f"移除钱包失败: {str(e)}")


@router.post("/update")
async def update_wallet(
    request: UpdateWalletRequest,
    background_tasks: BackgroundTasks
):
    """
    手动触发钱包更新
    
    - 立即更新钱包数据
    - 重新计算评分
    """
    try:
        # 检查是否存在
        existing = db.fetch_one(
            "SELECT id FROM wallets WHERE address = ?",
            (request.address,)
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="钱包不存在")
        
        # 后台任务：更新钱包
        analyzer = WalletAnalyzer(use_mock=False)
        background_tasks.add_task(
            analyzer.analyze_wallet,
            request.address,
            request.force
        )
        
        return {
            "success": True,
            "message": "钱包更新任务已提交",
            "data": {
                "address": request.address
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新钱包失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新钱包失败: {str(e)}")


@router.get("/{address}")
async def get_wallet(address: str):
    """
    获取钱包详情
    
    - 返回钱包完整信息
    - 包含评分、指标、交易记录等
    """
    try:
        analyzer = WalletAnalyzer()
        wallet = analyzer.get_wallet_from_db(address)
        
        if not wallet:
            raise HTTPException(status_code=404, detail="钱包不存在")
        
        # 获取最近交易
        recent_trades = db.fetch_all("""
            SELECT * FROM trades 
            WHERE wallet_address = ? 
            ORDER BY timestamp DESC 
            LIMIT 20
        """, (address,))
        
        # 获取当前持仓
        positions = db.fetch_all("""
            SELECT * FROM positions 
            WHERE wallet_address = ?
        """, (address,))
        
        return {
            "success": True,
            "data": {
                "wallet": wallet,
                "recent_trades": recent_trades,
                "positions": positions
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取钱包详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取钱包详情失败: {str(e)}")


@router.post("/query")
async def query_wallets(request: WalletQueryRequest):
    """
    查询钱包列表
    
    - 支持分页
    - 支持排序
    - 支持筛选
    """
    try:
        # 构建 SQL
        sql = "SELECT * FROM wallets WHERE 1=1"
        params = []
        
        # 应用筛选条件
        if request.filters:
            for key, value in request.filters.items():
                if isinstance(value, dict):
                    if "min" in value:
                        sql += f" AND {key} >= ?"
                        params.append(value["min"])
                    if "max" in value:
                        sql += f" AND {key} <= ?"
                        params.append(value["max"])
                else:
                    sql += f" AND {key} = ?"
                    params.append(value)
        
        # 计算总数
        count_sql = sql.replace("SELECT *", "SELECT COUNT(*)")
        total = db.fetch_one(count_sql, tuple(params))
        total_count = total["COUNT(*)"] if total else 0
        
        # 排序和分页
        sql += f" ORDER BY {request.sort_by} {request.sort_order}"
        sql += f" LIMIT ? OFFSET ?"
        params.extend([request.page_size, (request.page - 1) * request.page_size])
        
        # 查询数据
        wallets = db.fetch_all(sql, tuple(params))
        
        # 解析 JSON 字段
        for wallet in wallets:
            if wallet.get("tags"):
                try:
                    import json
                    wallet["tags"] = json.loads(wallet["tags"])
                except:
                    wallet["tags"] = []
        
        return {
            "success": True,
            "data": {
                "wallets": wallets,
                "pagination": {
                    "page": request.page,
                    "page_size": request.page_size,
                    "total": total_count,
                    "total_pages": (total_count + request.page_size - 1) // request.page_size
                }
            }
        }
        
    except Exception as e:
        logger.error(f"查询钱包列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/stats/summary")
async def get_stats_summary():
    """
    获取统计摘要
    
    - 总钱包数
    - 各等级分布
    - 平均评分
    - 今日更新数
    """
    try:
        # 总钱包数
        total = db.fetch_one("SELECT COUNT(*) as count FROM wallets")
        total_count = total["count"] if total else 0
        
        # 等级分布
        grade_stats = db.fetch_all("""
            SELECT score_grade, COUNT(*) as count 
            FROM wallets 
            GROUP BY score_grade 
            ORDER BY score_grade
        """)
        
        # 平均评分
        avg_score = db.fetch_one("""
            SELECT AVG(smart_money_score) as avg_score 
            FROM wallets 
            WHERE smart_money_score > 0
        """)
        avg = avg_score["avg_score"] if avg_score and avg_score["avg_score"] else 0
        
        # 今日更新数
        today_updates = db.fetch_one("""
            SELECT COUNT(*) as count 
            FROM wallets 
            WHERE date(last_updated) = date('now')
        """)
        today_count = today_updates["count"] if today_updates else 0
        
        return {
            "success": True,
            "data": {
                "total_wallets": total_count,
                "average_score": round(avg, 2),
                "today_updates": today_count,
                "grade_distribution": {
                    stat["score_grade"]: stat["count"] 
                    for stat in grade_stats
                }
            }
        }
        
    except Exception as e:
        logger.error(f"获取统计摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.get("/scheduler/status")
async def get_scheduler_status():
    """
    获取调度器状态
    
    - 是否运行中
    - 定时任务列表
    - 配置信息
    """
    try:
        status = scheduler.get_scheduler_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"获取调度器状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


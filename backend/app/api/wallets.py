"""钱包相关 API"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger

from app.services.storage import StorageService
from app.services.hyperliquid import HyperLiquidClient
from app.services.analyzer import AnalyzerService

router = APIRouter()

# 初始化服务
storage = StorageService()
hyperliquid = HyperLiquidClient()
analyzer = AnalyzerService()


class WalletImportRequest(BaseModel):
    """钱包导入请求"""
    addresses: List[str]


class WalletResponse(BaseModel):
    """钱包响应"""
    address: str
    imported_at: str
    last_updated: str
    metrics: dict
    metadata: dict


@router.post("/import")
async def import_wallets(request: WalletImportRequest):
    """导入钱包（单个或批量）"""
    try:
        results = {
            "success": [],
            "failed": [],
            "duplicated": []
        }
        
        for address in request.addresses:
            try:
                # 检查是否已存在
                if storage.wallet_exists(address):
                    results["duplicated"].append(address)
                    continue
                
                # 获取钱包数据
                wallet_data = await hyperliquid.get_wallet_data(address)
                
                # 分析钱包
                analyzed_data = analyzer.analyze_wallet(wallet_data)
                
                # 保存钱包
                storage.save_wallet(address, analyzed_data)
                
                results["success"].append(address)
                logger.info(f"✅ 成功导入钱包: {address}")
                
            except Exception as e:
                results["failed"].append({"address": address, "error": str(e)})
                logger.error(f"❌ 导入钱包失败 {address}: {e}")
        
        return results
        
    except Exception as e:
        logger.error(f"导入钱包异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def get_wallets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("score", regex="^(roi|win_rate|risk|age|score)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    search: Optional[str] = None,
    tag: str = Query("all", regex="^(all|recommended)$")
):
    """获取钱包列表"""
    try:
        wallets = storage.get_wallet_list(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            order=order,
            search=search,
            tag=tag
        )
        return wallets
    except Exception as e:
        logger.error(f"获取钱包列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{address}")
async def get_wallet_detail(address: str):
    """获取钱包详情"""
    try:
        wallet = storage.get_wallet(address)
        if not wallet:
            raise HTTPException(status_code=404, detail="钱包不存在")
        return wallet
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取钱包详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{address}/refresh")
async def refresh_wallet(address: str):
    """刷新钱包数据"""
    try:
        # 获取最新数据
        wallet_data = await hyperliquid.get_wallet_data(address)
        
        # 分析钱包
        analyzed_data = analyzer.analyze_wallet(wallet_data)
        
        # 更新钱包
        storage.save_wallet(address, analyzed_data)
        
        logger.info(f"✅ 刷新钱包成功: {address}")
        return {"success": True, "address": address}
        
    except Exception as e:
        logger.error(f"刷新钱包失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{address}")
async def delete_wallet(address: str):
    """删除钱包"""
    try:
        storage.delete_wallet(address)
        logger.info(f"✅ 删除钱包成功: {address}")
        return {"success": True}
    except Exception as e:
        logger.error(f"删除钱包失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{address}/deposits")
async def get_wallet_deposits(address: str):
    """获取钱包存款记录"""
    try:
        wallet = storage.get_wallet(address)
        if not wallet:
            raise HTTPException(status_code=404, detail="钱包不存在")
        return wallet.get("deposits", [])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取存款记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{address}/withdrawals")
async def get_wallet_withdrawals(address: str):
    """获取钱包取款记录"""
    try:
        wallet = storage.get_wallet(address)
        if not wallet:
            raise HTTPException(status_code=404, detail="钱包不存在")
        return wallet.get("withdrawals", [])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取取款记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


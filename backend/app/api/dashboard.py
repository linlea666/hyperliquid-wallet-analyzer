"""看板相关 API"""
from fastapi import APIRouter
from loguru import logger

from app.services.storage import StorageService
from app.services.analyzer import AnalyzerService

router = APIRouter()

storage = StorageService()
analyzer = AnalyzerService()


@router.get("/stats")
async def get_dashboard_stats():
    """获取看板统计数据"""
    try:
        wallets = storage.get_all_wallets()
        
        stats = {
            "total_wallets": len(wallets),
            "total_balance": sum(w.get("metrics", {}).get("current_balance", 0) for w in wallets),
            "total_pnl": sum(w.get("metrics", {}).get("total_pnl", 0) for w in wallets),
            "avg_roi": analyzer.calculate_avg_roi(wallets),
            "avg_win_rate": analyzer.calculate_avg_win_rate(wallets),
            "active_wallets_24h": analyzer.count_active_wallets(wallets, hours=24)
        }
        
        return stats
    except Exception as e:
        logger.error(f"获取看板统计失败: {e}")
        return {"error": str(e)}


@router.get("/long-short-ratio")
async def get_long_short_ratio():
    """获取多空比数据"""
    try:
        wallets = storage.get_all_wallets()
        ratio_data = analyzer.calculate_long_short_ratio(wallets)
        return ratio_data
    except Exception as e:
        logger.error(f"获取多空比失败: {e}")
        return {"error": str(e)}


@router.get("/anomalies")
async def get_anomalies():
    """获取异动数据"""
    try:
        wallets = storage.get_all_wallets()
        anomalies = analyzer.detect_anomalies(wallets)
        return {"anomalies": anomalies}
    except Exception as e:
        logger.error(f"获取异动数据失败: {e}")
        return {"error": str(e)}


@router.get("/rankings")
async def get_rankings():
    """获取排行榜"""
    try:
        wallets = storage.get_all_wallets()
        rankings = analyzer.get_rankings(wallets)
        return rankings
    except Exception as e:
        logger.error(f"获取排行榜失败: {e}")
        return {"error": str(e)}


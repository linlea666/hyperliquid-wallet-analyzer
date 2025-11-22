"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
import uvicorn

from app.api import wallets, dashboard, notifications, config as config_api, wallet_management, import_api, tag_api, auth, websocket, logs, monitoring, ai
from app.config import config, DATA_DIR
from app.utils.logger import setup_logger
from app.database import db
from app.services.scheduler import scheduler
from app.services.ai.ai_scheduler import ai_scheduler

# 设置日志
setup_logger()

# 创建 FastAPI 应用
app = FastAPI(
    title="HyperLiquid 钱包分析系统",
    description="聪明钱挖掘系统 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(websocket.router, prefix="/api", tags=["WebSocket"])
app.include_router(wallets.router, prefix="/api/wallets", tags=["钱包"])
app.include_router(wallet_management.router, prefix="/api/wallet-management", tags=["钱包管理"])
app.include_router(import_api.router, prefix="/api/import", tags=["批量导入"])
app.include_router(tag_api.router, prefix="/api/tags", tags=["标签管理"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["看板"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["通知"])
app.include_router(logs.router, prefix="/api/logs", tags=["日志管理"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["系统监控"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI分析"])
app.include_router(config_api.router, prefix="/api/config", tags=["配置"])


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("🚀 HyperLiquid 钱包分析系统启动中...")
    logger.info(f"📁 数据目录: {DATA_DIR}")
    
    # 初始化数据库
    try:
        logger.info("📊 初始化数据库...")
        db.create_tables()
        logger.info("✅ 数据库初始化完成")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise
    
    # 启动数据采集调度器
    try:
        scheduler_enabled = config.get_config("system").get("scheduler", {}).get("enabled", True)
        if scheduler_enabled:
            logger.info("⏰ 启动数据采集调度器...")
            scheduler.start()
        else:
            logger.info("⏰ 调度器已禁用")
    except Exception as e:
        logger.error(f"❌ 调度器启动失败: {e}")
        # 调度器失败不影响主程序
    
    # 启动 AI 调度器
    try:
        ai_enabled = config.get_config("ai", {}).get("enabled", False)
        if ai_enabled:
            logger.info("🤖 启动 AI 调度器...")
            await ai_scheduler.start()
        else:
            logger.info("🤖 AI 调度器已禁用")
    except Exception as e:
        logger.error(f"❌ AI 调度器启动失败: {e}")
        # AI 调度器失败不影响主程序
    
    logger.info("✅ 系统启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("👋 系统正在关闭...")
    
    # 停止调度器
    try:
        if scheduler.is_running:
            scheduler.stop()
    except Exception as e:
        logger.error(f"停止调度器失败: {e}")
    
    # 停止 AI 调度器
    try:
        ai_scheduler.stop()
    except Exception as e:
        logger.error(f"停止 AI 调度器失败: {e}")
    
    # 关闭数据库连接
    db.close()
    
    logger.info("✅ 系统已关闭")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "HyperLiquid 钱包分析系统 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "version": "2.0.0",
        "database": "connected" if db.conn else "disconnected",
        "data_scheduler": "running" if scheduler.is_running else "stopped",
        "ai_scheduler": "running" if ai_scheduler.running else "stopped"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


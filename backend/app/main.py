"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
import uvicorn

from app.api import wallets, dashboard, notifications, config as config_api
from app.config import config
from app.utils.logger import setup_logger

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
app.include_router(wallets.router, prefix="/api/wallets", tags=["钱包"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["看板"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["通知"])
app.include_router(config_api.router, prefix="/api/config", tags=["配置"])


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("🚀 HyperLiquid 钱包分析系统启动中...")
    logger.info(f"📁 数据目录: {config.DATA_DIR}")
    logger.info("✅ 系统启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("👋 系统正在关闭...")


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
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


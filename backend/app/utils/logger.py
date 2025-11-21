"""日志配置模块"""
import sys
from pathlib import Path
from loguru import logger

# 移除默认处理器
logger.remove()

# 控制台输出（带颜色）
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# 文件输出 - 应用日志
logger.add(
    Path(__file__).parent.parent.parent / "logs" / "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    encoding="utf-8"
)

# 文件输出 - 错误日志
logger.add(
    Path(__file__).parent.parent.parent / "logs" / "error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    encoding="utf-8"
)

# API 日志单独文件
api_logger = logger.bind(name="api")
api_logger.add(
    Path(__file__).parent.parent.parent / "logs" / "api.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="INFO",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
    filter=lambda record: record["name"] == "api"
)


def setup_logger():
    """设置日志（已在上方配置，此函数用于兼容）"""
    pass


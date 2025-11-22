"""
数据库管理模块
使用 SQLite 作为数据库
"""
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from app.config import DATA_DIR

# 数据库文件路径
DB_PATH = DATA_DIR / "hyperliquid_analyzer.db"


class Database:
    """数据库管理类"""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or DB_PATH
        self.conn: Optional[sqlite3.Connection] = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库连接"""
        # 确保目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 连接数据库
        self.conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            timeout=30.0
        )
        # 启用外键约束
        self.conn.execute("PRAGMA foreign_keys = ON")
        # 设置行工厂，返回字典格式
        self.conn.row_factory = sqlite3.Row
        
        logger.info(f"数据库连接成功: {self.db_path}")
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
    
    def execute(self, sql: str, params: tuple = None) -> sqlite3.Cursor:
        """执行 SQL 语句"""
        try:
            if params:
                cursor = self.conn.execute(sql, params)
            else:
                cursor = self.conn.execute(sql)
            self.conn.commit()
            return cursor
        except sqlite3.Error as e:
            logger.error(f"SQL 执行错误: {e}, SQL: {sql}")
            self.conn.rollback()
            raise
    
    def execute_many(self, sql: str, params_list: List[tuple]):
        """批量执行 SQL"""
        try:
            self.conn.executemany(sql, params_list)
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"批量 SQL 执行错误: {e}")
            self.conn.rollback()
            raise
    
    def fetch_one(self, sql: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """查询单条记录"""
        cursor = self.execute(sql, params)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def fetch_all(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """查询多条记录"""
        cursor = self.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def create_tables(self):
        """创建所有数据表"""
        logger.info("开始创建数据库表...")
        
        # 1. 钱包基础信息表
        self.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address VARCHAR(42) UNIQUE NOT NULL,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP,
                update_frequency VARCHAR(20) DEFAULT 'normal',
                
                -- 钱包元数据
                wallet_age_days INTEGER,
                first_trade_time TIMESTAMP,
                wallet_created_time TIMESTAMP,
                
                -- 基础指标
                total_pnl DECIMAL(18, 6) DEFAULT 0,
                roi DECIMAL(10, 4) DEFAULT 0,
                win_rate DECIMAL(5, 4) DEFAULT 0,
                profit_loss_ratio DECIMAL(10, 4) DEFAULT 0,
                max_drawdown DECIMAL(5, 4) DEFAULT 0,
                current_balance DECIMAL(18, 6) DEFAULT 0,
                initial_capital DECIMAL(18, 6) DEFAULT 0,
                total_deposits DECIMAL(18, 6) DEFAULT 0,
                total_withdrawals DECIMAL(18, 6) DEFAULT 0,
                net_deposits DECIMAL(18, 6) DEFAULT 0,
                margin_ratio DECIMAL(5, 4) DEFAULT 0,
                closed_trades_count INTEGER DEFAULT 0,
                
                -- 综合评分
                smart_money_score DECIMAL(5, 2) DEFAULT 0,
                score_grade VARCHAR(5) DEFAULT 'D',
                
                -- 高级指标
                annual_return DECIMAL(10, 4) DEFAULT 0,
                sharpe_ratio DECIMAL(10, 4) DEFAULT 0,
                calmar_ratio DECIMAL(10, 4) DEFAULT 0,
                sortino_ratio DECIMAL(10, 4) DEFAULT 0,
                volatility DECIMAL(5, 4) DEFAULT 0,
                
                -- 行为特征
                trading_frequency VARCHAR(20),
                holding_period VARCHAR(20),
                long_short_preference VARCHAR(20),
                style VARCHAR(50),
                
                -- 索引字段
                is_recommended BOOLEAN DEFAULT FALSE,
                is_favorite BOOLEAN DEFAULT FALSE,
                liquidation_count INTEGER DEFAULT 0,
                
                -- JSON 字段（存储复杂数据）
                tags TEXT,  -- JSON array
                favorite_coins TEXT,  -- JSON array
                equity_curve_24h TEXT,  -- JSON array
                equity_curve_7d TEXT,  -- JSON array
                equity_curve_30d TEXT,  -- JSON array
                equity_curve_all TEXT  -- JSON array
            )
        """)
        
        # 创建索引
        self.execute("CREATE INDEX IF NOT EXISTS idx_wallets_address ON wallets(address)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_wallets_score ON wallets(smart_money_score DESC)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_wallets_roi ON wallets(roi DESC)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_wallets_win_rate ON wallets(win_rate DESC)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_wallets_updated ON wallets(last_updated DESC)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_wallets_recommended ON wallets(is_recommended, smart_money_score DESC)")
        
        # 2. 交易记录表
        self.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address VARCHAR(42) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                size DECIMAL(18, 8),
                entry_price DECIMAL(18, 8),
                exit_price DECIMAL(18, 8),
                pnl DECIMAL(18, 6),
                pnl_percentage DECIMAL(10, 4),
                holding_time_minutes INTEGER,
                fees DECIMAL(18, 6),
                trade_count INTEGER DEFAULT 1,
                
                -- 原始数据字段
                hash VARCHAR(66),
                oid BIGINT,
                tid BIGINT,
                direction VARCHAR(50),
                start_position DECIMAL(18, 8),
                closed_pnl DECIMAL(18, 6),
                fee_token VARCHAR(10),
                
                FOREIGN KEY (wallet_address) REFERENCES wallets(address) ON DELETE CASCADE
            )
        """)
        
        # 交易表索引
        self.execute("CREATE INDEX IF NOT EXISTS idx_trades_wallet ON trades(wallet_address)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp DESC)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_trades_pnl ON trades(pnl DESC)")
        
        # 3. 持仓表
        self.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address VARCHAR(42) NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                size DECIMAL(18, 8),
                entry_price DECIMAL(18, 8),
                mark_price DECIMAL(18, 8),
                unrealized_pnl DECIMAL(18, 6),
                leverage INTEGER,
                margin_used DECIMAL(18, 6),
                liquidation_price DECIMAL(18, 8),
                position_value DECIMAL(18, 6),
                return_on_equity DECIMAL(10, 4),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (wallet_address) REFERENCES wallets(address) ON DELETE CASCADE,
                UNIQUE (wallet_address, symbol, side)
            )
        """)
        
        # 持仓表索引
        self.execute("CREATE INDEX IF NOT EXISTS idx_positions_wallet ON positions(wallet_address)")
        
        # 4. 资金流水表
        self.execute("""
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address VARCHAR(42) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                type VARCHAR(20) NOT NULL,
                amount DECIMAL(18, 6),
                tx_hash VARCHAR(66),
                status VARCHAR(20) DEFAULT 'confirmed',
                fee DECIMAL(18, 6) DEFAULT 0,
                
                FOREIGN KEY (wallet_address) REFERENCES wallets(address) ON DELETE CASCADE
            )
        """)
        
        # 资金流水表索引
        self.execute("CREATE INDEX IF NOT EXISTS idx_transfers_wallet ON transfers(wallet_address)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_transfers_timestamp ON transfers(timestamp DESC)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_transfers_type ON transfers(type)")
        
        # 5. 榜单配置表
        self.execute("""
            CREATE TABLE IF NOT EXISTS leaderboards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                display_name VARCHAR(100) NOT NULL,
                description TEXT,
                filters TEXT NOT NULL,  -- JSON 格式
                sort_by VARCHAR(50),
                sort_order VARCHAR(10) DEFAULT 'DESC',
                top_n INTEGER DEFAULT 20,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # 榜单表索引
        self.execute("CREATE INDEX IF NOT EXISTS idx_leaderboards_name ON leaderboards(name)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_leaderboards_enabled ON leaderboards(enabled)")
        
        # 6. 系统配置表
        self.execute("""
            CREATE TABLE IF NOT EXISTS system_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key VARCHAR(100) UNIQUE NOT NULL,
                config_value TEXT NOT NULL,  -- JSON 格式
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 系统配置表索引
        self.execute("CREATE INDEX IF NOT EXISTS idx_configs_key ON system_configs(config_key)")
        
        # 7. 通知记录表
        self.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address VARCHAR(42),
                type VARCHAR(50) NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                level VARCHAR(20) DEFAULT 'info',
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (wallet_address) REFERENCES wallets(address) ON DELETE CASCADE
            )
        """)
        
        # 通知表索引
        self.execute("CREATE INDEX IF NOT EXISTS idx_notifications_wallet ON notifications(wallet_address)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at DESC)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)")
        
        # 8. AI 分析缓存表（为 AI 功能预留）
        self.execute("""
            CREATE TABLE IF NOT EXISTS ai_analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address VARCHAR(42) NOT NULL,
                analysis_type VARCHAR(50) NOT NULL,
                analysis_result TEXT NOT NULL,  -- JSON 格式
                tokens_used INTEGER,
                cost DECIMAL(10, 6),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                
                UNIQUE (wallet_address, analysis_type)
            )
        """)
        
        # AI 缓存表索引
        self.execute("CREATE INDEX IF NOT EXISTS idx_ai_cache_wallet ON ai_analysis_cache(wallet_address)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_ai_cache_type ON ai_analysis_cache(analysis_type)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_ai_cache_expires ON ai_analysis_cache(expires_at)")
        
        # 9. AI 使用统计表（为 AI 功能预留）
        self.execute("""
            CREATE TABLE IF NOT EXISTS ai_usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                analysis_type VARCHAR(50) NOT NULL,
                total_requests INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                estimated_cost DECIMAL(10, 4) DEFAULT 0,
                cache_hits INTEGER DEFAULT 0,
                cache_misses INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE (date, analysis_type)
            )
        """)
        
        # AI 统计表索引
        self.execute("CREATE INDEX IF NOT EXISTS idx_ai_stats_date ON ai_usage_stats(date DESC)")
        
        # 10. 用户表
        self.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                must_change_password BOOLEAN DEFAULT FALSE
            )
        """)
        
        # 用户表索引
        self.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
        
        logger.info("数据库表创建完成")
        
        # 初始化预设榜单
        self._init_preset_leaderboards()
        
        # 初始化默认管理员
        self._init_default_admin()
    
    def _init_preset_leaderboards(self):
        """初始化预设榜单"""
        preset_leaderboards = [
            {
                "name": "small_loss_big_profit",
                "display_name": "小亏大赚型",
                "description": "盈亏比高，胜率适中，风险控制优秀",
                "filters": json.dumps({
                    "profit_loss_ratio": {"min": 3.0},
                    "win_rate": {"min": 40, "max": 60},
                    "max_drawdown": {"max": 30}
                }),
                "sort_by": "profit_loss_ratio",
                "sort_order": "DESC",
                "top_n": 20
            },
            {
                "name": "stable",
                "display_name": "稳健型",
                "description": "高胜率，低回撤，稳定盈利",
                "filters": json.dumps({
                    "win_rate": {"min": 60},
                    "max_drawdown": {"max": 20},
                    "liquidation_count": {"max": 0}
                }),
                "sort_by": "sharpe_ratio",
                "sort_order": "DESC",
                "top_n": 20
            },
            {
                "name": "high_win_rate",
                "display_name": "高胜率型",
                "description": "胜率超过 70%，交易稳定",
                "filters": json.dumps({
                    "win_rate": {"min": 70},
                    "closed_trades_count": {"min": 30}
                }),
                "sort_by": "win_rate",
                "sort_order": "DESC",
                "top_n": 20
            },
            {
                "name": "small_capital_master",
                "display_name": "小资金高手",
                "description": "小资金高收益，效率极高",
                "filters": json.dumps({
                    "initial_capital": {"max": 2000},
                    "roi": {"min": 200},
                    "closed_trades_count": {"min": 50}
                }),
                "sort_by": "roi",
                "sort_order": "DESC",
                "top_n": 20
            },
            {
                "name": "trend_master",
                "display_name": "趋势交易大师",
                "description": "擅长趋势交易，持仓周期长",
                "filters": json.dumps({
                    "style": "trend",
                    "profit_loss_ratio": {"min": 2.0}
                }),
                "sort_by": "total_pnl",
                "sort_order": "DESC",
                "top_n": 20
            },
            {
                "name": "scalping_master",
                "display_name": "短线高手",
                "description": "高频交易，快进快出",
                "filters": json.dumps({
                    "trading_frequency": "high",
                    "win_rate": {"min": 55}
                }),
                "sort_by": "closed_trades_count",
                "sort_order": "DESC",
                "top_n": 20
            },
            {
                "name": "potential_stars",
                "display_name": "潜力新星榜",
                "description": "刚崛起的新手高手，成长性强",
                "filters": json.dumps({
                    "wallet_age_days": {"min": 30, "max": 90},
                    "closed_trades_count": {"min": 30},
                    "roi": {"min": 100},
                    "win_rate": {"min": 50},
                    "max_drawdown": {"max": 40}
                }),
                "sort_by": "roi",
                "sort_order": "DESC",
                "top_n": 20
            }
        ]
        
        for leaderboard in preset_leaderboards:
            # 检查是否已存在
            existing = self.fetch_one(
                "SELECT id FROM leaderboards WHERE name = ?",
                (leaderboard["name"],)
            )
            
            if not existing:
                self.execute("""
                    INSERT INTO leaderboards 
                    (name, display_name, description, filters, sort_by, sort_order, top_n)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    leaderboard["name"],
                    leaderboard["display_name"],
                    leaderboard["description"],
                    leaderboard["filters"],
                    leaderboard["sort_by"],
                    leaderboard["sort_order"],
                    leaderboard["top_n"]
                ))
                logger.info(f"创建预设榜单: {leaderboard['display_name']}")
    
    def _init_default_admin(self):
        """初始化默认管理员账户"""
        try:
            # 检查是否已存在 admin 用户
            existing = self.fetch_one("SELECT id FROM users WHERE username = ?", ("admin",))
            
            if not existing:
                # 导入认证服务（延迟导入避免循环依赖）
                from app.services.auth_service import AuthService
                
                # 创建默认管理员
                password_hash = AuthService.get_password_hash("admin888")
                
                self.execute("""
                    INSERT INTO users (username, password_hash, role, is_active, created_at, must_change_password)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    "admin",
                    password_hash,
                    "admin",
                    True,
                    datetime.now().isoformat(),
                    False
                ))
                
                logger.info("✅ 默认管理员账户创建成功: admin / admin888")
        except Exception as e:
            logger.error(f"初始化管理员账户失败: {e}")
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return self.conn


# 全局数据库实例
db = Database()

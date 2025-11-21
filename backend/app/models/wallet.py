"""钱包数据模型"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class Trade(BaseModel):
    """交易模型"""
    timestamp: int
    symbol: str
    side: str  # long/short
    size: float
    entry_price: float
    exit_price: float
    pnl: float
    holding_time_minutes: int
    fees: float
    trade_count: int


class Position(BaseModel):
    """持仓模型"""
    symbol: str
    side: str
    size: float
    entry_price: float
    mark_price: float
    unrealized_pnl: float
    leverage: int


class Deposit(BaseModel):
    """存款模型"""
    timestamp: int
    amount: float
    tx_hash: str
    status: str


class Withdrawal(BaseModel):
    """取款模型"""
    timestamp: int
    amount: float
    tx_hash: str
    status: str


class Wallet(BaseModel):
    """钱包模型"""
    address: str
    imported_at: str
    last_updated: str
    update_frequency: str
    metadata: Dict[str, Any]
    metrics: Dict[str, Any]
    risk_metrics: Dict[str, Any]
    behavior: Dict[str, Any]
    trades: List[Trade]
    deposits: List[Deposit]
    withdrawals: List[Withdrawal]
    current_positions: List[Position]
    equity_curve: Dict[str, List]

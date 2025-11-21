"""HyperLiquid API 客户端"""
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.config import config


class HyperLiquidClient:
    """HyperLiquid API 客户端"""
    
    def __init__(self):
        self.base_url = config.get_config("system").get("api", {}).get("base_url", "https://api.hyperliquid.xyz/info")
        self.timeout = config.get_config("system").get("api", {}).get("timeout", 30)
        self.retry_times = config.get_config("system").get("api", {}).get("retry_times", 3)
        self.client = httpx.AsyncClient(timeout=self.timeout)
        self.use_mock = config.get_config("system").get("api", {}).get("use_mock", True)  # 默认使用 Mock
    
    async def get_wallet_data(self, address: str) -> Dict[str, Any]:
        """获取钱包完整数据"""
        if self.use_mock:
            logger.warning(f"⚠️ 使用 Mock 数据获取钱包: {address}")
            return self._generate_mock_wallet_data(address)
        
        try:
            # 获取所有交易历史（处理分页）
            fills = await self.get_user_fills_all(address)
            
            # 获取账户价值历史
            portfolio = await self.get_user_portfolio(address)
            
            # 获取当前挂单
            open_orders = await self.get_open_orders(address)
            
            # 获取清算所状态（包含当前持仓）
            clearinghouse_state = await self.get_clearinghouse_state(address)
            
            # 获取转账记录（存款/取款）
            transfers = await self.get_user_transfers(address)
            
            # 处理数据
            wallet_data = self._process_wallet_data(
                address, fills, portfolio, open_orders, clearinghouse_state, transfers
            )
            
            logger.info(f"✅ 成功获取钱包数据: {address}")
            return wallet_data
            
        except Exception as e:
            logger.error(f"❌ 获取钱包数据失败 {address}: {e}")
            # 失败时返回 Mock 数据
            logger.warning(f"⚠️ 回退到 Mock 数据")
            return self._generate_mock_wallet_data(address)
    
    async def get_user_fills(self, address: str, start_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取用户成交记录"""
        try:
            if start_time:
                # 按时间范围获取
                request_data = {
                    "type": "userFillsByTime",
                    "user": address,
                    "startTime": start_time
                }
            else:
                # 获取最近2000条
                request_data = {
                    "type": "userFills",
                    "user": address
                }
            
            response = await self.client.post(
                self.base_url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"获取成交记录失败: {e}")
            return []
    
    async def get_user_portfolio(self, address: str) -> Dict[str, Any]:
        """获取用户账户价值历史"""
        try:
            request_data = {
                "type": "portfolio",
                "user": address
            }
            
            response = await self.client.post(
                self.base_url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"获取账户价值历史失败: {e}")
            return {}
    
    async def get_open_orders(self, address: str) -> List[Dict[str, Any]]:
        """获取当前挂单（使用 frontendOpenOrders 获取更详细信息）"""
        try:
            request_data = {
                "type": "frontendOpenOrders",
                "user": address
            }
            
            response = await self.client.post(
                self.base_url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"获取挂单失败: {e}")
            return []
    
    async def get_clearinghouse_state(self, address: str) -> Dict[str, Any]:
        """获取清算所状态（包含当前持仓）"""
        try:
            request_data = {
                "type": "clearinghouseState",
                "user": address
            }
            
            response = await self.client.post(
                self.base_url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"获取清算所状态失败: {e}")
            return {}
    
    async def get_user_transfers(self, address: str, start_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取用户转账记录（存款/取款）"""
        try:
            request_data = {
                "type": "userNonFundingLedgerUpdates",
                "user": address
            }
            
            if start_time:
                request_data["startTime"] = start_time
            
            response = await self.client.post(
                self.base_url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            # API 可能返回列表或对象，统一处理
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and "transfers" in result:
                return result["transfers"]
            else:
                return []
            
        except Exception as e:
            logger.error(f"获取转账记录失败: {e}")
            return []
    
    def _process_wallet_data(
        self,
        address: str,
        fills: List[Dict[str, Any]],
        portfolio: Dict[str, Any],
        open_orders: List[Dict[str, Any]],
        clearinghouse_state: Dict[str, Any],
        transfers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """处理钱包数据，转换为标准格式"""
        # 处理交易记录
        trades = []
        for fill in fills:
            trade = {
                "timestamp": fill.get("time", 0) // 1000,  # 转换为秒
                "symbol": fill.get("coin", ""),
                "side": self._parse_side(fill.get("dir", "")),
                "size": float(fill.get("sz", 0)),
                "entry_price": float(fill.get("px", 0)),
                "exit_price": float(fill.get("px", 0)),  # Fills 中只有成交价
                "pnl": float(fill.get("closedPnl", 0)),
                "holding_time_minutes": 0,  # 需要计算
                "fees": float(fill.get("fee", 0)),
                "trade_count": 1,
                "hash": fill.get("hash", "")
            }
            trades.append(trade)
        
        # 按时间排序
        trades.sort(key=lambda x: x["timestamp"])
        
        # 计算第一笔交易时间
        first_trade_time = datetime.fromtimestamp(trades[0]["timestamp"]) if trades else datetime.now()
        
        # 处理账户价值历史
        equity_curve = self._process_portfolio(portfolio)
        
        # 计算初始资金（使用转账记录或账户价值历史）
        initial_capital = self._calculate_initial_capital(transfers, portfolio, trades)
        
        # 从清算所状态获取账户信息
        account_info = self._extract_account_info(clearinghouse_state)
        
        # 计算当前余额（优先使用清算所状态的账户价值）
        current_balance = account_info.get("account_value", self._get_current_balance_from_portfolio(portfolio))
        
        # 计算总盈亏（使用账户价值 - 初始资金，更准确）
        # 如果账户价值 > 初始资金，说明有盈利
        total_pnl = current_balance - initial_capital if initial_capital > 0 else 0
        
        # 处理当前持仓（从 clearinghouseState 获取）
        current_positions = self._process_positions_from_clearinghouse(clearinghouse_state)
        
        # 处理转账记录（存款/取款）
        deposits, withdrawals = self._process_transfers(transfers)
        
        return {
            "address": address,
            "imported_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "update_frequency": "active",
            "metadata": {
                "avatar": f"avatar_{address[:8]}",
                "tags": [],
                "wallet_age_days": (datetime.now() - first_trade_time).days if trades else 0,
                "first_trade_time": first_trade_time.isoformat() if trades else datetime.now().isoformat(),
                "wallet_created_time": self._get_wallet_created_time(transfers, first_trade_time)
            },
            "metrics": {
                "total_pnl": total_pnl,
                "roi": (total_pnl / initial_capital * 100) if initial_capital > 0 else 0,
                "win_rate": len([t for t in trades if t["pnl"] > 0]) / len(trades) if trades else 0,
                "profit_loss_ratio": self._calculate_profit_loss_ratio(trades),
                "max_drawdown": 0,  # 需要计算
                "current_balance": current_balance,
                "account_value": account_info.get("account_value", current_balance),  # 账户总资产
                "withdrawable": account_info.get("withdrawable", 0),  # 可提取金额
                "total_margin_used": account_info.get("total_margin_used", 0),  # 使用的保证金
                "total_position_value": account_info.get("total_position_value", 0),  # 持仓总价值
                "initial_capital": initial_capital,
                "total_deposits": sum(d.get("amount", 0) for d in deposits),
                "total_withdrawals": sum(w.get("amount", 0) for w in withdrawals),
                "net_deposits": sum(d.get("amount", 0) for d in deposits) - sum(w.get("amount", 0) for w in withdrawals),
                "margin_ratio": self._calculate_margin_ratio(account_info),  # 保证金率
                "closed_trades_count": len(trades),
                "smart_money_score": 0  # 需要计算
            },
            "risk_metrics": {
                "volatility": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "liquidation_count": 0
            },
            "behavior": {
                "trading_frequency": "medium",
                "holding_period": "short",
                "long_short_preference": "balanced",
                "style": "trend",
                "coin_preference": []
            },
            "trades": trades,
            "deposits": deposits,
            "withdrawals": withdrawals,
            "current_positions": current_positions,
            "equity_curve": equity_curve
        }
    
    def _parse_side(self, direction: str) -> str:
        """解析交易方向"""
        direction_lower = direction.lower()
        if "long" in direction_lower or "buy" in direction_lower:
            return "long"
        elif "short" in direction_lower or "sell" in direction_lower:
            return "short"
        return "long"  # 默认
    
    def _process_portfolio(self, portfolio: Dict[str, Any]) -> Dict[str, List]:
        """处理账户价值历史，生成收益曲线"""
        equity_curve = {
            "24h": [],
            "7d": [],
            "30d": [],
            "all": []
        }
        
        if not portfolio:
            return equity_curve
        
        # portfolio 格式: [["day", {...}], ["week", {...}], ...]
        for period_data in portfolio:
            period_name = period_data[0]
            period_info = period_data[1]
            
            account_value_history = period_info.get("accountValueHistory", [])
            
            for point in account_value_history:
                timestamp = point[0] // 1000  # 转换为秒
                value = float(point[1])
                equity_curve["all"].append([timestamp, value])
        
        return equity_curve
    
    def _estimate_initial_capital(self, portfolio: Dict[str, Any], trades: List[Dict]) -> float:
        """估算初始资金"""
        if not portfolio:
            return 1000.0  # 默认值
        
        # 尝试从 allTime 数据获取最早的账户价值
        for period_data in portfolio:
            period_name = period_data[0]
            if period_name == "allTime":
                period_info = period_data[1]
                account_value_history = period_info.get("accountValueHistory", [])
                if account_value_history:
                    # 返回最早的账户价值作为初始资金估算
                    return float(account_value_history[0][1])
        
        # 如果没有 allTime，使用第一笔交易前的账户价值
        if trades:
            # 简化处理：使用当前余额减去总盈亏
            return 1000.0
        
        return 1000.0
    
    def _get_current_balance(self, portfolio: Dict[str, Any]) -> float:
        """获取当前余额"""
        if not portfolio:
            return 0.0
        
        # 从 day 数据获取最新的账户价值
        for period_data in portfolio:
            period_name = period_data[0]
            if period_name == "day":
                period_info = period_data[1]
                account_value_history = period_info.get("accountValueHistory", [])
                if account_value_history:
                    return float(account_value_history[-1][1])
        
        return 0.0
    
    def _process_positions_from_clearinghouse(self, clearinghouse_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """处理持仓（从 clearinghouseState 获取）"""
        positions = []
        
        if not clearinghouse_state:
            return positions
        
        asset_positions = clearinghouse_state.get("assetPositions", [])
        
        for asset_pos in asset_positions:
            pos_data = asset_pos.get("position", {})
            if not pos_data:
                continue
            
            # 判断方向：szi > 0 为多头，szi < 0 为空头
            szi = float(pos_data.get("szi", 0))
            side = "long" if szi > 0 else "short"
            
            # 获取当前价格（需要从其他地方获取，这里先用 entryPx）
            entry_price = float(pos_data.get("entryPx", 0))
            
            # 计算当前价格（mark price）
            # positionValue = size * mark_price，所以 mark_price = positionValue / size
            position_value = float(pos_data.get("positionValue", 0))
            mark_price = position_value / abs(szi) if abs(szi) > 0 else entry_price
            
            position = {
                "symbol": pos_data.get("coin", ""),
                "side": side,
                "size": abs(szi),
                "entry_price": entry_price,
                "mark_price": mark_price,
                "unrealized_pnl": float(pos_data.get("unrealizedPnl", 0)),
                "leverage": pos_data.get("leverage", {}).get("value", 1) if isinstance(pos_data.get("leverage"), dict) else 1,
                "position_value": position_value,
                "margin_used": float(pos_data.get("marginUsed", 0)),
                "liquidation_price": float(pos_data.get("liquidationPx", 0)) if pos_data.get("liquidationPx") else None,
                "return_on_equity": float(pos_data.get("returnOnEquity", 0)),
                "cum_funding": pos_data.get("cumFunding", {})
            }
            positions.append(position)
        
        return positions
    
    def _process_transfers(self, transfers: List[Dict[str, Any]]) -> tuple:
        """处理转账记录，分离存款和取款"""
        deposits = []
        withdrawals = []
        
        for transfer in transfers:
            # userNonFundingLedgerUpdates 返回格式示例：
            # {"time": 1234567890, "delta": "1000.0", "hash": "0x...", ...}
            timestamp_ms = transfer.get("time", 0)
            timestamp = timestamp_ms // 1000 if timestamp_ms else int(datetime.now().timestamp())
            
            # delta 字段表示金额变化，正数为存款，负数为取款
            delta_str = transfer.get("delta", "0")
            delta = float(delta_str) if delta_str else 0.0
            amount = abs(delta)
            
            transfer_record = {
                "timestamp": timestamp,
                "amount": amount,
                "tx_hash": transfer.get("hash", transfer.get("txHash", "")),
                "status": "confirmed"
            }
            
            # delta > 0 表示资金增加（存款），delta < 0 表示资金减少（取款）
            if delta > 0:
                deposits.append(transfer_record)
            elif delta < 0:
                withdrawals.append(transfer_record)
        
        # 按时间排序
        deposits.sort(key=lambda x: x["timestamp"])
        withdrawals.sort(key=lambda x: x["timestamp"])
        
        return deposits, withdrawals
    
    def _calculate_initial_capital(
        self,
        transfers: List[Dict[str, Any]],
        portfolio: Dict[str, Any],
        trades: List[Dict]
    ) -> float:
        """计算初始资金（优先使用转账记录）"""
        # 如果有转账记录，使用转账记录计算
        if transfers:
            deposits, withdrawals = self._process_transfers(transfers)
            total_deposits = sum(d.get("amount", 0) for d in deposits)
            total_withdrawals = sum(w.get("amount", 0) for w in withdrawals)
            initial_capital = total_deposits - total_withdrawals
            if initial_capital > 0:
                return initial_capital
        
        # 否则使用账户价值历史估算
        return self._estimate_initial_capital(portfolio, trades)
    
    def _extract_account_info(self, clearinghouse_state: Dict[str, Any]) -> Dict[str, float]:
        """从清算所状态提取账户信息"""
        info = {
            "account_value": 0.0,
            "withdrawable": 0.0,
            "total_margin_used": 0.0,
            "total_position_value": 0.0,
            "maintenance_margin": 0.0
        }
        
        if not clearinghouse_state:
            return info
        
        # 从 marginSummary 获取账户价值
        margin_summary = clearinghouse_state.get("marginSummary", {})
        if margin_summary:
            account_value = margin_summary.get("accountValue")
            if account_value:
                info["account_value"] = float(account_value)
            
            total_margin_used = margin_summary.get("totalMarginUsed")
            if total_margin_used:
                info["total_margin_used"] = float(total_margin_used)
            
            total_position_value = margin_summary.get("totalNtlPos")
            if total_position_value:
                info["total_position_value"] = abs(float(total_position_value))
        
        # 获取可提取金额
        withdrawable = clearinghouse_state.get("withdrawable")
        if withdrawable:
            info["withdrawable"] = float(withdrawable)
        
        # 获取维持保证金
        maintenance_margin = clearinghouse_state.get("crossMaintenanceMarginUsed")
        if maintenance_margin:
            info["maintenance_margin"] = float(maintenance_margin)
        
        return info
    
    def _calculate_margin_ratio(self, account_info: Dict[str, float]) -> float:
        """计算保证金率"""
        account_value = account_info.get("account_value", 0)
        total_margin_used = account_info.get("total_margin_used", 0)
        
        if account_value > 0:
            return total_margin_used / account_value
        
        return 0.0
    
    def _get_wallet_created_time(self, transfers: List[Dict[str, Any]], first_trade_time: datetime) -> str:
        """获取钱包创建时间（第一笔存款时间或第一笔交易时间）"""
        if transfers:
            deposits, _ = self._process_transfers(transfers)
            if deposits:
                # 使用第一笔存款时间
                first_deposit_time = datetime.fromtimestamp(deposits[0]["timestamp"])
                return first_deposit_time.isoformat()
        
        # 否则使用第一笔交易时间
        return first_trade_time.isoformat()
    
    def _get_current_balance_from_portfolio(self, portfolio: Dict[str, Any]) -> float:
        """从 portfolio 获取当前余额"""
        if not portfolio:
            return 0.0
        
        # 从 day 数据获取最新的账户价值
        for period_data in portfolio:
            period_name = period_data[0]
            if period_name == "day":
                period_info = period_data[1]
                account_value_history = period_info.get("accountValueHistory", [])
                if account_value_history:
                    return float(account_value_history[-1][1])
        
        return 0.0
    
    def _generate_mock_wallet_data(self, address: str) -> Dict[str, Any]:
        """生成 Mock 钱包数据（用于开发和测试）"""
        import random
        import time
        
        now = datetime.now()
        first_trade_time = now - timedelta(days=random.randint(30, 180))
        wallet_created_time = first_trade_time - timedelta(days=random.randint(1, 30))
        
        # 生成交易记录
        trades = []
        base_time = int(first_trade_time.timestamp())
        for i in range(random.randint(50, 200)):
            trade_time = base_time + i * 3600
            side = random.choice(["long", "short"])
            pnl = random.uniform(-1000, 3000)
            
            trades.append({
                "timestamp": trade_time,
                "symbol": random.choice(["BTC", "ETH", "SOL"]),
                "side": side,
                "size": random.uniform(0.1, 10),
                "entry_price": random.uniform(30000, 50000),
                "exit_price": random.uniform(30000, 50000),
                "pnl": pnl,
                "holding_time_minutes": random.randint(10, 1440),
                "fees": random.uniform(1, 50),
                "trade_count": 1
            })
        
        # 生成存款记录
        deposits = []
        deposit_time = int(wallet_created_time.timestamp())
        initial_amount = random.uniform(500, 2000)
        deposits.append({
            "timestamp": deposit_time,
            "amount": initial_amount,
            "tx_hash": f"0x{random.randint(100000, 999999)}",
            "status": "confirmed"
        })
        
        # 生成取款记录（可选）
        withdrawals = []
        if random.random() > 0.5:
            withdrawal_time = deposit_time + random.randint(86400, 2592000)
            withdrawals.append({
                "timestamp": withdrawal_time,
                "amount": random.uniform(100, initial_amount * 0.5),
                "tx_hash": f"0x{random.randint(100000, 999999)}",
                "status": "confirmed"
            })
        
        # 计算初始资金
        total_deposits = sum(d["amount"] for d in deposits)
        total_withdrawals = sum(w["amount"] for w in withdrawals)
        initial_capital = total_deposits - total_withdrawals
        
        # 计算总盈亏
        total_pnl = sum(t["pnl"] for t in trades)
        
        # 计算当前余额
        current_balance = initial_capital + total_pnl
        
        return {
            "address": address,
            "imported_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "update_frequency": "active",
            "metadata": {
                "avatar": f"avatar_{address[:8]}",
                "tags": random.sample(["短线", "空头偏好", "稳健", "趋势"], random.randint(1, 3)),
                "wallet_age_days": (now - first_trade_time).days,
                "first_trade_time": datetime.fromtimestamp(base_time).isoformat(),
                "wallet_created_time": datetime.fromtimestamp(deposit_time).isoformat()
            },
            "metrics": {
                "total_pnl": total_pnl,
                "roi": (total_pnl / initial_capital * 100) if initial_capital > 0 else 0,
                "win_rate": len([t for t in trades if t["pnl"] > 0]) / len(trades) if trades else 0,
                "profit_loss_ratio": self._calculate_profit_loss_ratio(trades),
                "max_drawdown": random.uniform(0.1, 0.4),
                "current_balance": current_balance,
                "initial_capital": initial_capital,
                "total_deposits": total_deposits,
                "total_withdrawals": total_withdrawals,
                "net_deposits": initial_capital,
                "margin_ratio": random.uniform(0.1, 0.5),
                "closed_trades_count": len(trades),
                "smart_money_score": random.randint(60, 95)
            },
            "risk_metrics": {
                "volatility": random.uniform(0.1, 0.3),
                "max_drawdown": random.uniform(0.1, 0.4),
                "sharpe_ratio": random.uniform(1.0, 2.5),
                "liquidation_count": 0 if random.random() > 0.1 else random.randint(1, 3)
            },
            "behavior": {
                "trading_frequency": random.choice(["high", "medium", "low"]),
                "holding_period": random.choice(["short", "medium", "long"]),
                "long_short_preference": random.choice(["long", "short", "balanced"]),
                "style": random.choice(["trend", "scalping", "stable"]),
                "coin_preference": random.sample(["BTC", "ETH", "SOL"], random.randint(1, 3))
            },
            "trades": trades,
            "deposits": deposits,
            "withdrawals": withdrawals,
            "current_positions": [],
            "equity_curve": {
                "24h": [],
                "7d": [],
                "30d": [],
                "all": []
            }
        }
    
    def _calculate_profit_loss_ratio(self, trades: List[Dict]) -> float:
        """计算盈亏比"""
        profits = [t["pnl"] for t in trades if t["pnl"] > 0]
        losses = [abs(t["pnl"]) for t in trades if t["pnl"] < 0]
        
        if not profits or not losses:
            return 1.0
        
        avg_profit = sum(profits) / len(profits)
        avg_loss = sum(losses) / len(losses)
        
        return avg_profit / avg_loss if avg_loss > 0 else 0
    
    async def get_user_fills_all(self, address: str) -> List[Dict[str, Any]]:
        """获取所有成交记录（处理分页）"""
        all_fills = []
        start_time = None
        
        # 最多获取10000条（API限制）
        max_iterations = 5  # 每次2000条，最多5次
        
        for i in range(max_iterations):
            fills = await self.get_user_fills(address, start_time)
            
            if not fills:
                break
            
            all_fills.extend(fills)
            
            # 如果返回的数据少于2000条，说明已经获取完所有数据
            if len(fills) < 2000:
                break
            
            # 使用最后一条的时间戳作为下一次的 startTime
            last_time = fills[-1].get("time", 0)
            if last_time <= start_time if start_time else False:
                break
            
            start_time = last_time
        
        return all_fills
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


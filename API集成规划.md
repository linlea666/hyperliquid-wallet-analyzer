# HyperLiquid API 集成规划

## 一、API 调研

### 1.1 需要确认的 API 端点

由于无法直接访问 HyperLiquid API 文档，需要在实际开发时确认以下 API：

#### 钱包相关
- ✅ 获取钱包交易历史
- ✅ 获取钱包当前持仓
- ✅ 获取钱包余额信息
- ✅ 获取钱包保证金信息
- ✅ 获取钱包存款记录（Deposit History）
- ✅ 获取钱包取款记录（Withdraw History）

#### 市场数据
- ✅ 获取代币价格信息
- ✅ 获取市场深度

### 1.2 API 调用注意事项

- **频率限制**：需要确认 API 调用频率限制
- **认证方式**：是否需要 API Key（通常公开数据不需要）
- **数据格式**：确认返回数据格式（JSON）
- **错误处理**：了解错误码和错误信息格式

---

## 二、API 客户端设计

### 2.1 客户端结构

```python
# backend/app/services/hyperliquid.py

class HyperLiquidClient:
    """HyperLiquid API 客户端"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = httpx.AsyncClient(timeout=timeout)
    
    async def get_wallet_trades(self, address: str, start_time: int = None):
        """获取钱包交易历史"""
        pass
    
    async def get_wallet_positions(self, address: str):
        """获取钱包当前持仓"""
        pass
    
    async def get_wallet_balance(self, address: str):
        """获取钱包余额"""
        pass
    
    async def get_wallet_deposits(self, address: str, start_time: int = None):
        """获取钱包存款记录"""
        pass
    
    async def get_wallet_withdrawals(self, address: str, start_time: int = None):
        """获取钱包取款记录"""
        pass
    
    async def get_token_price(self, symbol: str):
        """获取代币价格"""
        pass
```

### 2.2 错误处理

```python
class HyperLiquidAPIError(Exception):
    """HyperLiquid API 错误"""
    pass

class RateLimitError(HyperLiquidAPIError):
    """API 限流错误"""
    pass

class InvalidAddressError(HyperLiquidAPIError):
    """无效地址错误"""
    pass
```

### 2.3 重试机制

```python
async def call_api_with_retry(self, func, max_retries=3):
    """带重试的 API 调用"""
    for attempt in range(max_retries):
        try:
            return await func()
        except RateLimitError:
            wait_time = 2 ** attempt  # 指数退避
            await asyncio.sleep(wait_time)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
```

---

## 三、数据获取策略

### 3.1 交易历史获取

#### 策略一：全量获取（首次导入）
```
1. 调用 API 获取所有历史交易
2. 按时间排序
3. 存储到本地文件
4. 记录最后更新时间戳
```

#### 策略二：增量获取（后续更新）
```
1. 读取本地最后更新时间戳
2. 调用 API 获取该时间之后的新交易
3. 合并到现有数据
4. 更新最后更新时间戳
```

### 3.2 数据缓存

```python
# API 响应缓存（5分钟）
cache_key = f"api:{endpoint}:{params}"
if cache.exists(cache_key) and not force_refresh:
    return cache.get(cache_key)

# 调用 API
data = await api_call()

# 缓存结果
cache.set(cache_key, data, ttl=300)
return data
```

---

## 四、数据解析和转换

### 4.1 交易数据解析

```python
def parse_trade_data(raw_data: dict) -> Trade:
    """解析原始交易数据"""
    return Trade(
        timestamp=parse_timestamp(raw_data['time']),
        symbol=raw_data['symbol'],
        side=raw_data['side'],  # 'long' or 'short'
        size=float(raw_data['size']),
        entry_price=float(raw_data['entryPrice']),
        exit_price=float(raw_data['exitPrice']),
        pnl=float(raw_data['pnl']),
        fees=float(raw_data['fees']),
        # ... 其他字段
    )
```

### 4.2 持仓数据解析

```python
def parse_position_data(raw_data: dict) -> Position:
    """解析持仓数据"""
    return Position(
        symbol=raw_data['symbol'],
        side=raw_data['side'],
        size=float(raw_data['size']),
        entry_price=float(raw_data['entryPrice']),
        mark_price=float(raw_data['markPrice']),
        unrealized_pnl=float(raw_data['unrealizedPnl']),
        leverage=int(raw_data['leverage']),
        # ... 其他字段
    )

def parse_deposit_data(raw_data: dict) -> Deposit:
    """解析存款数据"""
    return Deposit(
        timestamp=parse_timestamp(raw_data['time']),
        amount=float(raw_data['amount']),
        tx_hash=raw_data['txHash'],
        status=raw_data['status'],  # 'pending' or 'confirmed'
        # ... 其他字段
    )

def parse_withdrawal_data(raw_data: dict) -> Withdrawal:
    """解析取款数据"""
    return Withdrawal(
        timestamp=parse_timestamp(raw_data['time']),
        amount=float(raw_data['amount']),
        tx_hash=raw_data['txHash'],
        status=raw_data['status'],  # 'pending' or 'confirmed'
        # ... 其他字段
    )
```

---

## 五、API 调用优化

### 5.1 批量请求优化

```python
async def batch_get_wallets(self, addresses: List[str]):
    """批量获取钱包数据"""
    # 使用信号量控制并发
    semaphore = asyncio.Semaphore(10)
    
    async def fetch_one(address):
        async with semaphore:
            return await self.get_wallet_data(address)
    
    # 并发执行
    tasks = [fetch_one(addr) for addr in addresses]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```

### 5.2 请求去重

```python
class RequestDeduplicator:
    """请求去重器（相同请求只调用一次）"""
    
    def __init__(self):
        self.pending = {}
    
    async def get(self, key: str, func):
        if key in self.pending:
            return await self.pending[key]
        
        future = asyncio.create_task(func())
        self.pending[key] = future
        
        try:
            result = await future
            return result
        finally:
            del self.pending[key]
```

---

## 六、数据验证

### 6.1 地址验证

```python
def validate_address(address: str) -> bool:
    """验证钱包地址格式"""
    # HyperLiquid 地址格式（需要确认）
    if not address.startswith('0x'):
        return False
    if len(address) != 42:
        return False
    # 检查是否为有效的十六进制
    try:
        int(address, 16)
        return True
    except ValueError:
        return False
```

### 6.2 数据完整性检查

```python
def validate_trade_data(trade: dict) -> bool:
    """验证交易数据完整性"""
    required_fields = [
        'timestamp', 'symbol', 'side', 
        'size', 'entry_price', 'exit_price', 'pnl'
    ]
    
    for field in required_fields:
        if field not in trade:
            logger.warning(f"Missing field: {field}")
            return False
    
    # 验证数据类型和范围
    if trade['size'] <= 0:
        return False
    
    return True
```

---

## 七、API 监控和日志

### 7.1 API 调用日志

```python
async def log_api_call(endpoint: str, params: dict, response_time: float, status: str):
    """记录 API 调用日志"""
    logger.info(
        f"API Call: {endpoint} | "
        f"Params: {params} | "
        f"Response Time: {response_time}ms | "
        f"Status: {status}"
    )
```

### 7.2 性能监控

```python
class APIMonitor:
    """API 性能监控"""
    
    def __init__(self):
        self.stats = {
            'total_calls': 0,
            'success_calls': 0,
            'failed_calls': 0,
            'avg_response_time': 0,
            'rate_limit_hits': 0
        }
    
    def record_call(self, success: bool, response_time: float):
        self.stats['total_calls'] += 1
        if success:
            self.stats['success_calls'] += 1
        else:
            self.stats['failed_calls'] += 1
        
        # 更新平均响应时间
        # ...
```

---

## 八、Mock 数据（开发测试）

### 8.1 Mock API 客户端

```python
class MockHyperLiquidClient(HyperLiquidClient):
    """Mock API 客户端（用于开发和测试）"""
    
    async def get_wallet_trades(self, address: str, start_time: int = None):
        """返回模拟交易数据"""
        return generate_mock_trades(address, start_time)
    
    async def get_wallet_positions(self, address: str):
        """返回模拟持仓数据"""
        return generate_mock_positions(address)
```

### 8.2 测试数据生成

```python
def generate_mock_trades(address: str, count: int = 100):
    """生成模拟交易数据"""
    trades = []
    base_time = int(time.time()) - 86400 * 30  # 30天前
    
    for i in range(count):
        trade = {
            'timestamp': base_time + i * 3600,
            'symbol': random.choice(['BTC', 'ETH', 'SOL']),
            'side': random.choice(['long', 'short']),
            'size': random.uniform(0.1, 10),
            'entry_price': random.uniform(30000, 50000),
            'exit_price': random.uniform(30000, 50000),
            'pnl': random.uniform(-1000, 2000),
            'fees': random.uniform(1, 10),
        }
        trades.append(trade)
    
    return trades
```

---

## 九、配置管理

### 9.1 API 配置

```json
// config/system.json
{
  "api": {
    "base_url": "https://api.hyperliquid.xyz",
    "timeout": 30,
    "retry_times": 3,
    "retry_delay": 1,
    "rate_limit": {
      "requests_per_second": 10,
      "requests_per_minute": 100
    },
    "cache": {
      "ttl": 300,
      "enabled": true
    }
  }
}
```

### 9.2 环境变量支持

```python
# 支持环境变量覆盖配置
API_BASE_URL = os.getenv('HYPERLIQUID_API_URL', config['api']['base_url'])
API_TIMEOUT = int(os.getenv('HYPERLIQUID_API_TIMEOUT', config['api']['timeout']))
```

---

## 十、错误处理策略

### 10.1 错误分类

```python
# 网络错误（可重试）
- ConnectionTimeout
- ConnectionError
- TimeoutError

# API 错误（需处理）
- RateLimitError（等待后重试）
- InvalidAddressError（跳过）
- NotFoundError（记录日志）
- ServerError（重试）

# 数据错误（需验证）
- InvalidDataFormat
- MissingRequiredField
```

### 10.2 错误处理流程

```
API 调用
    ↓
捕获异常
    ↓
判断错误类型
    ↓
可重试？
  ├─ 是 → 重试（最多3次）
  └─ 否 → 记录错误，返回默认值或跳过
    ↓
记录错误日志
    ↓
返回结果或错误信息
```

---

## 十一、数据同步策略

### 11.1 首次同步

```
1. 获取钱包所有历史交易（可能需要分页）
2. 获取钱包所有存款记录（Deposit History）
3. 获取钱包所有取款记录（Withdraw History）
4. 按时间排序所有数据
5. 计算初始资金：
   - 初始资金 = 累计存款 - 累计取款
   - 第一笔存款时间 = 钱包创建时间（wallet_created_time）
   - 第一笔合约开仓时间 = 第一笔交易的时间（first_trade_time）
6. 计算钱包年龄（基于 first_trade_time）
7. 存储完整数据
8. 标记同步完成
```

### 11.2 增量同步

```
1. 读取本地最后更新时间戳
2. 调用 API 获取新交易（基于时间戳）
3. 调用 API 获取新存款记录（基于时间戳）
4. 调用 API 获取新取款记录（基于时间戳）
5. 验证数据连续性（检查是否有遗漏）
6. 合并新数据到现有数据
7. 重新计算初始资金（如果有新存款/取款）
8. 更新最后更新时间戳
```

### 11.3 数据修复

```
如果发现数据不一致：
1. 记录不一致的详细信息
2. 尝试重新获取该时间段的数据
3. 如果仍然不一致，标记为"需要人工检查"
4. 记录到错误日志
```

---

## 十二、实现步骤

### 步骤 1：API 调研
- [ ] 查找 HyperLiquid API 文档
- [ ] 确认 API 端点和参数
- [ ] 测试 API 调用
- [ ] 确认数据格式

### 步骤 2：基础客户端
- [ ] 实现基础 HTTP 客户端
- [ ] 实现错误处理
- [ ] 实现重试机制
- [ ] 添加日志记录

### 步骤 3：数据获取
- [ ] 实现交易历史获取
- [ ] 实现持仓信息获取
- [ ] 实现余额信息获取
- [ ] 实现增量更新

### 步骤 4：数据解析
- [ ] 实现交易数据解析
- [ ] 实现持仓数据解析
- [ ] 实现数据验证
- [ ] 实现数据转换

### 步骤 5：优化
- [ ] 实现缓存机制
- [ ] 实现批量请求优化
- [ ] 实现请求去重
- [ ] 性能测试和优化

---

## 十三、注意事项

### 13.1 API 限制
- ⚠️ 注意 API 调用频率限制
- ⚠️ 实现请求限流
- ⚠️ 监控 API 调用量

### 13.2 数据准确性
- ⚠️ 验证数据完整性
- ⚠️ 处理数据不一致情况
- ⚠️ 定期校验数据准确性

### 13.3 错误处理
- ⚠️ 完善的错误处理机制
- ⚠️ 详细的错误日志
- ⚠️ 用户友好的错误提示

### 13.4 性能考虑
- ⚠️ 避免频繁 API 调用
- ⚠️ 合理使用缓存
- ⚠️ 批量处理优化

---

## 总结

API 集成是本项目的核心，需要：

1. ✅ **完善的错误处理**：网络错误、API 错误、数据错误
2. ✅ **性能优化**：缓存、批量请求、并发控制
3. ✅ **数据准确性**：验证、校验、修复机制
4. ✅ **可维护性**：清晰的代码结构、完善的日志

**下一步**：在实际开发时，首先需要确认 HyperLiquid API 的具体端点和数据格式。


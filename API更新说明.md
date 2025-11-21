# API 更新说明

## 🎉 新增 API 集成

根据您提供的 API 文档，已集成以下三个重要 API：

### 1. ✅ 转账记录（存款/取款）

**API**: `userNonFundingLedgerUpdates`

**功能**:
- 获取用户的所有转账记录
- 自动区分存款和取款
- 支持时间范围查询（startTime）

**数据格式**:
```json
{
  "type": "userNonFundingLedgerUpdates",
  "user": "0x...",
  "startTime": 1700564422048  // 可选，毫秒时间戳
}
```

**返回数据**:
- `time`: 时间戳（毫秒）
- `delta`: 金额变化（正数=存款，负数=取款）
- `hash`: 交易哈希

**✅ 解决了初始资金计算问题！**

### 2. ✅ 当前持仓

**API**: `clearinghouseState`

**功能**:
- 获取清算所状态
- 包含 `assetPositions` 当前持仓信息
- 包含账户价值、保证金等详细信息

**数据格式**:
```json
{
  "type": "clearinghouseState",
  "user": "0x..."
}
```

**返回数据**:
- `assetPositions`: 持仓列表
  - `coin`: 币种
  - `szi`: 持仓数量（正数=多头，负数=空头）
  - `entryPx`: 开仓价格
  - `positionValue`: 持仓价值
  - `unrealizedPnl`: 未实现盈亏
  - `leverage`: 杠杆倍数
  - `liquidationPx`: 爆仓价格
  - `marginUsed`: 使用的保证金
  - `returnOnEquity`: 权益回报率

**✅ 解决了当前持仓显示问题！**

### 3. ✅ 当前委托（增强版）

**API**: `frontendOpenOrders`

**功能**:
- 获取当前挂单（比 `openOrders` 更详细）
- 包含订单类型、触发条件等前端信息

**数据格式**:
```json
{
  "type": "frontendOpenOrders",
  "user": "0x..."
}
```

**✅ 提供了更详细的订单信息！**

## 📊 数据完整性提升

### 之前（Mock/部分 API）
- ❌ 存款/取款记录：无
- ⚠️ 当前持仓：需要计算
- ✅ 交易历史：有
- ✅ 账户价值：有

### 现在（完整 API）
- ✅ 存款/取款记录：**完整**
- ✅ 当前持仓：**完整**
- ✅ 交易历史：**完整**
- ✅ 账户价值：**完整**
- ✅ 当前委托：**完整**

## 🔧 代码更新

### 新增方法

1. `get_user_transfers()` - 获取转账记录
2. `get_clearinghouse_state()` - 获取清算所状态
3. `_process_transfers()` - 处理转账记录
4. `_process_positions_from_clearinghouse()` - 处理持仓数据
5. `_calculate_initial_capital()` - 计算初始资金（使用转账记录）

### 数据流程

```
获取钱包数据
  ├─ 交易历史 (userFills)
  ├─ 账户价值 (portfolio)
  ├─ 转账记录 (userNonFundingLedgerUpdates) ← 新增
  ├─ 当前持仓 (clearinghouseState) ← 新增
  └─ 当前委托 (frontendOpenOrders) ← 增强
```

## 📈 功能改进

### 1. 初始资金计算

**之前**:
- 通过账户价值历史估算
- 不准确

**现在**:
- 使用转账记录计算
- `初始资金 = 累计存款 - 累计取款`
- **准确可靠**

### 2. 当前持仓显示

**之前**:
- 需要从交易记录计算
- 不准确

**现在**:
- 直接从 API 获取
- 包含完整信息：
  - 持仓方向（多/空）
  - 持仓数量
  - 开仓价格
  - 当前价格（mark price）
  - 未实现盈亏
  - 杠杆倍数
  - 爆仓价格
  - 保证金使用

### 3. 存款/取款记录

**之前**:
- 无数据

**现在**:
- 完整的存款记录
- 完整的取款记录
- 包含时间、金额、交易哈希

## 🎯 使用说明

### 启用真实 API

1. **修改配置**:
```bash
vim backend/data/config/system.json
```

2. **设置**:
```json
{
  "api": {
    "use_mock": false  // 改为 false
  }
}
```

3. **重启服务**:
```bash
./stop.sh
./start.sh
```

### 测试新功能

1. **导入钱包**:
   - 访问 http://localhost:5173
   - 导入一个真实钱包地址

2. **查看数据**:
   - 钱包详情页会显示：
     - ✅ 存款/取款记录
     - ✅ 当前持仓
     - ✅ 准确的初始资金
     - ✅ 准确的 ROI 计算

## 📝 数据格式说明

### 转账记录格式

```json
{
  "timestamp": 1700564422,  // 秒级时间戳
  "amount": 1000.0,         // 金额
  "tx_hash": "0x...",       // 交易哈希
  "status": "confirmed"      // 状态
}
```

### 持仓格式

```json
{
  "symbol": "BTC",
  "side": "long",           // long/short
  "size": 95.8222,          // 持仓数量
  "entry_price": 84035.2,   // 开仓价格
  "mark_price": 84000.0,    // 当前价格
  "unrealized_pnl": -160717.6124,  // 未实现盈亏
  "leverage": 25,            // 杠杆倍数
  "position_value": 7891724.75,    // 持仓价值
  "margin_used": 315668.99,        // 使用的保证金
  "liquidation_price": 7510.15,    // 爆仓价格
  "return_on_equity": -0.499       // 权益回报率
}
```

## ✅ 总结

**现在系统已支持完整的 HyperLiquid API 集成！**

- ✅ 交易历史
- ✅ 账户价值历史
- ✅ **存款/取款记录**（新增）
- ✅ **当前持仓**（新增）
- ✅ **当前委托**（增强）

**所有核心功能都已实现！** 🎉


# Issues: indicators.py (技術指標計算模組)

## 问题 1: RSI 计算中的除以零风险 [CRITICAL]

**文件**: `services/data-transformer/app/indicators.py` (Line 37-54)

**问题描述**:
在 RSI 计算中，当股票价格持续上涨（或持续下跌）时，`avg_loss`（或 `avg_gain`）为 0，导致：
- `rs = avg_gain / avg_loss` 产生 `inf` 或 `NaN`
- 最终 RSI 值计算失败，返回 `NaN`

```python
rs = avg_gain / avg_loss  # ❌ 分母可能为 0
rsi_val = 100 - (100 / (1 + rs))  # 结果为 NaN
```

**影响范围**:
- 股票持续上涨/下跌期间，RSI 指标无效
- 保存到数据库的 RSI 值为 `NaN`，导致下游分析失败

**复现方式**:
1. 使用连续上涨的股票数据（如牛市阶段）
2. 调用 `indicators.rsi(series, 14)`
3. 观察返回结果中是否包含 `NaN`

**修复方案**:
```python
def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    # ✓ 处理分母为零的情况
    with np.errstate(divide='ignore', invalid='ignore'):
        rs = avg_gain / avg_loss.replace(0, np.nan)
    
    rsi_val = 100 - (100 / (1 + rs))
    
    # ✓ 当无法计算时，使用中值 50
    rsi_val = rsi_val.fillna(50)
    
    return rsi_val
```

**优先级**: ⭐⭐⭐⭐⭐ 立即修复

---

## 问题 2: ADX 计算中的 ATR 调用不当 [MEDIUM]

**文件**: `services/data-transformer/app/indicators.py` (Line 167)

**问题描述**:
在 `adx()` 函数中计算 True Range 时，代码调用 `atr()` 函数但期望返回原始 TR 值：

```python
tr = atr(high, low, close, 1)  # ❌ 调用 atr() 但期望返回单日 true range
```

但 `atr()` 返回的是**平滑后的 ATR 值**（移动平均），而不是原始 True Range。

**影响范围**:
- ADX 计算基础数据错误
- DMI（+DI, -DI）指标值不准确
- 最终导出的技术分析数据不可信

**根本原因**:
- 重复使用了 `atr()` 而没有考虑其返回值含义
- 应该直接计算 TR，然后再平滑

**修复方案**:
```python
def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.DataFrame:
    # 计算 +DM 和 -DM
    high_diff = high.diff()
    low_diff = -low.diff()
    
    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
    
    # ✓ 直接计算 True Range，而不是调用 atr()
    high_low = high - low
    high_close = (high - close.shift()).abs()
    low_close = (low - close.shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # 计算平滑后的指标
    atr_val = tr.rolling(window=period, min_periods=period).mean()
    plus_dm_smooth = plus_dm.rolling(window=period, min_periods=period).mean()
    minus_dm_smooth = minus_dm.rolling(window=period, min_periods=period).mean()
    
    # 继续原有逻辑...
    pdi = 100 * (plus_dm_smooth / atr_val)
    mdi = 100 * (minus_dm_smooth / atr_val)
    # ...
```

**优先级**: ⭐⭐⭐ 中等，需要修复

---

## 问题 3: VWAP 计算的累积求和逻辑 [LOW]

**文件**: `services/data-transformer/app/indicators.py` (Line 125-133)

**问题描述**:
当前 VWAP 使用 `cumsum()` 全局累积：

```python
def vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    typical_price = (high + low + close) / 3
    return (typical_price * volume).cumsum() / volume.cumsum()
```

**问题**:
- 使用全局累积求和，计算的是"从开始以来"的 VWAP
- 但实际需要可能是"滑动窗口内"的 VWAP（如日内 VWAP）

**当前影响**:
- 数据首日的 VWAP 值会异常高（受所有历史数据影响）
- 如果跨年或跨月加载数据，历史分界处数据会不连贯

**修复建议**:
1. 如果需要全局 VWAP（当前逻辑），则在文档中明确说明
2. 如果需要日内 VWAP，需要添加按日期分组的逻辑：
   ```python
   def vwap(df: pd.DataFrame, date_col: str = 'trade_date') -> pd.Series:
       return df.groupby(date_col).apply(
           lambda x: ((x['high'] + x['low'] + x['close']) / 3 * x['volume']).sum() 
                     / x['volume'].sum()
       )
   ```

**优先级**: ⭐ 低，可选优化

---

## 问题总结

| 问题 | 严重程度 | 类型 | 修复时间 |
|------|---------|------|---------|
| RSI 除以零 | CRITICAL | 数据计算 | 30 分钟 |
| ADX/ATR 调用 | MEDIUM | 逻辑错误 | 20 分钟 |
| VWAP 累积 | LOW | 设计问题 | 可选 |


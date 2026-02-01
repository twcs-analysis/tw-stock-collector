# Issues: technical_analysis_transformer.py (技術分析轉換器)

## 问题 1: 历史数据加载的日期遍历逻辑 [CRITICAL]

**文件**: `services/data-transformer/app/technical_analysis_transformer.py` (Line 150-176)

**问题描述**:
使用 `timedelta(days=1)` 逐日遍历时，会加载**周末和假期**的数据（虽然最后失败，但浪费资源）：

```python
while current <= target_date:
    try:
        df = self.load_source_data(current, stock_id=None)
        # ...
    except Exception as e:
        self.logger.debug(f"載入 {current.date()} 資料失敗: {e}")
    
    current += timedelta(days=1)  # ❌ 逐日加载，包括周末和假期！
```

**影响范围**:
- 浪费 I/O 和网络资源（每周末/假期都会尝试加载失败）
- 如果有 1.5 年历史数据回溯需求，周末/假期会占 ~30% 的请求
- 日志中会产生大量失败记录，难以排查真实问题

**复现方式**:
1. 在周六早上运行转换器
2. 查看日志中 2024-01-01（跨年假期）的加载日志
3. 会看到大量 "載入 XXXX 資料失敗" 的 debug 信息

**修复方案**:

**方案 A: 从已加载的数据推断有效交易日**
```python
def _load_historical_data(self, target_date):
    # 先尝试加载目标日期，确定交易所状态
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d")
    
    start_date = target_date - timedelta(days=self.lookback_days)
    
    all_data = []
    current = start_date
    failed_consecutive = 0
    
    while current <= target_date:
        try:
            df = self.load_source_data(current, stock_id=None)
            if not df.empty:
                # ... 处理数据 ...
                all_data.append(df)
                failed_consecutive = 0  # 重置连续失败计数
        except Exception as e:
            failed_consecutive += 1
            # 连续失败超过 10 天后，跳过更多天数（推测假期）
            if failed_consecutive > 10:
                self.logger.debug(f"推测假期，跳过多日: {current.date()}")
                current += timedelta(days=5)  # 跳过可能的假期
                continue
        
        current += timedelta(days=1)
```

**方案 B: 维护交易日历（推荐）**
```python
# 在配置文件中添加台湾交易日历
# 或从外部 API 获取
TRADING_DATES = load_trading_calendar('tw')  # 2024 全年交易日

valid_dates = [d for d in date_range 
               if d in TRADING_DATES]

for current in valid_dates:
    df = self.load_source_data(current, stock_id=None)
    # ...
```

**优先级**: ⭐⭐⭐⭐⭐ 立即修复

---

## 问题 2: 跳过股票的不可见性 [HIGH]

**文件**: `services/data-transformer/app/technical_analysis_transformer.py` (Line 74-82)

**问题描述**:
当股票数据不足 240 天时，完全跳过该股票，但没有在最终结果中提示用户：

```python
if len(stock_df) < self.min_periods:
    self.logger.debug(...)  # ❌ 只记录 debug 级别，用户看不到
    continue
```

**影响范围**:
- 用户无法了解有多少股票被跳过
- 新上市的股票会无声地被忽略
- 数据验证和审计困难

**修复方案**:
```python
def transform(self, date, stock_id=None, **kwargs):
    # ...
    result_list = []
    skipped_stocks = {
        'insufficient_data': [],
        'other_errors': []
    }
    
    for idx, (stock_id_val, stock_df) in enumerate(grouped, 1):
        if len(stock_df) < self.min_periods:
            # ✓ 记录跳过的股票
            skipped_stocks['insufficient_data'].append({
                'stock_id': stock_id_val,
                'available_days': len(stock_df),
                'required_days': self.min_periods
            })
            continue
        
        try:
            stock_df_with_indicators = self._calculate_indicators(stock_df.copy())
            result_list.append(stock_df_with_indicators)
        except Exception as e:
            skipped_stocks['other_errors'].append({
                'stock_id': stock_id_val,
                'error': str(e)
            })
    
    # ✓ 在最后报告跳过情况
    if skipped_stocks['insufficient_data']:
        self.logger.warning(
            f"跳過 {len(skipped_stocks['insufficient_data'])} 檔股票 (資料不足): "
            f"{skipped_stocks['insufficient_data'][:5]}..."  # 显示前 5 个
        )
    
    if skipped_stocks['other_errors']:
        self.logger.error(
            f"跳過 {len(skipped_stocks['other_errors'])} 檔股票 (計算錯誤): "
            f"{skipped_stocks['other_errors'][:5]}..."
        )
    
    # 返回结果和跳过统计
    return result_df, skipped_stocks
```

**优先级**: ⭐⭐⭐⭐ 高优先级

---

## 问题 3: 数据类型转换不一致 [MEDIUM]

**文件**: `services/data-transformer/app/technical_analysis_transformer.py` (Line 158, 193)

**问题描述**:
数据在 datetime 和 string 之间反复转换，不仅低效还容易出错：

```python
# Line 158: 转为 datetime
df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values(['stock_id', 'trade_date'])

# ... 中间进行计算 ...

# Line 193: 转回 string
df['trade_date'] = df['trade_date'].dt.strftime('%Y-%m-%d')
```

**影响范围**:
- 性能：每次转换都需要解析/格式化字符串
- 一致性：某些中间步骤可能使用不同的格式
- 可维护性：未来修改时容易混淆

**修复方案**:
```python
def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    计算单一股票的所有技术指标
    
    ✓ 统一使用 datetime 格式进行所有计算
    ✓ 只在最后保存时转为字符串
    """
    # 确保 trade_date 是 datetime
    if not pd.api.types.is_datetime64_any_dtype(df['trade_date']):
        df['trade_date'] = pd.to_datetime(df['trade_date'])
    
    # 设置索引为日期
    df = df.set_index('trade_date').sort_index()
    
    # ✓ 所有计算都使用 datetime 格式的索引
    df['ma_5'] = indicators.sma(df['close'], 5)
    df['ma_10'] = indicators.sma(df['close'], 10)
    # ... 其他指标计算 ...
    
    # 重置索引
    df = df.reset_index()
    
    # 选择输出列
    output_columns = [...]
    df = df[existing_columns]
    
    # ✓ 只在最后转为字符串（保存时）
    df['trade_date'] = df['trade_date'].dt.strftime('%Y-%m-%d')
    
    return df
```

**优先级**: ⭐⭐⭐ 中等

---

## 问题 4: 指标计算中的 NaN 值未处理 [MEDIUM]

**文件**: `services/data-transformer/app/technical_analysis_transformer.py` (Line 115-144)

**问题描述**:
技术指标计算前期会产生大量 `NaN` 值（因为移动平均需要足够的数据点），这些 NaN 最终被保存到数据库：

```python
df['ma_5'] = indicators.sma(df['close'], 5)    # 前 4 个值为 NaN
df['ma_240'] = indicators.sma(df['close'], 240) # 前 239 个值为 NaN
# ...
# 只保留目标日期的资料
result_df = result_df[result_df['trade_date'] == target_date_str].copy()
# ❌ 这些目标日期可能仍然包含 NaN 值！
```

**影响范围**:
- 数据库中存储大量 `NULL` 值
- 下游 SQL 查询需要处理这些 NULL
- 某些分析可能因为 NaN 而失败

**修复方案**:
```python
def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
    # ... 计算所有指标 ...
    
    # ✓ 只保留完整的指标行（所有关键指标都非 NaN）
    # 这通常是从第 240 天开始
    critical_indicators = ['ma_240', 'rsi_14', 'macd_dif', 'adx']
    df_clean = df.dropna(subset=critical_indicators)
    
    if len(df_clean) < 1:
        self.logger.warning(
            f"股票 {df['stock_id'].iloc[0]}: 无足够数据计算指标"
        )
        return pd.DataFrame()
    
    self.logger.info(
        f"股票 {df['stock_id'].iloc[0]}: "
        f"总数据: {len(df)}, 有效指标数据: {len(df_clean)}"
    )
    
    return df_clean
```

**替代方案**:
如果需要保留所有日期的数据，可以使用前向填充或后向填充：
```python
# 前向填充 (不推荐，会传播错误)
df_ffill = df.fillna(method='ffill')

# 只保留有效指标行 (推荐)
df_valid = df.dropna(subset=['ma_240'])
```

**优先级**: ⭐⭐⭐ 中等

---

## 问题 5: 缺少输出列的容错性 [LOW]

**文件**: `services/data-transformer/app/technical_analysis_transformer.py` (Line 180-187)

**问题描述**:
输出列定义中假设所有欄位都存在，但某些股票可能缺少某些欄位（如 `amount`）：

```python
output_columns = [
    'trade_date', 'stock_id',
    'open', 'high', 'low', 'close', 'volume', 'amount',  # ❌ amount 可能不存在
    'ma_5', 'ma_10', # ...
]

existing_columns = [col for col in output_columns if col in df.columns]
df = df[existing_columns]  # ✓ 已有容错，但可改进
```

**问题**:
- 代码已有容错（`if col in df.columns`），但没有記錄缺少的欄位
- 某些欄位缺失時用戶不知道

**修復方案**:
```python
existing_columns = [col for col in output_columns if col in df.columns]
missing_columns = [col for col in output_columns if col not in df.columns]

if missing_columns:
    self.logger.warning(
        f"缺少欄位: {missing_columns} "
        f"(股票: {df['stock_id'].iloc[0] if not df.empty else 'unknown'})"
    )

df = df[existing_columns]
```

**優先級**: ⭐ 低，日誌改進

---

## 問題總結

| 問題 | 嚴重程度 | 類型 | 修復時間 |
|------|---------|------|---------|
| 日期遍歷邏輯 | CRITICAL | 效能 | 45 分鐘 |
| 跳過股票不可見 | HIGH | 可用性 | 30 分鐘 |
| 數據類型轉換 | MEDIUM | 效能 | 20 分鐘 |
| NaN 值處理 | MEDIUM | 數據質量 | 25 分鐘 |
| 缺少欄位日誌 | LOW | 可維護性 | 10 分鐘 |


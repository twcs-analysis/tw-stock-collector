# Analyzer Service

分析微服務，負責技術分析、籌碼分析、策略回測等運算密集型任務。

## 功能

- 技術指標批次計算 (MA, MACD, RSI, KD, 布林通道, OBV)
- 籌碼分析 (三大法人、融資融券、借券)
- 選股策略執行
- 策略回測與績效評估
- 風險指標計算 (Sharpe Ratio, Max Drawdown)

## 目錄結構

```
analyzer-service/
├── app/                    # 應用程式碼
│   ├── __init__.py
│   ├── main.py             # 主要執行入口
│   ├── technical/          # 技術分析
│   │   ├── indicators.py       # 技術指標計算
│   │   ├── patterns.py         # 型態辨識
│   │   └── signals.py          # 訊號產生
│   ├── fundamental/        # 籌碼分析
│   │   ├── institutional.py    # 法人分析
│   │   ├── margin.py           # 融資融券分析
│   │   └── chips.py            # 籌碼面指標
│   ├── strategies/         # 交易策略
│   │   ├── base_strategy.py
│   │   ├── ma_cross.py         # 均線交叉策略
│   │   ├── macd_divergence.py  # MACD 背離策略
│   │   └── institutional_follow.py  # 法人跟單策略
│   ├── backtest/           # 回測引擎
│   │   ├── engine.py
│   │   ├── portfolio.py
│   │   └── metrics.py
│   └── tasks/              # 背景任務
│       ├── daily_analysis.py
│       └── batch_calculation.py
│
├── tests/                  # 測試
├── Dockerfile              # Docker 建置檔
├── requirements.txt        # Python 依賴
└── README.md               # 本文件
```

## 技術指標

### 趨勢指標

- **MA** (Simple Moving Average) - 簡單移動平均線
- **EMA** (Exponential Moving Average) - 指數移動平均線
- **MACD** (Moving Average Convergence Divergence) - 平滑異同移動平均線

### 動量指標

- **RSI** (Relative Strength Index) - 相對強弱指標
- **KD** (Stochastic Oscillator) - 隨機指標
- **Williams %R** - 威廉指標

### 波動率指標

- **Bollinger Bands** - 布林通道
- **ATR** (Average True Range) - 真實波動幅度均值

### 量能指標

- **OBV** (On Balance Volume) - 能量潮
- **Volume Profile** - 成交量分布

## 籌碼分析

### 法人籌碼

- 外資連續買賣超天數
- 投信持股比例變化
- 自營商庫存水位

### 融資融券

- 融資使用率
- 融券餘額變化
- 資券比分析

### 借券分析

- 借券賣出餘額
- 借券使用率
- 借券成本

## 本地執行

```bash
# 安裝依賴
pip install -r requirements.txt

# 計算單一股票技術指標
python app/main.py --stock-id 2330 --indicators ma,macd,rsi

# 批次計算所有股票
python app/main.py --batch --date 2024-12-27

# 執行策略回測
python app/main.py --backtest --strategy ma_cross \
  --start 2024-01-01 --end 2024-12-31
```

## Docker 執行

```bash
# 建置映像檔
docker build -t tw-stock-analyzer-service:latest .

# 執行批次分析
docker run --rm \
  -e DATABASE_URL="postgresql://user:pass@db:5432/tw_stock" \
  -v $(pwd)/../../data:/app/data \
  tw-stock-analyzer-service:latest \
  --batch --date 2024-12-27
```

## 環境變數

| 變數 | 說明 | 範例 |
|-----|------|------|
| `DATABASE_URL` | 資料庫連線字串 | postgresql://user:pass@localhost:5432/tw_stock |
| `REDIS_URL` | Redis 連線 (任務佇列) | redis://localhost:6379 |
| `WORKER_THREADS` | 工作執行緒數 | 4 |
| `LOG_LEVEL` | 日誌等級 | INFO |

## 策略回測範例

```python
from app.strategies.ma_cross import MACrossStrategy
from app.backtest.engine import BacktestEngine

# 建立策略
strategy = MACrossStrategy(
    short_period=5,
    long_period=20
)

# 執行回測
engine = BacktestEngine(
    strategy=strategy,
    start_date="2024-01-01",
    end_date="2024-12-31",
    initial_capital=1000000
)

results = engine.run()

# 績效指標
print(f"總報酬率: {results.total_return:.2%}")
print(f"年化報酬: {results.annual_return:.2%}")
print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
print(f"最大回撤: {results.max_drawdown:.2%}")
```

## 效能優化

- 使用 NumPy 向量化計算
- Pandas 高效資料處理
- 多執行緒批次運算
- Redis 快取中間結果
- 資料庫查詢優化

## 相關服務

- [Data Collector](../data-collector/) - 資料收集服務
- [Data Importer](../data-importer/) - 資料匯入服務
- [API Service](../api-service/) - REST API 服務
- [Common Library](../common/) - 共用工具函式庫

# 技術分析轉換工具

將資料庫中的股票價格資料轉換為技術指標數據。

## 功能

- ✅ 從 PostgreSQL 資料庫載入股票價格資料
- ✅ 計算 30 個技術指標（MA、RSI、MACD、DMI/ADX、布林通道、成交量分析）
- ✅ 支援單日或日期區間轉換
- ✅ 支援特定股票篩選
- ✅ 輸出到 CSV 或 JSON 格式

## 技術指標列表

轉換器會計算以下 30 個技術指標：

### 基本資料（8個）
- `trade_date` - 交易日期
- `stock_id` - 股票代碼
- `open` - 開盤價
- `high` - 最高價
- `low` - 最低價
- `close` - 收盤價
- `volume` - 成交量
- `amount` - 成交金額

### 移動平均線（6個）
- `ma_5` - 5日均線
- `ma_10` - 10日均線
- `ma_20` - 20日均線
- `ma_60` - 季線
- `ma_120` - 半年線
- `ma_240` - 年線

### RSI 相對強弱指標（2個）
- `rsi_6` - 6日RSI
- `rsi_14` - 14日RSI

### MACD 指標（3個）
- `macd_dif` - DIF（快線）
- `macd_dea` - DEA（慢線/訊號線）
- `macd_hist` - Histogram（柱狀圖）

### DMI/ADX 趨向指標（4個）
- `dmi_pdi` - +DI（多方力道）
- `dmi_mdi` - -DI（空方力道）
- `dmi_adx` - ADX（趨勢強度，使用 Wilder's Smoothing）
- `dmi_adxr` - ADXR

### 布林通道（3個）
- `bb_upper` - 上軌
- `bb_mid` - 中軌
- `bb_lower` - 下軌

### 成交量分析（4個）
- `vol_ma5` - 5日均量
- `vol_ma20` - 20日均量
- `vol_ratio` - 量比（當日量/5日均量）
- `vwap` - 成交量加權平均價（amount/volume）

## 使用方式

### 前置需求

1. PostgreSQL 資料庫已啟動
2. 已匯入股票價格資料
3. 設定環境變數：
   ```bash
   export DB_PASSWORD=your_password  # 必要
   # 以下為選用，預設值如下
   export DB_TYPE=postgresql
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=tw_stock
   export DB_USER=postgres
   ```

### 快速開始（使用 Shell 腳本）⭐

**推薦使用 Shell 腳本** 進行日常轉換操作：

```bash
# 設定資料庫密碼
export DB_PASSWORD=your_password

# 轉換今天的資料
./scripts/data-transformer/transform.sh today

# 轉換指定日期
./scripts/data-transformer/transform.sh 2026-02-02

# 轉換特定股票
./scripts/data-transformer/transform.sh 2026-02-02 2330

# 轉換日期區間
./scripts/data-transformer/transform.sh range 2026-01-01 2026-01-31

# 轉換最近 7 天
./scripts/data-transformer/transform.sh latest 7

# 僅顯示結果不儲存
./scripts/data-transformer/transform.sh 2026-02-02 --no-save

# 查看完整說明
./scripts/data-transformer/transform.sh --help
```

**Shell 腳本特色**：
- ✅ 簡化的命令介面
- ✅ 自動產生輸出檔名
- ✅ 自動建立輸出目錄
- ✅ 彩色日誌輸出
- ✅ 友善的錯誤訊息

**預設輸出位置**：`data/transformed/technical/`

### 進階用法（直接使用 Python）

如需更細緻的控制，可直接使用 Python 腳本：

```bash
# 查看說明
python scripts/data-transformer/run_technical_analysis.py --help

# 轉換單日資料
python scripts/data-transformer/run_technical_analysis.py --date 2026-02-02

# 轉換日期區間（每日獨立計算）
python scripts/data-transformer/run_technical_analysis.py --start 2026-01-01 --end 2026-01-31

# 轉換特定股票
python scripts/data-transformer/run_technical_analysis.py --date 2026-02-02 --stock-id 2330

# 輸出到 CSV 檔案
python scripts/data-transformer/run_technical_analysis.py --date 2026-02-02 --output results/technical_2026-02-02.csv

# 輸出到 JSON 檔案
python scripts/data-transformer/run_technical_analysis.py --date 2026-02-02 --output results/technical_2026-02-02.json

# 顯示詳細日誌
python scripts/data-transformer/run_technical_analysis.py --date 2026-02-02 --verbose

# 顯示前 5 筆結果
python scripts/data-transformer/run_technical_analysis.py --date 2026-02-02 --show-sample 5
```

### 進階用法

```bash
# 轉換台積電 2026 年 1 月的資料並儲存
python scripts/data-transformer/run_technical_analysis.py \
    --start 2026-01-01 \
    --end 2026-01-31 \
    --stock-id 2330 \
    --output results/tsmc_2026_01.csv

# 轉換多檔股票（需多次執行）
for stock_id in 2330 2317 2454; do
    python scripts/data-transformer/run_technical_analysis.py \
        --date 2026-02-02 \
        --stock-id $stock_id \
        --output results/stock_${stock_id}_2026-02-02.csv
done
```

## 參數說明

### 必要參數（擇一）

- `--date YYYY-MM-DD` - 轉換單日資料
- `--start YYYY-MM-DD --end YYYY-MM-DD` - 轉換日期區間

### 選用參數

- `--stock-id CODE` - 指定股票代碼（例：2330）
- `--output PATH` - 輸出檔案路徑（支援 .csv 或 .json）
- `--verbose` - 顯示詳細日誌
- `--show-sample N` - 顯示前 N 筆結果（預設：10）

## 輸出格式

### 終端顯示

```
======================================================================
轉換結果摘要
======================================================================

總記錄數: 1877
股票數量: 1877
日期範圍: 2026-02-02 到 2026-02-02

欄位列表 (30 個):
trade_date, stock_id, open, high, low, close, volume, amount, ...

前 10 筆資料:
   trade_date stock_id    open    high     low   close      volume
0  2026-02-02     1101   58.50   58.90   58.20   58.80   12345678
...
```

### CSV 格式

```csv
trade_date,stock_id,open,high,low,close,volume,amount,ma_5,ma_10,...
2026-02-02,2330,1750.0,1765.0,1745.0,1765.0,33342359,58467099660,...
```

### JSON 格式

```json
[
  {
    "trade_date": "2026-02-02",
    "stock_id": "2330",
    "open": 1750.0,
    "high": 1765.0,
    "low": 1745.0,
    "close": 1765.0,
    "volume": 33342359,
    "amount": 58467099660.0,
    "ma_5": 1789.0,
    ...
  }
]
```

## 效能

- **單日轉換**：約 20-25 秒（處理 ~1,900 檔股票）
- **處理速度**：約 75-100 股/秒
- **資料載入**：回溯 550 天歷史資料（~700,000 筆記錄）

## 計算邏輯

### 歷史資料回溯

- 預設回溯 **550 天**（約 1.5 年）
- 確保 MA240（年線）有足夠資料計算

### 資料不足處理

- 如果歷史資料不足 240 天，相關指標（如 MA240）會顯示 `NaN`
- 系統會自動跳過資料不足的股票並記錄警告

### 指標計算方法

- **VWAP**：使用實際成交金額除以成交量
- **ADX**：使用 Wilder's Smoothing（指數平滑）方法
- **MACD**：使用 EMA（指數移動平均）計算
- **RSI**：使用標準 Wilder 公式

## 錯誤處理

### 常見錯誤

1. **資料庫連線失敗**
   ```
   錯誤: 無法連線到資料庫
   解決: 確認 PostgreSQL 已啟動且環境變數正確
   ```

2. **日期無資料**
   ```
   警告: 日期 2026-02-02 無資料
   解決: 確認該日期為交易日且已匯入資料
   ```

3. **股票代碼不存在**
   ```
   警告: 股票 9999 在 2026-02-02 無資料
   解決: 確認股票代碼正確
   ```

## 架構說明

```
scripts/data-transformer/
├── run_technical_analysis.py  # 主腳本
└── README.md                   # 本文件

services/
├── data-transformer/
│   └── app/
│       ├── technical_analysis_transformer.py  # 轉換器
│       ├── database_loader.py                 # 資料庫載入器
│       └── indicators.py                      # 技術指標計算
└── common/
    ├── database/                              # 資料庫連線
    └── utils/                                 # 共用工具
```

## 相關文件

- [技術分析轉換器規格](../../services/data-transformer/README.md)
- [資料庫 Schema](../../services/common/database/README.md)
- [專案 README](../../README.md)

## 維護記錄

- **2026-02-02**: 初版建立，支援 30 個技術指標
  - 修正 VWAP 計算邏輯（使用 amount/volume）
  - 修正 ADX 計算方法（使用 Wilder's Smoothing）
  - 支援資料庫直接載入模式

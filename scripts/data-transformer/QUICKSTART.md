# 技術分析轉換工具 - 快速開始

## 5 分鐘上手

### 1. 設定環境變數

```bash
export DB_PASSWORD=tw_stock_dev_password_2024
```

### 2. 執行轉換

```bash
# 轉換今天的資料
./scripts/data-transformer/transform.sh today

# 轉換指定日期
./scripts/data-transformer/transform.sh 2026-02-02
```

### 3. 查看結果

輸出檔案位於：`data/processed/technical/`

```bash
# 查看檔案
ls -lh data/processed/technical/

# 查看內容
head data/processed/technical/2026-02-02_all.csv
```

---

## 常用命令

### 轉換單日資料

```bash
# 今天
./scripts/data-transformer/transform.sh today

# 昨天
./scripts/data-transformer/transform.sh yesterday

# 指定日期
./scripts/data-transformer/transform.sh 2026-02-02
```

### 轉換特定股票

```bash
# 台積電 (2330)
./scripts/data-transformer/transform.sh 2026-02-02 2330

# 鴻海 (2317)
./scripts/data-transformer/transform.sh 2026-02-02 2317

# 聯發科 (2454)
./scripts/data-transformer/transform.sh 2026-02-02 2454
```

### 轉換日期區間

```bash
# 2026 年 1 月
./scripts/data-transformer/transform.sh range 2026-01-01 2026-01-31

# 2026 年 2 月
./scripts/data-transformer/transform.sh range 2026-02-01 2026-02-28

# 最近 7 天
./scripts/data-transformer/transform.sh latest 7

# 最近 30 天
./scripts/data-transformer/transform.sh latest 30
```

### 自訂輸出

```bash
# 指定輸出路徑
./scripts/data-transformer/transform.sh 2026-02-02 --output /tmp/result.csv

# 不儲存檔案，僅顯示結果
./scripts/data-transformer/transform.sh 2026-02-02 --no-save

# 顯示詳細日誌
./scripts/data-transformer/transform.sh 2026-02-02 --verbose
```

---

## 批次轉換範例

### 轉換多檔股票

```bash
# 方法 1: 使用 for 迴圈
for stock_id in 2330 2317 2454 2412 2308; do
    ./scripts/data-transformer/transform.sh 2026-02-02 $stock_id
done

# 方法 2: 使用 xargs（平行處理）
echo "2330 2317 2454 2412 2308" | xargs -n 1 -P 5 -I {} \
    ./scripts/data-transformer/transform.sh 2026-02-02 {}
```

### 轉換整個月份

```bash
# 轉換 2026 年 1 月所有交易日
./scripts/data-transformer/transform.sh range 2026-01-01 2026-01-31
```

### 定期轉換（Cron Job）

```bash
# 編輯 crontab
crontab -e

# 每天晚上 10 點轉換當天資料
0 22 * * * cd /path/to/tw-stock-collector && \
    export DB_PASSWORD=your_password && \
    ./scripts/data-transformer/transform.sh today >> /var/log/stock-transform.log 2>&1
```

---

## 輸出格式

### CSV 格式（預設）

```csv
trade_date,stock_id,open,high,low,close,volume,amount,ma_5,ma_10,...
2026-02-02,2330,1750.0,1765.0,1745.0,1765.0,33342359,58467099660,...
```

### 自動產生的檔名

- 單日全部股票：`2026-02-02_all.csv`
- 單日特定股票：`2026-02-02_2330.csv`
- 日期區間：`2026-01-01_to_2026-01-31.csv`

---

## 技術指標說明

轉換後的檔案包含 **30 個技術指標**：

| 類別 | 指標數量 | 指標名稱 |
|------|---------|---------|
| 基本資料 | 8 | trade_date, stock_id, open, high, low, close, volume, amount |
| 移動平均線 | 6 | ma_5, ma_10, ma_20, ma_60, ma_120, ma_240 |
| RSI | 2 | rsi_6, rsi_14 |
| MACD | 3 | macd_dif, macd_dea, macd_hist |
| DMI/ADX | 4 | dmi_pdi, dmi_mdi, dmi_adx, dmi_adxr |
| 布林通道 | 3 | bb_upper, bb_mid, bb_lower |
| 成交量分析 | 4 | vol_ma5, vol_ma20, vol_ratio, vwap |

---

## 疑難排解

### 錯誤：找不到資料

```
警告: 日期 2026-02-02 無資料
```

**解決方式**：
1. 確認該日期為交易日
2. 檢查資料庫是否已匯入該日期的價格資料
3. 使用 `psql` 確認資料：
   ```sql
   SELECT COUNT(*) FROM stock_price_daily
   WHERE trade_date = '2026-02-02';
   ```

### 錯誤：資料庫連線失敗

```
錯誤: 無法連線到資料庫
```

**解決方式**：
1. 確認 PostgreSQL 已啟動
2. 檢查環境變數是否正確
3. 測試連線：
   ```bash
   psql -h localhost -U postgres -d tw_stock -c "SELECT 1;"
   ```

### 錯誤：資料不足

```
警告: 跳過 133 檔股票 (資料不足)
```

**說明**：這是正常現象，部分新上市股票的歷史資料不足 240 天，無法計算 MA240（年線）。

---

## 效能參考

- **單日轉換**：20-25 秒（~1,900 檔股票）
- **處理速度**：75-100 股/秒
- **輸出檔案大小**：
  - 單日全部股票：約 200-300 KB
  - 單日單檔股票：約 0.6 KB

---

## 進階功能

### 使用 Python 腳本

需要更多控制時，可直接使用 Python：

```bash
python scripts/data-transformer/run_technical_analysis.py \
    --date 2026-02-02 \
    --stock-id 2330 \
    --output results.json \
    --show-sample 5 \
    --verbose
```

### 整合到程式中

```python
from app.technical_analysis_transformer import TechnicalAnalysisTransformer

# 建立轉換器
transformer = TechnicalAnalysisTransformer()

# 轉換資料
result_df = transformer.transform('2026-02-02')

# 篩選台積電
tsmc = result_df[result_df['stock_id'] == '2330']
print(tsmc[['close', 'ma_20', 'rsi_14', 'vwap']])
```

---

## 相關文件

- [完整使用手冊](README.md)
- [技術指標計算說明](../../services/data-transformer/README.md)
- [專案文件](../../README.md)

---

**快速求助**：
```bash
# 查看完整說明
./scripts/data-transformer/transform.sh --help

# 查看 Python 腳本說明
python scripts/data-transformer/run_technical_analysis.py --help
```

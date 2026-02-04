---
name: data-import
description: "資料匯入：將 JSON 資料匯入到 PostgreSQL 資料庫"
user-invocable: true
allowed-tools: Bash(python3:*), Read, Grep, Glob
---

# 台股資料匯入 Skill

將收集好的 JSON 格式資料匯入到 PostgreSQL 資料庫，支援多種資料類型與批次匯入。

## 功能說明

此 skill 使用專案中的 `scripts/data-importer/import_data.py` 腳本來匯入資料，支援：
- **price**: 股價資料 → `stock_prices` 表
- **institutional**: 三大法人資料 → `institutional_trades` 表
- **margin**: 融資融券資料 → `margin_trades` 表
- **lending**: 借券賣出資料 → `lending_trades` 表
- **top20_volume**: 成交量前 20 名 → `top20_volume` 表
- **analysis**: 技術分析資料 → `technical_analysis` 表

## 使用場景

### 場景 1: 匯入單一日期的所有資料
使用者說：「匯入 2026-02-03 的資料到資料庫」

**執行命令**：
```bash
python3 scripts/data-importer/import_data.py --date 2026-02-03
```

說明：
- 自動匯入所有可用的資料類型
- 會檢查 JSON 檔案是否存在

### 場景 2: 匯入特定類型資料
使用者說：「只匯入 2026-02-03 的股價資料」

**執行命令**：
```bash
python3 scripts/data-importer/import_data.py --date 2026-02-03 --types price
```

可用類型：
- `price` - 股價資料
- `institutional` - 三大法人
- `margin` - 融資融券
- `lending` - 借券賣出
- `top20_volume` - 成交量前 20 名
- `analysis` - 技術分析結果

### 場景 3: 匯入多種類型資料
使用者說：「匯入昨天的股價、法人和融資融券資料」

**執行命令**：
```bash
python3 scripts/data-importer/import_data.py --date 2026-02-03 --types price institutional margin
```

### 場景 4: 批次匯入日期區間
使用者說：「匯入 2026-01-01 到 2026-01-31 的所有資料」

**執行命令**：
```bash
python3 scripts/data-importer/import_data.py --start 2026-01-01 --end 2026-01-31
```

說明：
- 自動遍歷日期區間內的所有日期
- 跳過不存在的檔案（非交易日）

### 場景 5: 匯入技術分析資料
使用者說：「匯入 2026-02-03 的技術分析結果」

**執行命令**：
```bash
python3 scripts/data-importer/import_technical_analysis.py --date 2026-02-03
```

或使用統一腳本：
```bash
python3 scripts/data-importer/import_data.py --date 2026-02-03 --types analysis
```

說明：
- 技術分析資料位於 `data/transformed/technical_analysis/`
- 會自動處理 30 個技術指標欄位

## 執行流程

1. **解析使用者需求**
   - 確認要匯入的日期（單日或區間）
   - 確認要匯入的資料類型
   - 確認日期格式（YYYY-MM-DD）

2. **檢查前置條件**
   - 確認 PostgreSQL 資料庫正在運行
   - 確認資料檔案存在（`data/raw/{type}/YYYY/MM/YYYY-MM-DD.json`）
   - 檢查資料庫連線狀態

3. **執行匯入**
   - 組裝完整的命令列參數
   - 執行 Python 腳本
   - 監控匯入進度

4. **驗證結果**
   - 檢查匯入筆數
   - 確認資料已寫入資料庫
   - 回報匯入結果統計

5. **錯誤處理**
   - 檔案不存在：跳過並記錄
   - 資料重複：根據設定覆蓋或跳過
   - 資料庫錯誤：回報錯誤訊息

## 參數說明

### scripts/data-importer/import_data.py

**日期參數**（擇一必填）：
- `--date YYYY-MM-DD`: 單一日期匯入
- `--start YYYY-MM-DD`: 起始日期（需搭配 --end）
- `--end YYYY-MM-DD`: 結束日期（需搭配 --start）

**資料類型**（選填）：
- `--types TYPE [TYPE ...]`: 指定資料類型（預設：全部）
  - 可選值: `price`, `institutional`, `margin`, `lending`, `top20_volume`, `analysis`

**資料目錄**（選填）：
- `--data-root PATH`: 資料根目錄（預設：`data/raw`）

**資料庫配置**（選填，通常使用環境變數）：
- `--db-type`: 資料庫類型（預設：postgresql）
- `--db-host`: 資料庫主機（預設：localhost）
- `--db-port`: 資料庫埠號（預設：5432）
- `--db-name`: 資料庫名稱（預設：tw_stock）
- `--db-user`: 資料庫使用者（預設：postgres）

### scripts/data-importer/import_technical_analysis.py

- `--date YYYY-MM-DD`: 單一日期（必填）
- `--start YYYY-MM-DD`: 起始日期（可選，需搭配 --end）
- `--end YYYY-MM-DD`: 結束日期（可選，需搭配 --start）
- `--batch-size N`: 批次大小（預設：1000）

## 資料來源檔案位置

### 原始資料（data/raw）
```
data/raw/{type}/YYYY/MM/YYYY-MM-DD.json
```

範例：
- `data/raw/price/2026/02/2026-02-03.json`
- `data/raw/institutional/2026/02/2026-02-03.json`

### 轉換後資料（data/transformed）
```
data/transformed/technical_analysis/YYYY/MM/YYYY-MM-DD.json
```

範例：
- `data/transformed/technical_analysis/2026/02/2026-02-03.json`

## 資料庫表結構

### stock_prices（股價資料）
主要欄位：
- `date`, `stock_id`, `stock_name`
- `open`, `high`, `low`, `close`
- `volume`, `amount`, `transaction`
- `price_change`, `price_change_pct`

### institutional_trades（三大法人）
主要欄位：
- `date`, `stock_id`, `stock_name`
- `foreign_buy`, `foreign_sell`, `foreign_net`
- `trust_buy`, `trust_sell`, `trust_net`
- `dealer_buy`, `dealer_sell`, `dealer_net`

### margin_trades（融資融券）
主要欄位：
- `date`, `stock_id`, `stock_name`
- `margin_buy`, `margin_sell`, `margin_balance`
- `short_sell`, `short_cover`, `short_balance`

### technical_analysis（技術分析）
包含 30+ 個技術指標欄位：
- 移動平均：`ma_5`, `ma_10`, `ma_20`, `ma_60`
- 動量指標：`rsi_14`, `macd`, `macd_signal`
- 波動指標：`bb_upper`, `bb_middle`, `bb_lower`
- 趨勢指標：`adx_14`, `plus_di`, `minus_di`
- 成交量分析：`volume_ma_5`, `vwap`
- 等等...

## 錯誤處理

### 常見錯誤

1. **檔案不存在**
   ```
   Warning: File not found: data/raw/price/2026/02/2026-02-03.json
   ```
   處理：跳過該檔案，繼續處理其他資料

2. **資料庫連線失敗**
   ```
   Error: Could not connect to database
   ```
   解決：檢查 PostgreSQL 是否運行、連線設定是否正確

3. **重複資料**
   ```
   Info: Data already exists for 2026-02-03, skipping...
   ```
   處理：預設會跳過重複資料（可用 UPSERT 模式覆蓋）

4. **JSON 格式錯誤**
   ```
   Error: Invalid JSON format in file
   ```
   處理：檢查 JSON 檔案內容是否完整

## 注意事項

1. **資料庫狀態**
   - 執行前確認 PostgreSQL 已啟動
   - 確認資料庫 schema 已建立
   - 確認有足夠的磁碟空間

2. **資料完整性**
   - 匯入前應先完成資料收集
   - 建議先驗證 JSON 檔案格式
   - 可使用 `--types` 分批匯入

3. **效能考量**
   - 單日資料約 2,000-6,000 筆
   - 批次匯入建議不超過一個月（避免記憶體不足）
   - 技術分析資料較大，建議單獨匯入

4. **環境變數**
   資料庫設定可透過環境變數配置：
   ```bash
   export DB_TYPE=postgresql
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=tw_stock
   export DB_USER=postgres
   export DB_PASSWORD=tw_stock_dev_password_2024
   ```

## 範例對話

**使用者**: 匯入昨天的股價資料到資料庫

**助手回應**:
```
我會使用 import_data.py 將昨天（2026-02-03）的股價資料匯入資料庫。

執行命令：
python3 scripts/data-importer/import_data.py --date 2026-02-03 --types price

[執行結果...]
✓ 成功匯入 1,954 筆股價資料
✓ 資料表: stock_prices
✓ 日期: 2026-02-03
```

**使用者**: 匯入 2026-01 整月的所有資料

**助手回應**:
```
我會批次匯入 2026-01-01 到 2026-01-31 的所有資料類型。

執行命令：
python3 scripts/data-importer/import_data.py --start 2026-01-01 --end 2026-01-31

[執行結果...]
✓ 處理日期: 31 天
✓ 成功匯入: 20 個交易日
✓ 總計: 120,000+ 筆記錄
  - stock_prices: 39,080 筆
  - institutional_trades: 34,420 筆
  - margin_trades: 36,380 筆
  - lending_trades: 10,280 筆
```

## 驗證匯入結果

匯入完成後，可使用 SQL 查詢驗證：

```sql
-- 檢查匯入筆數
SELECT COUNT(*) FROM stock_prices WHERE date = '2026-02-03';

-- 檢查日期範圍
SELECT MIN(date), MAX(date), COUNT(DISTINCT date)
FROM stock_prices;

-- 檢查特定股票
SELECT * FROM stock_prices
WHERE stock_id = '2330'
  AND date = '2026-02-03';
```

## 相關檔案

- `scripts/data-importer/import_data.py` - 統一匯入腳本
- `scripts/data-importer/import_technical_analysis.py` - 技術分析匯入腳本
- `services/data-importer/app/main.py` - 匯入服務主程式
- `services/data-importer/app/importers/` - 各類型匯入器
- `services/common/database/models/` - 資料庫模型定義

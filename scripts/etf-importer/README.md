# ETF 持股分析系統

## 概述

本系統提供 ETF 持股資料的匯入、去重處理與選股策略整合功能。

## 資料庫架構

### 1. ETF 持股清單表 (`etf_holdings`)
儲存所有 ETF 的完整持股資料

**欄位**:
- `etf_id` - ETF 代碼（如 0050, 0051, 00733）
- `stock_id` - 股票代碼
- `snapshot_date` - 持股快照日期
- `weight` - 持股權重 (%)
- `shares` - 持有股數

### 2. ETF 去重清單表 (`etf_stock_union`)
從 `etf_holdings` 自動產生，包含所有 ETF 成分股（去重）

**欄位**:
- `stock_id` - 股票代碼
- `etf_count` - 被幾個 ETF 持有
- `total_weight` - 在所有 ETF 中的權重總和 (%)
- `latest_update` - 最後更新日期

## 使用方式

### 一鍵執行（推薦）

```bash
# 使用預設日期（今天）
bash scripts/etf-importer/run_all.sh

# 指定快照日期
bash scripts/etf-importer/run_all.sh 2026-02-04
```

### 分步驟執行

#### 步驟 1: 匯入 ETF 持股資料

```bash
# 匯入所有 ETF
python3.11 scripts/etf-importer/import_etf_holdings.py \
  --snapshot-date 2026-02-04

# 匯入單一 ETF
python3.11 scripts/etf-importer/import_etf_holdings.py \
  --snapshot-date 2026-02-04 \
  --etf 0050
```

#### 步驟 2: 產生去重清單

```bash
python3.11 scripts/etf-importer/generate_etf_union.py \
  --snapshot-date 2026-02-04
```

## 選股策略整合

系統提供整合 ETF 篩選的選股 SQL：

### 1. 主升段加速突破 + ETF 篩選

```bash
psql-17 -d tw_stock -f analysis/ETF持股篩選/主升段加速突破_ETF篩選.sql
```

**特色**:
- 篩選符合主升段加速突破條件的標的
- 限定被至少 N 個 ETF 持有（可調整）
- 提高流動性與機構認可度

### 2. 回頭買上漲 + ETF 篩選

```bash
psql-17 -d tw_stock -f analysis/ETF持股篩選/回頭買上漲_ETF篩選.sql
```

**特色**:
- 篩選符合回頭買上漲條件的標的
- 搭配 ETF 持股篩選降低風險

## 查詢範例

### 查詢 ETF 持股

```sql
-- 查詢特定 ETF 的持股
SELECT
    stock_id,
    stock_name,
    weight,
    shares
FROM etf_holdings
JOIN stocks USING (stock_id)
WHERE etf_id = '0050'
  AND snapshot_date = '2026-02-04'
ORDER BY weight DESC;
```

### 查詢去重清單

```sql
-- 查詢被多個 ETF 持有的熱門股
SELECT
    stock_id,
    stock_name,
    etf_count,
    total_weight
FROM etf_stock_union
JOIN stocks USING (stock_id)
WHERE etf_count >= 2
ORDER BY etf_count DESC, total_weight DESC
LIMIT 20;
```

### 查詢特定股票被哪些 ETF 持有

```sql
SELECT
    etf_id,
    etf_name,
    weight,
    shares
FROM etf_holdings
JOIN etfs USING (etf_id)
WHERE stock_id = '2330'
  AND snapshot_date = '2026-02-04'
ORDER BY weight DESC;
```

## 資料來源

ETF 持股資料存放於 `data/raw/etf-holdings/`：

```
data/raw/etf-holdings/
├── 0050.json   # 元大台灣50
├── 0051.json   # 元大中型100
├── 00733.json  # 富邦臺灣中小
└── ...
```

**JSON 格式**:
```json
{
  "metadata": {
    "etf_id": "0050",
    "etf_name": "元大台灣50",
    "total_holdings": 50,
    "collected_at": "2026-02-04",
    "source": "manual_import"
  },
  "holdings": [
    {
      "stock_id": "2330",
      "stock_name": "台積電",
      "weight": 47.50,
      "shares": 1234567
    }
  ]
}
```

## 注意事項

1. **股票必須先存在**: 匯入前確保 `stocks` 表已有對應股票資料
2. **日期一致性**: 建議使用相同的 `snapshot_date` 確保資料一致
3. **去重清單更新**: 每次匯入新的 ETF 持股後，需重新執行 `generate_etf_union.py`

## 錯誤處理

### 股票不存在於資料庫

**錯誤訊息**:
```
WARNING - 股票 2330 (台積電) 不存在於資料庫，跳過
```

**解決方式**:
```bash
# 先匯入股價資料以建立股票基本資訊
python3.11 scripts/data-importer/import_prices.py --date 2026-02-04
```

### 資料庫連線失敗

**檢查項目**:
1. PostgreSQL 是否啟動
2. 資料庫連線設定是否正確
3. 使用 `psql-17` 測試連線

## 效能統計

- ETF 持股匯入: ~1-2 秒/ETF
- 去重清單產生: ~1 秒（計算所有 ETF 成分股）
- 選股 SQL 執行: ~2-5 秒（視股票數量）

## 維護建議

1. **定期更新**: 建議每月更新 ETF 持股資料
2. **歷史資料**: 保留不同 `snapshot_date` 的資料可追蹤持股變化
3. **索引優化**: 系統已自動建立必要索引，無需手動調整

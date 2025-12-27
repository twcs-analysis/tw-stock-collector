# Phase 2: 資料庫設計與資料匯入

## 📋 階段概述

本階段專注於**資料庫設計與資料匯入**，將 Phase 1 收集的原始資料檔案匯入結構化資料庫，建立高效的查詢與分析基礎。

**核心目標**:
- 設計符合分析需求的資料庫結構
- 建立高效的資料匯入流程
- 實作資料查詢驗證機制
- 建立定時自動匯入系統

---

## 🎯 設計理念

### 為什麼需要資料庫？

Phase 1 使用 Git 儲存原始資料有其優勢（版本控制、免費），但面對分析需求時有以下限制：

| 需求 | Git 檔案 | 資料庫 |
|------|---------|--------|
| 複雜查詢 | ❌ 需要讀取多個檔案 | ✅ SQL 查詢 |
| 跨表關聯 | ❌ 需手動處理 | ✅ JOIN 操作 |
| 效能 | ❌ 檔案 I/O 慢 | ✅ 索引加速 |
| 即時查詢 | ❌ 不適合 | ✅ 毫秒級響應 |
| 聚合運算 | ❌ 需手動計算 | ✅ GROUP BY, SUM等 |

**結論**: Phase 2 將檔案資料匯入資料庫，以支援後續的數據分析。

---

## 💾 資料庫選型

### PostgreSQL vs MySQL vs SQLite

| 特性 | PostgreSQL | MySQL | SQLite |
|------|-----------|-------|--------|
| 資料型別 | 豐富 (JSON, Array) | 基本 | 基本 |
| 效能 | 優秀 | 優秀 | 中等 |
| 並發處理 | 強 | 強 | 弱 |
| 部署複雜度 | 中 | 中 | 低 (檔案型) |
| 適用規模 | 大 | 大 | 小至中 |

**建議選擇**:

1. **本地開發/小規模**: SQLite
   - 無需安裝資料庫服務
   - 檔案即資料庫
   - 適合個人使用

2. **生產環境/大規模**: PostgreSQL
   - 功能強大
   - 效能優異
   - 支援進階資料型別

**本文以 PostgreSQL 為主要說明，同時提供 SQLite 的對應說明。**

---

## 🗄️ 資料庫結構設計

### ER 模型概述

```
股票基本資料 (stocks)
    ↓ 1:N
    ├─→ 每日價量 (daily_prices)
    ├─→ 法人買賣超 (institutional_trading)
    ├─→ 融資融券 (margin_trading)
    ├─→ 借券資料 (securities_lending)
    ├─→ 外資持股 (foreign_holding)
    ├─→ 股權分散 (shareholding_distribution)
    └─→ 董監持股 (director_holding)
```

### 資料表設計

#### 1. 股票基本資料表 (stocks)

**用途**: 儲存所有股票的基本資訊

**欄位設計**:

| 欄位名稱 | 資料型別 | 說明 | 約束 |
|---------|---------|------|------|
| stock_id | VARCHAR(10) | 股票代號 | PRIMARY KEY |
| stock_name | VARCHAR(50) | 股票名稱 | NOT NULL |
| market_type | VARCHAR(10) | 市場別 (TWSE/TPEx) | NOT NULL |
| industry | VARCHAR(50) | 產業別 | |
| listing_date | DATE | 上市日期 | |
| is_active | BOOLEAN | 是否持續交易 | DEFAULT TRUE |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |
| updated_at | TIMESTAMP | 更新時間 | DEFAULT NOW() |

**索引**:
- PRIMARY KEY: `stock_id`
- INDEX: `market_type`, `industry`

---

#### 2. 每日價量資料表 (daily_prices)

**用途**: 儲存每日股價與成交量

**欄位設計**:

| 欄位名稱 | 資料型別 | 說明 | 約束 |
|---------|---------|------|------|
| id | BIGSERIAL | 自動編號 | PRIMARY KEY |
| stock_id | VARCHAR(10) | 股票代號 | FOREIGN KEY → stocks.stock_id |
| trade_date | DATE | 交易日期 | NOT NULL |
| open_price | DECIMAL(10,2) | 開盤價 | |
| high_price | DECIMAL(10,2) | 最高價 | |
| low_price | DECIMAL(10,2) | 最低價 | |
| close_price | DECIMAL(10,2) | 收盤價 | NOT NULL |
| volume | BIGINT | 成交量 (股) | |
| amount | BIGINT | 成交金額 (元) | |
| transaction_count | INTEGER | 成交筆數 | |
| change_price | DECIMAL(10,2) | 漲跌價差 | |
| change_percent | DECIMAL(5,2) | 漲跌幅 (%) | |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `(stock_id, trade_date)`
- INDEX: `trade_date`, `stock_id`

**分區策略** (可選):
- 按 `trade_date` 進行月份分區
- 提升查詢效能

---

#### 3. 三大法人買賣超表 (institutional_trading)

**用途**: 儲存外資、投信、自營商的買賣超資料

**欄位設計**:

| 欄位名稱 | 資料型別 | 說明 | 約束 |
|---------|---------|------|------|
| id | BIGSERIAL | 自動編號 | PRIMARY KEY |
| stock_id | VARCHAR(10) | 股票代號 | FOREIGN KEY |
| trade_date | DATE | 交易日期 | NOT NULL |
| foreign_buy | BIGINT | 外資買進 (千股) | |
| foreign_sell | BIGINT | 外資賣出 (千股) | |
| foreign_net | BIGINT | 外資買賣超 (千股) | |
| trust_buy | BIGINT | 投信買進 (千股) | |
| trust_sell | BIGINT | 投信賣出 (千股) | |
| trust_net | BIGINT | 投信買賣超 (千股) | |
| dealer_buy | BIGINT | 自營商買進 (千股) | |
| dealer_sell | BIGINT | 自營商賣出 (千股) | |
| dealer_net | BIGINT | 自營商買賣超 (千股) | |
| total_net | BIGINT | 三大法人合計 (千股) | |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `(stock_id, trade_date)`
- INDEX: `trade_date`, `foreign_net`, `total_net`

---

#### 4. 融資融券表 (margin_trading)

**用途**: 儲存融資融券餘額與變化

**欄位設計**:

| 欄位名稱 | 資料型別 | 說明 | 約束 |
|---------|---------|------|------|
| id | BIGSERIAL | 自動編號 | PRIMARY KEY |
| stock_id | VARCHAR(10) | 股票代號 | FOREIGN KEY |
| trade_date | DATE | 交易日期 | NOT NULL |
| margin_balance | BIGINT | 融資餘額 (千股) | |
| margin_change | INTEGER | 融資增減 (千股) | |
| margin_limit | BIGINT | 融資限額 (千股) | |
| short_balance | BIGINT | 融券餘額 (千股) | |
| short_change | INTEGER | 融券增減 (千股) | |
| short_limit | BIGINT | 融券限額 (千股) | |
| offset_volume | INTEGER | 資券相抵 (千股) | |
| margin_utilization | DECIMAL(5,2) | 融資使用率 (%) | |
| short_utilization | DECIMAL(5,2) | 融券使用率 (%) | |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `(stock_id, trade_date)`
- INDEX: `trade_date`, `margin_utilization`

---

#### 5. 借券資料表 (securities_lending)

**用途**: 儲存借券賣出餘額

**欄位設計**:

| 欄位名稱 | 資料型別 | 說明 | 約束 |
|---------|---------|------|------|
| id | BIGSERIAL | 自動編號 | PRIMARY KEY |
| stock_id | VARCHAR(10) | 股票代號 | FOREIGN KEY |
| trade_date | DATE | 交易日期 | NOT NULL |
| lending_balance | BIGINT | 借券賣出餘額 (股) | |
| lending_change | INTEGER | 借券賣出增減 (股) | |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `(stock_id, trade_date)`
- INDEX: `trade_date`

---

#### 6. 外資持股表 (foreign_holding)

**用途**: 儲存外資持股比例資訊

**欄位設計**:

| 欄位名稱 | 資料型別 | 說明 | 約束 |
|---------|---------|------|------|
| id | BIGSERIAL | 自動編號 | PRIMARY KEY |
| stock_id | VARCHAR(10) | 股票代號 | FOREIGN KEY |
| trade_date | DATE | 交易日期 | NOT NULL |
| foreign_shares | BIGINT | 外資持股 (千股) | |
| foreign_percent | DECIMAL(5,2) | 外資持股比例 (%) | |
| foreign_limit | DECIMAL(5,2) | 外資可投資比例 (%) | |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `(stock_id, trade_date)`
- INDEX: `trade_date`, `foreign_percent`

---

#### 7. 股權分散表 (shareholding_distribution)

**用途**: 儲存各級距持股人數與張數

**欄位設計**:

| 欄位名稱 | 資料型別 | 說明 | 約束 |
|---------|---------|------|------|
| id | BIGSERIAL | 自動編號 | PRIMARY KEY |
| stock_id | VARCHAR(10) | 股票代號 | FOREIGN KEY |
| report_date | DATE | 統計日期 | NOT NULL |
| level | VARCHAR(20) | 級距 (如 1-999張) | NOT NULL |
| holders | INTEGER | 持股人數 | |
| shares | BIGINT | 持股張數 (千股) | |
| percent | DECIMAL(5,2) | 持股比例 (%) | |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `(stock_id, report_date, level)`
- INDEX: `report_date`

---

#### 8. 董監持股表 (director_holding)

**用途**: 儲存董監事持股與質押資訊

**欄位設計**:

| 欄位名稱 | 資料型別 | 說明 | 約束 |
|---------|---------|------|------|
| id | BIGSERIAL | 自動編號 | PRIMARY KEY |
| stock_id | VARCHAR(10) | 股票代號 | FOREIGN KEY |
| report_date | DATE | 統計日期 | NOT NULL |
| director_shares | BIGINT | 董監持股 (千股) | |
| director_percent | DECIMAL(5,2) | 董監持股比例 (%) | |
| pledge_shares | BIGINT | 質押股數 (千股) | |
| pledge_percent | DECIMAL(5,2) | 質押比例 (%) | |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `(stock_id, report_date)`
- INDEX: `report_date`, `pledge_percent`

---

#### 9. 交易日曆表 (trading_calendar)

**用途**: 記錄交易日與休市日

**欄位設計**:

| 欄位名稱 | 資料型別 | 說明 | 約束 |
|---------|---------|------|------|
| trade_date | DATE | 日期 | PRIMARY KEY |
| is_trading_day | BOOLEAN | 是否為交易日 | NOT NULL |
| note | VARCHAR(100) | 備註 (如休市原因) | |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |

**索引**:
- PRIMARY KEY: `trade_date`
- INDEX: `is_trading_day`

---

#### 10. 資料匯入記錄表 (import_logs)

**用途**: 記錄每次資料匯入的執行狀況

**欄位設計**:

| 欄位名稱 | 資料型別 | 說明 | 約束 |
|---------|---------|------|------|
| id | BIGSERIAL | 自動編號 | PRIMARY KEY |
| import_date | DATE | 匯入的資料日期 | NOT NULL |
| table_name | VARCHAR(50) | 匯入的資料表 | NOT NULL |
| records_imported | INTEGER | 成功匯入筆數 | |
| records_failed | INTEGER | 失敗筆數 | |
| status | VARCHAR(20) | 執行狀態 | NOT NULL |
| error_message | TEXT | 錯誤訊息 | |
| execution_time | INTEGER | 執行時間 (秒) | |
| created_at | TIMESTAMP | 建立時間 | DEFAULT NOW() |

**索引**:
- PRIMARY KEY: `id`
- INDEX: `import_date`, `table_name`, `status`

---

## 📥 資料匯入流程

### 匯入架構設計

```
Git Repository (Phase 1)
    ↓
讀取原始資料檔案
    ↓
資料解析與轉換
    ↓
資料驗證
    ↓
批次寫入資料庫
    ↓
更新匯入記錄
    ↓
資料完整性檢查
```

### 匯入腳本架構

```
scripts/
├── database/
│   ├── __init__.py
│   ├── connection.py        # 資料庫連線管理
│   ├── schema.py            # 資料表結構定義
│   └── init_db.py           # 資料庫初始化
├── importers/
│   ├── __init__.py
│   ├── base.py              # 基礎匯入器
│   ├── price_importer.py    # 價量資料匯入
│   ├── institutional_importer.py  # 法人資料匯入
│   ├── margin_importer.py   # 信用交易匯入
│   └── ownership_importer.py  # 持股資料匯入
├── validators/
│   ├── __init__.py
│   ├── data_validator.py    # 資料驗證
│   └── integrity_checker.py # 完整性檢查
└── run_import.py            # 主執行腳本
```

### 匯入執行流程

#### 1. 初始化資料庫 (一次性)
- 建立所有資料表
- 建立索引與約束
- 初始化交易日曆
- 匯入股票基本資料

#### 2. 每日資料匯入
**觸發方式**:
- 手動執行: `python run_import.py --date 2025-01-28`
- 自動排程: GitHub Actions / Cron Job

**執行步驟**:
1. 檢查資料檔案是否存在
2. 依序匯入各類資料
   - 價量資料
   - 法人買賣超
   - 融資融券
   - 借券資料
   - 外資持股
3. 資料驗證與完整性檢查
4. 更新匯入日誌
5. 發送執行通知 (如有錯誤)

#### 3. 歷史資料批次匯入
**執行方式**:
```bash
python run_import.py --start-date 2024-01-01 --end-date 2024-12-31
```

**優化策略**:
- 批次插入 (每批 1000 筆)
- 關閉約束檢查 (匯入後再啟用)
- 使用 COPY 指令 (PostgreSQL)
- 平行處理 (多程序)

---

## ✅ 資料驗證機制

### 匯入前驗證

#### 1. 格式驗證
- 檢查必要欄位存在
- 驗證資料型別
- 確認日期格式

#### 2. 業務邏輯驗證
- 股價不可為負數
- 成交量合理性 (如不可為 0)
- 比例值範圍 (0-100%)
- 外資買賣超加總一致性

### 匯入後驗證

#### 1. 資料筆數檢查
- 比對原始檔案與資料庫筆數
- 檢查是否有遺漏

#### 2. 完整性檢查
- 檢查是否所有股票都有資料
- 驗證時間序列連續性
- 交叉驗證不同資料表

#### 3. 異常值檢測
- 股價異常波動 (>30%)
- 成交量異常 (偏離均值 3 個標準差)
- 法人買賣超異常

---

## 🔍 資料查詢驗證

### 常用查詢範例

#### 1. 查詢特定股票的每日價量
```sql
SELECT
    trade_date,
    close_price,
    volume,
    change_percent
FROM daily_prices
WHERE stock_id = '2330'
  AND trade_date >= '2025-01-01'
ORDER BY trade_date DESC;
```

#### 2. 查詢外資買超前 10 名
```sql
SELECT
    s.stock_name,
    it.foreign_net,
    dp.close_price,
    dp.change_percent
FROM institutional_trading it
JOIN stocks s ON it.stock_id = s.stock_id
JOIN daily_prices dp ON it.stock_id = dp.stock_id
                     AND it.trade_date = dp.trade_date
WHERE it.trade_date = '2025-01-28'
ORDER BY it.foreign_net DESC
LIMIT 10;
```

#### 3. 查詢融資使用率異常股票
```sql
SELECT
    s.stock_name,
    mt.margin_utilization,
    mt.margin_change,
    dp.close_price
FROM margin_trading mt
JOIN stocks s ON mt.stock_id = s.stock_id
JOIN daily_prices dp ON mt.stock_id = dp.stock_id
                     AND mt.trade_date = dp.trade_date
WHERE mt.trade_date = '2025-01-28'
  AND mt.margin_utilization > 80
ORDER BY mt.margin_utilization DESC;
```

#### 4. 查詢董監質押比例高的股票
```sql
SELECT
    s.stock_name,
    dh.director_percent,
    dh.pledge_percent,
    (dh.pledge_shares * 100.0 / dh.director_shares) as pledge_ratio
FROM director_holding dh
JOIN stocks s ON dh.stock_id = s.stock_id
WHERE dh.report_date = (SELECT MAX(report_date) FROM director_holding)
  AND dh.pledge_percent > 50
ORDER BY dh.pledge_percent DESC;
```

### 效能優化查詢

#### 使用 EXPLAIN 分析
```sql
EXPLAIN ANALYZE
SELECT * FROM daily_prices
WHERE trade_date = '2025-01-28';
```

#### 建立適當索引
```sql
CREATE INDEX idx_daily_prices_date_stock
ON daily_prices(trade_date, stock_id);
```

---

## ⏰ 定時自動匯入

### 方案選擇

#### 方案 A: GitHub Actions
**優點**:
- 與 Phase 1 整合
- 免費額度充足
- 無需額外主機

**流程**:
1. Phase 1 收集資料並 commit
2. 觸發 Phase 2 匯入工作流程
3. 連線至遠端資料庫
4. 執行資料匯入

#### 方案 B: Cron Job (本地/伺服器)
**優點**:
- 本地資料庫無需公開
- 執行更快速
- 不受 GitHub Actions 限制

**流程**:
1. 定時拉取 Git 倉庫最新資料
2. 檢查是否有新資料
3. 執行匯入腳本
4. 記錄執行日誌

**建議**:
- 本地開發: 方案 B
- 雲端資料庫: 方案 A

---

## 🛡️ 資料安全與備份

### 資料庫備份策略

#### 每日備份
- 備份方式: pg_dump (PostgreSQL) / .dump (SQLite)
- 保留期限: 最近 30 天
- 儲存位置: 本地 + 雲端儲存

#### 每週完整備份
- 備份整個資料庫
- 保留期限: 3 個月
- 壓縮後上傳雲端

### 資料恢復測試
- 每月測試一次資料恢復
- 驗證備份檔案完整性
- 記錄恢復所需時間

---

## 🚀 實作檢查清單

### Phase 2.1: 資料庫設計
- [ ] 選擇資料庫系統 (PostgreSQL/SQLite)
- [ ] 設計資料表結構
- [ ] 定義主鍵與外鍵關係
- [ ] 建立必要索引

### Phase 2.2: 資料庫初始化
- [ ] 撰寫資料表 DDL
- [ ] 實作資料庫初始化腳本
- [ ] 匯入股票基本資料
- [ ] 匯入交易日曆

### Phase 2.3: 匯入器開發
- [ ] 實作資料庫連線管理
- [ ] 實作基礎匯入器類別
- [ ] 實作各類資料匯入器
- [ ] 實作批次匯入功能

### Phase 2.4: 資料驗證
- [ ] 實作格式驗證
- [ ] 實作業務邏輯驗證
- [ ] 實作完整性檢查
- [ ] 實作異常值檢測

### Phase 2.5: 自動化排程
- [ ] 設定定時匯入機制
- [ ] 測試自動化流程
- [ ] 建立錯誤通知機制
- [ ] 記錄執行日誌

### Phase 2.6: 查詢驗證
- [ ] 撰寫常用查詢 SQL
- [ ] 測試查詢效能
- [ ] 優化索引設定
- [ ] 建立查詢文檔

### Phase 2.7: 備份與恢復
- [ ] 建立備份腳本
- [ ] 測試資料恢復流程
- [ ] 設定自動備份排程
- [ ] 驗證備份完整性

---

## 📅 預計時程

| 任務 | 預估時間 |
|------|---------|
| 資料庫設計 | 4h |
| 資料庫初始化 | 2h |
| 匯入器開發 | 8h |
| 資料驗證機制 | 4h |
| 自動化排程 | 3h |
| 查詢優化 | 3h |
| 備份機制 | 2h |
| 測試與調整 | 4h |
| **總計** | **30h** |

---

## ✅ 完成標準

Phase 2 完成後應達成:

1. **資料庫完整**: 所有資料表建立且資料完整
2. **自動匯入**: 定時自動從 Git 匯入最新資料
3. **查詢驗證**: 常用查詢測試通過且效能良好
4. **資料品質**: 無異常值、無遺漏資料
5. **備份機制**: 自動備份運行正常

---

**維護者**: Jason Huang
**版本**: 1.0
**最後更新**: 2025-12-28

# 資料收集腳本

此目錄包含台股資料的收集與回補工具。

---

## 📋 腳本列表

### 1. `collect.sh` - 單日資料收集

收集指定日期的台股資料到 `data/raw/` 目錄。

**功能**：
- ✅ 收集當天或指定日期資料
- ✅ 支援選擇資料類型
- ✅ 自動判斷交易日
- ✅ 整合五種資料來源

**使用方式**：

```bash
# 收集當天所有資料
./scripts/data-collector/collect.sh

# 收集指定日期所有資料
./scripts/data-collector/collect.sh 2026-02-02

# 收集指定類型資料
./scripts/data-collector/collect.sh 2026-02-02 price margin

# 收集單一類型
./scripts/data-collector/collect.sh 2026-02-02 institutional
```

**支援的資料類型**：
- `price` - 每日價格資料（開高低收、成交量）
- `institutional` - 三大法人買賣超
- `margin` - 融資融券
- `lending` - 借券賣出
- `top20_volume` - 成交量前 20 名

---

### 2. `backfill.sh` - 歷史資料回補

完整的歷史資料回補流程，整合三個步驟：
1. **收集原始資料** → `data/raw/`
2. **匯入資料庫** → PostgreSQL
3. **轉換技術指標** → `data/transformed/technical/`

**功能**：
- ✅ 自動化完整回補流程
- ✅ 支援日期區間指定
- ✅ 支援資料類型選擇
- ✅ 可選擇跳過技術指標轉換
- ✅ 完整的進度顯示

**使用方式**：

```bash
# 回補 2026 年 1 月所有資料
./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31

# 只回補價格資料
./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31 price

# 回補多種類型
./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31 price institutional margin

# 只收集和匯入，跳過技術指標轉換
./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31 --skip-transform
```

**回補流程**：

```
┌─────────────────────┐
│  1. 收集原始資料     │  ← scripts/backfill.py
│     data/raw/       │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  2. 匯入資料庫      │  ← scripts/data-importer/import_date_range.sh
│     PostgreSQL      │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  3. 轉換技術指標     │  ← scripts/data-transformer/transform.sh
│     data/transformed/│
└─────────────────────┘
```

---

## 🔄 完整工作流程

### 場景 1：首次設定（完整歷史資料）

```bash
# Step 1: 初始化資料庫
export DB_PASSWORD=tw_stock_dev_password_2024
./scripts/database/init_database.sh

# Step 2: 回補歷史資料（2024-2026）
./scripts/data-collector/backfill.sh 2024-01-02 2026-02-02

# Step 3: 查看結果
./scripts/database/check_status.sh
ls -lh data/transformed/technical/
```

**預計時間**：視資料量而定（約 30-60 分鐘）

---

### 場景 2：每日更新

```bash
# 收集當天資料
./scripts/data-collector/collect.sh

# 匯入資料庫
./scripts/data-importer/import_date_range.sh 2026-02-02 2026-02-02

# 轉換技術指標
./scripts/data-transformer/transform.sh today
```

**預計時間**：約 2-3 分鐘

---

### 場景 3：補缺失的單一日期

```bash
# 收集 → 匯入 → 轉換
./scripts/data-collector/collect.sh 2026-02-01
./scripts/data-importer/import_date_range.sh 2026-02-01 2026-02-01
./scripts/data-transformer/transform.sh 2026-02-01
```

---

### 場景 4：只補特定資料類型

```bash
# 只回補法人資料
./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31 institutional

# 只回補價格和融資融券
./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31 price margin
```

---

## 📊 資料收集說明

### 資料來源

所有資料來自官方公開 API，無需 token：

- **台灣證交所 (TWSE)** - 上市股票
  - OpenAPI: https://openapi.twse.com.tw
- **櫃買中心 (TPEx)** - 上櫃股票
  - OpenAPI: https://www.tpex.org.tw/openapi/v1

### 資料儲存結構

```
data/raw/{type}/YYYY/MM/YYYY-MM-DD.json
```

- 一個日期一個檔案
- 依年份（YYYY）和月份（MM）分目錄
- JSON 格式包含 metadata 和 data

**範例**：
```
data/raw/
├── price/2026/02/2026-02-02.json          # 價格資料
├── institutional/2026/02/2026-02-02.json  # 法人資料
├── margin/2026/02/2026-02-02.json         # 融資融券
├── lending/2026/02/2026-02-02.json        # 借券賣出
└── top20_volume/2026/02/2026-02-02.json   # 成交量前 20
```

### 資料量統計

單日資料量（約 2,000 檔股票）：

| 資料類型 | 記錄數 | 檔案大小 |
|---------|--------|---------|
| price | ~1,950 | ~600 KB |
| institutional | ~1,720 | ~4.1 MB |
| margin | ~1,820 | ~980 KB |
| lending | ~1,010 | ~550 KB |
| top20_volume | 20 | ~6.6 KB |
| **總計** | **~6,520** | **~6.2 MB** |

---

## ⚠️ 注意事項

### 交易日判斷

- 系統會自動判斷是否為交易日
- 週末和國定假日不收集資料
- 可用 `--skip-trading-day-check` 強制執行（開發測試用）

### 資料完整性

收集後建議驗證：

```bash
# 查看收集的檔案
ls -lh data/raw/price/2026/02/

# 檢查 JSON 格式
cat data/raw/price/2026/02/2026-02-02.json | jq '.metadata'

# 統計記錄數
cat data/raw/price/2026/02/2026-02-02.json | jq '.data | length'
```

### 錯誤處理

- 網路錯誤會自動重試（最多 3 次）
- 失敗的資料收集會記錄在日誌中
- 建議定期檢查 `logs/` 目錄

---

## 🔗 相關文件

- [資料匯入腳本](../data-importer/README.md) - 資料匯入到資料庫
- [技術指標轉換](../data-transformer/README.md) - 計算技術指標
- [資料庫管理](../database/README.md) - 資料庫初始化與查詢
- [專案說明](../../README.md) - 專案整體架構

---

## 🆘 疑難排解

### 問題 1：收集失敗

```bash
✗ 資料收集失敗
```

**可能原因**：
1. 網路連線問題
2. API 服務暫時不可用
3. 非交易日

**解決方式**：
```bash
# 檢查網路
curl -I https://openapi.twse.com.tw

# 查看詳細錯誤
cat logs/collection_YYYY-MM-DD.log

# 手動重試
./scripts/data-collector/collect.sh 2026-02-02
```

---

### 問題 2：部分資料缺失

```bash
# 收集成功但某些股票資料缺失
```

**解決方式**：
```bash
# 檢查 JSON 檔案
jq '.data | length' data/raw/price/2026/02/2026-02-02.json

# 如果筆數異常少（< 1000），重新收集
./scripts/data-collector/collect.sh 2026-02-02 price
```

---

### 問題 3：回補中斷

```bash
# backfill.sh 執行到一半失敗
```

**解決方式**：
```bash
# 查看已完成的日期
ls data/raw/price/2026/02/

# 從中斷處繼續
./scripts/data-collector/backfill.sh 2026-02-15 2026-02-28
```

---

## 💡 最佳實踐

### 1. 定期備份

```bash
# 備份原始資料
tar -czf data_raw_backup_$(date +%Y%m%d).tar.gz data/raw/

# 備份資料庫
pg_dump -h localhost -U postgres tw_stock > backup_$(date +%Y%m%d).sql
```

### 2. 批次處理

大量回補建議分批執行：

```bash
# 按月回補
./scripts/data-collector/backfill.sh 2024-01-01 2024-01-31
./scripts/data-collector/backfill.sh 2024-02-01 2024-02-29
./scripts/data-collector/backfill.sh 2024-03-01 2024-03-31
```

### 3. 自動化排程

使用 cron 自動每日收集：

```bash
# 編輯 crontab
crontab -e

# 每天 22:00 自動收集
0 22 * * * cd /path/to/tw-stock-collector && \
    ./scripts/data-collector/collect.sh && \
    ./scripts/data-importer/import_date_range.sh $(date +%Y-%m-%d) $(date +%Y-%m-%d) && \
    ./scripts/data-transformer/transform.sh today \
    >> /var/log/tw-stock-collect.log 2>&1
```

---

**維護日期**: 2026-02-02
**維護者**: Jason Huang

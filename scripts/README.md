# Scripts 目錄說明

本目錄包含台股資料收集系統的所有執行腳本，按功能分類。

---

## 📁 目錄結構

```
scripts/
├── data-collector/         # 資料收集相關
├── data-importer/          # 資料匯入資料庫
├── data-transformer/       # 資料轉換（技術指標等）
├── database/               # 資料庫管理
├── stock-list/             # 股票清單管理
├── deprecated/             # 已過時的腳本
├── run_collection.py       # 主要收集腳本
├── validate_data.py        # 資料驗證
├── batch_validate.sh       # 批次驗證
└── setup_github.sh         # GitHub 初始化設定
```

---

## 🎯 主要腳本

### 每日資料收集
```bash
# 收集當天所有資料類型
python scripts/run_collection.py

# 收集指定日期（僅當日或最新交易日）
python scripts/run_collection.py --date 2026-02-02

# 收集特定資料類型
python scripts/run_collection.py --types price institutional
```

### 資料驗證
```bash
# 驗證特定日期的資料
python scripts/validate_data.py --date 2026-02-02

# 批次驗證
./scripts/batch_validate.sh
```

---

## 📂 data-collector/ - 資料收集

### 快速啟動
```bash
# 使用 shell 腳本收集（簡化版）
./scripts/data-collector/collect.sh
```

### 歷史資料回補

使用 TWSE MI_INDEX API 快速回補歷史資料（約 2-3 秒）。
```bash
# 回補單一日期（快速，約 2-3 秒）
python scripts/data-collector/backfill_historical.py --date 2026-01-27

# 回補日期範圍
python scripts/data-collector/backfill_historical.py --start 2026-01-27 --end 2026-01-30

# 回補特定股票
python scripts/data-collector/backfill_historical.py --date 2026-01-27 --stocks 2330,2337,2454
```

**重要說明**：
- 使用 `MI_INDEX` API 一次取得所有股票資料
- 每個日期僅需 1 次 API 請求，速度快
- 約 2-3 秒即可完成單日回補（vs 舊方法 20-30 分鐘）

---

## 📂 data-importer/ - 資料匯入

將 JSON 原始資料匯入 PostgreSQL 資料庫。

```bash
# 匯入單一日期
./scripts/data-importer/import_single_date.sh 2026-02-02

# 匯入日期範圍
./scripts/data-importer/import_date_range.sh 2026-01-01 2026-01-31

# Python 匯入腳本
python scripts/data-importer/import_data.py --date 2026-02-02
```

---

## 📂 data-transformer/ - 資料轉換

將價格資料轉換為技術指標。

```bash
# 轉換單一日期
./scripts/data-transformer/transform.sh 2026-02-02

# 轉換整個月份
./scripts/data-transformer/transform_by_month.sh 2026 01

# Python 轉換腳本
python scripts/data-transformer/run_technical_analysis.py --date 2026-02-02
```

---

## 📂 database/ - 資料庫管理

```bash
# 初始化資料庫
./scripts/database/init_database.sh

# 檢查資料庫狀態
./scripts/database/check_status.sh
```

---

## 📂 stock-list/ - 股票清單管理

管理股票代碼清單。

```bash
# 初始化股票清單
python scripts/stock-list/init_stock_list.py

# 抓取最新股票清單
python scripts/stock-list/fetch_stock_list.py

# 建立股票清單
python scripts/stock-list/build_stock_list.py

# 建立股票清單（另一種方式）
python scripts/stock-list/create_stock_list.py
```

**注意**：`build_stock_list.py` 和 `create_stock_list.py` 功能可能重複，需進一步確認。

---

## 📂 deprecated/ - 已過時的腳本

這些腳本已不再使用或被新版本取代：

- `fetch_2025_price.sh` - 2025 年專用腳本（已過時）
- `refetch_2025.sh` - 重新抓取 2025（已過時）
- `quickstart.py` - 快速開始（功能已整合到其他腳本）

---

## 🔧 其他工具

### GitHub 設定
```bash
# 設定 GitHub Actions 相關配置
./scripts/setup_github.sh
```

---

## ⚠️ 重要提醒

1. **資料收集限制**：
   - OpenAPI 只能取得最新交易日資料
   - 歷史資料回補需要使用慢速模式（逐股查詢）

2. **建議工作流程**：
   - ✅ 使用 GitHub Actions 每日自動收集
   - ✅ 使用 `run_collection.py` 手動收集當日資料
   - ⚠️ 僅在必要時使用 `backfill_historical.py` 回補

3. **效能考量**：
   - 即時收集：1 次 API 請求，約 2-3 秒
   - 歷史回補：1,900 次請求，約 20-30 分鐘

---

**最後更新**: 2026-02-02
**維護者**: Jason Huang

# 月營收資料 - 每日收集模式 (Daily)

## 📊 資料說明

**每日收集模式**適用於月營收公告期間（每月 1-10 日），透過 MOPS API 逐一查詢各公司是否已公告，實現增量更新。

### 使用情境

- **時間**: 每月 1-10 日
- **特性**: 增量更新，每天只查詢未公告的公司
- **完整性**: 資料不完整，隨時間增加（約 30-100%）
- **用途**: 即時追蹤、早期分析

### 資料來源

**當月資料**（MOPS API，逐一查詢）:
- **API**: `https://mops.twse.com.tw/mops/api/t05st10_ifrs`
- **方式**: POST 請求，查詢單一股票是否已公告
- **延遲**: 每次查詢間隔 0.3 秒（避免過度請求）

**上月資料**（OpenAPI，用於計算 MoM）:
- **上市 (TWSE)**: `https://openapi.twse.com.tw/v1/opendata/t187ap05_L`
- **上櫃 (TPEx)**: `https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O`

## 📁 檔案結構

```
revenue-daily/
└── 2026/
    ├── 2026-01.json  # 2026-01 月營收（同一個月同一個檔案）
    ├── 2026-02.json  # 2026-02 月營收
    └── ...
```

**命名規則**: `YYYY/YYYY-MM.json`（**同一個月同一個檔案，增量更新**）

**⚠️ 重要變更** (2026-02-06):
- 從「每日一個檔案」改為「每月一個檔案，增量更新」
- 每次執行會載入已收集資料，只查詢未公告的股票
- 自動跳過已公告的股票，避免重複查詢

## 📊 資料格式

### Metadata

```json
{
  "metadata": {
    "year_month": "2026-01",              // 資料年月
    "mode": "daily",                      // 收集模式
    "collection_date": "2026-02-06",      // 收集日期
    "total_count": 618,                   // 累計已公告公司數
    "twse_count": 337,                    // 上市公司數
    "tpex_count": 281,                    // 上櫃公司數
    "total_stocks": 1940,                 // 股票總數
    "announced_ratio": "31.9%",           // 公告率
    "new_announced": 617,                 // 本次新增公告數
    "source": "MOPS API"
  }
}
```

### Data 格式

```json
{
  "year_month": "2026-01",               // 資料年月
  "stock_id": "1213",                    // 股票代碼
  "stock_name": "大飲",                  // 股票名稱
  "type": "twse",                        // twse 或 tpex
  "current_month_revenue": 24751.0,      // 當月營收（千元）
  "last_month_revenue": 20948,           // 上月營收（千元）✨ 新增
  "last_year_revenue": 22381.0,          // 去年同月營收（千元）
  "revenue_change": 2370.0,              // 營收變化（千元）
  "yoy_change_pct": 10.6,                // 年增率 (%)
  "ytd_revenue": 24751.0,                // 累計營收（千元）
  "ytd_last_year_revenue": 22381.0,      // 去年累計營收（千元）
  "ytd_yoy_change_pct": 10.59,           // 累計年增率 (%)
  "mom_change_pct": 18.15,               // 月增率 (%) ✨ 新增
  "note": null                           // 備註
}
```

**✨ 新功能** (2026-02-06):
- `last_month_revenue`: 從 OpenAPI 自動取得上月營收
- `mom_change_pct`: 自動計算月增率 = (當月 - 上月) / 上月 × 100

**欄位說明**:
- `last_month_revenue` 和 `mom_change_pct` 現在與 monthly 模式一致
- 資料來源：當月資料來自 MOPS API，上月資料來自 OpenAPI

## 🚀 使用方式

### 收集當天資料

```bash
python3.11 scripts/data-collector/collect_revenue.py --mode daily --year-month 2026-01
```

### 指定收集日期

```bash
python3.11 scripts/data-collector/collect_revenue.py --mode daily --year-month 2026-01 --date 2026-02-06
```

### 測試模式（不儲存）

```bash
python3.11 scripts/data-collector/collect_revenue.py --mode daily --year-month 2026-01 --dry-run --verbose
```

## 📈 資料成長範例

假設收集 2026-01 月營收（增量更新模式）：

| 日期 | 執行時間 | 待查詢 | 新增 | 累計 | 公告率 |
|------|---------|--------|------|------|--------|
| 02-02 | 10 分鐘 | 1,940 檔 | 150 檔 | 150 檔 | 8% |
| 02-03 | 9 分鐘 | 1,790 檔 | 300 檔 | 450 檔 | 23% |
| 02-05 | 4 分鐘 | 740 檔 | 750 檔 | 1,200 檔 | 62% |
| 02-06 | 4 分鐘 | 1,322 檔 | 418 檔 | 1,618 檔 | 83% |
| 02-10 | 2 分鐘 | 322 檔 | 322 檔 | 1,940 檔 | 100% |

**增量更新優勢**:
- ✅ 自動跳過已公告的股票，節省時間
- ✅ 同一個檔案持續更新，資料不分散
- ✅ 支援中斷後繼續收集

## ⚠️ 注意事項

1. **資料不完整**: 10 日前的資料都是部分公司，不適合整體分析
2. **增量更新**: 同一個月的資料會累積在同一個檔案中
3. **API 延遲**: 每次查詢間隔 0.3 秒，全量收集需 10 分鐘
4. **切換時機**: 10 日後應切換到 [monthly 模式](../revenue-monthly/)
5. **自動補 MoM**: 自動從 OpenAPI 取得上月營收並計算月增率

## 🔄 工作流程

```
1-10 日：使用 daily 模式
  ↓ 每日收集
  ↓ 資料逐漸完整
  ↓
10 日後：切換到 monthly 模式
  ↓ 一次收集完整資料
  ↓ 不再使用 daily 資料
```

## 💡 使用案例

### 查看當前公告狀態

```bash
# 查看 2026-01 月營收公告進度
cat data/raw/revenue-daily/2026/2026-01.json | jq '.metadata'
```

### 檢查特定公司是否已公告

```bash
# 查看台積電 (2330) 是否已公告
cat data/raw/revenue-daily/2026/2026-01.json | \
  jq '.data[] | select(.stock_id == "2330")'
```

### 列出已公告公司（含 MoM）

```bash
# 列出所有已公告公司的營收與月增率
cat data/raw/revenue-daily/2026/2026-01.json | \
  jq '.data[] | {stock_id, stock_name, current_month_revenue, mom_change_pct, yoy_change_pct}'
```

### 找出月增率最高的公司

```bash
# 找出 MoM 前 10 名
cat data/raw/revenue-daily/2026/2026-01.json | \
  jq '.data | sort_by(-.mom_change_pct) | .[0:10] |
      .[] | {stock_id, stock_name, mom_change_pct, yoy_change_pct}'
```

## 📚 相關文件

- [月度收集模式 (Monthly)](../revenue-monthly/)
- [收集腳本說明](../../../scripts/data-collector/collect_revenue.py)
- [專案說明文件](../../../README.md)

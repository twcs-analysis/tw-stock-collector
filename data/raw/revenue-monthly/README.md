# 月營收資料 - 月度收集模式 (Monthly)

## 📊 資料說明

**月度收集模式**適用於月營收公告完成後（每月 10 日後），一次取得完整月度資料。

### 使用情境

- **時間**: 每月 10 日後
- **特性**: 一次取得所有公司完整資料
- **完整性**: 100% 完整
- **用途**: 正式分析、統計、建模

### 資料來源

- **上市 (TWSE)**: `https://openapi.twse.com.tw/v1/opendata/t187ap05_L`
- **上櫃 (TPEx)**: `https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O`

### 更新頻率

- **每月 10 日左右**更新上個月的資料
- 建議在每月 11 日收集（避開更新當天）

## 📁 檔案結構

```
revenue-monthly/
├── 2025/
│   ├── 2025-11.json
│   ├── 2025-12.json
│   └── ...
├── 2026/
│   ├── 2026-01.json
│   ├── 2026-02.json
│   └── ...
└── README.md
```

**命名規則**: `YYYY/YYYY-MM.json`（以月為單位）

## 📊 資料格式

### Metadata

```json
{
  "metadata": {
    "year_month": "2025-12",              // 資料年月
    "mode": "monthly",                    // 收集模式
    "total_count": 1940,                  // 總公司數
    "twse_count": 1066,                   // 上市公司數
    "tpex_count": 874,                    // 上櫃公司數
    "source": "TWSE + TPEx Official API"
  }
}
```

### Data

```json
{
  "report_date": "2026-01-17",           // 出表日期
  "year_month": "2025-12",               // 資料年月
  "stock_id": "2330",                    // 股票代碼
  "stock_name": "台積電",                // 股票名稱
  "industry": "半導體業",                // 產業別
  "type": "twse",                        // twse 或 tpex
  "current_month_revenue": 335003568,    // 當月營收（千元）
  "last_month_revenue": 343613802,       // 上月營收（千元）
  "last_year_revenue": 278163107,        // 去年同月營收（千元）
  "mom_change_pct": -2.51,               // 月增率 (%)
  "yoy_change_pct": 20.43,               // 年增率 (%)
  "ytd_revenue": 3809054272,             // 累計營收（千元）
  "ytd_last_year_revenue": 2894307699,   // 去年累計營收（千元）
  "ytd_yoy_change_pct": 31.61,           // 累計年增率 (%)
  "note": "-"                            // 備註
}
```

## 🚀 使用方式

### 收集最新月份資料

```bash
python3.11 scripts/data-collector/collect_revenue.py --mode monthly
```

### 測試（不儲存）

```bash
python3.11 scripts/data-collector/collect_revenue.py --mode monthly --dry-run --verbose
```

### 指定年月（僅影響儲存路徑）

```bash
python3.11 scripts/data-collector/collect_revenue.py --mode monthly --year-month 2026-01
```

⚠️ **注意**: 即使指定年月，API 仍只會回傳最新月份的資料

## 📈 資料統計

### 每月資料量

- **公司數量**: 約 1,940 家（上市 1,066 + 上櫃 874）
- **檔案大小**: 約 1 MB/月
- **欄位數量**: 15 個欄位

### 儲存空間估算

- **每月**: 1 MB
- **每年**: 12 MB
- **5 年**: 60 MB

## 💡 使用案例

### 1. 查看台積電月營收

```bash
cat data/raw/revenue-monthly/2025/2025-12.json | \
  jq '.data[] | select(.stock_id == "2330")'
```

### 2. 列出年增率前 10 名

```bash
cat data/raw/revenue-monthly/2025/2025-12.json | \
  jq '.data | sort_by(-.yoy_change_pct) | .[0:10] |
      .[] | {stock_id, stock_name, yoy_change_pct}'
```

### 3. 統計各產業平均年增率

```bash
cat data/raw/revenue-monthly/2025/2025-12.json | \
  jq '[.data[] | {industry, yoy_change_pct}] |
      group_by(.industry) |
      map({
        industry: .[0].industry,
        avg_yoy: (map(.yoy_change_pct) | add / length)
      })'
```

### 4. 比較兩個月的營收變化

```bash
# 取得 11 月和 12 月的台積電營收
nov=$(cat data/raw/revenue-monthly/2025/2025-11.json | \
      jq '.data[] | select(.stock_id == "2330") | .current_month_revenue')
dec=$(cat data/raw/revenue-monthly/2025/2025-12.json | \
      jq '.data[] | select(.stock_id == "2330") | .current_month_revenue')

echo "台積電 11月: $nov 千元"
echo "台積電 12月: $dec 千元"
```

## 🔄 自動化收集

### GitHub Actions 設定

建議在 `.github/workflows/monthly-revenue-collection.yml` 中設定：

```yaml
name: Monthly Revenue Collection

on:
  schedule:
    # 每月 11 日 10:00 台北時間執行
    - cron: '0 2 11 * *'
  workflow_dispatch:

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Collect Revenue
        run: |
          python3 scripts/data-collector/collect_revenue.py --mode monthly
      - name: Commit
        run: |
          git add data/raw/revenue-monthly/
          git commit -m "data(revenue): 收集月營收資料"
          git push
```

## ⚠️ 重要特性

1. **API 限制**: 只提供最新月份的資料，無法查詢歷史
2. **完整性保證**: 10 日後收集，確保所有公司都已公告
3. **一次性收集**: 建議每月只收集一次，減少 API 請求
4. **資料備份**: 舊資料無法重新取得，務必妥善保存

## 📝 與 Daily 模式的差異

| 特性 | Daily 模式 | Monthly 模式 |
|------|-----------|--------------|
| **時間** | 1-10 日 | 10 日後 |
| **完整性** | 部分（30-100%） | 完整（100%） |
| **更新頻率** | 每日增量更新 | 每月一次 |
| **檔案結構** | `YYYY/YYYY-MM.json` | `YYYY/YYYY-MM.json` |
| **資料來源** | MOPS API（逐一查詢）+ OpenAPI（上月資料）| OpenAPI（一次取得所有） |
| **查詢方式** | POST 逐股查詢（慢）| GET 批次查詢（快） |
| **執行時間** | 5-10 分鐘（增量）| 2-3 秒 |
| **用途** | 即時追蹤 | 正式分析 |
| **公司數** | 變動（150-1940） | 固定（~1940） |
| **MoM 資料** | ✅ 有（從 OpenAPI 取得）| ✅ 有（直接提供） |

**資料欄位完整性**：
- 兩種模式的資料格式**完全一致**（自 2026-02-06 起）
- Daily 模式現在也包含 `last_month_revenue` 和 `mom_change_pct`
- 可無縫切換，不影響後續分析

## 📚 相關文件

- [每日收集模式 (Daily)](../revenue-daily/)
- [收集腳本說明](../../../scripts/data-collector/collect_revenue.py)
- [TWSE OpenAPI 文件](https://openapi.twse.com.tw/)
- [TPEx OpenAPI 文件](https://www.tpex.org.tw/openapi/)
- [專案說明文件](../../../README.md)

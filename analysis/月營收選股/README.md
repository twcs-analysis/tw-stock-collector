# 月營收選股

基於月營收資料的多維度選股策略。

## 🎯 選股邏輯（四大維度）

| 篩選維度 | 理想條件 | 意義 | 優先級 |
|---------|---------|------|-------|
| **成長性** | YoY > 20% 且 MoM > 0% | 確立短期與長期成長動能 | ⭐⭐⭐ 必要 |
| **歷史位階** | 創下 12 個月或歷史新高 | 尋求產業地位或產能突破 | ⭐⭐ 加分 |
| **趨勢強度** | 連續 3 個月 YoY 遞增 | 排除單月偶發性入帳 | ⭐⭐⭐ 必要 |
| **量價關係** | 營收公布後股價帶量突破 | 市場對營收表現給予肯定 | ⭐⭐ 加分 |

## 📋 選股策略

### 策略 A：嚴格成長股（推薦）
**同時滿足 4 個維度**，最嚴格篩選
```
✅ YoY > 20% 且 MoM > 0%
✅ 創 12 個月新高
✅ 連續 3 個月 YoY 遞增
✅ 股價帶量突破（需整合股價資料）
```

### 策略 B：強勢成長股（平衡）
**滿足 3 個必要維度**，不強制量價突破
```
✅ YoY > 20% 且 MoM > 0%
✅ 創 12 個月新高
✅ 連續 3 個月 YoY 遞增
⚪ 量價關係選填
```

### 策略 C：潛力成長股（寬鬆）
**滿足成長性與趨勢強度**
```
✅ YoY > 20% 且 MoM > 0%
✅ 連續 3 個月 YoY 遞增
⚪ 歷史位階選填
⚪ 量價關係選填
```

### 策略 D：爆發突破股（短線）
**營收暴增 + 歷史新高**，適合短線交易
```
✅ MoM > 30% 或 YoY > 50%
✅ 創歷史新高
⚪ 趨勢強度選填（可能是新突破）
```

## 📁 目錄結構

```
月營收選股/
├── README.md                    # 本文件
├── strategy_a_strict.sql        # 策略 A：嚴格成長股
├── strategy_b_balanced.sql      # 策略 B：強勢成長股
├── strategy_c_potential.sql     # 策略 C：潛力成長股
├── strategy_d_breakout.sql      # 策略 D：爆發突破股
└── STRATEGY_COMPARISON.md       # 策略對比文件
```

## 🚀 快速開始

### 使用 SQL 查詢

```bash
# 策略 B：強勢成長股（推薦）
psql-17 -U postgres -d tw_stock \
  -v target_month='2026-01' \
  -f analysis/月營收選股/strategy_b_balanced.sql

# 策略 A：嚴格成長股（最嚴格）
psql-17 -U postgres -d tw_stock \
  -v target_month='2026-01' \
  -f analysis/月營收選股/strategy_a_strict.sql
```

### 調整篩選條件

編輯 SQL 檔案中的參數：
```sql
\set target_month '''2026-01'''
\set min_yoy 20       -- 最低年增率 (%)
\set min_mom 0        -- 最低月增率 (%)
```

## 📊 資料來源

### 營收資料
- **資料表**: `stock_revenues`
- **欄位**: year_month, stock_id, revenue（千元）, mom_growth, yoy_growth
- **範圍**: 2024-01 至今

### 股價資料（量價關係）
- **資料表**: `stock_prices`
- **欄位**: trade_date, stock_id, close_price, volume
- **用途**: 判斷營收公布後的股價反應

## 📈 分析報告

報告儲存於：`analysis/reports/月營收選股/`

---

**最後更新**: 2026-02-08
**策略來源**: 結合技術分析與基本面篩選

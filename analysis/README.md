# 技術分析工具 (Analysis Tools)

本目錄包含台股技術分析相關的工具與腳本。**每個策略都提供 Python 腳本和對應的 SQL 查詢檔案**，可靈活選擇使用 Python 或直接在資料庫執行 SQL。

---

## 📊 目錄結構

```
analysis/
├── README.md                          # 本說明文件
│
├── 回檔買進/                          # 回檔買進策略
│   ├── filter_recovery_stocks.py      # Python 腳本（彈性條件版）
│   ├── filter_recovery_stocks.sql     # 對應 SQL 查詢
│   ├── pullback_buy_selector.py       # Python 腳本
│   └── pullback_buy_selector.sql      # 對應 SQL 查詢
│
├── 趨勢追蹤/                          # 趨勢追蹤策略
│   ├── find_bullish_stocks.py         # Python 腳本
│   └── find_bullish_stocks.sql        # 對應 SQL 查詢
│
├── 多策略綜合/                        # 多策略綜合
│   ├── recommend_stocks_20260202.py   # Python 腳本（文字報告版）
│   ├── recommend_stocks_with_names.py # Python 腳本（Markdown 版）
│   └── multi_strategy_selector.sql    # 對應 SQL 查詢
│
├── 月營收選股/                        # 月營收選股策略 ⭐ 新增
│   ├── README.md                      # 策略說明文件
│   ├── strategy_a_strict.sql          # 策略 A：嚴格成長股
│   ├── strategy_b_balanced.sql        # 策略 B：強勢成長股
│   ├── strategy_c_potential.sql       # 策略 C：潛力成長股
│   ├── strategy_d_breakout.sql        # 策略 D：爆發突破股
│   └── STRATEGY_COMPARISON.md         # 策略對比文件
│
├── reports/                           # 分析報告輸出目錄
│   ├── README.md                      # 報告說明文件
│   └── 月營收選股/                    # 月營收選股報告 ⭐ 新增
│       ├── README.md                  # 報告格式說明
│       ├── 2026-01/                   # 2026 年 1 月報告
│       └── archive/                   # 歷史報告封存
│
└── results/                           # 篩選結果輸出目錄
    └── [日期]/                        # 按日期組織的結果
```

---

## 🎯 主要工具

### 1. 回檔買進策略（回後買上漲型態篩選）

**專為「回後買上漲」型態設計的股票篩選器**，根據四個技術條件自動篩選符合型態的標的。

#### 1.1 filter_recovery_stocks.py（彈性條件版，推薦）

#### 功能特色

- ✅ 四大技術條件檢查
  - 條件 A：頭頭高 底底高（上升趨勢）
  - 條件 B：股價在月線之上且前低未破
  - 條件 C：今日紅 K 站上 5 均
  - 條件 D：收盤過昨日高
- ✅ 彈性條件數量設定（支援部分符合）
- ✅ 各條件通過率統計
- ✅ 自動匯出 CSV 結果

#### 使用方式

```bash
# 篩選符合所有 4 個條件的股票（嚴格）
python analysis/filter_recovery_stocks.py --date 2026-02-02

# 篩選至少符合 3 個條件的股票（平衡，推薦）
python analysis/filter_recovery_stocks.py --date 2026-02-02 --min-conditions 3

# 指定輸出檔案
python analysis/filter_recovery_stocks.py --date 2026-02-02 --output results.csv
```

#### 輸出結果

```
各條件通過統計:
  條件 A (頭頭高底底高): 468/1877 (24.9%)
  條件 B (在月線上且前低未破): 68/1877 (3.6%)
  條件 C (紅K站上5均): 68/1877 (3.6%)
  條件 D (收盤過昨高): 48/1877 (2.6%)

符合全部 4 個條件: 3 支股票
  1236 [4/4]  收盤:   26.30  5MA:   25.95  20MA:   25.26
  1590 [4/4]  收盤: 1170.00  5MA: 1080.00  20MA: 1021.70
  6552 [4/4]  收盤:   33.55  5MA:   30.69  20MA:   27.49

符合至少 3 個條件: 21 支股票
```

**輸出檔案位置**：`analysis/results/recovery_stocks_{date}.csv`

**對應 SQL 查詢**：[filter_recovery_stocks.sql](回檔買進/filter_recovery_stocks.sql)

#### 1.2 pullback_buy_selector.py（標準版）

與 `filter_recovery_stocks.py` 邏輯相同，但實作細節略有不同。

```bash
# 基本使用
python analysis/回檔買進/pullback_buy_selector.py 2026-02-03
```

**對應 SQL 查詢**：[pullback_buy_selector.sql](回檔買進/pullback_buy_selector.sql)

#### 條件說明

| 條件 | 檢查邏輯 | 意義 |
|-----|---------|------|
| A | 後 5 天均高/低點 > 前 5 天均高/低點 | 上升趨勢確認 |
| B | 收盤 > MA20 且最近低點 > 前一低點 | 月線支撐有效 |
| C | 收盤 > 開盤 且 收盤 > MA5 | 當日買方力道強 |
| D | 今日收盤 > 昨日最高 | 突破前高 |

#### 適用場景

- 尋找處於上升趨勢的股票
- 篩選「回後買上漲」型態標的
- 短中線交易參考

---

### 2. 趨勢追蹤策略

#### 2.1 find_bullish_stocks.py（多頭市場技術分析）

**簡化版的多頭選股工具**，快速篩選符合多頭條件的股票。

**選股條件**：
1. 價格在均線之上（多頭排列）
2. RSI 在 50-70 之間（強勢但未超買）
3. MACD 黃金交叉（DIF > DEA）且柱狀圖為正
4. ADX > 25（趨勢強勁）
5. 價格在布林通道中上軌
6. 成交量大於 20 日均量（活躍）

```bash
python analysis/趨勢追蹤/find_bullish_stocks.py
```

**對應 SQL 查詢**：[find_bullish_stocks.sql](趨勢追蹤/find_bullish_stocks.sql)

---

### 3. 多策略綜合

#### 3.1 recommend_stocks_with_names.py（推薦使用）

**最完整的股票推薦分析工具**，根據技術指標自動篩選並推薦適合的標的。

#### 功能特色

- ✅ 完整股票名稱顯示（從原始資料載入）
- ✅ 三種投資策略選股
  - 強勢多頭（適合積極投資者）
  - 穩健多頭（適合穩健投資者）
  - 突破型（適合短線交易者）
- ✅ 30 個技術指標分析
- ✅ 智慧評分系統
- ✅ 生成三種格式報告
  - Markdown (.md)
  - CSV (.csv)
  - 文字報告 (.txt)

#### 使用方式

```bash
python analysis/recommend_stocks_with_names.py
```

#### 輸出位置

```
~/Downloads/股票推薦/
├── 股票推薦報告_2026-02-02.md   # Markdown 格式
├── 股票推薦報告_2026-02-02.txt  # 純文字格式
└── 股票推薦清單_2026-02-02.csv  # Excel 可開啟
```

#### 技術指標說明

**選股條件**：

1. **強勢多頭**
   - 均線完整多頭排列（MA5 > MA10 > MA20）
   - RSI 強勢區間（60-75）
   - MACD 黃金交叉且柱狀圖強勁（> 0.05）
   - ADX > 30（趨勢非常強勁）
   - +DI 明顯大於 -DI（多頭力道強）
   - 成交量放大（量比 > 1.3）

2. **穩健多頭**
   - 均線多頭排列（收盤 > MA5 > MA20）
   - RSI 中性偏強（50-65）
   - MACD 黃金交叉
   - ADX > 25（趨勢明確）
   - 價格在布林通道中上軌
   - 成交量適中（量比 > 1.0）

3. **突破型**
   - 價格突破 MA20
   - RSI 快速上升（55-70）
   - MACD 剛黃金交叉（柱狀圖 0-0.3）
   - ADX 上升中（20-35）
   - +DI 快速上升
   - 大量突破（量比 > 1.5）

#### 評分系統

綜合評分由以下指標加權計算：

- RSI 評分（15%）：越接近 60 分越高
- MACD 評分（20%）：柱狀圖強度
- ADX 評分（20%）：趨勢強度
- DMI 評分（20%）：多頭力道（+DI - -DI）
- 成交量評分（15%）：量比
- 均線評分（10%）：短均線相對長均線位置

#### 後續處理

生成 Markdown 報告後，可使用 `markdown_to_pdf.py` 轉換為 PDF：

```bash
python scripts/common-tools/markdown_to_pdf.py \
    ~/Downloads/股票推薦/股票推薦報告_2026-02-02.md
```

詳見：[markdown_to_pdf.py 使用說明](../scripts/common-tools/README.md)

#### 3.2 recommend_stocks_20260202.py（文字報告版）

與 `recommend_stocks_with_names.py` 邏輯相同，但生成純文字報告（不含 Markdown）。

```bash
python analysis/多策略綜合/recommend_stocks_20260202.py
```

**對應 SQL 查詢**：[multi_strategy_selector.sql](多策略綜合/multi_strategy_selector.sql)

**註**：兩個 Python 腳本共用同一個 SQL 查詢檔案。

---

### 4. 月營收選股策略 ⭐ 新增

#### 4.1 概述

基於月營收資料的**四大維度**多策略選股系統。

#### 四大篩選維度

| 維度 | 條件 | 意義 | 優先級 |
|-----|------|------|-------|
| **成長性** | YoY > 20% 且 MoM > 0% | 確立短期與長期成長動能 | ⭐⭐⭐ 必要 |
| **歷史位階** | 創下 12 個月或歷史新高 | 尋求產業地位或產能突破 | ⭐⭐ 加分 |
| **趨勢強度** | 連續 3 個月 YoY 遞增 | 排除單月偶發性入帳 | ⭐⭐⭐ 必要 |
| **量價關係** | 營收公布後股價帶量突破 | 市場對營收表現給予肯定 | ⭐⭐ 加分 |

#### 四大選股策略

| 策略 | SQL 檔案 | 說明 | 適用場景 |
|-----|---------|------|---------|
| **策略 A** | [strategy_a_strict.sql](月營收選股/queries/strategy_a_strict.sql) | 嚴格成長股（滿足 4 維度） | 最嚴格篩選 |
| **策略 B** | [strategy_b_balanced.sql](月營收選股/queries/strategy_b_balanced.sql) | 強勢成長股（3 必要維度）⭐ 推薦 | 平衡選擇 |
| **策略 C** | [strategy_c_potential.sql](月營收選股/queries/strategy_c_potential.sql) | 潛力成長股（2 核心維度） | 寬鬆篩選 |
| **策略 D** | [strategy_d_breakout.sql](月營收選股/queries/strategy_d_breakout.sql) | 爆發突破股（爆發+新高） | 短線交易 |

#### 使用方式

```bash
# 策略 B：強勢成長股（推薦）
psql-17 -U postgres -d tw_stock \
  -v target_month='2026-01' \
  -f analysis/月營收選股/strategy_b_balanced.sql

# 策略 A：嚴格成長股（最嚴格）
psql-17 -U postgres -d tw_stock \
  -v target_month='2026-01' \
  -f analysis/月營收選股/strategy_a_strict.sql

# 策略 D：爆發突破股（短線）
psql-17 -U postgres -d tw_stock \
  -v target_month='2026-01' \
  -f analysis/月營收選股/strategy_d_breakout.sql
```

#### 資料來源

- **營收資料**: `stock_revenues`（2024-01 至今）
- **股價資料**: `stock_prices`（用於量價關係判斷）

#### 詳細說明

完整策略說明與技術細節：[月營收選股/README.md](月營收選股/README.md)

#### 分析報告

每月報告儲存於：[reports/月營收選股/](reports/月營收選股/)

---

## 🗄️ SQL 查詢檔案

**每個策略都提供對應的 SQL 查詢檔案**，可直接在 PostgreSQL 資料庫中執行，無需 Python 環境。

### SQL 檔案清單

| SQL 檔案 | 對應 Python 腳本 | 說明 |
|---------|----------------|------|
| [filter_recovery_stocks.sql](回檔買進/filter_recovery_stocks.sql) | filter_recovery_stocks.py | 回後買上漲型態篩選（彈性版） |
| [pullback_buy_selector.sql](回檔買進/pullback_buy_selector.sql) | pullback_buy_selector.py | 回檔買上漲選股（標準版） |
| [find_bullish_stocks.sql](趨勢追蹤/find_bullish_stocks.sql) | find_bullish_stocks.py | 多頭市場選股 |
| [multi_strategy_selector.sql](多策略綜合/multi_strategy_selector.sql) | recommend_stocks_*.py | 多策略綜合選股 |
| [strategy_a_strict.sql](月營收選股/strategy_a_strict.sql) | 待開發 | 營收選股：嚴格成長股 ⭐ 新增 |
| [strategy_b_balanced.sql](月營收選股/strategy_b_balanced.sql) | 待開發 | 營收選股：強勢成長股（推薦） ⭐ 新增 |
| [strategy_c_potential.sql](月營收選股/strategy_c_potential.sql) | 待開發 | 營收選股：潛力成長股 ⭐ 新增 |
| [strategy_d_breakout.sql](月營收選股/strategy_d_breakout.sql) | 待開發 | 營收選股：爆發突破股 ⭐ 新增 |

### SQL 使用方式

#### 方法一：使用 psql 命令執行

```bash
# 執行 SQL 查詢
psql -U postgres -d tw_stock -f analysis/回檔買進/filter_recovery_stocks.sql

# 匯出結果為 CSV
psql -U postgres -d tw_stock -f analysis/回檔買進/filter_recovery_stocks.sql -o results.csv
```

#### 方法二：在 psql 互動模式中執行

```bash
# 連接資料庫
psql -U postgres -d tw_stock

# 執行 SQL 檔案
\i analysis/回檔買進/filter_recovery_stocks.sql
```

#### 方法三：使用資料庫管理工具

使用 DBeaver、pgAdmin、DataGrip 等工具：
1. 開啟 SQL 檔案
2. 連接到 `tw_stock` 資料庫
3. 執行查詢

### SQL 調整參數

所有 SQL 檔案都支援以下調整：

#### 1. 修改目標日期

將 SQL 中的日期常數替換為目標日期：

```sql
-- 範例：從 2026-02-03 改為 2026-02-04
-- 原本
WHERE ti.trade_date = '2026-02-03'

-- 修改為
WHERE ti.trade_date = '2026-02-04'
```

#### 2. 調整篩選條件

```sql
-- 範例：放寬 RSI 範圍
-- 原本
AND rsi_14 > 50 AND rsi_14 < 70

-- 修改為
AND rsi_14 > 45 AND rsi_14 < 75
```

#### 3. 調整評分權重

```sql
-- 原本
rsi_score * 0.2 + macd_score * 0.2 + ...

-- 修改為（加重 RSI 權重）
rsi_score * 0.3 + macd_score * 0.15 + ...
```

#### 4. 限制輸出數量

```sql
-- 原本
LIMIT 10

-- 修改為
LIMIT 20
```

### SQL 查詢範例

#### 範例一：快速查看回檔買進標的

```sql
-- 執行簡化版查詢（僅顯示關鍵資訊）
SELECT
    stock_id AS "股票代號",
    close_price AS "收盤價",
    ma_5 AS "MA5",
    ma_20 AS "MA20"
FROM stock_prices
WHERE trade_date = '2026-02-03'
    AND close_price > open_price  -- 紅 K
    AND close_price > ma_5         -- 站上 MA5
    AND stock_id >= 1000
    AND volume >= 1000000
ORDER BY close_price DESC;
```

#### 範例二：查看各條件通過統計

```sql
-- 查看各條件通過的股票數量和比例
-- 參考 filter_recovery_stocks.sql 中的「各條件通過統計」查詢
```

### SQL vs Python 選擇建議

| 需求 | 建議 | 原因 |
|-----|------|-----|
| 快速查詢最新數據 | SQL | 速度快，無需載入 Python |
| 需要股票名稱 | Python | 自動載入名稱資料 |
| 生成報告（PDF/MD） | Python | 支援多種輸出格式 |
| 批次處理多日期 | Python | 支援迴圈和自動化 |
| 整合其他系統 | SQL | 標準 SQL 易於整合 |
| 學習和研究 | 兩者皆可 | 對照學習最佳 |

---

## 🔧 技術指標說明

本工具使用的 30 個技術指標來自 `data/transformed/technical/` 目錄：

### 移動平均線 (MA)
- MA5, MA10, MA20, MA60, MA120, MA240

### 相對強弱指標 (RSI)
- RSI(6), RSI(14)

### MACD 指標
- DIF (快線)
- DEA (慢線)
- HIST (柱狀圖)

### DMI/ADX 趨勢指標
- +DI (正向指標)
- -DI (負向指標)
- ADX (趨勢強度)
- ADXR (趨勢強度評估)

### 布林通道 (Bollinger Bands)
- 上軌
- 中軌
- 下軌

### 成交量分析
- 5 日均量
- 20 日均量
- 量比（當日成交量 / 20 日均量）

### 其他指標
- VWAP（成交量加權平均價）

---

## 📋 資料來源

### 技術指標資料
- 路徑：`data/transformed/technical/YYYY-MM-DD_all.csv`
- 生成工具：`scripts/data-transformer/run_technical_analysis.py`
- 資料來源：從 PostgreSQL 資料庫載入價格資料計算

### 股票名稱資料
- 路徑：`data/raw/price/YYYY/MM/YYYY-MM-DD.json`
- 資料來源：台灣證交所 (TWSE) 與櫃買中心 (TPEx) 官方 API

---

## ⚠️ 注意事項

### 投資風險提示

1. 本工具僅供參考，不構成投資建議
2. 技術分析需搭配基本面、籌碼面、消息面綜合判斷
3. 建議設定停損停利點，控制風險
4. 投資前請詳閱公開資訊觀測站的公司財報
5. 投資有風險，請謹慎評估自身風險承受能力

### 技術限制

- 僅分析一般股票，已排除 ETF（代碼 0 開頭）
- 排除成交量過低的股票（< 100 萬股）
- 技術指標基於歷史資料，無法預測未來
- 市場環境變化可能影響指標有效性

---

## 🚀 未來規劃

### 短期
- [ ] 加入更多技術指標（KD、威廉指標等）
- [ ] 支援自訂選股條件
- [ ] 加入回測功能

### 中期
- [ ] 整合籌碼面分析（法人買賣、融資融券）
- [ ] 加入基本面指標（本益比、殖利率）
- [ ] 建立股票評分模型

### 長期
- [ ] 機器學習預測模型
- [ ] 即時選股通知
- [ ] Web 介面

---

## 📖 相關文件

- [專案總覽](../README.md)
- [資料結構說明](../data/README.md)
- [技術指標生成](../scripts/data-transformer/README.md)
- [Markdown 轉 PDF 工具](../scripts/common-tools/README.md)

---

**最後更新**: 2026-02-08
**維護者**: Jason Huang

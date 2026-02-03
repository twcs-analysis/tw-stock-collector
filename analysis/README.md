# 技術分析工具 (Analysis Tools)

本目錄包含台股技術分析相關的工具與腳本。

---

## 📊 目錄結構

```
analysis/
├── README.md                          # 本說明文件
├── filter_recovery_stocks.py          # 回後買上漲型態篩選器（新）
├── find_bullish_stocks.py             # 多頭選股分析
├── recommend_stocks_20260202.py       # 2026-02-02 股票推薦（舊版）
├── recommend_stocks_with_names.py     # 股票推薦分析（完整版，含股票名稱）
└── results/                           # 篩選結果輸出目錄
```

---

## 🎯 主要工具

### 1. filter_recovery_stocks.py（回後買上漲型態篩選器，NEW！）

**專為「回後買上漲」型態設計的股票篩選器**，根據四個技術條件自動篩選符合型態的標的。

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

### 2. recommend_stocks_with_names.py（推薦使用）

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

---

### 3. find_bullish_stocks.py

**簡化版的多頭選股工具**，快速篩選符合多頭條件的股票。

#### 功能特色

- ✅ 單一多頭策略
- ✅ 快速篩選
- ✅ 終端輸出結果

#### 使用方式

```bash
python analysis/find_bullish_stocks.py
```

#### 適用場景

- 快速查看多頭標的
- 終端機直接查看結果
- 不需要完整報告

---

### 4. recommend_stocks_20260202.py（舊版，不建議使用）

**舊版的股票推薦工具**，功能類似 `recommend_stocks_with_names.py` 但缺少股票名稱。

建議使用 `recommend_stocks_with_names.py` 取代。

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

**最後更新**: 2026-02-03
**維護者**: Jason Huang

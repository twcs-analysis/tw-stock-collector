# Phase 3: 數據整理與分析

## 📋 階段概述

本階段專注於**數據整理與分析**，基於 Phase 2 建立的資料庫進行深度分析，產出有價值的投資洞察。

**核心目標**:
- 數據清洗與特徵工程
- 技術指標計算
- 籌碼分析與主力追蹤
- 多維度數據聚合
- 視覺化呈現與報表產出

---

## 🎯 設計理念

### 從資料到洞察的轉化

Phase 1 與 Phase 2 建立了完整的資料基礎，Phase 3 的目標是將**原始資料轉化為可執行的投資決策依據**。

```
原始資料 (Phase 1-2)
    ↓
數據清洗與整理
    ↓
特徵工程
    ↓
技術指標計算
    ↓
籌碼分析
    ↓
多維度聚合
    ↓
視覺化與報表
    ↓
投資決策支援
```

---

## 📊 分析維度規劃

### 1. 技術面分析

#### 趨勢指標
- **移動平均線 (MA)**
  - 5日、10日、20日、60日、120日、240日均線
  - 計算乖離率
  - 均線糾結分析

- **MACD (指數平滑異同移動平均線)**
  - DIF、DEA、MACD 柱狀圖
  - 黃金交叉/死亡交叉訊號
  - 背離分析

- **布林通道 (Bollinger Bands)**
  - 上軌、中軌、下軌
  - 布林寬度 (%B)
  - 突破訊號

#### 動能指標
- **RSI (相對強弱指標)**
  - 6日、12日 RSI
  - 超買/超賣區間判斷
  - RSI 背離

- **KD 隨機指標**
  - K值、D值
  - 黃金交叉/死亡交叉
  - 鈍化判斷

- **威廉指標 (%R)**
  - 超買超賣判斷
  - 背離訊號

#### 量價指標
- **OBV (能量潮)**
  - 累計量能變化
  - 價量背離

- **成交量分析**
  - 量增價漲/量縮價跌
  - 爆量分析
  - 量能比較 (vs 5日/20日均量)

---

### 2. 籌碼面分析

#### 三大法人分析
- **外資動向**
  - 連續買超/賣超天數
  - 累計買賣超金額
  - 持股比例變化
  - 外資進出排行

- **投信動向**
  - 投信同步買超 (多檔同時買入)
  - 投信持股集中度
  - 季底作帳分析

- **自營商動向**
  - 自營商避險行為
  - 自營商籌碼變化

#### 融資融券分析
- **融資分析**
  - 融資餘額變化趨勢
  - 融資使用率 (>80% 警戒)
  - 融資斷頭風險
  - 融資與股價關係

- **融券分析**
  - 融券餘額變化
  - 券資比
  - 軋空訊號

- **資券相抵**
  - 相抵張數異常

#### 借券分析
- **借券賣出**
  - 借券餘額變化
  - 大量借券警訊
  - 借券與股價關係

#### 主力進出分析
- **董監持股**
  - 董監持股比例
  - 質押比例警戒 (>50%)
  - 董監異常增減持

- **大戶持股**
  - 千張大戶人數變化
  - 持股集中度 (前10大股東)
  - 籌碼安定性

---

### 3. 多維度綜合分析

#### 強弱勢分析
- **相對強弱比較**
  - 個股 vs 大盤
  - 個股 vs 產業
  - 漲跌幅排行

#### 選股策略
- **多頭訊號**
  - 技術面多頭排列
  - 外資連續買超
  - 融資減少、融券增加
  - 成交量放大

- **風險警訊**
  - 融資使用率過高
  - 外資連續賣超
  - 董監質押比例高
  - 技術指標背離

#### 產業分析
- **產業表現**
  - 產業漲跌幅
  - 產業資金流向
  - 產業相對強弱

---

## 🔧 技術實作架構

### 分析模組結構

```
analysis/
├── __init__.py
├── technical/              # 技術分析
│   ├── __init__.py
│   ├── indicators.py       # 技術指標計算
│   ├── ma_analysis.py      # 均線分析
│   ├── momentum.py         # 動能指標
│   └── volume.py           # 量價分析
├── chip/                   # 籌碼分析
│   ├── __init__.py
│   ├── institutional.py    # 法人分析
│   ├── margin.py           # 信用交易分析
│   ├── ownership.py        # 持股結構分析
│   └── main_force.py       # 主力分析
├── composite/              # 綜合分析
│   ├── __init__.py
│   ├── strength.py         # 強弱分析
│   ├── screening.py        # 選股策略
│   └── sector.py           # 產業分析
├── aggregation/            # 數據聚合
│   ├── __init__.py
│   ├── daily_stats.py      # 每日統計
│   └── summary_tables.py   # 彙總表
└── utils/
    ├── __init__.py
    ├── calculator.py       # 計算工具
    └── ranker.py           # 排行工具
```

---

## 📈 技術指標計算

### 計算策略

#### 方案 A: 即時計算
**優點**: 資料最新、彈性高
**缺點**: 每次查詢都要計算、效能較差

**適用**: 複雜計算、較少使用的指標

#### 方案 B: 預先計算並儲存
**優點**: 查詢快速、效能佳
**缺點**: 需要額外儲存空間

**適用**: 常用指標、基礎計算

**建議**: 採用方案 B，建立獨立的技術指標表

### 技術指標資料表設計

#### daily_technical_indicators

| 欄位名稱 | 資料型別 | 說明 |
|---------|---------|------|
| id | BIGSERIAL | PRIMARY KEY |
| stock_id | VARCHAR(10) | FOREIGN KEY |
| trade_date | DATE | NOT NULL |
| ma_5 | DECIMAL(10,2) | 5日均線 |
| ma_10 | DECIMAL(10,2) | 10日均線 |
| ma_20 | DECIMAL(10,2) | 20日均線 |
| ma_60 | DECIMAL(10,2) | 60日均線 |
| ma_120 | DECIMAL(10,2) | 120日均線 |
| ma_240 | DECIMAL(10,2) | 240日均線 |
| macd_dif | DECIMAL(10,4) | MACD DIF |
| macd_dea | DECIMAL(10,4) | MACD DEA |
| macd_histogram | DECIMAL(10,4) | MACD 柱狀圖 |
| rsi_6 | DECIMAL(5,2) | 6日RSI |
| rsi_12 | DECIMAL(5,2) | 12日RSI |
| k_value | DECIMAL(5,2) | KD K值 |
| d_value | DECIMAL(5,2) | KD D值 |
| obv | BIGINT | OBV |
| bbands_upper | DECIMAL(10,2) | 布林上軌 |
| bbands_middle | DECIMAL(10,2) | 布林中軌 |
| bbands_lower | DECIMAL(10,2) | 布林下軌 |
| created_at | TIMESTAMP | DEFAULT NOW() |

**索引**:
- UNIQUE INDEX: `(stock_id, trade_date)`

---

## 🎲 籌碼分析資料表

### chip_analysis_daily

| 欄位名稱 | 資料型別 | 說明 |
|---------|---------|------|
| id | BIGSERIAL | PRIMARY KEY |
| stock_id | VARCHAR(10) | FOREIGN KEY |
| trade_date | DATE | NOT NULL |
| foreign_net_3d | BIGINT | 外資3日買賣超 |
| foreign_net_5d | BIGINT | 外資5日買賣超 |
| foreign_net_10d | BIGINT | 外資10日買賣超 |
| foreign_net_20d | BIGINT | 外資20日買賣超 |
| foreign_consecutive_days | INTEGER | 外資連續買超天數(負為賣超) |
| trust_net_5d | BIGINT | 投信5日買賣超 |
| trust_consecutive_days | INTEGER | 投信連續買超天數 |
| margin_change_5d | INTEGER | 融資5日增減 |
| margin_utilization_change | DECIMAL(5,2) | 融資使用率變化 |
| short_change_5d | INTEGER | 融券5日增減 |
| margin_short_ratio | DECIMAL(5,2) | 券資比 |
| created_at | TIMESTAMP | DEFAULT NOW() |

---

## 📊 資料聚合與彙總

### 每日市場統計表 (market_daily_stats)

**用途**: 整體市場每日統計數據

| 欄位名稱 | 資料型別 | 說明 |
|---------|---------|------|
| id | BIGSERIAL | PRIMARY KEY |
| trade_date | DATE | UNIQUE, NOT NULL |
| total_stocks | INTEGER | 交易股票數 |
| advancing_stocks | INTEGER | 上漲家數 |
| declining_stocks | INTEGER | 下跌家數 |
| unchanged_stocks | INTEGER | 持平家數 |
| limit_up_stocks | INTEGER | 漲停家數 |
| limit_down_stocks | INTEGER | 跌停家數 |
| total_volume | BIGINT | 總成交量 |
| total_amount | BIGINT | 總成交金額 |
| foreign_net_total | BIGINT | 外資買賣超總計 |
| trust_net_total | BIGINT | 投信買賣超總計 |
| dealer_net_total | BIGINT | 自營買賣超總計 |
| created_at | TIMESTAMP | DEFAULT NOW() |

### 產業統計表 (sector_daily_stats)

**用途**: 各產業每日統計

| 欄位名稱 | 資料型別 | 說明 |
|---------|---------|------|
| id | BIGSERIAL | PRIMARY KEY |
| trade_date | DATE | NOT NULL |
| industry | VARCHAR(50) | NOT NULL |
| stock_count | INTEGER | 產業股票數 |
| avg_change_percent | DECIMAL(5,2) | 平均漲跌幅 |
| advancing_count | INTEGER | 上漲家數 |
| declining_count | INTEGER | 下跌家數 |
| total_volume | BIGINT | 產業成交量 |
| foreign_net | BIGINT | 外資買賣超 |
| created_at | TIMESTAMP | DEFAULT NOW() |

**索引**:
- UNIQUE INDEX: `(trade_date, industry)`

---

## 📋 選股策略實作

### 策略表設計 (stock_screening_results)

**用途**: 儲存選股結果

| 欄位名稱 | 資料型別 | 說明 |
|---------|---------|------|
| id | BIGSERIAL | PRIMARY KEY |
| screen_date | DATE | NOT NULL |
| strategy_name | VARCHAR(50) | 策略名稱 |
| stock_id | VARCHAR(10) | FOREIGN KEY |
| score | DECIMAL(5,2) | 評分 |
| reason | TEXT | 入選原因 |
| created_at | TIMESTAMP | DEFAULT NOW() |

**索引**:
- INDEX: `(screen_date, strategy_name)`

### 常用選股策略

#### 1. 外資連買策略
**條件**:
- 外資連續買超 >= 3 天
- 外資5日買賣超 > 1000張
- 股價在20日均線之上

#### 2. 低融資高成長
**條件**:
- 融資使用率 < 20%
- 近5日成交量 > 20日均量
- 收盤價創近60日新高

#### 3. 籌碼集中
**條件**:
- 千張大戶增加
- 外資持股比例上升
- 融資減少、融券增加

#### 4. 技術多頭排列
**條件**:
- 短均線 > 中均線 > 長均線 (5MA > 20MA > 60MA)
- MACD DIF > 0
- RSI > 50

---

## 📊 視覺化與報表

### 報表類型

#### 1. 個股分析報表
**包含內容**:
- 基本資訊 (代號、名稱、產業)
- 技術面
  - K線圖 + 均線
  - 成交量
  - 技術指標 (MACD, KD, RSI)
- 籌碼面
  - 三大法人買賣超趨勢
  - 融資融券變化
  - 外資持股比例
  - 股權分散圖
- 綜合評分

#### 2. 市場總覽報表
**包含內容**:
- 大盤漲跌統計
- 資金流向 (法人買賣超)
- 產業表現排行
- 強勢股/弱勢股排行
- 異常股票警示

#### 3. 產業分析報表
**包含內容**:
- 產業漲跌幅
- 產業資金流向
- 產業龍頭股表現
- 產業內強弱股排行

#### 4. 選股結果報表
**包含內容**:
- 各策略選股清單
- 股票評分排序
- 入選原因說明
- 風險提示

### 視覺化工具選擇

#### Python 繪圖套件
- **Matplotlib**: 基礎繪圖
- **Plotly**: 互動式圖表
- **mplfinance**: K線圖專用
- **Seaborn**: 統計視覺化

#### Web 儀表板
- **Streamlit**: 快速建立互動式儀表板
- **Dash**: 更客製化的儀表板
- **Grafana**: 監控型儀表板 (可選)

---

## 🔄 分析執行流程

### 每日執行流程

```
資料匯入完成 (Phase 2)
    ↓
計算技術指標
    ↓
計算籌碼分析指標
    ↓
更新聚合統計表
    ↓
執行選股策略
    ↓
產生每日報表
    ↓
發送通知 / 更新儀表板
```

### 執行時機

| 任務 | 執行頻率 | 建議時間 |
|------|---------|---------|
| 技術指標計算 | 每日 | 資料匯入後 |
| 籌碼分析 | 每日 | 資料匯入後 |
| 選股策略 | 每日 | 19:00 |
| 每日報表產生 | 每日 | 20:00 |
| 週報產生 | 每週 | 週日 |

---

## 🚀 實作檢查清單

### Phase 3.1: 技術指標
- [ ] 建立技術指標資料表
- [ ] 實作移動平均線計算
- [ ] 實作 MACD 計算
- [ ] 實作 RSI 計算
- [ ] 實作 KD 計算
- [ ] 實作布林通道計算
- [ ] 實作 OBV 計算
- [ ] 測試指標正確性

### Phase 3.2: 籌碼分析
- [ ] 建立籌碼分析資料表
- [ ] 實作法人連續買賣超計算
- [ ] 實作融資融券分析
- [ ] 實作持股集中度計算
- [ ] 實作主力進出分析
- [ ] 測試分析正確性

### Phase 3.3: 數據聚合
- [ ] 建立市場統計表
- [ ] 建立產業統計表
- [ ] 實作每日統計計算
- [ ] 實作產業統計計算
- [ ] 測試聚合正確性

### Phase 3.4: 選股策略
- [ ] 建立選股結果表
- [ ] 實作外資連買策略
- [ ] 實作低融資高成長策略
- [ ] 實作籌碼集中策略
- [ ] 實作技術多頭策略
- [ ] 回測策略有效性

### Phase 3.5: 視覺化與報表
- [ ] 實作個股分析報表
- [ ] 實作市場總覽報表
- [ ] 實作產業分析報表
- [ ] 實作選股結果報表
- [ ] 建立互動式儀表板

### Phase 3.6: 自動化與通知
- [ ] 設定每日自動執行
- [ ] 實作報表產出
- [ ] 設定郵件/Line通知
- [ ] 測試自動化流程

---

## 📅 預計時程

| 任務 | 預估時間 |
|------|---------|
| 技術指標開發 | 8h |
| 籌碼分析開發 | 8h |
| 數據聚合 | 4h |
| 選股策略 | 6h |
| 視覺化與報表 | 10h |
| 儀表板開發 | 8h |
| 自動化設定 | 3h |
| 測試與調整 | 5h |
| **總計** | **52h** |

---

## ✅ 完成標準

Phase 3 完成後應達成:

1. **技術指標完整**: 常用技術指標全部計算並儲存
2. **籌碼分析完善**: 法人、信用交易、主力分析可用
3. **選股策略有效**: 至少3種以上選股策略運行
4. **報表自動產出**: 每日自動產生分析報表
5. **視覺化清晰**: 圖表美觀、資訊豐富
6. **儀表板可用**: 互動式儀表板可供查詢

---

## 💡 進階功能 (選配)

### 1. 機器學習預測
- 股價漲跌預測
- 成交量預測
- 法人買賣超預測

### 2. 量化回測
- 策略回測框架
- 績效評估指標
- 參數優化

### 3. 警示系統
- 突破訊號通知
- 異常波動警示
- 風險警告

### 4. API 服務
- RESTful API
- WebSocket 即時推送
- API 文檔

---

**維護者**: Jason Huang
**版本**: 1.0
**最後更新**: 2025-12-28

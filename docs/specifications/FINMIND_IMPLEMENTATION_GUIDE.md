# 台股資料收集系統規格書 (FinMind 免費版)

## 專案概述
使用 **FinMind 免費會員**作為主要資料來源，建立完整的台股資料收集系統，專注於**日線級別的技術面與籌碼面分析**。

**重要說明**：
- ✅ 本規格書僅使用 FinMind **免費功能**
- ✅ 不包含任何付費會員功能（如分K線）
- ✅ 專注於日線資料分析（已足夠大多數投資策略）

---

## 一、資料收集策略總覽

### 1.1 資料來源分配

| 資料類型 | 主要來源 | 涵蓋率 | 備註 |
|---------|---------|-------|------|
| 技術面資料 | ✅ FinMind | 100% | 完全涵蓋 |
| 籌碼面資料 | ✅ FinMind | 90% | 大部分涵蓋 |
| 主力進出 | ⚠️ FinMind + 自建爬蟲 | 40% | 需補充爬蟲 |

### 1.2 開發階段規劃

**階段一 (優先)：FinMind 基礎建設**
- 使用 FinMind 收集 90% 的資料
- 建立完整的資料庫架構
- 實作自動化排程

**階段二 (選配)：補充爬蟲**
- 主力分點前 15 大排行（如有需要）
- 其他特殊需求資料

---

## 二、FinMind 資料需求清單

### 2.1 技術面資料 (100% FinMind)

#### 2.1.1 每日價量資料
**FinMind API**: `taiwan_stock_daily`

```python
from FinMind.data import DataLoader

dl = DataLoader()
dl.login_by_token(api_token='your_token')

# 取得台積電每日價量資料
data = dl.taiwan_stock_daily(
    stock_id='2330',
    start_date='2024-01-01',
    end_date='2024-12-27'
)
```

**資料欄位**:
- `date`: 日期
- `stock_id`: 股票代號
- `Trading_Volume`: 成交股數
- `Trading_money`: 成交金額
- `open`: 開盤價
- `max`: 最高價
- `min`: 最低價
- `close`: 收盤價
- `spread`: 漲跌價差
- `Trading_turnover`: 成交筆數

**資料範圍**: 1994-10-01 至今
**更新時間**: 每日 17:30

---

#### 2.1.2 還原股價 (考慮除權息)
**FinMind API**: `taiwan_stock_daily_adj`

```python
# 取得還原股價 (用於技術指標計算)
data = dl.taiwan_stock_daily_adj(
    stock_id='2330',
    start_date='2024-01-01',
    end_date='2024-12-27'
)
```

**資料欄位**:
- 與 `taiwan_stock_daily` 相同
- 價格已調整除權息

**用途**: 計算長期技術指標 (如年線、MA250) 時使用

---

#### 2.1.3 個股 PER、PBR 資料
**FinMind API**: `taiwan_stock_per_pbr`

```python
# 取得本益比、股價淨值比
data = dl.taiwan_stock_per_pbr(
    stock_id='2330',
    start_date='2024-01-01',
    end_date='2024-12-27'
)
```

**資料欄位**:
- `date`: 日期
- `stock_id`: 股票代號
- `PER`: 本益比
- `PBR`: 股價淨值比
- `dividend_yield`: 殖利率
- `value`: 收盤價

**資料範圍**: 2005 年至今

---

#### 2.1.4 台股加權指數
**FinMind API**: `taiwan_stock_index`

```python
# 取得加權指數
data = dl.taiwan_stock_index(
    index_id='TAIEX',  # 加權指數
    start_date='2024-01-01',
    end_date='2024-12-27'
)
```

**常用指數代碼**:
- `TAIEX`: 加權股價指數
- `TWA00`: 水泥類指數
- `TWA01`: 食品類指數
- ... 等產業指數

---

### 2.2 籌碼面資料 (90% FinMind)

#### 2.2.1 三大法人買賣超 (個股)
**FinMind API**: `taiwan_stock_institutional_investors`

```python
# 取得個股三大法人買賣超
data = dl.taiwan_stock_institutional_investors(
    stock_id='2330',
    start_date='2024-01-01',
    end_date='2024-12-27'
)
```

**資料欄位**:
- `date`: 日期
- `stock_id`: 股票代號
- `buy`: 買進股數 (三大法人合計)
- `sell`: 賣出股數
- `difference`: 買賣超股數
- `ForeignInvestment_buy`: 外資買進
- `ForeignInvestment_sell`: 外資賣出
- `ForeignInvestment_difference`: 外資買賣超
- `Investment_Trust_buy`: 投信買進
- `Investment_Trust_sell`: 投信賣出
- `Investment_Trust_difference`: 投信買賣超
- `Dealer_buy`: 自營商買進 (合計)
- `Dealer_sell`: 自營商賣出
- `Dealer_difference`: 自營商買賣超
- `Dealer_Hedging_buy`: 自營商避險買進
- `Dealer_Hedging_sell`: 自營商避險賣出
- `Dealer_Hedging_difference`: 自營商避險買賣超

**資料範圍**: 2001 年至今
**更新時間**: 每日 15:00-23:30 之間

---

#### 2.2.2 三大法人買賣超 (整體市場)
**FinMind API**: `taiwan_stock_institutional_investors_total`

```python
# 取得整體市場三大法人買賣超
data = dl.taiwan_stock_institutional_investors_total(
    start_date='2024-01-01',
    end_date='2024-12-27'
)
```

**用途**: 觀察整體市場資金流向

---

#### 2.2.3 融資融券 (個股)
**FinMind API**: `taiwan_stock_margin_purchase_short_sale`

```python
# 取得個股融資融券資料
data = dl.taiwan_stock_margin_purchase_short_sale(
    stock_id='2330',
    start_date='2024-01-01',
    end_date='2024-12-27'
)
```

**資料欄位**:
- `date`: 日期
- `stock_id`: 股票代號
- `MarginPurchaseBuy`: 融資買進
- `MarginPurchaseSell`: 融資賣出
- `MarginPurchaseCashRepayment`: 融資現金償還
- `MarginPurchaseYesterdayBalance`: 融資前日餘額
- `MarginPurchaseTodayBalance`: 融資今日餘額
- `MarginPurchaseLimit`: 融資限額
- `ShortSaleBuy`: 融券買進
- `ShortSaleSell`: 融券賣出
- `ShortSaleCashRepayment`: 融券現金償還
- `ShortSaleYesterdayBalance`: 融券前日餘額
- `ShortSaleTodayBalance`: 融券今日餘額
- `ShortSaleLimit`: 融券限額
- `offset`: 資券相抵
- `note`: 備註

**資料範圍**: 2001 年至今
**更新時間**: 每日 15:00-23:30

---

#### 2.2.4 融資融券 (整體市場)
**FinMind API**: `taiwan_stock_margin_purchase_short_sale_total`

```python
# 取得整體市場融資融券
data = dl.taiwan_stock_margin_purchase_short_sale_total(
    start_date='2024-01-01',
    end_date='2024-12-27'
)
```

---

#### 2.2.5 外資持股表
**FinMind API**: `taiwan_stock_shareholding`

```python
# 取得外資持股資料
data = dl.taiwan_stock_shareholding(
    stock_id='2330',
    start_date='2024-01-01',
    end_date='2024-12-27'
)
```

**資料欄位**:
- `date`: 日期
- `stock_id`: 股票代號
- `ForeignInvestmentRemainingShares`: 外資持股張數
- `ForeignInvestmentShareholding`: 外資持股比例
- `ForeignInvestmentUpperLimitShares`: 外資可投資張數上限

**資料範圍**: 2011 年至今

---

#### 2.2.6 股權分散表 (持股分級)
**FinMind API**: `taiwan_stock_holding_shares_per`

```python
# 取得股權分散表
data = dl.taiwan_stock_holding_shares_per(
    stock_id='2330',
    start_date='2024-01-01',
    end_date='2024-12-27'
)
```

**資料欄位**:
- `date`: 統計日期
- `stock_id`: 股票代號
- `HoldingSharesLevel`: 持股級距 (如 "1-999", "1000-5000")
- `people`: 該級距持股人數
- `percent`: 該級距持股佔比
- `unit`: 該級距持股張數

**持股級距**:
- 1-999股
- 1,000-5,000股
- 5,001-10,000股
- 10,001-15,000股
- 15,001-20,000股
- 20,001-30,000股
- 30,001-40,000股
- 40,001-50,000股
- 50,001-100,000股
- 100,001-200,000股
- 200,001-400,000股
- 400,001-600,000股
- 600,001-800,000股
- 800,001-1,000,000股
- 1,000,001股以上

**更新頻率**: 每週更新

---

#### 2.2.7 借券成交明細
**FinMind API**: `taiwan_stock_securities_lending`

```python
# 取得借券資料
data = dl.taiwan_stock_securities_lending(
    stock_id='2330',
    start_date='2024-01-01',
    end_date='2024-12-27'
)
```

**資料欄位**:
- `date`: 日期
- `stock_id`: 股票代號
- `Securities_Lending_Return`: 借券還券
- `Securities_Lending_Balance`: 借券餘額
- `Securities_Lending_Utilization_Rate`: 借券使用率

---

#### 2.2.8 八大行庫買賣表
**FinMind API**: `taiwan_stock_government_bank_buysell`

```python
# 取得八大行庫(官股券商)買賣資料
data = dl.taiwan_stock_government_bank_buysell(
    stock_id='2330',
    start_date='2024-01-01',
    end_date='2024-12-27'
)
```

**資料欄位**:
- `date`: 日期
- `stock_id`: 股票代號
- `buy`: 買進金額
- `sell`: 賣出金額
- `difference`: 買賣超金額

**八大行庫包含**: 台銀、土銀、合庫、一銀、華南、彰銀、兆豐、台企銀

---

#### 2.2.9 董監持股異動 (需確認)
**FinMind API**: 需要查證是否有提供

⚠️ **待確認**: FinMind 文件未明確列出董監持股 API，可能需要：
1. 進一步查詢 FinMind 完整文件
2. 或自行爬取 MOPS 公開資訊觀測站

---

### 2.3 主力進出資料 (40% FinMind + 60% 自建爬蟲)

#### 2.3.1 券商分點資料 (FinMind 提供)
**FinMind API**: `taiwan_stock_trading_daily_report`

```python
# 方法一: 查詢特定股票的所有分點資料
data = dl.taiwan_stock_trading_daily_report(
    stock_id='2330',
    start_date='2024-12-27',
    end_date='2024-12-27'
)

# 方法二: 查詢特定券商分點的交易資料
data = dl.taiwan_stock_trading_daily_report(
    broker_id='1160',  # 券商分點代號
    start_date='2024-12-27',
    end_date='2024-12-27'
)
```

**資料欄位**:
- `date`: 日期
- `stock_id`: 股票代號
- `broker_id`: 券商分點代號
- `buy`: 買進股數
- `sell`: 賣出股數
- `difference`: 買賣超

**限制**:
- ✅ 可以取得所有分點的交易資料
- ❌ **沒有自動排序功能**，需要自己計算前 15 大
- ❌ 資料量大，單一股票可能有數百個分點

---

#### 2.3.2 ⚠️ 需要自建爬蟲的主力資料

以下資料 **FinMind 無法提供**，需要自己爬取：

**1. 前 15 大分點排行**
- 資料來源: 券商軟體、財經網站 (如 Goodinfo、HiStock)
- 實作方式:
  - 選項 A: 從 FinMind 分點資料自己排序計算
  - 選項 B: 爬取財經網站的整理好的排行

**2. 買賣超券商家數統計**
- 實作方式: 從 FinMind 分點資料自己統計

---

## 三、FinMind 使用設定

### 3.1 安裝與認證

#### 安裝
```bash
pip install FinMind
```

#### 註冊與取得 API Token
1. 前往 https://finmindtrade.com/
2. 註冊帳號
3. 登入後到個人頁面取得 API Token

#### 認證方式
```python
from FinMind.data import DataLoader

# 方法一: 使用 Token (推薦)
dl = DataLoader()
dl.login_by_token(api_token='your_api_token_here')

# 方法二: 使用帳號密碼
dl = DataLoader()
dl.login(user_id='your_email', password='your_password')
```

---

### 3.2 FinMind 免費會員使用

**本專案使用 FinMind 免費會員**：
- ✅ 免費註冊，無需付費
- ✅ 提供所有日線級別的技術面與籌碼面資料
- ⚠️ 每日有 API 請求次數限制
- ⚠️ 單次請求可能有筆數限制

**使用建議**：
- 合理控制請求頻率（建議 0.5-1 秒間隔）
- 避免短時間內大量請求
- 分批收集歷史資料（例如按月或按季）

---

### 3.3 API 使用限制與注意事項

#### 請求頻率限制
- 免費會員每日有請求次數限制（具體數量見官方文件）
- 建議在請求間加入延遲（0.5-1秒）
- 大量資料建議分批收集，避免觸發限制

#### 資料延遲
- 大部分資料在**收盤後 15:00-23:30** 更新
- 非即時資料，適合日線級別的波段或長線分析

#### 歷史資料範圍
- 不同資料集的起始日期不同
- 大部分從 2001 年或更早開始

---

## 四、資料庫設計

### 4.1 資料表結構

#### 4.1.1 price_daily (每日價量)
```sql
CREATE TABLE price_daily (
    id SERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    turnover BIGINT,
    transaction_count INTEGER,
    spread DECIMAL(10,2),
    data_source VARCHAR(20) DEFAULT 'FinMind',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, trade_date)
);

CREATE INDEX idx_price_stock_date ON price_daily(stock_id, trade_date);
CREATE INDEX idx_price_date ON price_daily(trade_date);
```

---

#### 4.1.2 price_daily_adj (還原股價)
```sql
CREATE TABLE price_daily_adj (
    id SERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open_adj DECIMAL(10,2),
    high_adj DECIMAL(10,2),
    low_adj DECIMAL(10,2),
    close_adj DECIMAL(10,2),
    volume BIGINT,
    data_source VARCHAR(20) DEFAULT 'FinMind',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, trade_date)
);

CREATE INDEX idx_price_adj_stock_date ON price_daily_adj(stock_id, trade_date);
```

---

#### 4.1.3 institutional_investors (三大法人)
```sql
CREATE TABLE institutional_investors (
    id SERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    -- 外資
    foreign_buy BIGINT,
    foreign_sell BIGINT,
    foreign_net BIGINT,
    -- 投信
    trust_buy BIGINT,
    trust_sell BIGINT,
    trust_net BIGINT,
    -- 自營商 (合計)
    dealer_buy BIGINT,
    dealer_sell BIGINT,
    dealer_net BIGINT,
    -- 自營商 (避險)
    dealer_hedging_buy BIGINT,
    dealer_hedging_sell BIGINT,
    dealer_hedging_net BIGINT,
    -- 總計
    total_buy BIGINT,
    total_sell BIGINT,
    total_net BIGINT,
    data_source VARCHAR(20) DEFAULT 'FinMind',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, trade_date)
);

CREATE INDEX idx_institutional_stock_date ON institutional_investors(stock_id, trade_date);
CREATE INDEX idx_institutional_date ON institutional_investors(trade_date);
```

---

#### 4.1.4 margin_trading (融資融券)
```sql
CREATE TABLE margin_trading (
    id SERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    -- 融資
    margin_buy BIGINT,
    margin_sell BIGINT,
    margin_cash_repay BIGINT,
    margin_balance_prev BIGINT,
    margin_balance BIGINT,
    margin_limit BIGINT,
    -- 融券
    short_buy BIGINT,
    short_sell BIGINT,
    short_cash_repay BIGINT,
    short_balance_prev BIGINT,
    short_balance BIGINT,
    short_limit BIGINT,
    -- 資券相抵
    offset BIGINT,
    -- 使用率 (自行計算)
    margin_usage_rate DECIMAL(5,2),
    short_usage_rate DECIMAL(5,2),
    note VARCHAR(200),
    data_source VARCHAR(20) DEFAULT 'FinMind',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, trade_date)
);

CREATE INDEX idx_margin_stock_date ON margin_trading(stock_id, trade_date);
```

---

#### 4.1.5 foreign_shareholding (外資持股)
```sql
CREATE TABLE foreign_shareholding (
    id SERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    foreign_shares BIGINT,
    foreign_percent DECIMAL(5,2),
    foreign_limit_shares BIGINT,
    foreign_available_shares BIGINT,
    data_source VARCHAR(20) DEFAULT 'FinMind',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, trade_date)
);

CREATE INDEX idx_foreign_stock_date ON foreign_shareholding(stock_id, trade_date);
```

---

#### 4.1.6 holding_shares_distribution (股權分散表)
```sql
CREATE TABLE holding_shares_distribution (
    id SERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    level VARCHAR(50) NOT NULL,  -- 持股級距 (如 "1-999", "1000-5000")
    people_count INTEGER,        -- 該級距人數
    shares_count BIGINT,         -- 該級距持股張數
    percent DECIMAL(5,2),        -- 該級距持股佔比
    data_source VARCHAR(20) DEFAULT 'FinMind',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, trade_date, level)
);

CREATE INDEX idx_holding_stock_date ON holding_shares_distribution(stock_id, trade_date);
```

---

#### 4.1.7 securities_lending (借券資料)
```sql
CREATE TABLE securities_lending (
    id SERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    lending_return BIGINT,       -- 借券還券
    lending_balance BIGINT,      -- 借券餘額
    utilization_rate DECIMAL(5,2), -- 借券使用率
    data_source VARCHAR(20) DEFAULT 'FinMind',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, trade_date)
);

CREATE INDEX idx_lending_stock_date ON securities_lending(stock_id, trade_date);
```

---

#### 4.1.8 government_bank_trades (八大行庫)
```sql
CREATE TABLE government_bank_trades (
    id SERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    buy_amount BIGINT,
    sell_amount BIGINT,
    net_amount BIGINT,
    data_source VARCHAR(20) DEFAULT 'FinMind',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, trade_date)
);

CREATE INDEX idx_gov_bank_stock_date ON government_bank_trades(stock_id, trade_date);
```

---

#### 4.1.9 broker_trading (券商分點) - 選配
```sql
CREATE TABLE broker_trading (
    id SERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    broker_id VARCHAR(10) NOT NULL,  -- 券商分點代號
    buy BIGINT,
    sell BIGINT,
    net BIGINT,
    data_source VARCHAR(20) DEFAULT 'FinMind',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, trade_date, broker_id)
);

CREATE INDEX idx_broker_stock_date ON broker_trading(stock_id, trade_date);
CREATE INDEX idx_broker_date_net ON broker_trading(trade_date, net DESC);
```

**注意**: 分點資料量非常大，建議：
- 只儲存買賣超前 20 大的分點
- 或定期清理舊資料

---

#### 4.1.10 stock_info (股票基本資料)
```sql
CREATE TABLE stock_info (
    stock_id VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(100),
    market VARCHAR(10),  -- 'TWSE' 上市, 'TPEx' 上櫃
    industry VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    listed_date DATE,
    data_source VARCHAR(20) DEFAULT 'FinMind',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stock_market ON stock_info(market);
CREATE INDEX idx_stock_active ON stock_info(is_active);
```

---

### 4.2 資料庫選擇建議

| 資料庫 | 適用情境 | 優點 | 缺點 |
|--------|---------|------|------|
| **PostgreSQL** | 中大型專案 | 強大查詢、支援 JSON、成熟穩定 | 需安裝配置 |
| **SQLite** | 個人小型專案 | 零配置、輕量級 | 不適合多用戶、效能較低 |
| **ClickHouse** | 海量歷史資料分析 | 極快查詢速度 | 學習曲線較陡 |

**推薦**:
- 個人研究 → **SQLite**
- 專業分析 → **PostgreSQL**

---

## 五、專案結構

```
tw-stock-collector/
├── README.md
├── SPECIFICATION_FINMIND.md     # 本規格書
├── requirements.txt             # Python 套件
├── .env.example                 # 環境變數範例
├── .gitignore
│
├── config/
│   ├── config.yaml             # 主要配置
│   └── database.yaml           # 資料庫配置
│
├── src/
│   ├── __init__.py
│   │
│   ├── collectors/             # 資料收集器
│   │   ├── __init__.py
│   │   ├── base_collector.py        # 基礎收集器類別
│   │   ├── finmind_collector.py     # FinMind 收集器
│   │   ├── price_collector.py       # 價量資料收集
│   │   ├── institutional_collector.py  # 籌碼資料收集
│   │   └── custom_crawler.py        # 自定義爬蟲 (主力進出補充)
│   │
│   ├── models/                 # ORM 模型
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── price.py
│   │   ├── institutional.py
│   │   ├── margin.py
│   │   ├── shareholding.py
│   │   └── stock_info.py
│   │
│   ├── database/               # 資料庫操作
│   │   ├── __init__.py
│   │   ├── connection.py       # 資料庫連線
│   │   ├── crud.py            # CRUD 操作
│   │   └── init_db.sql        # 初始化 SQL
│   │
│   ├── utils/                  # 工具函數
│   │   ├── __init__.py
│   │   ├── date_utils.py      # 日期處理
│   │   ├── validator.py       # 資料驗證
│   │   ├── logger.py          # 日誌
│   │   └── stock_list.py      # 股票清單管理
│   │
│   ├── schedulers/             # 排程器
│   │   ├── __init__.py
│   │   ├── daily_scheduler.py  # 每日排程
│   │   └── weekly_scheduler.py # 每週排程
│   │
│   └── analyzers/              # 分析工具 (後續擴展)
│       ├── __init__.py
│       ├── technical.py        # 技術分析
│       └── chip.py            # 籌碼分析
│
├── scripts/                    # 執行腳本
│   ├── init_database.py       # 初始化資料庫
│   ├── backfill_history.py    # 歷史資料回補
│   ├── daily_collection.py    # 每日收集腳本
│   ├── test_finmind.py        # 測試 FinMind 連線
│   └── export_data.py         # 資料匯出
│
├── tests/                      # 單元測試
│   ├── __init__.py
│   ├── test_collectors.py
│   ├── test_database.py
│   └── test_utils.py
│
├── data/                       # 資料檔案
│   ├── stock_list.csv         # 股票清單
│   └── trading_calendar.csv   # 交易日曆
│
├── logs/                       # 日誌檔案
│   └── .gitkeep
│
└── notebooks/                  # Jupyter 筆記本 (分析用)
    └── exploratory_analysis.ipynb
```

---

## 六、核心套件需求

### requirements.txt

```txt
# FinMind
FinMind>=4.0.0

# 資料處理
pandas>=2.0.0
numpy>=1.24.0

# 資料庫
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0  # PostgreSQL
# 或使用 SQLite (Python 內建，無需安裝)

# 排程
APScheduler>=3.10.0

# 配置檔解析
PyYAML>=6.0

# 環境變數
python-dotenv>=1.0.0

# 日誌
loguru>=0.7.0

# HTTP 請求 (自定義爬蟲用)
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0

# 技術指標 (後續使用)
ta-lib>=0.4.0
pandas-ta>=0.3.0

# 測試
pytest>=7.4.0
pytest-cov>=4.1.0

# 資料視覺化 (選配)
matplotlib>=3.7.0
plotly>=5.14.0
```

---

## 七、配置檔範例

### 7.1 config/config.yaml

```yaml
# FinMind 設定
finmind:
  use_token: true
  # Token 從環境變數讀取，不要寫在這裡
  # api_token: 從 .env 讀取

  # 或使用帳號密碼
  # user_id: 從 .env 讀取
  # password: 從 .env 讀取

# 資料收集設定
collection:
  # 收集的資料類型
  data_types:
    - price_daily          # 每日價量
    - price_daily_adj      # 還原股價
    - institutional        # 三大法人
    - margin               # 融資融券
    - foreign_holding      # 外資持股
    - shareholding_dist    # 股權分散
    - securities_lending   # 借券
    - government_bank      # 八大行庫
    # - broker_trading     # 券商分點 (選配，資料量大)

  # 股票清單
  stock_list_source: "finmind"  # 或 "file"
  stock_list_file: "data/stock_list.csv"

  # 市場選擇
  markets:
    - "TWSE"  # 上市
    - "TPEx"  # 上櫃

  # 日期設定
  historical_start_date: "2020-01-01"

  # 請求設定
  request_interval: 0.5  # 每次請求間隔 (秒)
  retry_times: 3
  retry_delay: 5
  timeout: 30

# 排程設定
schedule:
  # 每日收集
  daily_collection:
    enabled: true
    time: "18:00"  # FinMind 資料約 17:30 後可用

  # 每週收集 (股權分散表)
  weekly_collection:
    enabled: true
    day: "saturday"
    time: "10:00"

# 資料庫設定
database:
  type: "postgresql"  # 或 "sqlite"
  # 詳細配置在 database.yaml

# 日誌設定
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "logs/collector.log"
  rotation: "10 MB"
  retention: "30 days"
  format: "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"

# 資料驗證
validation:
  enable_price_check: true
  max_price_change_percent: 20  # 單日漲跌幅超過 20% 發出警告
  min_volume: 0

# 通知設定 (選配)
notification:
  enabled: false
  # email, line, telegram 等
```

---

### 7.2 config/database.yaml

```yaml
# PostgreSQL 設定
postgresql:
  host: "localhost"
  port: 5432
  database: "tw_stock"
  # 帳密從環境變數讀取
  # user: 從 .env 讀取
  # password: 從 .env 讀取

  # 連線池設定
  pool_size: 5
  max_overflow: 10
  pool_timeout: 30
  pool_recycle: 3600

# SQLite 設定
sqlite:
  database_path: "data/tw_stock.db"

# 通用設定
common:
  echo: false  # 是否顯示 SQL 語句
  pool_pre_ping: true
```

---

### 7.3 .env.example

```bash
# FinMind 認證
FINMIND_API_TOKEN=your_api_token_here
# 或使用帳號密碼
# FINMIND_USER_ID=your_email@example.com
# FINMIND_PASSWORD=your_password

# 資料庫 (PostgreSQL)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tw_stock
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# 或使用 SQLite
# DB_PATH=data/tw_stock.db

# 環境
ENVIRONMENT=development  # development, production
```

**使用方式**:
1. 複製 `.env.example` 為 `.env`
2. 填入實際的憑證
3. 將 `.env` 加入 `.gitignore`

---

## 八、實作流程

### 階段一：環境建置與測試 (第 1-2 天)

**1. 安裝環境**
```bash
# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝套件
pip install -r requirements.txt
```

**2. 設定 FinMind**
```bash
# 複製環境變數範例
cp .env.example .env

# 編輯 .env，填入 FinMind Token
```

**3. 測試 FinMind 連線**
```bash
python scripts/test_finmind.py
```

---

### 階段二：資料庫建置 (第 3 天)

**1. 初始化資料庫**
```bash
python scripts/init_database.py
```

**2. 驗證資料表**
```bash
# 使用 PostgreSQL
psql -U your_user -d tw_stock -c "\dt"

# 或使用 SQLite
sqlite3 data/tw_stock.db ".tables"
```

---

### 階段三：基礎資料收集 (第 4-7 天)

**優先順序**:

1. **價量資料** (最重要)
   - `price_daily`
   - `price_daily_adj`

2. **籌碼資料**
   - `institutional_investors` (三大法人)
   - `margin_trading` (融資融券)

3. **其他籌碼資料**
   - `foreign_shareholding`
   - `holding_shares_distribution`
   - `securities_lending`
   - `government_bank_trades`

**實作步驟**:
```bash
# 1. 取得股票清單
python scripts/get_stock_list.py

# 2. 回補歷史資料 (從 2020-01-01 開始)
python scripts/backfill_history.py --start-date 2020-01-01

# 3. 驗證資料
python scripts/validate_data.py
```

---

### 階段四：自動化排程 (第 8-10 天)

**1. 設定每日排程**
```bash
# 測試每日收集腳本
python scripts/daily_collection.py

# 使用 cron (Linux/Mac)
crontab -e

# 加入以下行 (每天 18:00 執行)
0 18 * * 1-5 /path/to/venv/bin/python /path/to/scripts/daily_collection.py
```

**2. 設定每週排程**
```bash
# 每週六 10:00 收集股權分散表
0 10 * * 6 /path/to/venv/bin/python /path/to/scripts/weekly_collection.py
```

**或使用 APScheduler** (推薦):
```python
# 在 src/schedulers/daily_scheduler.py 中實作
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=18, minute=0)
def daily_job():
    # 執行每日收集
    pass

scheduler.start()
```

---

### 階段五：資料驗證與監控 (第 11-14 天)

**1. 建立資料品質檢查**
- 檢查資料完整性
- 檢查異常值
- 比對筆數

**2. 建立監控儀表板** (選配)
- 使用 Grafana + PostgreSQL
- 或簡單的 Jupyter Notebook

**3. 錯誤通知機制**
- 郵件通知
- Line Notify
- Telegram Bot

---

### 階段六：擴展功能 (選配)

**1. 主力進出補充爬蟲**
- 爬取 Goodinfo、HiStock 等網站的主力分點排行
- 或從 FinMind 分點資料自行計算排行

**2. 技術指標計算**
- 使用 ta-lib 或 pandas-ta
- 計算 MA、MACD、RSI、KD 等指標

**3. 籌碼分析指標**
- 外資連續買超天數
- 融資使用率變化
- 主力集中度

**4. 資料 API**
- 使用 FastAPI 建立 REST API
- 供其他應用或前端使用

---

## 九、FinMind 收集器範例程式碼

### 9.1 基礎收集器

```python
# src/collectors/finmind_collector.py

from FinMind.data import DataLoader
from typing import Optional, List
import pandas as pd
from datetime import datetime, timedelta
import time
from loguru import logger

class FinMindCollector:
    """FinMind 資料收集器基礎類別"""

    def __init__(self, api_token: Optional[str] = None):
        self.dl = DataLoader()
        if api_token:
            self.dl.login_by_token(api_token=api_token)
            logger.info("FinMind 已使用 Token 登入")
        else:
            logger.warning("FinMind 未登入，使用免費額度")

    def get_stock_list(self, market: str = 'ALL') -> pd.DataFrame:
        """
        取得股票清單

        Args:
            market: 'TWSE' (上市), 'TPEx' (上櫃), 'ALL' (全部)

        Returns:
            DataFrame with columns: stock_id, stock_name, industry, market
        """
        logger.info(f"取得股票清單: {market}")

        # 上市股票
        twse = self.dl.taiwan_stock_info()
        twse['market'] = 'TWSE'

        # 上櫃股票
        tpex = self.dl.taiwan_stock_info(data_source='TPEx')
        tpex['market'] = 'TPEx'

        # 合併
        all_stocks = pd.concat([twse, tpex], ignore_index=True)

        if market == 'TWSE':
            return twse
        elif market == 'TPEx':
            return tpex
        else:
            return all_stocks

    def collect_with_retry(self,
                          func,
                          max_retries: int = 3,
                          delay: int = 5,
                          **kwargs) -> Optional[pd.DataFrame]:
        """
        帶重試機制的資料收集

        Args:
            func: FinMind API 函數
            max_retries: 最大重試次數
            delay: 重試延遲 (秒)
            **kwargs: API 參數

        Returns:
            DataFrame 或 None
        """
        for attempt in range(max_retries):
            try:
                data = func(**kwargs)
                if data is not None and not data.empty:
                    return data
                else:
                    logger.warning(f"嘗試 {attempt + 1}/{max_retries}: 資料為空")
            except Exception as e:
                logger.error(f"嘗試 {attempt + 1}/{max_retries} 失敗: {e}")

            if attempt < max_retries - 1:
                logger.info(f"等待 {delay} 秒後重試...")
                time.sleep(delay)

        logger.error(f"收集失敗，已重試 {max_retries} 次")
        return None
```

---

### 9.2 價量資料收集器

```python
# src/collectors/price_collector.py

from .finmind_collector import FinMindCollector
import pandas as pd
from datetime import datetime
from loguru import logger

class PriceCollector(FinMindCollector):
    """價量資料收集器"""

    def collect_daily_price(self,
                           stock_id: str,
                           start_date: str,
                           end_date: str) -> pd.DataFrame:
        """
        收集每日價量資料

        Args:
            stock_id: 股票代號
            start_date: 開始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)

        Returns:
            DataFrame
        """
        logger.info(f"收集價量資料: {stock_id} ({start_date} ~ {end_date})")

        data = self.collect_with_retry(
            self.dl.taiwan_stock_daily,
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )

        if data is not None:
            # 欄位對應與處理
            data = data.rename(columns={
                'Trading_Volume': 'volume',
                'Trading_money': 'turnover',
                'Trading_turnover': 'transaction_count',
                'max': 'high',
                'min': 'low'
            })

            # 選取需要的欄位
            columns = ['date', 'stock_id', 'open', 'high', 'low', 'close',
                      'volume', 'turnover', 'transaction_count', 'spread']
            data = data[columns]

            logger.success(f"成功收集 {len(data)} 筆資料")

        return data

    def collect_daily_price_adj(self,
                               stock_id: str,
                               start_date: str,
                               end_date: str) -> pd.DataFrame:
        """收集還原股價"""
        logger.info(f"收集還原股價: {stock_id}")

        data = self.collect_with_retry(
            self.dl.taiwan_stock_daily_adj,
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )

        return data

    def batch_collect_daily_price(self,
                                  stock_ids: list,
                                  start_date: str,
                                  end_date: str,
                                  interval: float = 0.5) -> pd.DataFrame:
        """
        批次收集多檔股票的價量資料

        Args:
            stock_ids: 股票代號列表
            start_date: 開始日期
            end_date: 結束日期
            interval: 每次請求間隔 (秒)

        Returns:
            合併後的 DataFrame
        """
        all_data = []

        for i, stock_id in enumerate(stock_ids, 1):
            logger.info(f"進度: {i}/{len(stock_ids)} - {stock_id}")

            data = self.collect_daily_price(stock_id, start_date, end_date)
            if data is not None:
                all_data.append(data)

            # 請求間隔
            if i < len(stock_ids):
                time.sleep(interval)

        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            logger.success(f"批次收集完成，共 {len(result)} 筆資料")
            return result
        else:
            logger.warning("批次收集失敗，無資料")
            return pd.DataFrame()
```

---

### 9.3 籌碼資料收集器

```python
# src/collectors/institutional_collector.py

from .finmind_collector import FinMindCollector
import pandas as pd
from loguru import logger

class InstitutionalCollector(FinMindCollector):
    """籌碼資料收集器"""

    def collect_institutional_investors(self,
                                       stock_id: str,
                                       start_date: str,
                                       end_date: str) -> pd.DataFrame:
        """收集三大法人資料"""
        logger.info(f"收集三大法人: {stock_id}")

        data = self.collect_with_retry(
            self.dl.taiwan_stock_institutional_investors,
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )

        if data is not None:
            # 欄位重新命名
            data = data.rename(columns={
                'ForeignInvestment_buy': 'foreign_buy',
                'ForeignInvestment_sell': 'foreign_sell',
                'ForeignInvestment_difference': 'foreign_net',
                'Investment_Trust_buy': 'trust_buy',
                'Investment_Trust_sell': 'trust_sell',
                'Investment_Trust_difference': 'trust_net',
                'Dealer_buy': 'dealer_buy',
                'Dealer_sell': 'dealer_sell',
                'Dealer_difference': 'dealer_net',
                'Dealer_Hedging_buy': 'dealer_hedging_buy',
                'Dealer_Hedging_sell': 'dealer_hedging_sell',
                'Dealer_Hedging_difference': 'dealer_hedging_net',
                'buy': 'total_buy',
                'sell': 'total_sell',
                'difference': 'total_net'
            })

        return data

    def collect_margin_trading(self,
                              stock_id: str,
                              start_date: str,
                              end_date: str) -> pd.DataFrame:
        """收集融資融券資料"""
        logger.info(f"收集融資融券: {stock_id}")

        data = self.collect_with_retry(
            self.dl.taiwan_stock_margin_purchase_short_sale,
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )

        if data is not None:
            # 計算使用率
            data['margin_usage_rate'] = (
                data['MarginPurchaseTodayBalance'] / data['MarginPurchaseLimit'] * 100
            ).round(2)

            data['short_usage_rate'] = (
                data['ShortSaleTodayBalance'] / data['ShortSaleLimit'] * 100
            ).round(2)

        return data

    def collect_foreign_shareholding(self,
                                    stock_id: str,
                                    start_date: str,
                                    end_date: str) -> pd.DataFrame:
        """收集外資持股"""
        logger.info(f"收集外資持股: {stock_id}")

        data = self.collect_with_retry(
            self.dl.taiwan_stock_shareholding,
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )

        return data

    def collect_holding_distribution(self,
                                    stock_id: str,
                                    start_date: str,
                                    end_date: str) -> pd.DataFrame:
        """收集股權分散表"""
        logger.info(f"收集股權分散: {stock_id}")

        data = self.collect_with_retry(
            self.dl.taiwan_stock_holding_shares_per,
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )

        return data
```

---

## 十、每日收集腳本範例

```python
# scripts/daily_collection.py

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger

# 加入專案路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.collectors.price_collector import PriceCollector
from src.collectors.institutional_collector import InstitutionalCollector
from src.database.connection import get_db_session
from src.database.crud import save_price_data, save_institutional_data
from src.utils.stock_list import get_active_stock_list
from src.utils.date_utils import is_trading_day, get_last_trading_day

# 載入環境變數
load_dotenv()

def main():
    """每日資料收集主程式"""

    # 設定日誌
    logger.add(
        "logs/daily_collection_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )

    logger.info("=" * 50)
    logger.info("開始每日資料收集")
    logger.info("=" * 50)

    # 檢查今天是否為交易日
    today = datetime.now().date()
    if not is_trading_day(today):
        logger.warning(f"{today} 非交易日，跳過收集")
        return

    # 取得收集日期 (昨天或最後交易日)
    collection_date = get_last_trading_day()
    date_str = collection_date.strftime('%Y-%m-%d')

    logger.info(f"收集日期: {date_str}")

    # 初始化收集器
    api_token = os.getenv('FINMIND_API_TOKEN')
    price_collector = PriceCollector(api_token=api_token)
    inst_collector = InstitutionalCollector(api_token=api_token)

    # 取得股票清單
    logger.info("載入股票清單...")
    stock_list = get_active_stock_list()
    logger.info(f"共 {len(stock_list)} 檔股票")

    # 資料庫連線
    session = get_db_session()

    success_count = 0
    fail_count = 0

    try:
        for i, stock_id in enumerate(stock_list, 1):
            logger.info(f"[{i}/{len(stock_list)}] 處理 {stock_id}")

            try:
                # 1. 收集價量資料
                price_data = price_collector.collect_daily_price(
                    stock_id=stock_id,
                    start_date=date_str,
                    end_date=date_str
                )

                if price_data is not None and not price_data.empty:
                    save_price_data(session, price_data)

                # 2. 收集三大法人
                inst_data = inst_collector.collect_institutional_investors(
                    stock_id=stock_id,
                    start_date=date_str,
                    end_date=date_str
                )

                if inst_data is not None and not inst_data.empty:
                    save_institutional_data(session, inst_data)

                # 3. 收集融資融券
                margin_data = inst_collector.collect_margin_trading(
                    stock_id=stock_id,
                    start_date=date_str,
                    end_date=date_str
                )

                if margin_data is not None and not margin_data.empty:
                    save_margin_data(session, margin_data)

                success_count += 1

            except Exception as e:
                logger.error(f"{stock_id} 收集失敗: {e}")
                fail_count += 1

            # 請求間隔
            if i < len(stock_list):
                time.sleep(0.5)

        # 提交資料庫
        session.commit()
        logger.success("資料庫提交成功")

    except Exception as e:
        logger.error(f"收集過程發生錯誤: {e}")
        session.rollback()

    finally:
        session.close()

    # 統計
    logger.info("=" * 50)
    logger.info(f"收集完成")
    logger.info(f"成功: {success_count} 檔")
    logger.info(f"失敗: {fail_count} 檔")
    logger.info("=" * 50)

if __name__ == '__main__':
    main()
```

---

## 十一、後續擴展：主力進出補充爬蟲

由於 FinMind 的分點資料沒有自動排序，如果你需要「前 15 大分點」，有兩個選項：

### 選項 A: 從 FinMind 分點資料自行計算

```python
# src/analyzers/broker_ranking.py

from src.collectors.finmind_collector import FinMindCollector
import pandas as pd

class BrokerRankingAnalyzer:
    """主力分點排行分析"""

    def __init__(self, api_token):
        self.collector = FinMindCollector(api_token)

    def get_top_brokers(self, stock_id: str, date: str, top_n: int = 15):
        """
        計算前 N 大買超/賣超分點

        Args:
            stock_id: 股票代號
            date: 日期
            top_n: 前幾名

        Returns:
            tuple: (top_buyers, top_sellers)
        """
        # 取得所有分點資料
        data = self.collector.dl.taiwan_stock_trading_daily_report(
            stock_id=stock_id,
            start_date=date,
            end_date=date
        )

        if data is None or data.empty:
            return None, None

        # 計算買賣超
        data['net'] = data['buy'] - data['sell']

        # 前 15 大買超
        top_buyers = data.nlargest(top_n, 'net')

        # 前 15 大賣超
        top_sellers = data.nsmallest(top_n, 'net')

        return top_buyers, top_sellers
```

**優點**:
- 使用 FinMind 官方資料，穩定
- 不需要額外爬蟲

**缺點**:
- 資料量大，每次需下載所有分點
- API 請求次數消耗較多

---

### 選項 B: 爬取財經網站整理好的排行

常見網站：
- **Goodinfo! 台灣股市資訊網**: https://goodinfo.tw
- **HiStock 嗨投資**: https://histock.tw
- **玩股網**: https://www.wantgoo.com

**範例爬蟲** (Goodinfo):

```python
# src/collectors/custom_crawler.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
from loguru import logger

class GoodinfoTopBrokerCrawler:
    """Goodinfo 主力分點爬蟲"""

    BASE_URL = "https://goodinfo.tw/tw/StockBroker.asp"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_top_brokers(self, stock_id: str, date: str = None):
        """
        爬取 Goodinfo 主力分點排行

        Args:
            stock_id: 股票代號
            date: 日期 (若無則取最新)

        Returns:
            DataFrame
        """
        params = {
            'STOCK_ID': stock_id
        }

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'lxml')

            # 解析 HTML 表格
            # (需根據實際網站結構調整)
            table = soup.find('table', {'class': 'solid_1_padding_4'})

            if table:
                df = pd.read_html(str(table))[0]
                logger.success(f"成功爬取 {stock_id} 主力分點")
                return df
            else:
                logger.warning(f"{stock_id} 未找到分點資料")
                return None

        except Exception as e:
            logger.error(f"爬取失敗: {e}")
            return None
```

**注意**:
- 爬蟲可能因網站改版而失效
- 需遵守網站的 robots.txt 與服務條款
- 建議加入請求間隔，避免被封鎖

---

## 十二、常見問題 FAQ

### Q1: FinMind 免費會員的 API 請求限制是多少？
A: 免費會員每日有請求次數限制，具體數量請參考官方文件。建議分批收集資料，並在請求間加入適當延遲（0.5-1秒）。

### Q2: 如何處理除權息的股價調整？
A: 使用 FinMind 的 `taiwan_stock_daily_adj` API，會自動調整除權息。

### Q3: 資料更新時間是何時？
A: FinMind 大部分資料在每日 **17:30 - 23:30** 之間更新，建議在 **18:00 後**開始收集。

### Q4: 如何取得歷史資料？
A: 使用腳本 `scripts/backfill_history.py`，指定起始日期即可批次回補。

### Q5: 分點資料量太大怎麼辦？
A: 建議只儲存買賣超前 20 名的分點，或定期清理舊資料。

### Q6: 如何確認資料正確性？
A: 可以隨機抽樣幾檔股票，與證交所官網或其他來源比對。

### Q7: 董監持股異動 FinMind 有提供嗎？
A: 需要進一步查證 FinMind 官方文件，如果沒有則需自行爬取 MOPS。

---

## 十三、參考資源

### 官方文件
- [FinMind 官網](https://finmindtrade.com/)
- [FinMind GitHub](https://github.com/FinMind/FinMind)
- [FinMind 文件 - 技術面](https://finmind.github.io/tutor/TaiwanMarket/Technical/)
- [FinMind 文件 - 籌碼面](https://finmind.github.io/tutor/TaiwanMarket/Chip/)

### 台股官方來源
- [台灣證券交易所](https://www.twse.com.tw)
- [證券櫃買中心](https://www.tpex.org.tw)
- [公開資訊觀測站](https://mops.twse.com.tw)

### 社群資源
- FinMind Discord 社群
- PTT Stock 版
- Mobile01 投資理財版

---

## 附錄

### A. FinMind 免費會員 API 快速對照表

| 需求 | FinMind API | 免費會員可用 | 備註 |
|------|------------|-------------|------|
| 每日價量 | `taiwan_stock_daily` | ✅ 是 | 完整支援 |
| 還原股價 | `taiwan_stock_daily_adj` | ✅ 是 | 完整支援 |
| 三大法人 | `taiwan_stock_institutional_investors` | ✅ 是 | 完整支援 |
| 融資融券 | `taiwan_stock_margin_purchase_short_sale` | ✅ 是 | 完整支援 |
| 外資持股 | `taiwan_stock_shareholding` | ✅ 是 | 完整支援 |
| 股權分散 | `taiwan_stock_holding_shares_per` | ✅ 是 | 完整支援 |
| 借券 | `taiwan_stock_securities_lending` | ✅ 是 | 完整支援 |
| 八大行庫 | `taiwan_stock_government_bank_buysell` | ✅ 是 | 完整支援 |
| 分點資料 | `taiwan_stock_trading_daily_report` | ✅ 是 | 無排序，需自行處理 |
| 前15大分點 | - | ❌ 否 | 需自行計算或爬蟲 |
| 分K線資料 | `taiwan_stock_kbar` | ❌ 否 | 需付費會員（本專案不使用）|

### B. 資料收集檢查清單

**上線前檢查**:
- [ ] FinMind Token 設定正確
- [ ] 資料庫連線正常
- [ ] 所有資料表已建立
- [ ] 股票清單已更新
- [ ] 日誌目錄已建立
- [ ] 環境變數已設定 (.env)
- [ ] 排程腳本測試成功

**每日檢查**:
- [ ] 排程是否正常執行
- [ ] 資料筆數是否正常
- [ ] 有無錯誤日誌
- [ ] 資料庫容量是否足夠

**每週檢查**:
- [ ] 股權分散表是否更新
- [ ] 清理舊日誌
- [ ] 資料備份

---

**文件版本**: 2.1 (FinMind 免費版)
**最後更新**: 2025-12-28
**維護者**: Jason Huang

**版本更新說明**:
- v2.1: 移除所有付費功能，專注於 FinMind 免費會員可用的功能
- v2.0: 初版 FinMind 規格書

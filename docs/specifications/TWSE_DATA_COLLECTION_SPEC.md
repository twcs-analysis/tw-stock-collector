# 台股資料收集系統規格書

## 專案概述
建立一個完整的台股資料收集系統，用於籌碼面與技術面分析。

---

## 一、資料需求分析

### 1.1 技術面資料

#### 1.1.1 基本價量資料
- **資料項目**
  - 日期 (Date)
  - 股票代號 (Stock Code)
  - 股票名稱 (Stock Name)
  - 開盤價 (Open)
  - 最高價 (High)
  - 最低價 (Low)
  - 收盤價 (Close)
  - 成交量 (Volume)
  - 成交金額 (Turnover)
  - 成交筆數 (Transaction Count)

- **資料來源**
  - 台灣證券交易所 (TWSE) - 上市股票
  - 證券櫃買中心 (TPEx) - 上櫃股票

- **更新頻率**
  - 每日盤後更新（15:00 後）

#### 1.1.2 技術指標基礎資料
為計算技術指標，需收集：
- 調整後價格（考慮除權息）
- 歷史波動率計算用資料
- 至少 250 個交易日的歷史資料（用於年線計算）

---

### 1.2 籌碼面資料

#### 1.2.1 三大法人買賣超
- **資料項目**
  - 日期
  - 股票代號
  - 外資及陸資買賣超股數
  - 外資及陸資買賣超金額
  - 投信買賣超股數
  - 投信買賣超金額
  - 自營商買賣超股數（合計）
  - 自營商買賣超金額（合計）
  - 自營商（自行買賣）
  - 自營商（避險）
  - 三大法人買賣超合計

- **資料來源**
  - 台灣證券交易所 - 三大法人買賣超日報
  - API: `https://www.twse.com.tw/fund/T86`

#### 1.2.2 融資融券資料
- **資料項目**
  - 日期
  - 股票代號
  - 融資買進
  - 融資賣出
  - 融資現金償還
  - 融資前日餘額
  - 融資今日餘額
  - 融資限額
  - 融券買進
  - 融券賣出
  - 融券現金償還
  - 融券前日餘額
  - 融券今日餘額
  - 融券限額
  - 資券相抵
  - 融資使用率
  - 融券使用率

- **資料來源**
  - 台灣證券交易所 - 融資融券彙總資料
  - API: `https://www.twse.com.tw/exchangeReport/MI_MARGN`

#### 1.2.3 主力進出分析資料
- **資料項目**
  - 日期
  - 股票代號
  - 分點進出明細（前15大分點）
  - 買賣超券商家數
  - 大額交易資訊

- **資料來源**
  - 需付費資料來源或爬蟲
  - 台灣證券交易所有提供部分資訊

#### 1.2.4 董監持股與內部人交易
- **資料項目**
  - 申報日期
  - 股票代號
  - 董監事姓名
  - 職稱
  - 目前持股
  - 本次異動股數
  - 異動原因
  - 異動後持股

- **資料來源**
  - 公開資訊觀測站
  - API: `https://mops.twse.com.tw/`

#### 1.2.5 借券資料
- **資料項目**
  - 日期
  - 股票代號
  - 借券賣出餘額
  - 借券賣出當日餘額增減
  - 借券賣出餘額占發行量比率

- **資料來源**
  - 證券櫃買中心 - 借券資料

#### 1.2.6 外資持股比例
- **資料項目**
  - 日期
  - 股票代號
  - 外資持股比例
  - 外資持股張數
  - 外資可投資張數
  - 外資尚可投資張數

- **資料來源**
  - 台灣證券交易所

#### 1.2.7 股權分散表
- **資料項目**
  - 統計日期
  - 股票代號
  - 各級別持股人數分布
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

- **資料來源**
  - 台灣證券交易所 - 每週更新
  - API: `https://www.twse.com.tw/exchangeReport/TWT38U`

---

## 二、資料來源與取得方式

### 2.1 官方資料來源

#### 2.1.1 台灣證券交易所 (TWSE)
- **網站**: https://www.twse.com.tw
- **主要 API 端點**:
  ```
  每日收盤行情: /exchangeReport/MI_INDEX
  個股日成交資訊: /exchangeReport/STOCK_DAY
  三大法人買賣超: /fund/T86
  融資融券: /exchangeReport/MI_MARGN
  股權分散表: /exchangeReport/TWT38U
  ```
- **格式**: JSON / CSV
- **限制**:
  - 單次查詢有筆數限制
  - 需注意請求頻率，避免被封鎖
  - 建議每次請求間隔 3-5 秒

#### 2.1.2 證券櫃買中心 (TPEx)
- **網站**: https://www.tpex.org.tw
- **主要 API 端點**:
  ```
  上櫃股票收盤行情: /web/stock/aftertrading/daily_close_quotes/stk_quote_result.php
  三大法人買賣超: /web/stock/3insti/daily_trade/3itrade_hedge_result.php
  融資融券: /web/stock/margin_trading/margin_balance/margin_bal_result.php
  ```
- **格式**: JSON
- **限制**: 與 TWSE 類似

#### 2.1.3 公開資訊觀測站 (MOPS)
- **網站**: https://mops.twse.com.tw
- **資料類型**:
  - 董監事持股異動
  - 內部人交易
  - 月營收
  - 財報資訊
- **格式**: HTML / JSON
- **限制**: 部分資料需解析 HTML

### 2.2 第三方資料來源（選用）

#### 2.2.1 Python 套件
1. **FinMind**
   - GitHub: https://github.com/FinMindTrade/FinMind
   - 優點: 整合多種台股資料，API 簡單易用
   - 限制: 部分功能需註冊 API Token
   - 安裝: `pip install FinMind`

2. **twstock**
   - GitHub: https://github.com/mlouielu/twstock
   - 優點: 輕量級，專注台股基本資料
   - 限制: 更新頻率較慢
   - 安裝: `pip install twstock`

3. **yfinance**
   - 優點: 國際通用，資料穩定
   - 限制: 台股資料較不完整
   - 安裝: `pip install yfinance`

#### 2.2.2 付費資料來源
- XQ 全球贏家
- CMoney
- 各券商提供的 API

---

## 三、資料收集策略

### 3.1 收集頻率

| 資料類型 | 更新頻率 | 收集時間 | 保留期限 |
|---------|---------|---------|---------|
| 每日價量資料 | 每日 | 15:30 後 | 永久 |
| 三大法人 | 每日 | 15:30 後 | 永久 |
| 融資融券 | 每日 | 15:30 後 | 永久 |
| 股權分散表 | 每週 | 週六 | 永久 |
| 董監持股 | 即時監控 | 每日 18:00 | 永久 |
| 借券資料 | 每日 | 15:30 後 | 永久 |

### 3.2 資料儲存架構

#### 3.2.1 建議使用的資料庫
1. **PostgreSQL** (推薦)
   - 優點: 強大的查詢能力、支援時間序列、JSON 欄位
   - 適合: 結構化資料與複雜查詢

2. **ClickHouse**
   - 優點: 專為時間序列設計、查詢速度極快
   - 適合: 大量歷史資料分析

3. **SQLite**
   - 優點: 輕量級、無需額外安裝
   - 適合: 小型專案或個人使用

#### 3.2.2 資料表結構建議

**price_daily (每日價量)**
```sql
CREATE TABLE price_daily (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    turnover BIGINT,
    transaction_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, trade_date)
);
CREATE INDEX idx_price_stock_date ON price_daily(stock_code, trade_date);
```

**institutional_investors (三大法人)**
```sql
CREATE TABLE institutional_investors (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    foreign_buy BIGINT,
    foreign_sell BIGINT,
    foreign_net BIGINT,
    investment_trust_buy BIGINT,
    investment_trust_sell BIGINT,
    investment_trust_net BIGINT,
    dealer_buy BIGINT,
    dealer_sell BIGINT,
    dealer_net BIGINT,
    total_net BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, trade_date)
);
CREATE INDEX idx_institutional_stock_date ON institutional_investors(stock_code, trade_date);
```

**margin_trading (融資融券)**
```sql
CREATE TABLE margin_trading (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    margin_buy BIGINT,
    margin_sell BIGINT,
    margin_cash_repay BIGINT,
    margin_balance_prev BIGINT,
    margin_balance BIGINT,
    margin_limit BIGINT,
    short_buy BIGINT,
    short_sell BIGINT,
    short_cash_repay BIGINT,
    short_balance_prev BIGINT,
    short_balance BIGINT,
    short_limit BIGINT,
    margin_usage_rate DECIMAL(5,2),
    short_usage_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, trade_date)
);
CREATE INDEX idx_margin_stock_date ON margin_trading(stock_code, trade_date);
```

### 3.3 資料收集流程

```
1. 初始化
   ├── 載入股票清單（上市+上櫃）
   ├── 檢查資料庫連線
   └── 設定日期範圍

2. 每日資料收集 (15:30 執行)
   ├── 收集價量資料
   │   ├── TWSE 上市股票
   │   └── TPEx 上櫃股票
   ├── 收集三大法人資料
   ├── 收集融資融券資料
   ├── 收集借券資料
   └── 資料驗證與儲存

3. 每週資料收集 (週六執行)
   └── 收集股權分散表

4. 錯誤處理
   ├── 網路錯誤重試機制（最多3次）
   ├── 資料異常記錄
   └── 通知管理員
```

---

## 四、技術實作建議

### 4.1 開發語言選擇
- **Python** (強烈推薦)
  - 豐富的資料分析套件
  - 現成的台股資料收集工具
  - 社群支援完善

### 4.2 核心套件需求

```python
# 資料收集
requests          # HTTP 請求
beautifulsoup4    # HTML 解析
selenium          # 動態網頁（如需要）

# 資料處理
pandas            # 資料處理與分析
numpy             # 數值計算

# 資料庫
psycopg2-binary   # PostgreSQL 連接器
sqlalchemy        # ORM 框架

# 任務排程
schedule          # 簡單排程
APScheduler       # 進階排程

# 第三方資料源
FinMind           # 台股資料 API
twstock           # 台股資料

# 技術指標計算（後續使用）
ta-lib            # 技術指標庫
pandas-ta         # Pandas 技術指標
```

### 4.3 專案結構建議

```
tw-stock-collector/
├── README.md
├── SPECIFICATION.md          # 本規格書
├── requirements.txt          # Python 套件依賴
├── config/
│   ├── config.yaml          # 配置檔
│   └── database.yaml        # 資料庫配置
├── src/
│   ├── collectors/          # 資料收集器
│   │   ├── __init__.py
│   │   ├── base_collector.py
│   │   ├── twse_collector.py      # 台灣證交所
│   │   ├── tpex_collector.py      # 櫃買中心
│   │   └── mops_collector.py      # 公開資訊觀測站
│   ├── models/              # 資料模型
│   │   ├── __init__.py
│   │   ├── price.py
│   │   ├── institutional.py
│   │   └── margin.py
│   ├── database/            # 資料庫操作
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── crud.py
│   ├── utils/               # 工具函數
│   │   ├── __init__.py
│   │   ├── date_utils.py
│   │   ├── validator.py
│   │   └── logger.py
│   └── schedulers/          # 排程器
│       ├── __init__.py
│       └── daily_job.py
├── scripts/                 # 執行腳本
│   ├── init_db.py          # 初始化資料庫
│   ├── backfill.py         # 歷史資料回補
│   └── daily_collect.py    # 每日收集
├── tests/                   # 測試
│   └── test_collectors.py
└── logs/                    # 日誌檔案
```

### 4.4 配置檔範例

**config/config.yaml**
```yaml
# 資料收集設定
collection:
  # 請求設定
  request_timeout: 30
  retry_times: 3
  retry_delay: 5

  # 請求間隔（秒）
  request_interval: 3

  # 股票清單
  stock_list_file: "data/stock_list.csv"

  # 日期範圍
  start_date: "2020-01-01"

# 排程設定
schedule:
  daily_collection_time: "15:30"
  weekly_collection_day: "saturday"
  weekly_collection_time: "09:00"

# 日誌設定
logging:
  level: "INFO"
  file: "logs/collector.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5
```

**config/database.yaml**
```yaml
postgresql:
  host: "localhost"
  port: 5432
  database: "tw_stock"
  user: "your_user"
  password: "your_password"
```

---

## 五、資料品質控制

### 5.1 資料驗證規則
- 價格不可為負數
- 成交量不可為負數
- 日期必須為交易日
- 必要欄位不可為空
- 數值範圍檢查（如：漲跌幅不超過10%）

### 5.2 異常處理
- 資料缺失記錄到日誌
- 自動重試機制
- 人工審核機制

### 5.3 資料完整性檢查
- 每日檢查收集筆數是否合理
- 交叉比對不同資料來源
- 定期備份

---

## 六、效能考量

### 6.1 爬蟲禮儀
- 遵守 robots.txt
- 合理的請求間隔（3-5秒）
- 使用適當的 User-Agent
- 避免在交易時段高頻請求

### 6.2 平行處理
- 可考慮多執行緒/多進程收集不同股票
- 但要注意 API 限制

### 6.3 快取機制
- 已收集的資料不重複抓取
- 股票清單快取（每日更新）

---

## 七、後續擴展規劃

### 7.1 近期目標
1. 完成基礎價量資料收集
2. 完成三大法人資料收集
3. 完成融資融券資料收集
4. 建立每日自動排程

### 7.2 中期目標
1. 加入技術指標計算模組
2. 加入籌碼分析模組
3. 建立資料視覺化介面
4. 開發 API 供其他應用使用

### 7.3 長期目標
1. 機器學習預測模型
2. 即時資料收集
3. 多市場支援（如美股、港股）
4. 自動化交易策略回測

---

## 八、風險與注意事項

### 8.1 法律風險
- 確保資料使用符合各網站的服務條款
- 個人使用通常無問題，商業使用需注意版權

### 8.2 技術風險
- 網站改版可能導致爬蟲失效
- API 格式變更
- IP 被封鎖

### 8.3 資料風險
- 資料可能有誤或延遲
- 除權息需調整
- 盤中撮合異常

---

## 九、成本估算

### 9.1 開發成本
- 伺服器/VPS: 約 $5-20/月（視需求）
- 資料庫: 可使用免費的 PostgreSQL
- 開發時間: 約 2-4 週（視功能完整度）

### 9.2 維護成本
- 每週檢查系統運行狀態: 約 1-2 小時
- 每月更新與優化: 約 4-8 小時

---

## 十、參考資源

### 10.1 官方文件
- [台灣證券交易所統計資料](https://www.twse.com.tw/zh/page/trading/exchange/FMTQIK.html)
- [證券櫃買中心](https://www.tpex.org.tw/web/index.php)
- [公開資訊觀測站](https://mops.twse.com.tw/)

### 10.2 開源專案
- [FinMind](https://github.com/FinMindTrade/FinMind)
- [twstock](https://github.com/mlouielu/twstock)
- [台股歷史資料爬蟲](https://github.com/Asoul/tsrtc)

### 10.3 學習資源
- [Python 金融數據分析](https://www.books.com.tw/products/0010822932)
- [台股程式交易：從零開始](https://www.youtube.com/playlist?list=PLXuB3FqbWPXXJv0DUqL6RFUNTHpN8Avvj)

---

## 附錄

### A. 台股交易日曆注意事項
- 週末不交易
- 國定假日不交易
- 特殊狀況休市（如颱風）
- 需維護台股行事曆

### B. 股票代號格式
- 上市股票: 4 位數字（如 2330）
- 上櫃股票: 4 位數字（如 5274）
- ETF: 可能為 4 或 5 位（如 0050, 00631L）

### C. 資料時間說明
- 所有時間以台北時間 (UTC+8) 為準
- 盤後資料約在 15:00-17:00 之間完整
- 籌碼資料可能延遲至 17:00 後

---

**文件版本**: 1.0
**最後更新**: 2025-12-27
**維護者**: Jason Huang

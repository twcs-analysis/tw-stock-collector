-- ====================================
-- 台股資料收集系統 - 資料表定義
-- 版本: 1.0.0
-- 支援: PostgreSQL 12+ / SQLite 3.35+
-- ====================================
--
-- 設計原則:
-- 1. 使用兩種資料庫共通的資料型態
-- 2. 主鍵使用 BIGINT/INTEGER (根據資料庫自動處理)
-- 3. 外鍵約束確保資料完整性
-- 4. UNIQUE 約束防止重複資料
-- ====================================

-- ==========================================
-- 1. 股票基本資料表 (stocks)
-- ==========================================
-- 說明: 儲存股票代號、名稱、市場類型等基本資訊
-- 更新頻率: 當有新股票上市時更新
CREATE TABLE IF NOT EXISTS stocks (
    stock_id VARCHAR(10) PRIMARY KEY,         -- 股票代號 (例: 2330)
    stock_name VARCHAR(100) NOT NULL,         -- 股票名稱 (例: 台積電)
    market_type VARCHAR(10) NOT NULL,         -- 市場類型: 'twse' 或 'tpex'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_market_type CHECK (market_type IN ('twse', 'tpex'))
);

-- ==========================================
-- 2. 價格資料表 (stock_prices)
-- ==========================================
-- 說明: 每日開高低收與成交量資料
-- 更新頻率: 每交易日
-- 資料來源: data/raw/price/
CREATE TABLE IF NOT EXISTS stock_prices (
    id BIGINT PRIMARY KEY,                    -- 自動遞增 ID (PostgreSQL: SERIAL, SQLite: AUTOINCREMENT)
    stock_id VARCHAR(10) NOT NULL,            -- 股票代號
    trade_date DATE NOT NULL,                 -- 交易日期
    open_price DECIMAL(10, 2),                -- 開盤價
    high_price DECIMAL(10, 2),                -- 最高價
    low_price DECIMAL(10, 2),                 -- 最低價
    close_price DECIMAL(10, 2),               -- 收盤價 (建議使用還原股價)
    volume BIGINT,                            -- 成交量 (股)
    amount DECIMAL(18, 2),                    -- 成交金額 (元)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE (stock_id, trade_date)
);

-- ==========================================
-- 3. 三大法人買賣超資料表 (institutional_investors)
-- ==========================================
-- 說明: 外資、投信、自營商的買賣超資料
-- 更新頻率: 每交易日
-- 資料來源: data/raw/institutional/
CREATE TABLE IF NOT EXISTS institutional_investors (
    id BIGINT PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,

    -- 外資 (Foreign Investors)
    foreign_buy BIGINT,                       -- 外資買進 (股)
    foreign_sell BIGINT,                      -- 外資賣出 (股)
    foreign_net BIGINT,                       -- 外資買賣超 (股)

    -- 外資細分
    foreign_main_buy BIGINT,                  -- 外陸資買進 (不含外資自營商)
    foreign_main_sell BIGINT,                 -- 外陸資賣出
    foreign_main_net BIGINT,                  -- 外陸資買賣超
    foreign_dealer_buy BIGINT,                -- 外資自營商買進
    foreign_dealer_sell BIGINT,               -- 外資自營商賣出
    foreign_dealer_net BIGINT,                -- 外資自營商買賣超

    -- 投信 (Investment Trust)
    trust_buy BIGINT,                         -- 投信買進 (股)
    trust_sell BIGINT,                        -- 投信賣出 (股)
    trust_net BIGINT,                         -- 投信買賣超 (股)

    -- 自營商 (Dealers)
    dealer_buy BIGINT,                        -- 自營商買進 (股)
    dealer_sell BIGINT,                       -- 自營商賣出 (股)
    dealer_net BIGINT,                        -- 自營商買賣超 (股)

    -- 自營商細分
    dealer_self_buy BIGINT,                   -- 自營商買進 (自行買賣)
    dealer_self_sell BIGINT,                  -- 自營商賣出 (自行買賣)
    dealer_self_net BIGINT,                   -- 自營商買賣超 (自行買賣)
    dealer_hedge_buy BIGINT,                  -- 自營商買進 (避險)
    dealer_hedge_sell BIGINT,                 -- 自營商賣出 (避險)
    dealer_hedge_net BIGINT,                  -- 自營商買賣超 (避險)

    -- 合計
    total_net BIGINT,                         -- 三大法人買賣超合計 (股)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE (stock_id, trade_date)
);

-- ==========================================
-- 4. 融資融券資料表 (margin_trading)
-- ==========================================
-- 說明: 融資融券餘額與變化
-- 更新頻率: 每交易日
-- 資料來源: data/raw/margin/
CREATE TABLE IF NOT EXISTS margin_trading (
    id BIGINT PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,

    -- 融資 (Margin Trading)
    margin_balance DECIMAL(15, 2),            -- 融資餘額 (千元)
    margin_change DECIMAL(15, 2),             -- 融資增減 (千元)

    -- 融券 (Short Selling)
    short_balance BIGINT,                     -- 融券餘額 (股)
    short_change BIGINT,                      -- 融券增減 (股)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE (stock_id, trade_date)
);

-- ==========================================
-- 5. 借券賣出資料表 (securities_lending)
-- ==========================================
-- 說明: 借券賣出餘額與變化
-- 更新頻率: 每交易日
-- 資料來源: data/raw/lending/
CREATE TABLE IF NOT EXISTS securities_lending (
    id BIGINT PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,

    -- 借券資料
    lending_balance BIGINT,                   -- 借券餘額 (股)
    lending_change BIGINT,                    -- 借券增減 (股)
    prev_balance BIGINT,                      -- 前日餘額 (股)
    daily_sell BIGINT,                        -- 當日賣出 (股)
    daily_return BIGINT,                      -- 當日還券 (股)
    daily_adjust BIGINT,                      -- 當日調整 (股)
    next_day_available BIGINT,                -- 次一營業日可限額 (股)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE (stock_id, trade_date)
);

-- ==========================================
-- 6. 成交量前 20 名資料表 (top20_volume)
-- ==========================================
-- 說明: 每日成交量排名前 20 名的股票
-- 更新頻率: 每交易日
-- 資料來源: data/raw/top20_volume/
CREATE TABLE IF NOT EXISTS top20_volume (
    id BIGINT PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,

    rank INTEGER NOT NULL,                    -- 成交量排名
    volume BIGINT,                            -- 成交量 (股)
    amount DECIMAL(18, 2),                    -- 成交金額 (元)
    transaction_count INTEGER,                -- 成交筆數

    -- 價格資料
    open_price DECIMAL(10, 2),                -- 開盤價
    high_price DECIMAL(10, 2),                -- 最高價
    low_price DECIMAL(10, 2),                 -- 最低價
    close_price DECIMAL(10, 2),               -- 收盤價
    change_price DECIMAL(10, 2),              -- 漲跌價差

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE (trade_date, rank),
    CONSTRAINT chk_rank CHECK (rank BETWEEN 1 AND 20)
);

-- ==========================================
-- 7. 技術分析日資料表 (stock_analysis_daily)
-- ==========================================
-- 說明: 全功能技術分析寬表，包含均線、指標、波動與量能分析
-- 更新頻率: 每交易日計算後更新
-- 用途: 選股、回測、技術分析
CREATE TABLE IF NOT EXISTS stock_analysis_daily (
    -- ==========================================
    -- 基礎標記與量價資料
    -- ==========================================
    trade_date DATE NOT NULL,                 -- 交易日期
    stock_id VARCHAR(10) NOT NULL,            -- 股票代號

    -- 原始價量資料
    open_price DECIMAL(10, 2),
    high_price DECIMAL(10, 2),
    low_price DECIMAL(10, 2),
    close_price DECIMAL(10, 2),               -- 建議存還原股價 (Adjusted Close)
    volume BIGINT,                            -- 成交量 (股)
    amount DECIMAL(18, 2),                    -- 成交金額 (過濾冷門股)

    -- ==========================================
    -- 均線系統 (Moving Averages)
    -- ==========================================
    ma_5 DECIMAL(10, 2),                      -- 週線
    ma_10 DECIMAL(10, 2),                     -- 雙週線
    ma_20 DECIMAL(10, 2),                     -- 月線 (生命線)
    ma_60 DECIMAL(10, 2),                     -- 季線 (趨勢線)
    ma_120 DECIMAL(10, 2),                    -- 半年線
    ma_240 DECIMAL(10, 2),                    -- 年線 (牛熊分界)

    -- ==========================================
    -- 指標系統 (RSI, MACD, DMI)
    -- ==========================================
    -- RSI (相對強弱指標)
    rsi_6 DECIMAL(10, 2),                     -- 短期超買超賣
    rsi_14 DECIMAL(10, 2),                    -- 中期超買超賣

    -- MACD (指數平滑異同移動平均線)
    macd_dif DECIMAL(10, 2),                  -- 快線 (DIF)
    macd_dea DECIMAL(10, 2),                  -- 慢線 (DEA/Signal)
    macd_hist DECIMAL(10, 2),                 -- 柱狀體 (Histogram)

    -- DMI (趨向指標)
    dmi_pdi DECIMAL(10, 2),                   -- +DI (上升方向指標)
    dmi_mdi DECIMAL(10, 2),                   -- -DI (下降方向指標)
    dmi_adx DECIMAL(10, 2),                   -- ADX (趨勢強度)
    dmi_adxr DECIMAL(10, 2),                  -- ADXR (趨勢平均)

    -- ==========================================
    -- 波動與量能衍生 (Bollinger, Volume MA)
    -- ==========================================
    -- Bollinger Bands (布林通道)
    bb_upper DECIMAL(10, 2),                  -- 布林上軌
    bb_mid DECIMAL(10, 2),                    -- 布林中軌 (通常為 MA20)
    bb_lower DECIMAL(10, 2),                  -- 布林下軌

    -- 成交量分析
    vol_ma5 BIGINT,                           -- 5日均量
    vol_ma20 BIGINT,                          -- 20日均量
    vol_ratio DECIMAL(10, 2),                 -- 量比 (當日量 / 5日均量)

    -- VWAP (成交量加權平均價)
    vwap DECIMAL(10, 2),                      -- 當日量價加權平均價

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (trade_date, stock_id),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE
);

-- ==========================================
-- 8. 資料匯入日誌表 (import_logs)
-- ==========================================
-- 說明: 記錄每次資料匯入的狀態，用於追蹤與除錯
CREATE TABLE IF NOT EXISTS import_logs (
    id BIGINT PRIMARY KEY,
    import_date DATE NOT NULL,                -- 匯入的資料日期
    data_type VARCHAR(50) NOT NULL,           -- 資料類型: price, institutional, margin, lending, top20_volume
    start_time TIMESTAMP NOT NULL,            -- 匯入開始時間
    end_time TIMESTAMP,                       -- 匯入結束時間
    status VARCHAR(20) NOT NULL,              -- 狀態: running, completed, failed
    records_count INTEGER,                    -- 匯入的記錄數
    error_message TEXT,                       -- 錯誤訊息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_status CHECK (status IN ('running', 'completed', 'failed'))
);

-- ==========================================
-- 9. ETF 基本資訊表 (etfs)
-- ==========================================
-- 說明: 儲存 ETF 代號、名稱等基本資訊
-- 更新頻率: 手動維護
CREATE TABLE IF NOT EXISTS etfs (
    etf_id VARCHAR(10) PRIMARY KEY,           -- ETF 代碼 (例: 0050, 00733)
    etf_name VARCHAR(100) NOT NULL,           -- ETF 名稱 (例: 元大台灣50)
    description VARCHAR(500),                 -- ETF 說明
    created_at TIMESTAMP DEFAULT CURRENT_timestamp,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 10. ETF 持股明細表 (etf_holdings)
-- ==========================================
-- 說明: 儲存 ETF 的持股組成與權重
-- 更新頻率: 不定期 (隨 ETF 持股變動)
-- 資料來源: data/raw/etf-holdings/
CREATE TABLE IF NOT EXISTS etf_holdings (
    id BIGINT PRIMARY KEY,
    etf_id VARCHAR(10) NOT NULL,              -- ETF 代碼
    stock_id VARCHAR(10) NOT NULL,            -- 成分股代碼
    snapshot_date DATE NOT NULL,              -- 持股快照日期
    weight DECIMAL(10, 2),                    -- 持股權重 (%)
    shares BIGINT,                            -- 持有股數
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (etf_id) REFERENCES etfs(etf_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE (etf_id, stock_id, snapshot_date)
);

-- ==========================================
-- 11. ETF 持股去重清單表 (etf_stock_union)
-- ==========================================
-- 說明: 包含所有 ETF 的成分股（去重），用於選股策略篩選
-- 更新頻率: 每次 ETF 持股更新後重新計算
CREATE TABLE IF NOT EXISTS etf_stock_union (
    stock_id VARCHAR(10) PRIMARY KEY,         -- 股票代碼
    etf_count INTEGER NOT NULL,               -- 被幾個 ETF 持有
    total_weight DECIMAL(10, 2),              -- 所有 ETF 中的權重總和 (%)
    latest_update DATE NOT NULL,              -- 最後更新日期
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE
);

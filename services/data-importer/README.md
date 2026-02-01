# Data Importer Service

資料匯入微服務，負責將 JSON 格式的原始資料匯入到資料庫。

## 功能

- 將收集的 JSON 資料匯入 PostgreSQL/MySQL
- 支援批次匯入與增量更新
- 資料轉換與正規化
- 匯入狀態追蹤與錯誤處理

## 目錄結構

```
data-importer/
├── app/                    # 應用程式碼
│   ├── __init__.py
│   ├── main.py             # 主要執行入口
│   ├── importers/          # 各類資料匯入器
│   │   ├── price_importer.py
│   │   ├── institutional_importer.py
│   │   ├── margin_importer.py
│   │   └── lending_importer.py
│   └── db/                 # 資料庫連線與操作
│       ├── connection.py
│       └── models.py
│
├── tests/                  # 測試
├── Dockerfile              # Docker 建置檔
├── requirements.txt        # Python 依賴
└── README.md               # 本文件
```

## 資料庫 Schema

### 價格資料表 (stock_prices)

```sql
CREATE TABLE stock_prices (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    stock_id VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2),
    volume BIGINT,
    market_type VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, stock_id)
);
```

### 三大法人資料表 (institutional_trades)

```sql
CREATE TABLE institutional_trades (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    stock_id VARCHAR(10) NOT NULL,
    foreign_buy BIGINT,
    foreign_sell BIGINT,
    foreign_net BIGINT,
    trust_buy BIGINT,
    trust_sell BIGINT,
    trust_net BIGINT,
    dealer_buy BIGINT,
    dealer_sell BIGINT,
    dealer_net BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, stock_id)
);
```

## 本地執行

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定資料庫連線
export DATABASE_URL="postgresql://user:pass@localhost:5432/tw_stock"

# 匯入指定日期的資料
python app/main.py --date 2024-12-27

# 匯入指定類型
python app/main.py --date 2024-12-27 --types price institutional

# 匯入日期範圍
python app/main.py --start 2024-12-01 --end 2024-12-31
```

## Docker 執行

```bash
# 建置映像檔
docker build -t tw-stock-data-importer:latest .

# 執行容器
docker run --rm \
  -e DATABASE_URL="postgresql://user:pass@db:5432/tw_stock" \
  -v $(pwd)/../../data:/app/data \
  tw-stock-data-importer:latest \
  --date 2024-12-27
```

## 環境變數

| 變數 | 說明 | 範例 |
|-----|------|------|
| `DATABASE_URL` | 資料庫連線字串 | postgresql://user:pass@localhost:5432/tw_stock |
| `BATCH_SIZE` | 批次匯入筆數 | 1000 |
| `LOG_LEVEL` | 日誌等級 | INFO |

## 支援的資料庫

- PostgreSQL 12+
- MySQL 8.0+
- SQLite (開發測試用)

## 相關服務

- [Data Collector](../data-collector/) - 資料收集服務
- [Common Library](../common/) - 共用工具函式庫
- [API Service](../api-service/) - REST API 服務

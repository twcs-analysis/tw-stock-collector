# API Service

REST API 微服務，提供股票資料查詢、技術指標計算等功能。

## 功能

- 股票基本資料查詢
- 歷史價格資料查詢
- 三大法人買賣超查詢
- 融資融券資料查詢
- 技術指標計算 (MA, MACD, RSI, KD, 布林通道)
- 籌碼分析資料

## 技術棧

- **Framework**: FastAPI / Flask
- **Database**: PostgreSQL (透過 data-importer 匯入)
- **Cache**: Redis (選用)
- **Authentication**: JWT

## 目錄結構

```
api-service/
├── app/                    # 應用程式碼
│   ├── __init__.py
│   ├── main.py             # FastAPI 應用程式入口
│   ├── api/                # API 路由
│   │   ├── v1/
│   │   │   ├── stocks.py       # 股票基本資料
│   │   │   ├── prices.py       # 價格資料
│   │   │   ├── institutional.py # 三大法人
│   │   │   ├── margin.py       # 融資融券
│   │   │   └── indicators.py   # 技術指標
│   │   └── __init__.py
│   ├── services/           # 業務邏輯
│   │   ├── stock_service.py
│   │   ├── indicator_service.py
│   │   └── analysis_service.py
│   ├── db/                 # 資料庫
│   │   ├── connection.py
│   │   └── queries.py
│   └── middleware/         # 中介層
│       ├── auth.py
│       └── rate_limit.py
│
├── tests/                  # 測試
├── Dockerfile              # Docker 建置檔
├── requirements.txt        # Python 依賴
└── README.md               # 本文件
```

## API 端點

### 股票資料

```
GET /api/v1/stocks                    # 取得所有股票列表
GET /api/v1/stocks/{stock_id}         # 取得單一股票資訊
GET /api/v1/stocks/{stock_id}/prices  # 取得歷史價格
```

### 三大法人

```
GET /api/v1/institutional/{stock_id}  # 取得三大法人買賣超
GET /api/v1/institutional/summary     # 取得市場法人買賣超統計
```

### 融資融券

```
GET /api/v1/margin/{stock_id}         # 取得融資融券資料
GET /api/v1/margin/ranking            # 取得融資融券排行
```

### 技術指標

```
GET /api/v1/indicators/{stock_id}/ma      # 移動平均線
GET /api/v1/indicators/{stock_id}/macd    # MACD
GET /api/v1/indicators/{stock_id}/rsi     # RSI
GET /api/v1/indicators/{stock_id}/kd      # KD 指標
GET /api/v1/indicators/{stock_id}/bb      # 布林通道
```

## 本地開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
export DATABASE_URL="postgresql://user:pass@localhost:5432/tw_stock"
export SECRET_KEY="your-secret-key"

# 啟動開發伺服器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

訪問 http://localhost:8000/docs 查看 API 文件

## Docker 執行

```bash
# 建置映像檔
docker build -t tw-stock-api-service:latest .

# 執行容器
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/tw_stock" \
  -e SECRET_KEY="your-secret-key" \
  tw-stock-api-service:latest
```

## 環境變數

| 變數 | 說明 | 範例 |
|-----|------|------|
| `DATABASE_URL` | 資料庫連線字串 | postgresql://user:pass@localhost:5432/tw_stock |
| `SECRET_KEY` | JWT 簽章金鑰 | your-secret-key-here |
| `REDIS_URL` | Redis 連線字串 (選用) | redis://localhost:6379 |
| `API_PORT` | API 服務埠號 | 8000 |
| `CORS_ORIGINS` | 允許的 CORS 來源 | http://localhost:3000 |

## 效能優化

- 使用 Redis 快取常用查詢
- 資料庫查詢索引優化
- 分頁查詢避免大量資料傳輸
- API 速率限制

## 相關服務

- [Data Importer](../data-importer/) - 資料匯入服務
- [Analyzer Service](../analyzer-service/) - 分析服務
- [Common Library](../common/) - 共用工具函式庫

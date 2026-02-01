# Data Collector Service

台股資料收集微服務，負責從證交所和櫃買中心收集各類股票資料。

## 功能

- 每日價量資料收集 (price)
- 三大法人買賣超 (institutional)
- 融資融券資料 (margin)
- 借券賣出資料 (lending)
- 成交量前 20 名 (top20_volume)

## 目錄結構

```
data-collector/
├── app/                    # 應用程式碼
│   ├── __init__.py
│   ├── main.py             # 主要執行入口
│   ├── backfill.py         # 歷史資料回補
│   ├── base_collector.py   # Collector 基礎類別
│   ├── base.py
│   ├── price_collector.py
│   ├── institutional_collector.py
│   ├── margin_collector.py
│   ├── lending_collector.py
│   └── top20_volume_collector.py
│
├── tests/                  # 測試
├── Dockerfile              # Docker 建置檔
├── requirements.txt        # Python 依賴
└── README.md               # 本文件
```

## 本地執行

```bash
# 安裝依賴
pip install -r requirements.txt

# 收集今日資料
python app/main.py

# 收集指定日期
python app/main.py --date 2024-12-27

# 收集特定類型
python app/main.py --date 2024-12-27 --types price margin

# 回補歷史資料
python app/backfill.py --start 2025-01-01 --end 2025-01-31
```

## Docker 執行

```bash
# 建置映像檔
docker build -t tw-stock-data-collector:latest .

# 執行容器
docker run --rm \
  -v $(pwd)/../../data:/app/data \
  tw-stock-data-collector:latest \
  --date 2024-12-27
```

## 環境變數

| 變數 | 說明 | 預設值 |
|-----|------|--------|
| `LOG_LEVEL` | 日誌等級 | INFO |
| `DATA_PATH` | 資料儲存路徑 | /app/data |
| `TZ` | 時區 | Asia/Taipei |

## 資料輸出

資料會儲存在 `data/raw/{type}/YYYY/MM/YYYY-MM-DD.json`

## 相關服務

- [Common Library](../common/) - 共用工具函式庫
- [Data Importer](../data-importer/) - 資料匯入服務
- [API Service](../api-service/) - REST API 服務

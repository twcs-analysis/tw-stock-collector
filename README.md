# 台股資料收集系統 (Taiwan Stock Collector)

建立一個完整的台股資料收集系統,用於籌碼面與技術面分析。

## 📖 文檔

- **[快速入門指南](README.md)** - 本文件
- **[台股數據收集規格書](docs/specifications/TWSE_DATA_COLLECTION_SPEC.md)** - 完整的台股資料收集系統設計文檔
- **[FinMind 實作指南](docs/specifications/FINMIND_IMPLEMENTATION_GUIDE.md)** - 基於 FinMind 免費版的實作指南
- **[文檔中心](docs/README.md)** - 所有文檔的導覽頁面

## 專案結構

```
tw-stock-collector/
├── README.md                    # 專案說明
├── requirements.txt             # Python 套件依賴
├── .env.example                 # 環境變數範例
├── docs/                        # 文檔目錄
│   ├── README.md               # 文檔導覽
│   ├── specifications/         # 規格書
│   │   ├── TWSE_DATA_COLLECTION_SPEC.md
│   │   └── FINMIND_IMPLEMENTATION_GUIDE.md
│   ├── api-examples/           # API 範例
│   └── notebooks/              # Jupyter 筆記本
├── config/
│   ├── config.yaml             # 主要配置檔
│   └── database.yaml           # 資料庫配置
├── src/
│   ├── collectors/             # 資料收集器
│   │   ├── __init__.py
│   │   ├── base_collector.py
│   │   ├── twse_collector.py   # 台灣證交所
│   │   ├── tpex_collector.py   # 櫃買中心
│   │   └── mops_collector.py   # 公開資訊觀測站
│   ├── models/                 # 資料模型
│   │   ├── __init__.py
│   │   ├── price.py
│   │   ├── institutional.py
│   │   └── margin.py
│   ├── database/               # 資料庫操作
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── crud.py
│   ├── utils/                  # 工具函數
│   │   ├── __init__.py
│   │   ├── date_utils.py
│   │   ├── validator.py
│   │   └── logger.py
│   └── schedulers/             # 排程器
│       ├── __init__.py
│       └── daily_job.py
├── scripts/                    # 執行腳本
│   ├── init_db.py             # 初始化資料庫
│   ├── backfill.py            # 歷史資料回補
│   └── daily_collect.py       # 每日收集
├── tests/                      # 測試
│   └── test_collectors.py
├── logs/                       # 日誌檔案
└── data/                       # 資料檔案
```

## 資料來源

### 技術面資料
- 每日價量資料（TWSE、TPEx）
- 調整後價格（除權息）
- 技術指標基礎資料

### 籌碼面資料
- 三大法人買賣超
- 融資融券資料
- 主力進出分析
- 董監持股與內部人交易
- 借券資料
- 外資持股比例
- 股權分散表

## 安裝步驟

### 1. 複製專案
```bash
git clone <repository-url>
cd tw-stock-collector
```

### 2. 安裝 Python 套件
```bash
pip install -r requirements.txt
```

### 3. 配置環境變數
```bash
cp .env.example .env
# 編輯 .env 檔案，填入資料庫連線資訊等
```

### 4. 配置檔案設定
編輯 `config/config.yaml` 和 `config/database.yaml` 檔案

### 5. 初始化資料庫
```bash
python scripts/init_db.py
```

## 使用方式

### 每日資料收集
```bash
python scripts/daily_collect.py
```

### 歷史資料回補
```bash
python scripts/backfill.py --start-date 2020-01-01 --end-date 2023-12-31
```

## 資料收集時間表

| 資料類型 | 更新頻率 | 收集時間 |
|---------|---------|---------|
| 每日價量資料 | 每日 | 15:30 後 |
| 三大法人 | 每日 | 15:30 後 |
| 融資融券 | 每日 | 15:30 後 |
| 股權分散表 | 每週 | 週六 |
| 董監持股 | 每日 | 18:00 |
| 借券資料 | 每日 | 15:30 後 |

## 技術架構

- **語言**: Python 3.8+
- **資料庫**: PostgreSQL
- **資料處理**: Pandas, NumPy
- **任務排程**: APScheduler
- **資料來源**: TWSE, TPEx, MOPS, FinMind

## 注意事項

1. 遵守爬蟲禮儀,合理的請求間隔（3-5秒）
2. 確保資料使用符合各網站的服務條款
3. 定期備份資料庫
4. 監控系統運行狀態

## 開發計畫

### 近期目標
- [ ] 完成基礎價量資料收集
- [ ] 完成三大法人資料收集
- [ ] 完成融資融券資料收集
- [ ] 建立每日自動排程

### 中期目標
- [ ] 加入技術指標計算模組
- [ ] 加入籌碼分析模組
- [ ] 建立資料視覺化介面
- [ ] 開發 API 供其他應用使用

## 授權

MIT License

## 維護者

Jason Huang

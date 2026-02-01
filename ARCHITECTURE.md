# 台股資料系統 - 微服務架構

本文件說明專案的微服務架構設計。

## 🏗️ 架構概覽

台股資料系統採用微服務架構，將功能分散到四個獨立服務：

```
┌─────────────────────────────────────────────────────────────┐
│                     台股資料系統                              │
└─────────────────────────────────────────────────────────────┘
        │
        ├──> Data Collector Service (資料收集)
        │    • 從證交所、櫃買中心收集資料
        │    • 儲存為 JSON 格式
        │
        ├──> Data Importer Service (資料匯入)
        │    • 讀取 JSON 檔案
        │    • 匯入 PostgreSQL 資料庫
        │
        ├──> API Service (REST API)
        │    • 提供 RESTful API
        │    • 查詢股票資料、技術指標
        │
        └──> Analyzer Service (分析服務)
             • 技術分析、籌碼分析
             • 策略回測與績效評估
```

## 📁 專案結構

```
tw-stock-collector/
├── services/                   # 微服務目錄
│   ├── data-collector/         # 資料收集服務
│   │   ├── app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   ├── data-importer/          # 資料匯入服務
│   │   ├── app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   ├── api-service/            # REST API 服務
│   │   ├── app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   ├── analyzer-service/       # 分析服務
│   │   ├── app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   ├── common/                 # 共用程式庫
│   │   ├── utils/              # 工具函式
│   │   ├── models/             # 資料模型
│   │   ├── validators/         # 驗證器
│   │   ├── datasources/        # 資料源 API
│   │   └── README.md
│   │
│   └── README.md               # 服務總覽
│
├── build/                      # Docker 建置
│   ├── data-collector/
│   ├── data-importer/
│   ├── api-service/
│   ├── analyzer-service/
│   ├── build-all.sh            # 一鍵建置腳本
│   └── README.md
│
├── deployment/                 # 部署配置
│   ├── deploy.sh               # 部署腳本
│   ├── stock-data-collector/   # Docker Compose 配置
│   └── README.md
│
├── data/                       # 資料儲存
│   ├── raw/                    # 原始 JSON 資料
│   │   ├── price/
│   │   ├── institutional/
│   │   ├── margin/
│   │   ├── lending/
│   │   └── top20_volume/
│   └── README.md
│
├── database/                   # 資料庫
│   ├── init/                   # 初始化腳本
│   ├── migrations/             # 資料庫遷移
│   └── README.md
│
├── config/                     # 設定檔
│   ├── config.yaml
│   ├── database.yaml
│   └── logging.yaml
│
├── docs/                       # 文檔
│   ├── specifications/         # 規格書
│   ├── api-examples/           # API 範例
│   └── README.md
│
├── dev-scripts/                # 開發測試腳本
│   └── README.md
│
├── src/                        # 舊版程式碼 (向後相容)
├── scripts/                    # 生產腳本 (向後相容)
│
├── .github/workflows/          # GitHub Actions
│   ├── daily-collection.yml
│   └── backfill.yml
│
├── README.md                   # 專案說明
├── CLAUDE.md                   # AI 助手指南
├── ARCHITECTURE.md             # 本文件
├── CHANGELOG.md                # 變更日誌
└── requirements.txt            # 整體依賴
```

## 🔄 資料流程

### 1. 資料收集流程

```
證交所 API ──┐
            ├──> Data Collector ──> JSON Files ──> Git Repository
櫃買中心 API ─┘
```

1. Data Collector 從官方 API 收集資料
2. 驗證資料完整性與正確性
3. 儲存為標準化 JSON 格式
4. 自動 commit 並 push 到 Git

### 2. 資料匯入流程

```
JSON Files ──> Data Importer ──> PostgreSQL Database
```

1. Data Importer 讀取 JSON 檔案
2. 解析並驗證資料
3. 轉換為資料庫 schema
4. 批次匯入資料庫

### 3. API 查詢流程

```
Client ──> API Service ──> PostgreSQL ──> Response
                │
                └──> Redis Cache (選用)
```

1. Client 發送 HTTP 請求
2. API Service 查詢資料庫或快取
3. 計算技術指標 (如需要)
4. 回傳 JSON 格式資料

### 4. 分析流程

```
PostgreSQL ──> Analyzer Service ──> 分析結果
                     │
                     └──> API Service (提供給前端)
```

1. Analyzer Service 讀取資料庫
2. 執行技術分析、籌碼分析
3. 策略回測與績效計算
4. 結果存回資料庫或透過 API 提供

## 🎯 微服務設計原則

### 1. 單一職責

每個服務負責單一功能領域：
- Data Collector: 只負責資料收集
- Data Importer: 只負責資料匯入
- API Service: 只負責 API 服務
- Analyzer Service: 只負責分析計算

### 2. 獨立部署

- 每個服務有獨立的 Dockerfile
- 可以獨立建置、測試、部署
- 互不影響，減少部署風險

### 3. 共用程式庫

- Common Library 提供共用功能
- 避免程式碼重複
- 統一介面與標準

### 4. 資料獨立

- 使用檔案系統 (JSON) 作為資料交換
- 透過資料庫共享資料
- 避免服務間直接呼叫

## 🔧 技術棧

### Data Collector
- **語言**: Python 3.11
- **主要函式庫**: Requests, Pandas
- **儲存**: JSON 檔案
- **部署**: Docker, GitHub Actions

### Data Importer
- **語言**: Python 3.11
- **主要函式庫**: SQLAlchemy, Pandas
- **資料庫**: PostgreSQL 12+
- **部署**: Docker

### API Service
- **語言**: Python 3.11
- **框架**: FastAPI
- **資料庫**: PostgreSQL
- **快取**: Redis (選用)
- **部署**: Docker
- **文檔**: OpenAPI (Swagger)

### Analyzer Service
- **語言**: Python 3.11
- **主要函式庫**: TA-Lib, Pandas, NumPy
- **部署**: Docker
- **執行**: 批次處理或背景任務

### Common Library
- **工具**: 日期處理、檔案操作、日誌
- **模型**: 資料模型定義
- **驗證**: 資料驗證器
- **API**: 證交所、櫃買中心 API 封裝

## 📊 部署架構

### 開發環境

```
Docker Compose
├── data-collector (on-demand)
├── data-importer (on-demand)
├── api-service (port 8000)
├── analyzer-service (on-demand)
├── postgresql (port 5432)
└── redis (port 6379)
```

### 生產環境

```
GitHub Actions + Docker
├── Data Collector (排程執行)
│   └── Cron: 週一至週六 21:30
│
Cloud Platform (AWS/GCP/Azure)
├── API Service (長期運行)
├── PostgreSQL (RDS/Cloud SQL)
├── Redis (ElastiCache/MemoryStore)
└── Analyzer Service (背景任務)
```

## 🔐 安全考量

### API Service
- JWT 認證
- API Rate Limiting
- CORS 設定
- SQL Injection 防護

### Database
- 連線加密 (SSL)
- 權限最小化原則
- 定期備份

### Docker
- 非 root 使用者執行
- 映像檔漏洞掃描
- 敏感資訊環境變數化

## 📈 擴展性

### 水平擴展

可以獨立擴展各服務：

```bash
# API Service 擴展到 3 個實例
docker-compose up --scale api-service=3

# Analyzer Service 擴展
docker-compose up --scale analyzer-service=5
```

### 垂直擴展

調整容器資源限制：

```yaml
services:
  api-service:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## 🔄 未來優化

### 1. 訊息佇列

引入 RabbitMQ 或 Kafka 進行服務間通訊：

```
Data Collector ──> Message Queue ──> Data Importer
```

### 2. 服務註冊與發現

使用 Consul 或 Eureka 管理服務：

```
Service Registry
├── data-collector:v1.0
├── api-service:v2.1
└── analyzer-service:v1.5
```

### 3. API Gateway

統一 API 入口：

```
Client ──> API Gateway ──┬──> API Service
                        └──> Analyzer Service
```

### 4. 分散式追蹤

使用 Jaeger 或 Zipkin 追蹤請求：

```
Request ID: abc123
├── API Service (10ms)
├── Database Query (50ms)
└── Cache Lookup (2ms)
```

## 📖 參考文件

- [Services README](services/README.md) - 微服務詳細說明
- [Build README](build/README.md) - Docker 建置指南
- [Deployment README](deployment/README.md) - 部署說明
- [CLAUDE.md](CLAUDE.md) - AI 助手指南

---

**維護者**: Jason Huang
**最後更新**: 2026-02-01
**架構版本**: v2.0 (微服務架構)

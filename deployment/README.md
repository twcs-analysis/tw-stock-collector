# Deployment 目錄

此目錄包含台股資料收集與分析系統的部署配置,依功能模組分類。

## 📁 目錄結構

```
deployment/
├── stock-data-collector/   # 資料收集服務部署
│   ├── docker-compose.yml
│   ├── .env.example
│   └── .dockerignore
│
└── README.md              # 本文件
```

## 🚀 模組說明

### stock-data-collector
台股資料收集服務,負責從證交所和櫃買中心收集資料。

**主要功能:**
- 每日價量資料收集
- 三大法人買賣超
- 融資融券餘額
- 借券賣出資料

**使用方式:**
```bash
cd deployment/stock-data-collector
cp .env.example .env

# 執行資料收集
COLLECTION_DATE=2025-01-28 docker-compose up
```

詳細說明請參考: [stock-data-collector/README.md](stock-data-collector/README.md)

## 📝 部署注意事項

### 主要部署方式
本專案主要透過 **GitHub Actions** 進行自動化部署:
- 每交易日 21:30 自動收集資料
- 自動判斷交易日,跳過非交易日
- 收集完成後自動 commit 並 push

### Docker 部署用途
此目錄的 Docker 配置主要用於:
- **本地開發測試**
- **回補歷史資料**
- **驗證資料源連線**
- **新功能開發與測試**

## 🔧 通用設定

### 環境變數
各模組都使用 `.env` 檔案管理環境變數:
```bash
# 複製範例檔案
cp .env.example .env

# 編輯設定
vim .env
```

### 網路配置
所有服務使用共同的 Docker 網路:
```bash
NETWORK_NAME=tw-stock-network
```

## 📖 相關文件

- **[主要 README](../README.md)** - 專案整體說明
- **[Build 目錄](../build/)** - Docker 映像檔建置

---

**最後更新**: 2026-02-01

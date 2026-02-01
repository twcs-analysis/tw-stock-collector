# Deployment 目錄

此目錄包含台股資料收集與分析系統的部署配置,依功能模組分類。

## 📁 目錄結構

```
deployment/
├── stock-data-collector/   # 資料收集服務部署
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── .dockerignore
│   └── README.md
│
└── README.md              # 本文件
```

## 🚀 模組說明

### stock-data-collector
台股資料收集服務,負責從證交所和櫃買中心收集資料。

**收集資料類型:**
- 每日價量資料 (開高低收、成交量)
- 三大法人買賣超 (外資、投信、自營商)
- 融資融券餘額與變化
- 借券賣出資料
- 成交量前 20 名個股

**快速開始:**
```bash
cd deployment/stock-data-collector

# 1. 準備環境
cp .env.example .env

# 2. 修改收集日期
# 編輯 docker-compose.yml 中的 command 參數
vim docker-compose.yml

# 3. 執行資料收集
docker-compose up

# 4. 查看結果
ls -lh ../../data/raw/price/2024/12/
```

詳細說明請參考: [stock-data-collector/README.md](stock-data-collector/README.md)

## 📝 部署注意事項

### 主要部署方式
本專案主要透過 **GitHub Actions** 進行自動化部署:
- **排程**: 每週一至週六 21:30 (台北時間)
- **智能判斷**: 自動跳過非交易日
- **自動提交**: 收集完成後自動 commit 並 push 到 Git
- **資料類型**: price, institutional, margin, lending, top20_volume

### Docker 部署用途
此目錄的 Docker 配置主要用於:
- ✅ **本地開發測試** - 測試資料收集功能
- ✅ **回補歷史資料** - 手動補充缺漏的資料
- ✅ **驗證資料源連線** - 確認 API 可正常存取
- ✅ **新功能開發** - 開發新收集器時的測試環境

### 使用限制
- ❌ **不建議用於生產環境長期運行**
- ❌ **不支援環境變數動態設定日期** (需修改 docker-compose.yml)
- ❌ **無自動排程功能** (建議使用 GitHub Actions)

## 🔧 通用設定

### 環境變數

各模組都使用 `.env` 檔案管理環境變數:

```bash
# 複製範例檔案
cp .env.example .env

# 編輯設定
vim .env
```

**可設定項目:**
- `LOG_LEVEL`: 日誌等級 (DEBUG, INFO, WARNING, ERROR)
- `TZ`: 時區設定 (預設: Asia/Taipei)
- `NETWORK_NAME`: Docker 網路名稱

### 網路配置

所有服務使用共同的 Docker 網路:

```yaml
networks:
  stock-network:
    name: tw-stock-network
    driver: bridge
```

## 📊 測試狀態

✅ **已驗證可正常運作** (2026-02-01)

測試收集 2024-12-27 資料:
- price: 1,954 筆 (604 KB)
- institutional: 1,721 筆 (4.1 MB)
- margin: 1,819 筆 (980 KB)
- lending: 1,014 筆 (551 KB)
- top20_volume: 20 筆 (6.6 KB)

總計: 6,528 筆資料

## 📖 相關文件

- **[主要 README](../README.md)** - 專案整體說明
- **[Build 目錄](../build/)** - Docker 映像檔建置
- **[GitHub Actions](.github/workflows/)** - 自動化工作流程

---

**最後更新**: 2026-02-01
**維護狀態**: ✅ 活躍維護中

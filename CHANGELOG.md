# 變更日誌 (Changelog)

本文件記錄專案的所有重要變更。

## [Unreleased]

### 新增
- 新增成交量前 20 名資料收集器 (`Top20VolumeCollector`)
  - 使用 TWSE OpenAPI `/exchangeReport/MI_INDEX20`
  - 收集每日成交量排名前 20 名股票資訊
  - 包含價格、成交量、成交金額等完整資訊
- 新增 TWSE API 參考文件 (`docs/TWSE_API_REFERENCE.md`)
  - 記錄 TWSE OpenAPI 143 個端點
  - 包含本專案已使用和值得收集的 API
- 新增成交量前 20 名使用說明 (`docs/TOP20_VOLUME_USAGE.md`)
  - 包含資料欄位說明、使用範例、分析範例
- 新增測試腳本 (`scripts/test_top20_volume.py`)

### 修改
- 更新 `README.md` 加入 TWSE API 參考文件連結
- 更新 `data/README.md` 加入成交量前 20 名資料說明
- 修正 `institutional_collector.py` TPEx 資料收集的 SSL 憑證問題
  - 使用 requests 先取得 HTML 再解析，避免 pandas.read_html 的憑證錯誤

### 資料
- 新增 2026-01-27 資料收集
  - 價格資料 (1951 筆股票)
  - 三大法人買賣超資料
  - 融資融券資料
  - 借券賣出資料
  - 成交量前 20 名資料

### 計劃功能
- 實作 FinMind 資料收集器
- 建立資料庫初始化腳本
- 實作每日自動排程
- 加入資料驗證機制

---

## [0.1.0] - 2025-12-28

### 新增
- 初始化專案結構
- 建立完整目錄架構
- 新增專案說明文件 (README.md)
- 新增系統規格書 (SPECIFICATION.md)
- 新增 FinMind 實作規格 (SPECIFICATION_FINMIND.md)
- 建立 Python 套件依賴清單 (requirements.txt)
- 建立配置檔範本 (config.yaml, database.yaml)
- 建立環境變數範例 (.env.example)
- 建立 .gitignore 檔案
- 建立文檔中心 (docs/)
  - API 範例目錄
  - Notebooks 目錄
  - 規格書目錄

### 目錄結構
```
tw-stock-collector/
├── config/              # 配置檔案
├── data/               # 資料檔案
├── docs/               # 文檔目錄
│   ├── api-examples/
│   ├── notebooks/
│   └── specifications/
├── logs/               # 日誌檔案
├── scripts/            # 執行腳本
├── src/                # 原始碼
│   ├── collectors/
│   ├── database/
│   ├── models/
│   ├── schedulers/
│   └── utils/
└── tests/              # 測試檔案
```

---

## 版本說明

版本號格式: `主版本.次版本.修訂號`
- **主版本**: 重大功能變更或不相容的 API 變更
- **次版本**: 新增功能且向下相容
- **修訂號**: 向下相容的問題修正

---

**維護者**: Jason Huang

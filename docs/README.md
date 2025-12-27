# 台股資料收集系統 - 文檔中心

## 📚 文檔結構

### 核心規格書 (Core Specifications)

專案採用**三階段架構**,各階段有獨立的規格書:

#### [Phase 1: 資料擷取與儲存](specifications/PHASE1_DATA_COLLECTION.md)
使用 GitHub Actions 自動化資料收集,儲存至 Git 倉庫:
- GitHub Actions 工作流程設計
- 資料來源與收集策略
- 檔案儲存結構規範
- 資料驗證與品質控制
- 執行日誌與錯誤處理

**適用對象**: 準備實作 Phase 1 資料收集的開發者

#### [Phase 2: 資料庫設計與匯入](specifications/PHASE2_DATABASE_IMPORT.md)
設計資料庫結構並從 Git 匯入資料:
- 資料庫選型與結構設計
- 完整的資料表設計 (10+ 資料表)
- 資料匯入流程與腳本架構
- 資料驗證與完整性檢查
- 定時自動匯入機制

**適用對象**: 準備實作 Phase 2 資料庫匯入的開發者

#### [Phase 3: 數據整理與分析](specifications/PHASE3_DATA_ANALYSIS.md)
基於資料庫進行深度分析與視覺化:
- 技術指標計算 (MA, MACD, RSI, KD等)
- 籌碼分析 (法人、融資融券、主力)
- 選股策略設計與實作
- 數據聚合與彙總表
- 視覺化儀表板與報表

**適用對象**: 準備實作 Phase 3 數據分析的開發者

---

### 參考文檔 (Reference Documents)

以下為原始的參考規格書,提供更詳細的背景資訊:

#### [台股數據收集規格書](specifications/TWSE_DATA_COLLECTION_SPEC.md)
台股資料收集系統的原始完整規格書,涵蓋:
- 資料需求分析（技術面、籌碼面）
- 資料來源與取得方式（TWSE、TPEx、MOPS）
- 資料收集策略與儲存架構
- 技術實作建議與專案結構
- 資料品質控制與效能考量

**用途**: 了解系統設計的完整背景

#### [FinMind 實作指南](specifications/FINMIND_IMPLEMENTATION_GUIDE.md)
基於 FinMind 免費版的原始實作指南,包含:
- FinMind API 完整使用指南
- 資料收集策略與排程規劃
- 資料庫設計與 ORM 模型
- 配置檔與環境設定
- 常見問題解答

**用途**: FinMind API 使用參考

---

### 專案管理 (Project Management)

#### [專案路線圖](project-management/PROJECT_ROADMAP.md)
完整的專案階段規劃與進度追蹤:
- Phase 0-7 詳細任務清單
- 整體進度追蹤
- 里程碑時間表
- 當前優先事項

#### [開發時程表](project-management/DEVELOPMENT_SCHEDULE.md)
詳細的開發時程安排:
- 週次開發計劃
- 每日任務時間預估
- 實際工時記錄
- 進度追蹤看板

**適用對象**: 需要了解專案規劃與時程的所有人


---

## 📖 快速導覽

### 新手入門 (推薦路徑)
1. 📘 閱讀 [README.md](../README.md) - 了解專案三階段架構
2. 📗 閱讀 [Phase 1 規格書](specifications/PHASE1_DATA_COLLECTION.md) - 了解資料收集方式
3. 📙 閱讀 [Phase 2 規格書](specifications/PHASE2_DATABASE_IMPORT.md) - 了解資料庫設計
4. 📕 閱讀 [Phase 3 規格書](specifications/PHASE3_DATA_ANALYSIS.md) - 了解數據分析方式
5. 🚀 開始實作！

### 依階段選擇
- **準備實作 Phase 1**: [資料擷取與儲存](specifications/PHASE1_DATA_COLLECTION.md)
- **準備實作 Phase 2**: [資料庫設計與匯入](specifications/PHASE2_DATABASE_IMPORT.md)
- **準備實作 Phase 3**: [數據整理與分析](specifications/PHASE3_DATA_ANALYSIS.md)

### 參考資料
- **深入了解系統**: [台股數據收集規格書](specifications/TWSE_DATA_COLLECTION_SPEC.md)
- **FinMind 使用**: [FinMind 實作指南](specifications/FINMIND_IMPLEMENTATION_GUIDE.md)
- **專案規劃**: [專案路線圖](project-management/PROJECT_ROADMAP.md)

---

## 🗂️ 目錄說明

```
docs/
├── README.md                              # 本文件 - 文檔導覽
├── specifications/                        # 規格書
│   ├── PHASE1_DATA_COLLECTION.md         # ⭐ Phase 1: 資料擷取與儲存
│   ├── PHASE2_DATABASE_IMPORT.md         # ⭐ Phase 2: 資料庫設計與匯入
│   ├── PHASE3_DATA_ANALYSIS.md           # ⭐ Phase 3: 數據整理與分析
│   ├── TWSE_DATA_COLLECTION_SPEC.md      # 台股數據收集規格書 (參考)
│   └── FINMIND_IMPLEMENTATION_GUIDE.md   # FinMind 實作指南 (參考)
├── project-management/                    # 專案管理
│   ├── README.md                          # 管理文件導覽
│   ├── PROJECT_ROADMAP.md                 # 專案路線圖
│   └── DEVELOPMENT_SCHEDULE.md            # 開發時程表
├── api-examples/                          # API 使用範例
│   └── (待新增)
└── notebooks/                             # Jupyter 筆記本
    └── (待新增)
```

---

## 📋 規格書版本對照

| 文檔 | 版本 | 更新日期 | 類型 | 主要內容 |
|------|------|---------|------|---------|
| PHASE1_DATA_COLLECTION.md | 1.0 | 2025-12-28 | 核心 | 資料擷取與儲存 |
| PHASE2_DATABASE_IMPORT.md | 1.0 | 2025-12-28 | 核心 | 資料庫設計與匯入 |
| PHASE3_DATA_ANALYSIS.md | 1.0 | 2025-12-28 | 核心 | 數據整理與分析 |
| TWSE_DATA_COLLECTION_SPEC.md | 1.0 | 2025-12-27 | 參考 | 台股數據收集完整規格 |
| FINMIND_IMPLEMENTATION_GUIDE.md | 2.1 | 2025-12-28 | 參考 | FinMind 免費版實作指南 |

---

## 🔗 相關資源

### 官方文檔
- [FinMind 官網](https://finmindtrade.com/)
- [FinMind GitHub](https://github.com/FinMind/FinMind)
- [台灣證券交易所](https://www.twse.com.tw)
- [證券櫃買中心](https://www.tpex.org.tw)

### 學習資源
- [FinMind 技術面文檔](https://finmind.github.io/tutor/TaiwanMarket/Technical/)
- [FinMind 籌碼面文檔](https://finmind.github.io/tutor/TaiwanMarket/Chip/)

---

## 📝 文檔貢獻

如果你發現文檔有錯誤或需要補充，歡迎：
1. 提出 Issue
2. 提交 Pull Request
3. 聯繫維護者

---

**維護者**: Jason Huang
**最後更新**: 2025-12-28

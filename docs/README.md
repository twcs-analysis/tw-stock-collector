# 台股資料收集系統 - 文檔中心

## 📚 文檔結構

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

### 規格書 (Specifications)

#### [台股數據收集規格書](specifications/TWSE_DATA_COLLECTION_SPEC.md)
台股資料收集系統的完整規格書，涵蓋：
- 資料需求分析（技術面、籌碼面）
- 資料來源與取得方式（TWSE、TPEx、MOPS）
- 資料收集策略與儲存架構
- 技術實作建議與專案結構
- 資料品質控制與效能考量

**適用對象**：需要完整了解系統設計的開發者

#### [FinMind 實作指南](specifications/FINMIND_IMPLEMENTATION_GUIDE.md)
基於 **FinMind 免費版**的實作指南，包含：
- FinMind API 完整使用指南
- 資料收集策略與排程規劃
- 資料庫設計與 ORM 模型
- 範例程式碼（收集器、排程器）
- 配置檔與環境設定
- 常見問題解答

**適用對象**：準備開始實作的開發者

**重點特色**：
- ✅ 完全使用免費功能
- ✅ 提供完整程式碼範例
- ✅ 包含實作流程與檢查清單

---

## 📖 快速導覽

### 新手入門
1. 閱讀 [README.md](../README.md) - 了解專案概述
2. 閱讀 [FinMind 實作指南](specifications/FINMIND_IMPLEMENTATION_GUIDE.md) - 學習 FinMind 實作方式
3. 依照實作流程開始建置

### 進階使用
1. 參考 [台股數據收集規格書](specifications/TWSE_DATA_COLLECTION_SPEC.md) - 了解完整資料收集策略
2. 探索 API 範例 - 學習不同資料源的整合方式
3. 查看 Notebooks - 了解資料分析應用

---

## 🗂️ 目錄說明

```
docs/
├── README.md                              # 本文件 - 文檔導覽
├── project-management/                    # 專案管理
│   ├── README.md                          # 管理文件導覽
│   ├── PROJECT_ROADMAP.md                 # 專案路線圖
│   └── DEVELOPMENT_SCHEDULE.md            # 開發時程表
├── specifications/                        # 規格書
│   ├── TWSE_DATA_COLLECTION_SPEC.md      # 台股數據收集規格書
│   └── FINMIND_IMPLEMENTATION_GUIDE.md   # FinMind 實作指南
├── api-examples/                          # API 使用範例
│   └── (待新增)
└── notebooks/                             # Jupyter 筆記本
    └── (待新增)
```

---

## 📋 規格書版本對照

| 文檔 | 版本 | 更新日期 | 主要內容 |
|------|------|---------|---------|
| TWSE_DATA_COLLECTION_SPEC.md | 1.0 | 2025-12-27 | 台股數據收集完整規格 |
| FINMIND_IMPLEMENTATION_GUIDE.md | 2.1 | 2025-12-28 | FinMind 免費版實作指南 |

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

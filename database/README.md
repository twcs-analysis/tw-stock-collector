# 資料庫架構說明

本目錄包含台股資料收集系統的資料庫 schema 定義、遷移腳本與相關配置。

---

## 📁 目錄結構

```
database/
├── schemas/                  # Schema 定義（版本控制）
│   ├── common/               # 通用 Schema（PostgreSQL + SQLite）
│   │   ├── 01-tables.sql     # 表格定義
│   │   ├── 02-indexes.sql    # 索引定義
│   │   └── 03-constraints.sql # 約束條件
│   ├── postgresql/           # PostgreSQL 專用
│   │   ├── 01-extensions.sql # 擴充功能
│   │   ├── 02-sequences.sql  # 序列定義
│   │   └── 03-triggers.sql   # 觸發器
│   └── sqlite/               # SQLite 專用
│       └── 01-pragmas.sql    # PRAGMA 設定與觸發器
│
├── migrations/               # 資料庫遷移（Alembic）
│   ├── versions/             # 遷移版本
│   ├── alembic.ini           # Alembic 配置
│   └── env.py                # Alembic 環境
│
├── seeds/                    # 測試資料
│   └── test_stocks.sql       # 股票基本資料
│
├── backups/                  # 資料庫備份（不納入 Git）
│   └── .gitkeep
│
├── sqlite/                   # SQLite 檔案儲存（不納入 Git）
│   ├── dev.db                # 開發環境
│   ├── test.db               # 測試環境
│   └── .gitkeep
│
└── README.md                 # 本說明文件
```

---

## 📊 資料表結構

### 核心資料表

| 表格名稱 | 說明 | 資料來源 | 更新頻率 |
|---------|------|---------|---------|
| \`stocks\` | 股票基本資料 | 手動維護 | 新股上市時 |
| \`stock_prices\` | 每日價格資料 | data/raw/price/ | 每交易日 |
| \`institutional_investors\` | 三大法人買賣超 | data/raw/institutional/ | 每交易日 |
| \`margin_trading\` | 融資融券資料 | data/raw/margin/ | 每交易日 |
| \`securities_lending\` | 借券賣出資料 | data/raw/lending/ | 每交易日 |
| \`top20_volume\` | 成交量前20名 | data/raw/top20_volume/ | 每交易日 |
| \`stock_analysis_daily\` | 技術分析寬表 | 計算產生 | 每交易日 |
| \`import_logs\` | 資料匯入日誌 | 系統自動 | 每次匯入 |

---

**最後更新**: 2026-02-01
**維護者**: tw-stock-collector 專案團隊

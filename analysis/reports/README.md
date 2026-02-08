# Analysis Reports

此目錄存放各種分析報告的輸出結果。

## 📁 目錄結構

```
analysis/reports/
├── 封關選股/          # 年線策略選股報告
│   ├── 2026-02-06/    # 按日期分層
│   │   ├── 年線選股_2026-02-06_*.txt
│   │   ├── 年線選股_2026-02-06_*.csv
│   │   └── 年線選股報告_2026-02-06.md
│   └── YYYY-MM-DD/    # 其他日期
└── [其他分析類型]/
```

## 📋 報告類型

### 1. 封關選股（年線策略）

**說明**：基於錢線百分百技術面分析，篩選年線附近的安全買點標的

**輸出檔案**：
- `年線選股_YYYY-MM-DD_HHMMSS.txt` - 完整選股結果（文字格式）
- `年線選股_YYYY-MM-DD_HHMMSS.csv` - CSV 格式（可用 Excel 開啟）
- `年線選股報告_YYYY-MM-DD.md` - Markdown 格式報告
- `年線選股清單_YYYY-MM-DD.md` - 選股清單與分類

**執行方式**：
```bash
export DB_PASSWORD=tw_stock_dev_password_2024
./analysis/封關選股/run.sh
```

**策略說明**：參考 [analysis/封關選股/README.md](../封關選股/README.md)

---

## 🗂️ 版本控制

### Git 控制策略

- ✅ **保留範例報告**：首次產生的報告作為範例（如 2026-02-06）
- ❌ **忽略後續報告**：每日自動產生的報告不納入版本控制
- 📁 **保留目錄結構**：透過 .gitkeep 保留空目錄結構

### 為什麼不版本控制所有報告？

1. **報告可重現**：使用相同的 SQL 和資料可重新產生報告
2. **減少 repo 大小**：避免累積大量重複的報告檔案
3. **保持靈活性**：本地可以產生任意日期的報告

---

## 📊 查看報告

### 文字格式（TXT）

```bash
# 查看最新報告
ls -t analysis/reports/封關選股/*/年線選股_*.txt | head -1 | xargs cat
```

### CSV 格式

```bash
# 用 Excel 或 Numbers 開啟
open analysis/reports/封關選股/2026-02-06/年線選股_2026-02-06_含ETF備註.csv
```

### Markdown 格式

```bash
# 在 VS Code 或 GitHub 上直接預覽
code analysis/reports/封關選股/2026-02-06/年線選股報告_2026-02-06.md
```

---

## 🧹 清理舊報告

```bash
# 刪除 7 天前的報告（保留最近 7 天）
find analysis/reports/封關選股/ -type f -mtime +7 -delete

# 只保留每週五的報告（其他刪除）
# TODO: 實作清理腳本
```

---

## 📝 新增其他分析報告

如需新增其他類型的分析報告，請遵循以下結構：

```
analysis/reports/
└── [分析名稱]/
    ├── README.md          # 說明此分析的用途
    ├── YYYY-MM-DD/        # 按日期分層
    │   └── 報告檔案
    └── .gitkeep
```

---

**最後更新**：2026-02-08

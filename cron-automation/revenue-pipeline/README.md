# Revenue Pipeline 自動化執行

自動執行月營收資料處理流程：智慧收集 → 匯入資料庫 → 展示結果

---

## 📁 檔案說明

- **run.sh**: 主執行腳本（呼叫 execute.sh + 日誌管理）
- **execute.sh**: 獨立執行腳本（直接執行 Pipeline 流程）
- **logs/**: 日誌目錄（以日期命名）
- **README.md**: 使用說明（本檔案）

---

## 🚀 使用方式

### 手動執行

```bash
# 在專案根目錄執行
./cron-automation/revenue-pipeline/run.sh

# 或指定完整路徑
/Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/revenue-pipeline/run.sh
```

### Cron 自動執行

編輯 crontab：
```bash
crontab -e
```

加入以下內容（日誌會自動儲存到 `logs/` 目錄）：

#### 範例 1：每天早上 8:30 執行

```cron
30 8 * * * /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/revenue-pipeline/run.sh
```

#### 範例 2：每月 1-10 號早上 8:30 執行（公告期）

```cron
30 8 1-10 * * /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/revenue-pipeline/run.sh
```

#### 範例 3：每週一早上 9:00 執行

```cron
0 9 * * 1 /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/revenue-pipeline/run.sh
```

**注意**：日誌會自動儲存到 `cron-automation/revenue-pipeline/logs/YYYY-MM-DD.log`，不需要手動重導向。

---

## 📊 執行內容

腳本會自動執行以下步驟：

1. ✅ **確認 PostgreSQL 啟動**（自動檢查並啟動）
2. ✅ **檢查 monthly 完整資料**（若有新月份則保存）
3. ✅ **智慧收集目標月營收**（自動判斷 daily/monthly 模式）
4. ✅ **匯入資料庫**（寫入 `stock_revenues` 表）
5. ✅ **展示最新月份營收**（隨機挑選 8 檔股票，表格格式）

---

## 🔧 環境需求

- **Claude CLI**: 已安裝並可執行
- **PostgreSQL**: 資料庫已啟動
- **環境變數**: `DB_PASSWORD` 已設定（或使用預設值）

---

## 📝 日誌查看

日誌檔案位置：`cron-automation/revenue-pipeline/logs/YYYY-MM-DD.log`

### 查看今天的日誌

```bash
cat cron-automation/revenue-pipeline/logs/$(date '+%Y-%m-%d').log
```

### 查看最後 50 行

```bash
tail -50 cron-automation/revenue-pipeline/logs/$(date '+%Y-%m-%d').log
```

### 即時監控

```bash
tail -f cron-automation/revenue-pipeline/logs/$(date '+%Y-%m-%d').log
```

### 查看所有日誌檔案

```bash
ls -lh cron-automation/revenue-pipeline/logs/
```

### 查看特定日期的日誌

```bash
cat cron-automation/revenue-pipeline/logs/2026-02-07.log
```

---

## ⚙️ 自訂設定

### 修改執行參數

編輯 `execute.sh` 或在 `run.sh` 中傳遞參數：

```bash
# 原始指令（使用預設參數）
./cron-automation/revenue-pipeline/run.sh

# 指定年月
./cron-automation/revenue-pipeline/execute.sh --year-month 2026-01

# 增加展示數量
./cron-automation/revenue-pipeline/execute.sh --sample 15

# 測試模式（不實際儲存）
./cron-automation/revenue-pipeline/execute.sh --dry-run

# 組合參數
./cron-automation/revenue-pipeline/execute.sh --year-month 2026-01 --sample 15
```

### 修改日誌路徑

修改 crontab 中的 `>> /tmp/revenue-pipeline.log` 為您想要的路徑。

---

## 🐛 故障排除

### 腳本無法執行

```bash
# 確認執行權限
ls -l cron-automation/revenue-pipeline/run.sh

# 若無執行權限，賦予權限
chmod +x cron-automation/revenue-pipeline/run.sh
```

### Cron 未執行

```bash
# 檢查 cron 服務狀態（macOS）
launchctl list | grep cron

# 查看系統日誌
tail -f /var/log/system.log | grep cron
```

### 資料庫連線失敗

```bash
# 確認 PostgreSQL 狀態
brew services list | grep postgresql

# 手動啟動
brew services start postgresql@17

# 測試連線
psql-17 -h localhost -U postgres -d tw_stock -c "SELECT 1;"
```

### API 請求超時

```bash
# 症狀：Step 2 顯示 "Read timed out" 錯誤
# 原因：網路不穩定或 API 暫時不可用
# 影響：Step 2 會跳過，但不影響後續步驟執行

# 解決方案：
# 1. 檢查網路連線
# 2. 稍後重新執行
# 3. Step 2 失敗不影響主要收集流程（Step 3）
```

---

## 📅 建議執行時間

| 日期範圍 | 建議執行時間 | 原因 |
|---------|-------------|------|
| 1-10 號 | 每天早上 8:30 | 公告期，漸進式收集 |
| 11-31 號 | 每週一次 | 非公告期，維護完整資料 |

---

## 🔗 相關檔案

- **執行腳本**: `cron-automation/revenue-pipeline/execute.sh`（獨立執行）
- **Skill 定義**: `.claude/skills/revenue-pipeline/SKILL.md`（互動式使用）
- **執行指令**: `.claude/skills/revenue-pipeline/instructions.md`
- **收集腳本**: `scripts/data-collector/collect_revenue.py`
- **匯入腳本**: `scripts/data-importer/import.sh`

---

**建立日期**: 2026-02-07
**維護者**: Jason Huang

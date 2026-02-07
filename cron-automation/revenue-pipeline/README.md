# Revenue Pipeline 自動化執行

自動執行月營收資料處理流程：智慧收集 → 匯入資料庫 → 展示結果

---

## 📁 檔案說明

- **run.sh**: 執行腳本（執行 `/revenue-pipeline` skill）
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

1. ✅ **檢查 monthly 完整資料**（若有新月份則保存）
2. ✅ **智慧收集目標月營收**（自動判斷 daily/monthly 模式）
3. ✅ **匯入資料庫**（寫入 `stock_revenues` 表）
4. ✅ **隨機展示 5-10 檔股票**（月增率、年增率）

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

編輯 `run.sh`，修改 Claude 指令：

```bash
# 原始指令
claude "/revenue-pipeline"

# 指定年月
claude "/revenue-pipeline --year-month 2026-01"

# 增加展示數量
claude "/revenue-pipeline --sample 15"

# 測試模式（不實際儲存）
claude "/revenue-pipeline --dry-run"
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

### Claude 找不到

```bash
# 確認 Claude CLI 已安裝
which claude

# 若未安裝，請參考 Claude Code 安裝文件
```

---

## 📅 建議執行時間

| 日期範圍 | 建議執行時間 | 原因 |
|---------|-------------|------|
| 1-10 號 | 每天早上 8:30 | 公告期，漸進式收集 |
| 11-31 號 | 每週一次 | 非公告期，維護完整資料 |

---

## 🔗 相關檔案

- **Skill 定義**: `.claude/skills/revenue-pipeline/SKILL.md`
- **執行指令**: `.claude/skills/revenue-pipeline/instructions.md`
- **收集腳本**: `scripts/data-collector/collect_revenue.py`
- **匯入腳本**: `scripts/data-importer/import.sh`

---

**建立日期**: 2026-02-07
**維護者**: Jason Huang

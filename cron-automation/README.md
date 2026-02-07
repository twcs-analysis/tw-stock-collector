# Cron Automation 自動化執行目錄

此目錄包含所有可透過 cron 自動執行的腳本，依功能分類到子目錄。

---

## 📁 目錄結構

```
cron-automation/
├── README.md                    # 本檔案
├── revenue-pipeline/            # 月營收資料處理
│   ├── run.sh                   # 執行腳本
│   ├── execute.sh               # 獨立執行腳本
│   └── README.md                # 使用說明
└── yt-finance-show/             # 理財達人秀影片處理
    ├── run.sh                   # 執行腳本
    ├── execute.sh               # 獨立執行腳本
    ├── analyze_transcript.py    # AI 分析腳本
    └── README.md                # 使用說明
```

---

## 🎯 可用的自動化任務

### 1. Revenue Pipeline（月營收資料處理）

**路徑**: `cron-automation/revenue-pipeline/`

**功能**:
- 智慧收集月營收資料（自動判斷 daily/monthly 模式）
- 匯入資料到 PostgreSQL
- 隨機展示 5-10 檔股票營收數據

**執行**:
```bash
./cron-automation/revenue-pipeline/run.sh
```

**Cron 設定**:
```cron
# 每天早上 8:30 執行
30 8 * * * /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/revenue-pipeline/run.sh
```

**詳細說明**: 請參考 [revenue-pipeline/README.md](revenue-pipeline/README.md)

---

### 2. YT Finance Show（理財達人秀影片處理）

**路徑**: `cron-automation/yt-finance-show/`

**功能**:
- 自動抓取理財達人秀 YouTube 頻道最新影片
- 使用 whisper-cpp 轉換為中文逐字稿
- AI 分析並產生結構化報告

**執行**:
```bash
./cron-automation/yt-finance-show/run.sh
```

**Cron 設定**:
```cron
# 每天晚上 22:00 執行（理財達人秀通常晚上 8-9 點播出）
0 22 * * * /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/yt-finance-show/run.sh
```

**詳細說明**: 請參考 [yt-finance-show/README.md](yt-finance-show/README.md)

---

## 📋 使用指南

### 基本步驟

1. **選擇要執行的任務**
   - 進入對應的子目錄
   - 閱讀該目錄的 README.md

2. **測試手動執行**
   ```bash
   ./cron-automation/<任務目錄>/run.sh
   ```

3. **設定 Cron 自動執行**
   ```bash
   crontab -e
   ```

4. **查看日誌**
   ```bash
   tail -f /tmp/<任務名稱>.log
   ```

---

## 🔧 Cron 時間格式

```
┌───────────── 分鐘 (0-59)
│ ┌─────────── 小時 (0-23)
│ │ ┌───────── 日期 (1-31)
│ │ │ ┌─────── 月份 (1-12)
│ │ │ │ ┌───── 星期 (0-7，0和7都是星期日)
│ │ │ │ │
* * * * * 指令
```

### 常用範例

```cron
# 每天早上 8:30
30 8 * * *

# 每週一早上 9:00
0 9 * * 1

# 每月 1 號早上 10:00
0 10 1 * *

# 每月 1-10 號早上 8:30（公告期）
30 8 1-10 * *

# 每小時執行
0 * * * *

# 每 30 分鐘執行
*/30 * * * *
```

---

## 📝 日誌管理

### 日誌路徑建議

- **專案日誌**: `/tmp/<任務名稱>.log`（暫存，重開機會清空）
- **永久日誌**: `~/logs/<任務名稱>.log`（永久保存）
- **系統日誌**: `/var/log/<任務名稱>.log`（需 root 權限）

### 日誌輪替

建立日誌輪替配置 `/etc/logrotate.d/tw-stock-collector`：

```
/tmp/revenue-pipeline.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

---

## 🐛 故障排除

### Cron 未執行

1. **檢查 cron 服務**
   ```bash
   # macOS
   launchctl list | grep cron

   # Linux
   sudo systemctl status cron
   ```

2. **檢查 crontab 語法**
   ```bash
   crontab -l
   ```

3. **查看系統日誌**
   ```bash
   # macOS
   tail -f /var/log/system.log | grep cron

   # Linux
   sudo tail -f /var/log/syslog | grep CRON
   ```

### 腳本執行失敗

1. **確認執行權限**
   ```bash
   chmod +x cron-automation/*/run.sh
   ```

2. **手動測試執行**
   ```bash
   ./cron-automation/<任務目錄>/run.sh
   ```

3. **檢查日誌輸出**
   ```bash
   tail -100 /tmp/<任務名稱>.log
   ```

---

## 📊 監控與通知

### 執行狀態監控

建立監控腳本 `cron-automation/check_status.sh`：

```bash
#!/bin/bash
LOGFILE="/tmp/revenue-pipeline.log"

if [ -f "$LOGFILE" ]; then
    LAST_RUN=$(grep "結束時間" "$LOGFILE" | tail -1)
    STATUS=$(grep "執行狀態" "$LOGFILE" | tail -1)
    echo "最後執行: $LAST_RUN"
    echo "$STATUS"
else
    echo "尚未執行或日誌不存在"
fi
```

### 郵件通知（選用）

修改 cron 指令加入郵件通知：

```cron
MAILTO=your@email.com
30 8 * * * /path/to/run.sh >> /tmp/revenue-pipeline.log 2>&1
```

---

## 🔐 安全注意事項

1. **環境變數**
   - 避免在腳本中硬編碼密碼
   - 使用 `~/.bash_profile` 或 `~/.zshrc` 設定環境變數

2. **執行權限**
   - 腳本檔案建議權限：`755` (rwxr-xr-x)
   - 日誌檔案建議權限：`644` (rw-r--r--)

3. **日誌安全**
   - 避免日誌中記錄敏感資訊（密碼、API key）
   - 定期清理舊日誌

---

## 📖 相關文檔

- [Claude Code 文檔](https://docs.anthropic.com/claude/docs/claude-code)
- [Cron 使用指南](https://man7.org/linux/man-pages/man5/crontab.5.html)
- [專案 CLAUDE.md](../CLAUDE.md)

---

**建立日期**: 2026-02-07
**維護者**: Jason Huang
**版本**: 1.0.0

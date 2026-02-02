# 資料庫管理 - 快速上手

5 分鐘快速設定和使用資料庫管理工具。

---

## ⚡ 快速開始

### 1. 設定環境變數

```bash
export DB_PASSWORD=tw_stock_dev_password_2024
```

💡 **小技巧**：將此命令加入 `~/.bashrc` 或 `~/.zshrc`，避免每次都要設定。

---

### 2. 初始化資料庫（首次使用）

```bash
# 建立所有資料表
./scripts/database/init_database.sh
```

**預期輸出**：
```
========================================
資料庫初始化腳本
========================================

[INFO] 檢查資料庫連線...
✓ 資料庫連線成功
[INFO] 開始初始化資料庫...

✓ 成功建立 8 個資料表:
  - import_logs
  - institutional_investors
  - margin_trading
  - securities_lending
  - stock_analysis_daily
  - stock_prices
  - stocks
  - top20_volume

✓ 所有預期的資料表都已建立

========================================
[SUCCESS] 資料庫初始化完成
========================================
```

---

### 3. 查看資料庫狀態

```bash
# 查詢資料庫統計資訊
./scripts/database/check_status.sh
```

**顯示內容**：
- ✅ 資料庫連線狀態
- ✅ 所有資料表統計
- ✅ 資料範圍和分布
- ✅ 最近匯入記錄

---

## 📋 常用命令

### 初始化相關

```bash
# 檢查說明
./scripts/database/init_database.sh --help

# 初始化（保留現有資料）
./scripts/database/init_database.sh

# 刪除並重建（謹慎！）
./scripts/database/init_database.sh --drop-existing
```

### 狀態查詢

```bash
# 完整狀態報告
./scripts/database/check_status.sh

# 搭配 grep 篩選
./scripts/database/check_status.sh | grep "stock_prices"
```

---

## 🔄 完整工作流程範例

### 情境 1：全新安裝

```bash
# Step 1: 設定密碼
export DB_PASSWORD=tw_stock_dev_password_2024

# Step 2: 初始化資料庫
./scripts/database/init_database.sh

# Step 3: 匯入資料
./scripts/data-importer/import_date_range.sh 2024-01-02 2026-02-02

# Step 4: 查看狀態
./scripts/database/check_status.sh

# Step 5: 轉換技術指標
./scripts/data-transformer/transform.sh today
```

**預計時間**：約 5-10 分鐘（視資料量而定）

---

### 情境 2：資料庫損壞，需要重建

```bash
export DB_PASSWORD=tw_stock_dev_password_2024

# Step 1: 刪除並重建資料表
./scripts/database/init_database.sh --drop-existing
# 輸入 "yes" 確認刪除

# Step 2: 重新匯入資料
./scripts/data-importer/import_date_range.sh 2024-01-02 2026-02-02

# Step 3: 驗證
./scripts/database/check_status.sh
```

**⚠️ 警告**：此操作會刪除所有資料，請確保已備份！

---

### 情境 3：日常維護檢查

```bash
export DB_PASSWORD=tw_stock_dev_password_2024

# 查看資料庫狀態
./scripts/database/check_status.sh

# 如果發現資料缺失，匯入最新資料
./scripts/data-importer/import_date_range.sh 2026-02-01 2026-02-28

# 再次檢查
./scripts/database/check_status.sh
```

---

## 🎯 快速診斷

### 問題：無法連線資料庫

```bash
✗ 資料庫連線失敗: connection refused
```

**檢查清單**：
1. ✅ PostgreSQL 是否已啟動？
2. ✅ DB_PASSWORD 是否正確設定？
3. ✅ 資料庫名稱是否為 `tw_stock`？

**解決方式**：
```bash
# 檢查 PostgreSQL 狀態（macOS）
brew services list | grep postgres

# 啟動 PostgreSQL（macOS）
brew services start postgresql@14

# 確認資料庫存在
psql -U postgres -l | grep tw_stock
```

---

### 問題：資料表為空

```bash
✓ stock_prices
    記錄數: 0
```

**解決方式**：
```bash
# 匯入資料
./scripts/data-importer/import_date_range.sh 2024-01-02 2026-02-02
```

---

### 問題：資料表不存在

```bash
✗ stocks - 股票基本資訊 (不存在)
```

**解決方式**：
```bash
# 重新初始化資料庫
./scripts/database/init_database.sh
```

---

## 💡 實用技巧

### 技巧 1：建立命令別名

在 `~/.bashrc` 或 `~/.zshrc` 中加入：

```bash
# 資料庫管理別名
export DB_PASSWORD=tw_stock_dev_password_2024

alias db-init='./scripts/database/init_database.sh'
alias db-status='./scripts/database/check_status.sh'
alias db-import='./scripts/data-importer/import_date_range.sh'
alias db-transform='./scripts/data-transformer/transform.sh'
```

使用方式：
```bash
db-status              # 查看狀態
db-import 2026-02-01 2026-02-28  # 匯入資料
db-transform today     # 轉換今天的資料
```

---

### 技巧 2：定期自動檢查

建立 cron job 每天檢查資料庫狀態：

```bash
# 編輯 crontab
crontab -e

# 每天早上 9 點檢查並記錄
0 9 * * * cd /path/to/tw-stock-collector && \
    export DB_PASSWORD=your_password && \
    ./scripts/database/check_status.sh >> /var/log/db-status.log 2>&1
```

---

### 技巧 3：快速備份

```bash
# 備份資料庫
pg_dump -h localhost -U postgres tw_stock > backup_$(date +%Y%m%d).sql

# 還原資料庫
psql -h localhost -U postgres tw_stock < backup_20260202.sql
```

---

## 🔗 下一步

資料庫設定完成後，可以：

1. **匯入資料** → [資料匯入快速指南](../data-importer/QUICK_START.md)
2. **轉換技術指標** → [技術分析快速指南](../data-transformer/QUICKSTART.md)
3. **查看完整文檔** → [資料庫管理 README](README.md)

---

## 📞 需要幫助？

- 查看完整文檔：[README.md](README.md)
- 查看專案說明：[../../README.md](../../README.md)
- 查看故障排除：[README.md#疑難排解](README.md#疑難排解)

---

**最後更新**: 2026-02-02
**預計閱讀時間**: 5 分鐘

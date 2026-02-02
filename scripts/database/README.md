# 資料庫管理腳本

此目錄包含資料庫初始化、管理和查詢的腳本工具。

## 📋 腳本列表

### 1. `init_database.sh` - 資料庫初始化

初始化資料庫 schema，建立所有資料表、索引和約束。

**功能**：
- ✅ 建立所有資料表
- ✅ 建立索引和約束
- ✅ 驗證資料庫結構
- ✅ 支援刪除現有資料表並重建

**使用方式**：

```bash
# 設定資料庫密碼
export DB_PASSWORD=your_password

# 初始化資料庫（保留現有資料）
./scripts/database/init_database.sh

# 刪除現有資料表並重新建立（謹慎使用！）
./scripts/database/init_database.sh --drop-existing
```

**環境變數**：
- `DB_HOST` - 資料庫主機（預設: localhost）
- `DB_PORT` - 資料庫埠號（預設: 5432）
- `DB_NAME` - 資料庫名稱（預設: tw_stock）
- `DB_USER` - 資料庫使用者（預設: postgres）
- `DB_PASSWORD` - 資料庫密碼（必要）

---

### 2. `check_status.sh` - 資料庫狀態查詢

查詢資料庫連線狀態、資料表統計和資料範圍。

**功能**：
- ✅ 檢查資料庫連線
- ✅ 顯示所有資料表統計
- ✅ 顯示資料範圍和分布
- ✅ 顯示最近匯入記錄

**使用方式**：

```bash
# 設定資料庫密碼
export DB_PASSWORD=your_password

# 查詢資料庫狀態
./scripts/database/check_status.sh
```

**輸出範例**：

```
======================================================================
資料庫狀態查詢
======================================================================

✓ 資料庫連線成功

資料庫資訊:
  主機: localhost:5432
  資料庫: tw_stock
  使用者: postgres

資料表統計:
  總數: 8 個資料表

核心資料表:
  ✓ stocks
      描述: 股票基本資訊
      記錄數: 2,019
      結構: 5 欄位, 0 索引

  ✓ stock_prices
      描述: 每日價格資料
      記錄數: 958,793
      結構: 9 欄位, 4 索引
      日期範圍: 2024-01-02 ~ 2026-02-02 (513 個交易日)

stock_prices 詳細統計:
  股票總數: 2,019 檔
  總記錄數: 958,793 筆
  交易日數: 513 天
  日期範圍: 2024-01-02 ~ 2026-02-02

  年度分布:
    2024: 242 個交易日, 445,184 筆記錄
    2025: 249 個交易日, 470,725 筆記錄
    2026:  22 個交易日,  42,884 筆記錄
```

---

## 🔄 完整工作流程

### 首次設定

```bash
# 1. 設定環境變數
export DB_PASSWORD=tw_stock_dev_password_2024

# 2. 初始化資料庫
./scripts/database/init_database.sh

# 3. 匯入歷史資料
./scripts/data-importer/import_date_range.sh 2024-01-02 2026-02-02

# 4. 查看資料庫狀態
./scripts/database/check_status.sh

# 5. 轉換技術指標
./scripts/data-transformer/transform.sh today
```

### 重建資料庫

```bash
# 警告：此操作會刪除所有資料！
export DB_PASSWORD=tw_stock_dev_password_2024

# 1. 刪除並重建資料表
./scripts/database/init_database.sh --drop-existing

# 2. 重新匯入資料
./scripts/data-importer/import_date_range.sh 2024-01-02 2026-02-02
```

### 日常維護

```bash
export DB_PASSWORD=tw_stock_dev_password_2024

# 查看資料庫狀態
./scripts/database/check_status.sh

# 匯入最新資料
./scripts/data-importer/import_date_range.sh 2026-02-01 2026-02-28

# 轉換技術指標
./scripts/data-transformer/transform.sh latest 7
```

---

## 📊 資料表說明

### 核心資料表（8 個）

| 資料表 | 說明 | 主要欄位 |
|--------|------|----------|
| `stocks` | 股票基本資訊 | stock_id, stock_name, market_type |
| `stock_prices` | 每日價格資料 | trade_date, stock_id, open, high, low, close, volume, amount |
| `institutional_investors` | 三大法人買賣超 | trade_date, stock_id, foreign_net, trust_net, dealer_net |
| `margin_trading` | 融資融券 | trade_date, stock_id, margin_balance, short_balance |
| `securities_lending` | 借券賣出 | trade_date, stock_id, lending_balance |
| `top20_volume` | 成交量前 20 名 | trade_date, rank, stock_id, volume |
| `stock_analysis_daily` | 技術分析寬表 | trade_date, stock_id, ma_5, rsi_14, macd_dif, ... (30+ 指標) |
| `import_logs` | 匯入記錄 | import_date, data_type, status, records_count |

---

## ⚠️ 注意事項

### 資料庫密碼

- **絕對不要** 將密碼硬編碼在腳本中
- **務必使用** 環境變數傳遞密碼
- **建議設定** `.bashrc` 或 `.zshrc` 中的別名：

```bash
# 在 ~/.bashrc 或 ~/.zshrc 中加入
alias db-init='export DB_PASSWORD=your_password && ./scripts/database/init_database.sh'
alias db-status='export DB_PASSWORD=your_password && ./scripts/database/check_status.sh'
```

### 刪除資料

- `--drop-existing` 選項會刪除所有資料，**無法復原**
- 使用前請務必備份重要資料
- 刪除操作需要使用者確認（輸入 `yes`）

### 效能考量

- 大量資料匯入建議使用批次操作
- 建議在非營業時間進行大規模資料維護
- 定期執行 `VACUUM` 和 `ANALYZE` 優化資料庫效能

---

## 🔗 相關文件

- [資料匯入腳本](../data-importer/README.md) - 資料匯入工具
- [技術分析轉換器](../data-transformer/README.md) - 技術指標計算
- [資料庫 Schema](../../services/common/database/README.md) - ORM 模型定義
- [專案說明](../../README.md) - 專案整體架構

---

## 🆘 疑難排解

### 連線失敗

```bash
✗ 資料庫連線失敗: connection refused
```

**解決方式**：
1. 確認 PostgreSQL 已啟動
2. 檢查連線參數（主機、埠號、資料庫名稱）
3. 確認防火牆設定

### 權限不足

```bash
✗ permission denied for table stocks
```

**解決方式**：
1. 確認資料庫使用者有足夠權限
2. 以資料庫管理員身份執行初始化

### 資料表已存在

```bash
✗ relation "stocks" already exists
```

**解決方式**：
1. 使用 `--drop-existing` 選項重建
2. 或手動刪除衝突的資料表

---

**維護日期**: 2026-02-02
**維護者**: Jason Huang

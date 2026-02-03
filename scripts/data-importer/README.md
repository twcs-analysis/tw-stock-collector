# 台股資料匯入工具

將原始資料（JSON）和技術分析資料（CSV）匯入到 PostgreSQL 資料庫。

## 📋 目錄

- [快速開始](#快速開始)
- [資料類型](#資料類型)
- [使用方式](#使用方式)
- [環境設定](#環境設定)
- [範例](#範例)
- [進階用法](#進階用法)
- [常見問題](#常見問題)

---

## 🚀 快速開始

### 1. 設定資料庫密碼

```bash
export DB_PASSWORD=tw_stock_dev_password_2024
```

### 2. 匯入資料

```bash
# 匯入單日價格資料
./scripts/data-importer/import.sh price --date 2026-02-03

# 匯入技術分析資料
./scripts/data-importer/import.sh technical --date 2026-02-03

# 匯入所有類型
./scripts/data-importer/import.sh all --date 2026-02-03
```

---

## 📊 資料類型

### 原始資料類型（來源：JSON）

從 `data/raw/` 目錄讀取 JSON 檔案：

| 類型 | 說明 | 資料表 | 來源檔案 |
|------|------|--------|----------|
| `price` | 每日價量資料 | `stock_prices` | `data/raw/price/YYYY/MM/YYYY-MM-DD.json` |
| `institutional` | 三大法人買賣超 | `institutional_investors` | `data/raw/institutional/...` |
| `margin` | 融資融券 | `margin_trading` | `data/raw/margin/...` |
| `lending` | 借券賣出 | `securities_lending` | `data/raw/lending/...` |
| `top20_volume` | 成交量前20名 | `top20_volume` | `data/raw/top20_volume/...` |

### 技術分析資料（來源：CSV）

從 `data/transformed/technical/` 目錄讀取 CSV 檔案：

| 類型 | 說明 | 資料表 | 來源檔案 |
|------|------|--------|----------|
| `technical` | 30+ 技術指標 | `stock_analysis_daily` | `data/transformed/technical/YYYY-MM-DD_all.csv` |

**技術指標包含**：
- 移動平均線（MA5, MA10, MA20, MA60, MA120, MA240）
- RSI 指標（RSI6, RSI14）
- MACD 指標（DIF, DEA, HIST）
- DMI/ADX 指標
- 布林通道（上軌、中軌、下軌）
- 成交量分析（量比、VWAP、均量）

---

## 💻 使用方式

### 基本語法

```bash
./scripts/data-importer/import.sh <資料類型> <日期選項> [其他參數]
```

### 資料類型選項

```bash
# 單一類型
./import.sh price --date 2026-02-03

# 多個類型（逗號分隔）
./import.sh price,institutional,margin --date 2026-02-03

# 所有原始資料類型
./import.sh all --date 2026-02-03

# 技術分析資料
./import.sh technical --date 2026-02-03
```

### 日期選項

```bash
# 匯入單一日期
./import.sh price --date 2026-02-03

# 匯入日期區間
./import.sh price --start 2026-01-01 --end 2026-01-31
```

### 完整參數列表

```bash
./scripts/data-importer/import.sh --help
```

**主要參數**：
- `--date YYYY-MM-DD` - 匯入單一日期
- `--start YYYY-MM-DD` - 日期區間起始
- `--end YYYY-MM-DD` - 日期區間結束
- `--db-password PASSWORD` - 資料庫密碼
- `--log-level LEVEL` - 日誌等級（DEBUG/INFO/WARNING/ERROR）

**進階參數**：
- `--data-root PATH` - 原始資料根目錄（預設：data/raw）
- `--data-dir PATH` - 技術分析資料目錄（預設：data/transformed/technical）
- `--db-host HOST` - 資料庫主機
- `--db-port PORT` - 資料庫埠號
- `--db-name NAME` - 資料庫名稱
- `--db-user USER` - 資料庫使用者

---

## ⚙️ 環境設定

### 資料庫連線資訊

**方法 1：環境變數（推薦）**

```bash
# 設定環境變數
export DB_PASSWORD=tw_stock_dev_password_2024
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=tw_stock
export DB_USER=postgres

# 執行匯入
./scripts/data-importer/import.sh price --date 2026-02-03
```

**方法 2：命令列參數**

```bash
./scripts/data-importer/import.sh price --date 2026-02-03 \
  --db-password tw_stock_dev_password_2024 \
  --db-host localhost \
  --db-port 5432
```

**方法 3：.env 檔案**

在專案根目錄建立 `.env` 檔案（已在 .gitignore 中）：

```bash
DB_PASSWORD=tw_stock_dev_password_2024
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tw_stock
DB_USER=postgres
```

---

## 📝 範例

### 1. 匯入單日資料

```bash
# 設定密碼
export DB_PASSWORD=tw_stock_dev_password_2024

# 匯入單日價格資料
./scripts/data-importer/import.sh price --date 2026-02-03

# 匯入單日技術分析
./scripts/data-importer/import.sh technical --date 2026-02-03

# 匯入單日所有原始資料
./scripts/data-importer/import.sh all --date 2026-02-03
```

### 2. 匯入日期區間

```bash
export DB_PASSWORD=tw_stock_dev_password_2024

# 匯入一個月的價格資料
./scripts/data-importer/import.sh price \
  --start 2026-01-01 \
  --end 2026-01-31

# 匯入一週的技術分析資料
./scripts/data-importer/import.sh technical \
  --start 2026-01-27 \
  --end 2026-01-31
```

### 3. 匯入多種類型

```bash
export DB_PASSWORD=tw_stock_dev_password_2024

# 匯入價格 + 法人 + 融資融券
./scripts/data-importer/import.sh price,institutional,margin \
  --date 2026-02-03

# 匯入所有原始資料類型
./scripts/data-importer/import.sh all --date 2026-02-03
```

### 4. 完整匯入流程（原始資料 + 技術分析）

```bash
export DB_PASSWORD=tw_stock_dev_password_2024

# 設定日期
TARGET_DATE="2026-02-03"

# 1. 匯入原始資料
./scripts/data-importer/import.sh all --date "$TARGET_DATE"

# 2. 匯入技術分析
./scripts/data-importer/import.sh technical --date "$TARGET_DATE"

echo "✅ $TARGET_DATE 所有資料匯入完成"
```

### 5. 批次匯入最近 N 天

```bash
export DB_PASSWORD=tw_stock_dev_password_2024

# 匯入最近 7 天的所有資料
DAYS_AGO=7
START_DATE=$(date -v-${DAYS_AGO}d +%Y-%m-%d)  # macOS
# START_DATE=$(date -d "$DAYS_AGO days ago" +%Y-%m-%d)  # Linux
END_DATE=$(date +%Y-%m-%d)

echo "匯入 $START_DATE 到 $END_DATE 的資料..."

# 匯入原始資料
./scripts/data-importer/import.sh all \
  --start "$START_DATE" \
  --end "$END_DATE"

# 匯入技術分析
./scripts/data-importer/import.sh technical \
  --start "$START_DATE" \
  --end "$END_DATE"
```

### 6. 每日自動化腳本

建立 `daily_import.sh` 函數：

```bash
#!/bin/bash
export DB_PASSWORD=tw_stock_dev_password_2024

daily_import() {
    local target_date="${1:-$(date +%Y-%m-%d)}"

    echo "=========================================="
    echo "開始匯入 $target_date 的資料"
    echo "=========================================="

    # 匯入所有原始資料類型
    echo "1. 匯入原始資料..."
    ./scripts/data-importer/import.sh all --date "$target_date"

    if [ $? -ne 0 ]; then
        echo "❌ 原始資料匯入失敗"
        return 1
    fi

    # 匯入技術分析
    echo "2. 匯入技術分析..."
    ./scripts/data-importer/import.sh technical --date "$target_date"

    if [ $? -ne 0 ]; then
        echo "❌ 技術分析匯入失敗"
        return 1
    fi

    echo "=========================================="
    echo "✅ $target_date 所有資料匯入完成"
    echo "=========================================="
}

# 執行每日匯入（預設今天，或指定日期）
daily_import "2026-02-03"
```

### 7. Cron 定時任務

每天自動匯入前一天的資料：

```bash
# 編輯 crontab
crontab -e

# 每天早上 8:00 執行，匯入前一天的原始資料
0 8 * * * cd /path/to/tw-stock-collector && export DB_PASSWORD=your_password && ./scripts/data-importer/import.sh all --date $(date -d 'yesterday' +\%Y-\%m-\%d) >> /var/log/stock-import.log 2>&1

# 每天早上 8:30 執行，匯入技術分析
30 8 * * * cd /path/to/tw-stock-collector && export DB_PASSWORD=your_password && ./scripts/data-importer/import.sh technical --date $(date -d 'yesterday' +\%Y-\%m-\%d) >> /var/log/stock-import.log 2>&1
```

---

## 🔧 進階用法

### 1. 自訂資料目錄

```bash
# 技術分析資料在其他位置
./scripts/data-importer/import.sh technical --date 2026-02-03 \
  --data-dir /custom/path/technical

# 原始資料在其他位置
./scripts/data-importer/import.sh price --date 2026-02-03 \
  --data-root /custom/path/raw
```

### 2. 調整日誌等級

```bash
# 顯示詳細除錯資訊
./scripts/data-importer/import.sh price --date 2026-02-03 \
  --log-level DEBUG

# 只顯示錯誤
./scripts/data-importer/import.sh price --date 2026-02-03 \
  --log-level ERROR
```

### 3. 直接使用 Python 腳本

如果需要更精細的控制，可以直接調用 Python 腳本：

```bash
# 原始資料匯入
python scripts/data-importer/import_data.py \
  --date 2026-02-03 \
  --types price institutional

# 技術分析匯入
python scripts/data-importer/import_technical_analysis.py \
  --date 2026-02-03
```

---

## ❓ 常見問題

### Q1: 資料庫連線失敗 - "no password supplied"

**A**: 確認已設定 `DB_PASSWORD` 環境變數：

```bash
export DB_PASSWORD=tw_stock_dev_password_2024
./scripts/data-importer/import.sh price --date 2026-02-03
```

### Q2: 檔案找不到 - "File not found"

**A**: 檢查資料檔案是否存在：

```bash
# 原始資料
ls data/raw/price/2026/02/2026-02-03.json

# 技術分析資料
ls data/transformed/technical/2026-02-03_all.csv
```

### Q3: 如何重新匯入資料？

**A**: 系統使用 UPSERT 機制，重複匯入會自動更新：

```bash
# 直接重新執行即可，會覆蓋舊資料
./scripts/data-importer/import.sh price --date 2026-02-03
```

### Q4: 如何查看匯入記錄？

**A**: 查詢 `import_logs` 表格：

```sql
-- 查看最近的匯入記錄
SELECT * FROM import_logs
ORDER BY start_time DESC
LIMIT 10;

-- 查看特定日期的匯入狀態
SELECT * FROM import_logs
WHERE import_date = '2026-02-03';
```

### Q5: 匯入速度慢怎麼辦？

**A**: 優化建議：

1. **批次匯入**：使用日期區間而非逐日匯入
2. **檢查索引**：確保資料庫索引已建立
3. **調整批次大小**：修改 Python 腳本中的批次參數
4. **使用 PostgreSQL**：比 SQLite 快得多

### Q6: 支援其他資料庫嗎？

**A**: 目前支援：
- ✅ PostgreSQL（推薦）
- ✅ SQLite
- ⚠️ MySQL（需額外設定）

### Q7: 如何匯出資料？

**A**: 使用 PostgreSQL 的 COPY 命令：

```sql
-- 匯出為 CSV
COPY stock_prices TO '/path/to/output.csv' CSV HEADER;

-- 匯出技術分析資料
COPY stock_analysis_daily TO '/path/to/technical.csv' CSV HEADER;
```

---

## 📁 檔案結構

```
scripts/data-importer/
├── import.sh                          # 統一入口腳本（執行此檔案）
├── import_data.py                     # 原始資料匯入器
├── import_technical_analysis.py       # 技術分析匯入器
└── README.md                          # 本文件
```

**內部模組**（不需直接調用）：

```
services/data-importer/app/
├── db/                                # 資料庫連線管理
├── importers/                         # 各類資料匯入器
│   ├── price_importer.py
│   ├── institutional_importer.py
│   ├── margin_importer.py
│   ├── lending_importer.py
│   ├── top20_volume_importer.py
│   └── analysis_importer.py
└── main.py                            # 主程式入口
```

---

## 🔐 安全注意事項

1. **不要提交密碼到 Git**
   - 使用環境變數
   - `.env` 檔案已在 `.gitignore` 中

2. **生產環境建議**
   - 使用 AWS Secrets Manager 或類似服務
   - 限制資料庫使用者權限
   - 定期更換密碼

3. **日誌安全**
   - 日誌不會記錄密碼
   - 注意日誌檔案的存取權限

---

## 📞 支援

如有問題或建議：
1. 查看本 README 的常見問題
2. 檢查 GitHub Issues
3. 建立新的 Issue

---

## 📝 更新日誌

### 2026-02-04
- ✅ 新增統一的 `import.sh` 入口腳本
- ✅ 整合所有資料類型的匯入功能
- ✅ 支援 `all` 關鍵字匯入所有原始資料
- ✅ 統一 README 文件

### 2026-02-03
- ✅ 新增技術分析資料匯入工具
- ✅ 支援 CSV 格式匯入
- ✅ 自動 UPSERT 機制

### 2026-02-01
- ✅ 完成原始資料匯入器（price, institutional, margin, lending, top20_volume）
- ✅ 資料庫 schema 建立
- ✅ 匯入記錄追蹤

---

**最後更新**: 2026-02-04
**維護者**: Jason Huang
**專案**: tw-stock-collector

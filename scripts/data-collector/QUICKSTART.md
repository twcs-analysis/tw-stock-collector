# 資料收集 - 快速上手

5 分鐘快速開始收集台股資料。

---

## ⚡ 快速開始

### 單日收集

```bash
# 收集當天資料
./scripts/data-collector/collect.sh

# 收集指定日期
./scripts/data-collector/collect.sh 2026-02-02

# 收集特定類型
./scripts/data-collector/collect.sh 2026-02-02 price institutional
```

---

### 歷史回補

```bash
# 回補一個月資料（自動：收集 → 匯入 → 轉換）
./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31

# 只回補特定類型
./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31 price

# 跳過技術指標轉換（更快）
./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31 --skip-transform
```

---

## 📋 支援的資料類型

| 類型 | 說明 | 範例筆數 |
|------|------|---------|
| `price` | 每日價格資料 | ~1,950 |
| `institutional` | 三大法人買賣超 | ~1,720 |
| `margin` | 融資融券 | ~1,820 |
| `lending` | 借券賣出 | ~1,010 |
| `top20_volume` | 成交量前 20 名 | 20 |

---

## 🔄 完整工作流程

### 情境 1：首次設定

```bash
# 1. 初始化資料庫
export DB_PASSWORD=tw_stock_dev_password_2024
./scripts/database/init_database.sh

# 2. 回補 2 年歷史資料
./scripts/data-collector/backfill.sh 2024-01-02 2026-02-02

# 3. 查看結果
./scripts/database/check_status.sh
```

**預計時間**：約 30-60 分鐘

---

### 情境 2：每日更新

```bash
# 方式 1：使用 collect.sh（需要手動匯入和轉換）
./scripts/data-collector/collect.sh
./scripts/data-importer/import_date_range.sh 2026-02-02 2026-02-02
./scripts/data-transformer/transform.sh today

# 方式 2：使用 backfill.sh（自動完成三步驟）
./scripts/data-collector/backfill.sh 2026-02-02 2026-02-02
```

**預計時間**：約 2-3 分鐘

---

### 情境 3：補特定日期

```bash
# 發現 2026-02-01 資料缺失
./scripts/data-collector/backfill.sh 2026-02-01 2026-02-01
```

---

### 情境 4：只補法人資料

```bash
# 只收集和匯入法人資料
./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31 institutional
```

---

## 📊 資料流程

```
收集 (collect.sh / backfill.sh)
  ↓
data/raw/{type}/YYYY/MM/YYYY-MM-DD.json
  ↓
匯入 (import_date_range.sh)
  ↓
PostgreSQL 資料庫
  ↓
轉換 (transform.sh)
  ↓
data/transformed/technical/{date}_all.csv
```

---

## 🔍 查看結果

### 查看原始資料

```bash
# 列出收集的檔案
ls -lh data/raw/price/2026/02/

# 查看 JSON 內容
cat data/raw/price/2026/02/2026-02-02.json | jq '.metadata'

# 統計記錄數
cat data/raw/price/2026/02/2026-02-02.json | jq '.data | length'
```

---

### 查看資料庫

```bash
# 查看資料庫狀態
export DB_PASSWORD=tw_stock_dev_password_2024
./scripts/database/check_status.sh
```

---

### 查看技術指標

```bash
# 列出轉換結果
ls -lh data/transformed/technical/

# 查看 CSV 內容（前 10 筆）
head -n 10 data/transformed/technical/2026-02-02_all.csv
```

---

## 🎯 快速診斷

### 問題：收集失敗

```bash
✗ 資料收集失敗
```

**檢查清單**：
1. ✅ 網路連線正常？
2. ✅ 是否為交易日？
3. ✅ API 服務正常？

**解決方式**：
```bash
# 檢查網路
curl -I https://openapi.twse.com.tw

# 查看詳細日誌
ls -lt logs/ | head -5

# 手動重試
./scripts/data-collector/collect.sh 2026-02-02
```

---

### 問題：資料筆數異常

```bash
# 收集成功但筆數太少
```

**解決方式**：
```bash
# 檢查筆數
jq '.data | length' data/raw/price/2026/02/2026-02-02.json

# 如果 < 1000，重新收集
./scripts/data-collector/collect.sh 2026-02-02 price
```

---

### 問題：回補中斷

```bash
# backfill.sh 執行到一半失敗
```

**解決方式**：
```bash
# 查看已完成的日期
ls data/raw/price/2026/02/ | sort

# 從中斷處繼續
./scripts/data-collector/backfill.sh 2026-02-15 2026-02-28
```

---

## 💡 實用技巧

### 技巧 1：建立別名

在 `~/.bashrc` 或 `~/.zshrc` 中加入：

```bash
# 資料收集別名
alias collect='cd /path/to/tw-stock-collector && ./scripts/data-collector/collect.sh'
alias backfill='cd /path/to/tw-stock-collector && ./scripts/data-collector/backfill.sh'
```

使用方式：
```bash
collect                      # 收集當天
collect 2026-02-02           # 收集指定日期
backfill 2026-01-01 2026-01-31  # 回補一月
```

---

### 技巧 2：批次回補

大量回補建議按月分批：

```bash
# 建立批次腳本
cat > batch_backfill.sh << 'EOF'
#!/bin/bash
for month in {01..12}; do
    echo "回補 2024-$month"
    ./scripts/data-collector/backfill.sh 2024-$month-01 2024-$month-31
done
EOF

chmod +x batch_backfill.sh
./batch_backfill.sh
```

---

### 技巧 3：自動化排程

使用 cron 每天自動收集：

```bash
# 編輯 crontab
crontab -e

# 每天 22:00 執行
0 22 * * * cd /path/to/tw-stock-collector && \
    ./scripts/data-collector/backfill.sh $(date +%Y-%m-%d) $(date +%Y-%m-%d) \
    >> /var/log/tw-stock.log 2>&1
```

---

## 🔗 下一步

收集資料後，可以：

1. **查看資料庫** → [資料庫管理快速指南](../database/QUICKSTART.md)
2. **計算技術指標** → [技術分析快速指南](../data-transformer/QUICKSTART.md)
3. **查看完整文檔** → [資料收集 README](README.md)

---

## 📞 需要幫助？

- 查看完整文檔：[README.md](README.md)
- 查看專案說明：[../../README.md](../../README.md)

---

**最後更新**: 2026-02-02
**預計閱讀時間**: 5 分鐘

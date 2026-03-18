---
name: data-pipeline
description: "完整資料處理流程：收集 → 匯入 → 轉換（自動化執行三階段）"
user-invocable: true
allowed-tools: Bash(python3:*), Read, Grep, Glob, TodoWrite
---

# 台股資料處理 Pipeline Skill

自動執行完整的台股資料處理流程，包含資料收集、資料庫匯入、技術分析轉換、Git 提交四個階段。

## 功能說明

此 skill 按順序執行以下四個階段：

1. **資料收集（data-collect）**
   - 使用 `scripts/run_collection.py`
   - 收集：price, institutional, margin, lending, top20_volume
   - 使用 `scripts/data-collector/collect_stock_futures.py`
   - 收集：stock_futures（個股期貨）

2. **資料匯入（data-import）**
   - 使用 `scripts/data-importer/import.sh`
   - 匯入到 PostgreSQL 資料庫

3. **資料轉換（data-transform）**
   - 使用 `scripts/data-transformer/transform.sh`
   - 計算 30 個技術指標

4. **Git 提交（git commit & push）**
   - 使用 Skill tool 呼叫 git skill
   - 自動分析變更、code review、更新文檔、提交並推送

## 使用場景

### 場景 1: 執行今日完整流程（預設）

**使用者說**：
- 「執行今天的資料處理流程」
- 「更新今日資料並計算技術指標」
- 「運行完整 pipeline」
- 「data pipeline」

**執行流程**：
```bash
# 階段 1: 收集今日資料
python3 scripts/run_collection.py

# 階段 2: 匯入資料庫
export DB_PASSWORD=<請參考 CLAUDE.md>
scripts/data-importer/import.sh all --date $(date +%Y-%m-%d)

# 階段 3: 計算技術指標
export DB_PASSWORD=<請參考 CLAUDE.md>
scripts/data-transformer/transform.sh $(date +%Y-%m-%d)
```

---

### 場景 2: 執行指定日期的完整流程

**使用者說**：
- 「執行 2026-02-05 的資料處理」
- 「處理 2026-02-05 的資料」
- 「data pipeline 2026-02-05」

**執行流程**：
```bash
# 使用者指定日期
TARGET_DATE="2026-02-05"

# 階段 1: 收集資料
python3 scripts/run_collection.py --date $TARGET_DATE

# 階段 2: 匯入資料庫
export DB_PASSWORD=<請參考 CLAUDE.md>
scripts/data-importer/import.sh all --date $TARGET_DATE

# 階段 3: 計算技術指標
scripts/data-transformer/transform.sh $TARGET_DATE
```

---

### 場景 3: 只執行特定資料類型

**使用者說**：
- 「只收集並處理 price 資料」
- 「執行 price 和 margin 的完整流程」

**執行流程**：
```bash
# 使用者指定類型：price, institutional
TARGET_DATE="2026-02-05"
TYPES="price institutional"

# 階段 1: 收集指定類型
python3 scripts/run_collection.py --date $TARGET_DATE --types $TYPES

# 階段 2: 匯入指定類型
export DB_PASSWORD=<請參考 CLAUDE.md>
scripts/data-importer/import.sh price,institutional --date $TARGET_DATE

# 階段 3: 計算技術指標（不分類型）
scripts/data-transformer/transform.sh $TARGET_DATE
```

---

## 執行步驟（詳細）

### 📋 Step 1: 解析參數

1. **日期處理**：
   - 若使用者未指定日期 → 使用今天日期
   - 若使用者指定日期 → 使用指定日期
   - 格式：YYYY-MM-DD

2. **資料類型處理**：
   - 預設：all（所有類型）
   - 可選：price, institutional, margin, lending, top20_volume, stock_futures

### 📋 Step 2: 建立 Todo List

使用 TodoWrite 建立任務清單：
```
1. ⏳ 收集股票資料（price, institutional, margin, lending, top20_volume）
2. ⏳ 收集個股期貨資料（stock_futures）
3. ⏳ 匯入資料庫（data-import）
4. ⏳ 計算技術指標（data-transform）
5. ⏳ Git 提交（git commit & push）
```

### 📋 Step 3: 階段 1 - 資料收集

```bash
# 執行收集
python3 scripts/run_collection.py --date $TARGET_DATE --types $TYPES

# 檢查結果
ls -lh data/raw/price/$YEAR/$MONTH/$TARGET_DATE.json
```

**成功條件**：
- ✅ JSON 檔案已生成
- ✅ 檔案大小 > 0
- ✅ metadata.total_count > 0

**🔍 日期驗證（關鍵步驟）**：
收集完成後，**必須驗證資料日期是否正確**，避免使用錯誤日期的資料。

**驗證步驟**：
```bash
# 1. 從 JSON 檔案提取 metadata.date
COLLECTED_DATE=$(cat data/raw/price/$YEAR/$MONTH/$TARGET_DATE.json | jq -r '.metadata.date')

# 2. 比對日期
if [ "$COLLECTED_DATE" != "$TARGET_DATE" ]; then
    echo "❌ 日期驗證失敗！"
    echo "目標日期: $TARGET_DATE"
    echo "實際收集日期: $COLLECTED_DATE"
    echo ""
    echo "⚠️  警告：資料日期不符，停止後續處理！"
    echo "可能原因："
    echo "  - API 回傳的是最新交易日資料（非指定日期）"
    echo "  - 指定日期為非交易日"
    echo "  - API 資料尚未更新"
    exit 1
fi

echo "✅ 日期驗證通過：$COLLECTED_DATE"
```

**失敗處理**：
- 🛑 日期不符時，**立即停止**，不執行後續的「匯入」和「轉換」階段
- ⚠️ 顯示詳細的錯誤訊息和可能原因
- 📋 更新 Todo：標記「收集資料」為 failed
- 🔄 建議使用者：
  1. 確認指定日期是否為交易日
  2. 檢查 API 資料是否已更新
  3. 使用 `--skip-trading-day-check` 測試（僅開發用）

**📊 顯示重點股票資訊**：
日期驗證通過後，自動從 JSON 檔案中提取並顯示以下股票的當日價格：
- **台積電 (2330)**
- **櫻花建 (2539)**

顯示欄位：
- stock_id: 股票代碼
- stock_name: 股票名稱
- date: 日期
- open: 開盤價
- high: 最高價
- low: 最低價
- close: 收盤價
- volume: 成交量
- change: 漲跌幅 (計算方式：如有前一日收盤價則顯示)

**實作方式**（僅在日期驗證通過後執行）：
```bash
# 使用 jq 提取台積電和櫻花建的資料
cat data/raw/price/$YEAR/$MONTH/$TARGET_DATE.json | jq -r '
  ["股票代碼", "股票名稱", "日期", "開盤", "最高", "最低", "收盤", "漲跌", "成交量"],
  (.data[] |
   select(.stock_id == "2330" or .stock_id == "2539") |
   [.stock_id, .stock_name, .date, .open, .high, .low, .close, .change_price, .volume]
  ) | @tsv
' | column -t -s $'\t'
```

**輸出範例**：
```
股票代碼  股票名稱  日期          開盤    最高    最低    收盤    漲跌   成交量
2330      台積電    2026-02-06   1745.0  1780.0  1740.0  1780.0  15.0   36484181
2539      櫻花建    2026-02-06   47.1    48.05   46.7    47.9    0.4    785721
```

**更新 Todo**: 標記「收集股票資料」為 completed

### 📋 Step 3.5: 階段 1.5 - 收集個股期貨資料

```bash
# 執行收集
python3.11 scripts/data-collector/collect_stock_futures.py --date $TARGET_DATE

# 檢查結果
ls -lh data/raw/stock_futures/$YEAR/$MONTH/$TARGET_DATE.json
```

**成功條件**：
- ✅ JSON 檔案已生成
- ✅ 檔案大小 > 0
- ✅ metadata.total_count > 0（通常約 154 筆合約）

**🔍 日期驗證**：
```bash
# 從 JSON 檔案提取 metadata.date
COLLECTED_DATE=$(cat data/raw/stock_futures/$YEAR/$MONTH/$TARGET_DATE.json | jq -r '.metadata.date')

if [ "$COLLECTED_DATE" != "$TARGET_DATE" ]; then
    echo "❌ 個股期貨日期驗證失敗！"
    echo "目標日期: $TARGET_DATE"
    echo "實際收集日期: $COLLECTED_DATE"
    exit 1
fi

echo "✅ 個股期貨日期驗證通過：$COLLECTED_DATE"
```

**📊 顯示重點期貨資訊**：
顯示以下個股期貨合約的當日行情：
- **台積電期貨 (CDF)**
- **0050 期貨 (NYF)**

```bash
# 使用 jq 提取台積電期貨和 0050 期貨的資料
cat data/raw/stock_futures/$YEAR/$MONTH/$TARGET_DATE.json | jq -r '
  ["合約", "股票代碼", "股票名稱", "到期月份", "開盤", "最高", "最低", "收盤", "成交量", "未平倉"],
  (.data[] |
   select(.contract == "CDF" or .contract == "NYF") |
   select(.contract_month[0:6] == (.date[0:4] + .date[5:7])) |
   [.contract, .stock_id, .stock_name, .contract_month, .open, .high, .low, .close, .volume, .open_interest]
  ) | @tsv
' | column -t -s $'\t'
```

**輸出範例**：
```
合約  股票代碼  股票名稱  到期月份  開盤    最高    最低    收盤    成交量  未平倉
CDF   2330      台積電    202603    1870.0  1880.0  1845.0  1870.0  7706    12345
NYF   0050      元大台灣50 202603    75.6    76.7    75.45   75.6    2156    8901
```

**更新 Todo**: 標記「收集個股期貨資料」為 completed

### 📋 Step 4: 階段 2 - 資料庫匯入

```bash
# 設定環境變數
export DB_PASSWORD=<請參考 CLAUDE.md>

# 執行匯入
scripts/data-importer/import.sh $TYPES_COMMA --date $TARGET_DATE

# 驗證匯入（Docker PostgreSQL）
docker exec tw-stock-postgres psql -U postgres -d tw_stock -c \
  "SELECT COUNT(*) FROM stock_prices WHERE trade_date = '$TARGET_DATE';"
```

**成功條件**：
- ✅ 匯入成功訊息
- ✅ 資料庫中有對應日期的記錄

**更新 Todo**: 標記「匯入資料庫」為 completed

### 📋 Step 5: 階段 3 - 技術分析轉換

```bash
# 執行轉換
scripts/data-transformer/transform.sh $TARGET_DATE

# 檢查結果
ls -lh data/transformed/technical/$YEAR/$MONTH/$TARGET_DATE.json
```

**成功條件**：
- ✅ JSON 檔案已生成
- ✅ 包含 30 個技術指標
- ✅ 股票數量 > 1,900

**更新 Todo**: 標記「計算技術指標」為 completed

### 📋 Step 6: Git 提交

**執行步驟**：
1. 使用 Skill tool 呼叫 git skill
2. Git skill 會自動執行：
   - 分析變更內容（git status, git diff）
   - Code review（檢查安全性、邏輯錯誤）
   - 更新 CHANGELOG.md
   - 建立 commit（使用繁體中文訊息）
   - 推送到遠端 repo

**Commit 訊息格式**：
```
data: Daily collection for YYYY-MM-DD

- price: X 筆
- institutional: X 筆
- margin: X 筆
- top20_volume: X 筆
- stock_futures: X 筆合約
- 技術分析: X 檔股票

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**成功條件**：
- ✅ Commit 建立成功
- ✅ 推送到 origin/main

**更新 Todo**: 標記「Git 提交」為 completed

### 📋 Step 7: 完成報告

輸出摘要：
```
✅ 資料處理 Pipeline 完成！

📊 執行摘要：
- 日期: 2026-02-05
- 資料類型: price, institutional, margin, lending, top20_volume, stock_futures
- 收集股票數: 1,958 檔
- 收集期貨合約: 154 筆
- 匯入資料庫: 2,112 筆（股票 1,958 + 期貨 154）
- 技術分析: 1,921 檔（30 個指標）
- Git Commit: 32deeb51

📁 生成的檔案：
- data/raw/price/2026/02/2026-02-05.json
- data/raw/stock_futures/2026/02/2026-02-05.json
- data/transformed/technical/2026/02/2026-02-05.json
```

---

## 錯誤處理

### 階段 1 失敗：資料收集

**常見錯誤 1：日期驗證失敗** 🔴
- **錯誤訊息**：「❌ 日期驗證失敗！目標日期: YYYY-MM-DD, 實際收集日期: YYYY-MM-DD」
- **原因**：
  - API 回傳的是最新交易日資料（非指定日期）
  - 指定日期為非交易日或假日
  - API 資料尚未更新
- **處理方式**：
  1. 🛑 **立即停止後續階段**（匯入、轉換、Git 提交）
  2. 檢查指定日期是否為交易日：
     ```bash
     python scripts/common-tools/get_trading_days.py check YYYY-MM-DD
     ```
  3. 若為交易日但 API 未更新，等待 API 更新後重試
  4. 若要收集最新交易日資料，使用 `today` 參數

**常見錯誤 2：API 無回應**
- **處理方式**：檢查網路連線，稍後重試

**常見錯誤 3：收集腳本執行失敗**
- **處理方式**：
  1. 檢查 Python 環境
  2. 查看錯誤日誌
  3. 停止後續階段

---

### 階段 2 失敗：資料庫匯入

**常見錯誤**：
- PostgreSQL 未啟動
- 資料庫連接失敗
- 資料已存在

**處理方式**：
1. 檢查 Docker 容器狀態：`docker ps | grep postgres`
2. 檢查資料庫連接：`docker exec tw-stock-postgres psql -U postgres -l`
3. 若資料已存在，詢問是否覆蓋

---

### 階段 3 失敗：技術分析轉換

**常見錯誤**：
- 資料庫無資料
- Python 套件缺失

**處理方式**：
1. 確認階段 2 已成功
2. 檢查 Python 環境：`python3.11 -m pip list | grep pandas`

---

## 環境需求

### 必要條件
- ✅ Python 3.11
- ✅ Docker PostgreSQL 運行中（tw-stock-postgres）
- ✅ 資料庫密碼：請參考 CLAUDE.md 中的環境配置

### 檢查命令
```bash
# 檢查 Python 版本
python3.11 --version

# 檢查 PostgreSQL
docker ps | grep tw-stock-postgres

# 測試資料庫連接
docker exec tw-stock-postgres psql -U postgres -d tw_stock -c "SELECT 1;"
```

---

## 進階用法

### 僅執行部分階段

**使用者說**: 「只執行資料收集和匯入，跳過技術分析」

**執行**：
```bash
# 只執行前兩階段
python3 scripts/run_collection.py --date $TARGET_DATE
scripts/data-importer/import.sh all --date $TARGET_DATE
# 跳過階段 3
```

---

### 批次處理多個日期

**使用者說**: 「處理 2026-02-01 到 2026-02-05 的資料」

**執行**：
```bash
# 逐日執行
export DB_PASSWORD=<請參考 CLAUDE.md>
for date in $(seq -f "%Y-%m-%d" $(date -d "2026-02-01" +%s) 86400 $(date -d "2026-02-05" +%s)); do
    python3 scripts/run_collection.py --date $date
    scripts/data-importer/import.sh all --date $date
    scripts/data-transformer/transform.sh $date
done
```

---

## 注意事項

### ⚠️ 執行順序

**不可跳過階段**：
- ❌ 不能先執行階段 2（需要階段 1 的 JSON 檔案）
- ❌ 不能先執行階段 3（需要階段 2 的資料庫資料）

**正確順序**：
1️⃣ data-collect → 2️⃣ data-import → 3️⃣ data-transform

### ⚠️ 資料覆蓋

- 重複執行會**覆蓋**現有資料
- 匯入資料庫時會先刪除該日期的舊資料
- 技術分析 JSON 會直接覆蓋

### ⚠️ 交易日檢查

- 資料收集預設會檢查是否為交易日
- 若非交易日，收集會失敗
- 使用 `--skip-trading-day-check` 可強制執行（僅測試用）

---

## 範例對話

### 範例 1: 預設執行

```
使用者: data pipeline
助手: 好的！我來執行今日的完整資料處理流程...

📋 任務清單：
1. ⏳ 收集資料（data-collect）
2. ⏳ 匯入資料庫（data-import）
3. ⏳ 計算技術指標（data-transform）

[執行階段 1...]
✅ 階段 1 完成：收集 1,958 檔股票資料

[執行階段 2...]
✅ 階段 2 完成：匯入 1,958 筆資料到資料庫

[執行階段 3...]
✅ 階段 3 完成：計算 1,921 檔股票技術指標

✅ 所有階段完成！
```

### 範例 2: 指定日期

```
使用者: 執行 2026-02-03 的 data pipeline
助手: 好的！我來執行 2026-02-03 的完整資料處理流程...

[同上...]
```

### 範例 3: 指定類型

```
使用者: 只處理 price 資料
助手: 好的！我來執行 price 資料的處理流程...

階段 1: 收集 price 資料
階段 2: 匯入 price 資料
階段 3: 計算技術指標（所有股票）
```

---

## 相關 Skills

- **data-collect**: 單獨執行資料收集
- **data-import**: 單獨執行資料匯入
- **data-transform**: 單獨執行技術分析轉換

---

## 故障排除

### 問題 1: PostgreSQL 未啟動

**錯誤訊息**: `could not connect to server`

**解決方式**:
```bash
# 檢查容器狀態
docker ps -a | grep tw-stock-postgres

# 啟動容器
docker start tw-stock-postgres
```

### 問題 2: Python 版本錯誤

**錯誤訊息**: `ModuleNotFoundError: No module named 'pandas'`

**解決方式**:
```bash
# 使用正確的 Python 版本
python3.11 -m pip install -r requirements.txt
```

### 問題 3: 權限問題

**錯誤訊息**: `permission denied`

**解決方式**:
```bash
# 添加執行權限
chmod +x scripts/data-importer/import.sh
chmod +x scripts/run_collection.py
```

---

---

## 個股期貨收集說明

### 資料來源
- **API**: TAIFEX OpenAPI（台灣期貨交易所）
- **URL**: `https://openapi.taifex.com.tw/v1/DailyMarketReportFut`
- **無需認證**: 完全免費的公開 API

### 收集範圍
- **合約數量**: 每日約 154 筆個股期貨合約
- **涵蓋股票**: 約 21 檔標的股票（包含 ETF）
- **合約類型**:
  - 近月合約（當月）
  - 次月合約
  - 季月合約
  - 跨月價差合約

### 資料欄位
每筆期貨資料包含：
- 基本資訊：合約代碼、股票代碼、股票名稱、到期月份
- 價格資訊：開盤、最高、最低、收盤、結算價
- 交易資訊：成交量、未平倉量
- 交易時段：一般交易、盤後交易

### 執行方式
```bash
# 單日收集
python3.11 scripts/data-collector/collect_stock_futures.py --date 2026-03-17

# 使用 shell wrapper
scripts/data-collector/collect_stock_futures.sh 2026-03-17
```

### 儲存位置
```
data/raw/stock_futures/YYYY/MM/YYYY-MM-DD.json
```

### 注意事項
- ⚠️ 非交易日會自動跳過（回傳空資料或錯誤）
- ⚠️ 使用 `python3.11` 而非 `python3`
- ⚠️ 期貨資料會在交易日結束後更新（通常 15:00 後）

---

**最後更新**: 2026-03-17

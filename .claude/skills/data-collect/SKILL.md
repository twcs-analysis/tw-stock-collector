---
name: data-collect
description: "資料收集：收集台股每日交易資料（價格、法人、融資融券等）"
user-invocable: true
allowed-tools: Bash(python3:*), Read, Grep, Glob
---

# 台股資料收集 Skill

自動執行台股資料收集任務，支援當日資料收集與歷史資料回補。

## 功能說明

此 skill 使用專案中的 `scripts/run_collection.py` 腳本來收集台股資料，包含：
- **price**: 每日價量資料（開高低收、成交量）
- **institutional**: 三大法人買賣超
- **margin**: 融資融券資料
- **lending**: 借券賣出資料
- **top20_volume**: 成交量前 20 名

## 使用場景

### 場景 1: 收集今日資料（當天交易日）
使用者說：「收集今天的股價資料」或「更新今日資料」

**執行命令**：
```bash
python3 scripts/run_collection.py
```

說明：
- 不指定日期時，自動使用當天日期
- 自動判斷是否為交易日
- 收集所有類型資料

### 場景 2: 收集指定日期的所有資料
使用者說：「收集 2026-02-03 的所有資料」

**執行命令**：
```bash
python3 scripts/run_collection.py --date 2026-02-03
```

### 場景 3: 收集特定類型資料
使用者說：「收集昨天的股價和法人資料」

**執行命令**：
```bash
python3 scripts/run_collection.py --date 2026-02-03 --types price institutional
```

可用類型：
- `price` - 價格資料
- `institutional` - 三大法人
- `margin` - 融資融券
- `lending` - 借券賣出
- `top20_volume` - 成交量前 20 名

### 場景 4: 強制收集（跳過交易日檢查）
使用者說：「強制收集 2026-01-01 的資料（即使不是交易日）」

**執行命令**：
```bash
python3 scripts/run_collection.py --date 2026-01-01 --skip-trading-day-check
```

說明：
- 用於測試或特殊情況
- 跳過交易日驗證

### 場景 5: 回補歷史資料
使用者說：「回補 2026-01-01 到 2026-01-31 的歷史資料」

**執行命令**：
```bash
python3 scripts/data-collector/backfill_historical.py --start 2026-01-01 --end 2026-01-31
```

或單一日期：
```bash
python3 scripts/data-collector/backfill_historical.py --date 2026-01-15
```

說明：
- 使用回補模式 API（支援歷史日期）
- 可指定資料類型：`--types price margin institutional lending`
- 自動跳過非交易日

## 執行流程

1. **解析使用者需求**
   - 判斷是當日資料還是歷史資料
   - 確認日期格式（YYYY-MM-DD）
   - 確認需要收集的資料類型

2. **檢查前置條件**
   - 確認日期是否為交易日（除非明確要求跳過檢查）
   - 確認是否已有該日期的資料（詢問是否覆蓋）

3. **選擇正確的腳本**
   - **當日/近期資料**：使用 `scripts/run_collection.py`
   - **歷史資料回補**：使用 `scripts/data-collector/backfill_historical.py`

4. **執行收集**
   - 組裝完整的命令列參數
   - 執行 Python 腳本
   - 監控執行過程

5. **驗證結果**
   - 檢查輸出日誌
   - 確認資料檔案已建立
   - 回報收集結果統計

## 參數說明

### scripts/run_collection.py
- `--date YYYY-MM-DD`: 收集日期（選填，預設為當天）
- `--types TYPE [TYPE ...]`: 資料類型（選填，預設收集全部）
- `--skip-trading-day-check`: 跳過交易日檢查（選填）
- `--no-validation`: 跳過資料驗證（不建議使用）

### scripts/data-collector/backfill_historical.py
- `--date YYYY-MM-DD`: 單一日期回補
- `--start YYYY-MM-DD`: 起始日期（需搭配 --end）
- `--end YYYY-MM-DD`: 結束日期（需搭配 --start）
- `--types TYPE [TYPE ...]`: 資料類型（選填，預設收集全部）

## 輸出檔案位置

收集完成後，資料會儲存在：
```
data/raw/{type}/YYYY/MM/YYYY-MM-DD.json
```

範例：
- `data/raw/price/2026/02/2026-02-03.json` - 價格資料
- `data/raw/institutional/2026/02/2026-02-03.json` - 法人資料

## 錯誤處理

### 常見錯誤

1. **非交易日錯誤**
   ```
   Error: 2026-01-01 is not a trading day
   ```
   解決：加上 `--skip-trading-day-check` 或選擇交易日

2. **資料已存在**
   ```
   Warning: Data file already exists
   ```
   處理：詢問使用者是否要覆蓋

3. **API 請求失敗**
   ```
   Error: Failed to fetch data from TWSE
   ```
   處理：稍後重試或檢查網路連線

4. **資料驗證失敗**
   ```
   Error: Data validation failed
   ```
   處理：檢查 API 回應內容，可能需要手動檢查

## 注意事項

1. **交易日判斷**
   - 系統會自動判斷是否為交易日
   - 週末、國定假日通常不是交易日
   - 可使用 `python3 scripts/common-tools/get_trading_days.py check YYYY-MM-DD` 檢查

2. **資料收集時間**
   - 建議在每個交易日 **21:30 之後**執行
   - 確保證交所已完成當日資料結算

3. **歷史資料回補**
   - 歷史資料使用不同的 API（MI_INDEX）
   - 回補速度較慢，請耐心等待
   - 建議分批回補（例如一次一個月）

4. **資料類型選擇**
   - 如果只需要特定類型，請明確指定
   - 收集所有類型約需 2-3 分鐘

## 範例對話

**使用者**: 幫我收集今天的股價資料

**助手回應**:
```
我會使用 run_collection.py 收集今天的股價資料。

執行命令：
python3 scripts/run_collection.py --types price

[執行結果...]
✓ 成功收集 1,954 筆股價資料
資料已儲存至: data/raw/price/2026/02/2026-02-04.json
```

**使用者**: 回補 2026-01-01 到 2026-01-31 的所有資料

**助手回應**:
```
我會使用 backfill_historical.py 回補 2026-01 整月的歷史資料。

執行命令：
python3 scripts/data-collector/backfill_historical.py --start 2026-01-01 --end 2026-01-31

[執行結果...]
✓ 成功回補 20 個交易日的資料
✓ 總計收集 39,080 筆記錄
```

## 相關檔案

- `scripts/run_collection.py` - 當日資料收集腳本
- `scripts/data-collector/backfill_historical.py` - 歷史資料回補腳本
- `scripts/common-tools/get_trading_days.py` - 交易日查詢工具
- `services/common/collectors/` - 收集器模組
- `services/common/datasources/` - 資料源 API 模組

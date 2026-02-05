---
name: data-transform
description: "資料轉換：計算技術指標（MA、RSI、MACD、布林通道等 30 個指標）"
user-invocable: true
allowed-tools: Bash(python3:*), Read, Grep, Glob
---

# 台股資料轉換 Skill

從資料庫讀取股價資料，計算技術分析指標，輸出為 JSON 或 CSV 格式。

## 功能說明

此 skill 使用專案中的 `scripts/data-transformer/run_technical.py` 腳本來轉換資料，計算包含：

### 技術指標（共 30 個）

**移動平均（MA）**：
- `ma_5`, `ma_10`, `ma_20`, `ma_60`, `ma_120`, `ma_240`
- 短期、中期、長期趨勢判斷

**指數移動平均（EMA）**：
- `ema_12`, `ema_26`
- MACD 計算基礎

**相對強弱指標（RSI）**：
- `rsi_6`, `rsi_12`, `rsi_14`
- 超買超賣判斷（0-100）

**MACD 指標**：
- `macd` - DIF 值（快線）
- `macd_signal` - DEA 值（慢線）
- `macd_hist` - 柱狀圖（快線-慢線）

**布林通道（Bollinger Bands）**：
- `bb_upper` - 上軌（+2σ）
- `bb_middle` - 中軌（20MA）
- `bb_lower` - 下軌（-2σ）
- `bb_width` - 通道寬度
- `bb_pct` - 價格位置百分比

**DMI/ADX 指標**：
- `plus_di` - +DI（上升動向指標）
- `minus_di` - -DI（下降動向指標）
- `adx_14` - ADX（趨勢強度，0-100）

**成交量分析**：
- `volume_ma_5` - 5 日均量
- `volume_ma_20` - 20 日均量
- `volume_ratio` - 量比
- `turnover_rate` - 換手率
- `vwap` - 加權平均價

**價格動能**：
- `momentum_10` - 10 日動能
- `roc_10` - 10 日變動率（%）

**其他指標**：
- `obv` - 能量潮（On-Balance Volume）

## 使用場景

### 場景 1: 計算單日技術指標
使用者說：「計算 2026-02-03 的技術指標」

**執行命令**：
```bash
python3 scripts/data-transformer/run_technical.py --date 2026-02-03
```

說明：
- 從資料庫讀取歷史價格資料（需要約 240 天歷史資料計算 MA240）
- 計算所有 30 個技術指標
- 輸出 JSON 檔案到 `data/transformed/technical/2026/02/2026-02-03.json`

### 場景 2: 計算日期區間的技術指標
使用者說：「計算 2026-01-01 到 2026-01-31 的技術指標」

**執行命令**：
```bash
python3 scripts/data-transformer/run_technical.py --start 2026-01-01 --end 2026-01-31
```

說明：
- 批次處理整個月份的資料
- 每個交易日產生一個 JSON 檔案

### 場景 3: 計算特定股票的技術指標
使用者說：「只計算台積電（2330）的技術指標」

**執行命令**：
```bash
python3 scripts/data-transformer/run_technical.py --date 2026-02-03 --stock-id 2330
```

說明：
- 只處理指定股票代碼
- 適合快速查看單一股票

### 場景 4: 輸出為 CSV 格式
使用者說：「計算昨天的技術指標並輸出成 CSV」

**執行命令**：
```bash
python3 scripts/data-transformer/run_technical.py --date 2026-02-03 --output result.csv
```

說明：
- 輸出為 CSV 格式，方便 Excel 開啟
- 包含所有股票和所有技術指標

### 場景 5: 僅顯示結果不儲存
使用者說：「計算技術指標但不要儲存檔案」

**執行命令**：
```bash
python3 scripts/data-transformer/run_technical.py --date 2026-02-03 --no-save
```

說明：
- 計算結果僅顯示在終端
- 不產生 JSON 檔案

## 執行流程

1. **解析使用者需求**
   - 確認要計算的日期（單日或區間）
   - 確認是否指定特定股票
   - 確認輸出格式（JSON 或 CSV）
   - 確認日期格式（YYYY-MM-DD）

2. **檢查前置條件**
   - 確認 PostgreSQL 資料庫正在運行
   - 確認該日期的股價資料已匯入資料庫
   - 確認有足夠的歷史資料（至少 240 天，用於計算 MA240）

3. **執行轉換**
   - 組裝完整的命令列參數
   - 執行 Python 腳本
   - 監控計算進度

4. **驗證結果**
   - 檢查計算筆數（應與股票數量一致）
   - 確認輸出檔案已建立
   - 回報轉換結果統計

5. **後續處理**
   - 詢問是否需要匯入到資料庫
   - 詢問是否需要執行分析腳本

## 參數說明

### scripts/data-transformer/run_technical.py

**日期參數**（擇一必填）：
- `--date YYYY-MM-DD`: 單一日期轉換
- `--start YYYY-MM-DD`: 起始日期（需搭配 --end）

**結束日期**（與 --start 搭配使用）：
- `--end YYYY-MM-DD`: 結束日期

**篩選參數**（選填）：
- `--stock-id STOCK_ID`: 指定股票代碼（例如：2330）
- `--market {twse,tpex}`: 指定市場（上市或上櫃）

**輸出參數**（選填）：
- `--output FILENAME`: 輸出檔案名稱（.json 或 .csv）
- `--no-save`: 不儲存檔案（僅顯示結果）
- `--format {json,csv}`: 輸出格式（預設：json）

**其他參數**（選填）：
- `--min-history-days N`: 最小歷史資料天數（預設：240）
- `--batch-size N`: 批次大小（預設：100）

## 輸出檔案位置

### 預設輸出路徑（JSON）
```
data/transformed/technical/YYYY/MM/YYYY-MM-DD.json
```

範例：
- `data/transformed/technical/2026/02/2026-02-03.json`

### 自訂輸出路徑
使用 `--output` 參數時：
```bash
# 輸出到當前目錄
--output result.csv

# 輸出到指定路徑
--output /path/to/output/indicators.csv
```

## 輸出格式範例

### JSON 格式
```json
{
  "metadata": {
    "date": "2026-02-03",
    "calculated_at": "2026-02-04T10:30:00",
    "total_stocks": 1954,
    "indicators_count": 30
  },
  "data": [
    {
      "date": "2026-02-03",
      "stock_id": "2330",
      "stock_name": "台積電",
      "close": 1090.0,
      "ma_5": 1085.2,
      "ma_20": 1078.5,
      "rsi_14": 62.3,
      "macd": 5.2,
      "macd_signal": 3.8,
      "adx_14": 28.5,
      "bb_upper": 1100.0,
      "bb_middle": 1078.5,
      "bb_lower": 1057.0,
      ...
    }
  ]
}
```

### CSV 格式
```csv
date,stock_id,stock_name,close,ma_5,ma_20,rsi_14,macd,adx_14,...
2026-02-03,2330,台積電,1090.0,1085.2,1078.5,62.3,5.2,28.5,...
2026-02-03,2317,鴻海,105.5,104.2,103.8,58.7,1.2,25.3,...
```

## 效能指標

- **處理時間**: 約 20 秒（1,900 檔股票）
- **資料量**: 單日約 2-3 MB（JSON 格式）
- **記憶體使用**: 約 500 MB（載入歷史資料）
- **資料庫查詢**: 1 次（批次載入所有股票歷史資料）

## 錯誤處理

### 常見錯誤

1. **歷史資料不足**
   ```
   Warning: Stock 2330 has insufficient history (only 150 days, need 240)
   ```
   處理：該股票會被跳過，不計算技術指標

2. **資料庫無資料**
   ```
   Error: No price data found for date 2026-02-03
   ```
   解決：先執行資料收集和匯入

3. **資料庫連線失敗**
   ```
   Error: Could not connect to database
   ```
   解決：檢查 PostgreSQL 是否運行

4. **計算錯誤**
   ```
   Error: Failed to calculate indicators for stock 1234
   ```
   處理：記錄錯誤，繼續處理其他股票

## 注意事項

1. **歷史資料需求**
   - 計算 MA240 需要至少 240 天歷史資料
   - 新上市股票可能無法計算長期指標
   - 建議先匯入足夠的歷史資料

2. **資料庫狀態**
   - 確認 PostgreSQL 已啟動
   - 確認 `stock_prices` 表有資料
   - 建議先執行資料匯入

3. **效能考量**
   - 單日計算約 20 秒
   - 批次計算建議不超過一個月
   - 可使用 `--stock-id` 測試單一股票

4. **輸出檔案管理**
   - JSON 檔案較大（2-3 MB/日）
   - 建議定期清理舊檔案
   - 可選擇匯入資料庫後刪除 JSON

5. **資料品質**
   - 計算結果品質取決於輸入資料
   - 建議先驗證股價資料正確性
   - 注意除權息日的影響

## 範例對話

**使用者**: 計算昨天的技術指標

**助手回應**:
```
我會使用 run_technical.py 計算昨天（2026-02-03）的技術指標。

執行前檢查：
✓ PostgreSQL 資料庫已連線
✓ 2026-02-03 股價資料已存在
✓ 歷史資料充足（513 個交易日）

執行命令：
python3 scripts/data-transformer/run_technical.py --date 2026-02-03

[執行結果...]
✓ 成功計算 1,954 檔股票的技術指標
✓ 計算指標數: 30 個
✓ 處理時間: 18.5 秒
✓ 輸出檔案: data/transformed/technical/2026/02/2026-02-03.json

指標包含：
- 移動平均: MA5/10/20/60/120/240
- 動量指標: RSI、MACD、動能
- 波動指標: 布林通道
- 趨勢指標: DMI/ADX
- 成交量分析: VWAP、量比
```

**使用者**: 只計算台積電和鴻海的技術指標並輸出 CSV

**助手回應**:
```
我會計算台積電（2330）和鴻海（2317）的技術指標。

注意：腳本一次只支援單一股票的 --stock-id 參數。
我會分別執行兩次並合併結果。

執行命令 1：
python3 scripts/data-transformer/run_technical.py --date 2026-02-03 --stock-id 2330 --output tsmc.csv

執行命令 2：
python3 scripts/data-transformer/run_technical.py --date 2026-02-03 --stock-id 2317 --output hon_hai.csv

[執行結果...]
✓ 台積電指標已輸出至: tsmc.csv
✓ 鴻海指標已輸出至: hon_hai.csv
```

## 後續步驟建議

計算完成後，通常會進行：

1. **匯入資料庫**
   ```bash
   python3 scripts/data-importer/import_data.py --date 2026-02-03 --types analysis
   ```

2. **執行選股分析**
   ```bash
   python3 scripts/run_all_analysis.py --date 2026-02-03
   ```

3. **查詢特定股票**
   ```bash
   python3 scripts/query_stock_analysis.py --stock-id 2330
   ```

## 相關檔案

- `scripts/data-transformer/run_technical.py` - 轉換腳本
- `services/data-transformer/app/technical_transformer.py` - 轉換服務
- `services/data-transformer/app/indicators/` - 技術指標計算模組
- `services/common/database/models/technical.py` - 資料模型
- `scripts/data-transformer/README.md` - 詳細說明文件

# GAS Caller 使用說明

## 🚀 快速開始

### 1. 安裝依賴

```bash
# 使用 uv（推薦）
uv pip install requests

# 或使用 pip
python3.11 -m pip install --user requests
```

### 2. 確保有資料

```bash
# 檢查是否有技術分析資料
ls -lh data/transformed/technical/2026-02-04.json

# 如果沒有，執行轉換
python scripts/data-transformer/transform.py --date 2026-02-04
```

### 3. 執行測試

```bash
# 基本測試（使用大量 3167）
python3.11 scripts/gas/gas_caller.py --stock-id 3167

# 測試其他股票
python3.11 scripts/gas/gas_caller.py --stock-id 2330  # 台積電
python3.11 scripts/gas/gas_caller.py --stock-id 0050  # 元大台灣50
```

---

## 📋 命令列參數

### 必要參數

- `--stock-id` - 股票代號（如：3167、2330）

### 選填參數

- `--date` - 交易日期（預設：今天，格式：YYYY-MM-DD）
- `--callback-url` - 回調 URL（測試用，選填）
- `--save-payload` - 儲存發送的 payload 到檔案（除錯用）

---

## 🎯 使用範例

### 範例 1：測試單一股票

```bash
python3.11 scripts/gas/gas_caller.py --stock-id 3167
```

**輸出**：
```
============================================================
📊 GAS Web App 測試腳本
============================================================

🔍 載入股票資料: 3167 (2026-02-04)
✅ 成功載入: 大量

📋 建立報告資料...

📤 發送請求到 GAS Web App...
URL: https://script.google.com/macros/s/AKfycb.../exec
Report ID: test_20260205_153620
Stock: 大量 (3167)

✅ HTTP 狀態碼: 200

============================================================
📥 GAS 回應結果
============================================================
{
  "status": "success",
  "message": "Analysis started and callback sent.",
  "reportId": "test_20260205_153620"
}

✅ 測試成功！
📝 請檢查 Google Drive 查看分析報告
```

### 範例 2：指定日期

```bash
python3.11 scripts/gas/gas_caller.py \
  --stock-id 2330 \
  --date 2026-02-03
```

### 範例 3：儲存 payload（除錯用）

```bash
python3.11 scripts/gas/gas_caller.py \
  --stock-id 3167 \
  --save-payload

# 查看生成的檔案
cat scripts/gas/test_payload_3167_2026-02-04.json
```

### 範例 4：批次測試多檔股票

```bash
# 測試熱門股票
for stock_id in 2330 2454 3167 2884 0050; do
  echo ""
  echo "========================================"
  echo "測試股票: $stock_id"
  echo "========================================"
  python3.11 scripts/gas/gas_caller.py --stock-id $stock_id
  sleep 5  # 避免請求過於頻繁
done
```

---

## 🐛 常見問題

### 問題 1：找不到資料檔案

**錯誤訊息**：
```
❌ 找不到資料檔案: FileNotFoundError: 找不到技術分析資料: data/transformed/technical/2026-02-04.json
```

**解決方式**：
```bash
# 執行資料轉換
python scripts/data-transformer/transform.py --date 2026-02-04

# 確認檔案存在
ls -lh data/transformed/technical/2026-02-04.json
```

---

### 問題 2：找不到指定股票

**錯誤訊息**：
```
❌ 資料錯誤: ValueError: 找不到股票 9999 的資料
```

**解決方式**：
```bash
# 查看可用的股票代號（前 20 筆）
python3.11 -c "
import json
data = json.load(open('data/raw/price/2026/02/2026-02-04.json'))
for s in data['data'][:20]:
    print(f\"{s['stock_id']}: {s['stock_name']}\")
"

# 搜尋特定股票名稱
python3.11 -c "
import json
keyword = '台積'
data = json.load(open('data/raw/price/2026/02/2026-02-04.json'))
matches = [s for s in data['data'] if keyword in s.get('stock_name', '')]
for s in matches:
    print(f\"{s['stock_id']}: {s['stock_name']}\")
"
```

---

### 問題 3：Gemini API 配額用盡

**錯誤訊息**：
```json
{
  "status": "error",
  "message": "Error: Gemini API 失敗 (429): ... quota exceeded ..."
}
```

**說明**：
- Gemini API 有免費額度限制
- 錯誤訊息會建議重試時間（如：Please retry in 38s）

**解決方式**：
1. 等待指定時間後再次嘗試
2. 檢查 [API 使用量](https://ai.dev/rate-limit)
3. 升級到付費方案（如需要）
4. 使用不同的 API Key

---

### 問題 4：GAS Web App 回應逾時

**錯誤訊息**：
```
❌ 請求逾時（GAS 可能需要較長時間處理）
```

**說明**：
- Gemini API 回應可能需要較長時間
- 腳本預設等待 60 秒

**解決方式**：
1. 耐心等待
2. 稍後到 Google Drive 查看報告
3. 檢查 GAS 執行日誌

---

## 📊 資料格式參考

### 發送到 GAS 的資料結構

```json
{
  "reportId": "test_20260205_153620",
  "reportData": {
    "stock_info": {
      "stock_id": "3167",
      "stock_name": "大量",
      "trade_date": "2026-02-04"
    },
    "price_data": {
      "open": 205.5,
      "high": 215.0,
      "low": 202.0,
      "close": 212.5,
      "volume": 3142938,
      "amount": 661470753
    },
    "technical_indicators": {
      "ma": {
        "ma_5": 212.3,
        "ma_10": 221.45,
        "ma_20": 223.725,
        "ma_60": 219.225,
        "ma_120": 203.78,
        "ma_240": 155.76
      },
      "rsi": {
        "rsi_6": 21.13,
        "rsi_14": 41.32
      },
      "macd": {
        "dif": -2.76,
        "dea": -0.04,
        "histogram": -2.71
      },
      "dmi": {
        "pdi": 16.23,
        "mdi": 24.18,
        "adx": 18.12,
        "adxr": null
      },
      "bollinger": {
        "upper": 243.30,
        "mid": 223.73,
        "lower": 204.15
      },
      "volume": {
        "vol_ma5": 3728637.4,
        "vol_ma20": 6621546.05,
        "vol_ratio": 0.84,
        "vwap": 210.46
      }
    }
  },
  "callbackUrl": "",
  "timestamp": "2026-02-05T15:36:20.123456"
}
```

---

## 🔍 除錯技巧

### 1. 查看完整的 payload

```bash
python3.11 scripts/gas/gas_caller.py \
  --stock-id 3167 \
  --save-payload

# 使用 jq 格式化輸出
cat scripts/gas/test_payload_3167_2026-02-04.json | jq .
```

### 2. 手動測試 GAS Web App

在 Google Apps Script 編輯器中：
1. 選擇 `testManualTrigger` 函式
2. 點擊「執行」
3. 查看「執行記錄」

### 3. 查看 GAS 日誌

1. 開啟 Apps Script 編輯器
2. 點擊「執行」→ 查看最近的執行
3. 檢查錯誤訊息

---

## 📚 相關文件

- **主 README**: [scripts/gas/README.md](README.md)
- **GAS 程式碼**: [network-diagnostic-analyzer.gs](network-diagnostic-analyzer.gs)
- **專案說明**: [/CLAUDE.md](/CLAUDE.md)

---

## ✅ 測試檢查清單

執行測試前，確認：

- [ ] 已安裝 `requests` 套件
- [ ] 有指定日期的技術分析資料
- [ ] GAS Web App 已正確部署
- [ ] Gemini API Key 已設定且有配額
- [ ] Google Drive 資料夾已設定

執行測試後，檢查：

- [ ] HTTP 狀態碼為 200
- [ ] 回應狀態為 "success"
- [ ] Google Drive 中有新的分析報告
- [ ] 報告內容正確且完整

---

**最後更新**: 2026-02-05

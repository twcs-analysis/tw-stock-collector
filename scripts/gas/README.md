# Google Apps Script - 台股分析 AI

這個目錄包含用於台股數據分析的 Google Apps Script 腳本。

## 📂 檔案說明

- `network-diagnostic-analyzer.gs` - 主程式腳本（使用 Gemini AI 進行台股分析）
- `config.example.gs` - 配置範例檔案
- `config.gs` - 實際配置檔案（**不會提交到 Git**）

## 🔐 安全配置

### 方法一：使用 Google Apps Script Properties Service（推薦）

這是最安全的方式，適合生產環境。

1. 開啟 Google Apps Script 編輯器
2. 點選左側「專案設定」（齒輪圖示）
3. 在「指令碼屬性」區段點選「新增指令碼屬性」
4. 新增以下三個屬性：

   | 屬性名稱 | 說明 | 範例值 |
   |---------|------|--------|
   | `GEMINI_API_KEY` | Gemini API 金鑰 | `AIzaSy...` |
   | `DRIVE_FOLDER_ID` | Google Drive 資料夾 ID | `1JqcJC...` |
   | `SERVICE_SECRET` | 服務驗證密鑰 | `aJ4cj...` |

5. 儲存後，腳本會自動從 Script Properties 讀取這些值

### 方法二：使用本地 config.gs 檔案（開發環境）

1. 複製範例檔案：
   ```bash
   cp scripts/gas/config.example.gs scripts/gas/config.gs
   ```

2. 編輯 `config.gs`，填入實際的 API Key：
   ```javascript
   const CONFIG = {
     GEMINI_API_KEY: 'your_actual_key_here',
     DRIVE_FOLDER_ID: 'your_folder_id_here',
     SERVICE_SECRET: 'your_secret_here'
   };
   ```

3. `config.gs` 已被加入 `.gitignore`，不會被提交到 Git

## 🚀 部署步驟

### 1. 建立 Google Apps Script 專案

1. 前往 [Google Apps Script](https://script.google.com/)
2. 點選「新專案」
3. 將專案命名為「台股分析 AI」

### 2. 複製程式碼

將以下檔案內容複製到 Google Apps Script 編輯器：

- 主程式：`network-diagnostic-analyzer.gs`
- 配置（選擇其一）：
  - 使用 Script Properties（推薦）
  - 或建立 `config.gs` 檔案

### 3. 設定 Gemini API Key

#### 取得 API Key：
1. 前往 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 點選「Create API Key」
3. 複製產生的 API Key

#### 設定到 Script Properties：
按照「方法一」的步驟設定

### 4. 設定 Google Drive 資料夾（選用）

**注意**：Google Drive 儲存是**選用功能**。預設模式下，GAS 會直接在回應中回傳完整的 Markdown 內容，不需要 Drive。

如果需要額外將報告儲存到 Drive，請依照以下步驟：

1. 在 Google Drive 建立一個資料夾用於儲存分析報告
2. 開啟該資料夾，從網址列複製資料夾 ID
   ```
   https://drive.google.com/drive/folders/1JqcJCkuuqL_sHdE7Nm_l6z5a-iIH1Yzc
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                          這就是資料夾 ID
   ```
3. 在 Script Properties 設定：
   - `DRIVE_FOLDER_ID`: 資料夾 ID
   - `ENABLE_DRIVE_STORAGE`: `true`（啟用 Drive 儲存）

**詳細說明**：請參考 [DRIVE_CONFIG.md](DRIVE_CONFIG.md)

### 5. 部署為 Web App

1. 在 Google Apps Script 編輯器中，點選「部署」→「新增部署作業」
2. 選擇類型：「網頁應用程式」
3. 設定：
   - **執行身分**：我
   - **具有存取權的使用者**：所有人
4. 點選「部署」
5. 複製產生的 Web App URL（這是你的 API 端點）

### 6. 測試部署

使用 `testManualTrigger()` 函式測試：

1. 在 Google Apps Script 編輯器中選擇 `testManualTrigger` 函式
2. 點選「執行」
3. 首次執行需要授權存取 Drive 和外部 API
4. 查看執行日誌確認是否成功

## 📊 使用方式

### 方法一：使用 Python 測試腳本（推薦）

```bash
# 基本使用：測試大量（3167）
python scripts/gas/gas_caller.py --stock-id 3167

# 測試台積電（2330）
python scripts/gas/gas_caller.py --stock-id 2330

# 指定日期
python scripts/gas/gas_caller.py --stock-id 2330 --date 2026-02-04

# 指定回調 URL
python scripts/gas/gas_caller.py \
  --stock-id 3167 \
  --callback-url "http://localhost:3000/api/reports/test_001/callback"

# 儲存發送的 payload（除錯用）
python scripts/gas/gas_caller.py --stock-id 3167 --save-payload
```

**腳本功能**：
- ✅ 自動載入股票技術分析資料
- ✅ 組織符合 GAS 格式的請求
- ✅ 發送 POST 請求並顯示結果
- ✅ 錯誤處理與除錯資訊

**前置需求**：
```bash
# 1. 安裝 requests 套件
uv pip install requests

# 2. 確保有技術分析資料
python scripts/data-transformer/transform.py --date 2026-02-04
```

### 方法二：使用 curl 直接測試

```bash
curl -X POST "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec" \
  -H "Content-Type: application/json" \
  -d '{
    "reportId": "test_001",
    "reportData": {
      "stock_info": {
        "stock_id": "2330",
        "stock_name": "台積電",
        "trade_date": "2026-02-04"
      },
      "price_data": {
        "open": 1080.0,
        "high": 1095.0,
        "low": 1075.0,
        "close": 1090.0,
        "volume": 45678912,
        "amount": 49789753600
      },
      "technical_indicators": {
        "ma": {
          "ma_5": 1085.5,
          "ma_10": 1080.2,
          "ma_20": 1075.8
        },
        "rsi": {
          "rsi_6": 65.5,
          "rsi_14": 58.3
        }
      }
    },
    "callbackUrl": "https://your-api.com/callback",
    "timestamp": "2026-02-04T14:30:00Z"
  }'
```

### 請求格式說明

完整的資料結構範例：
```json
{
  "reportId": "test_20260205_143022",
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
      "ma": { "ma_5": 212.3, "ma_10": 221.45, "ma_20": 223.73 },
      "rsi": { "rsi_6": 21.13, "rsi_14": 41.32 },
      "macd": { "dif": -2.76, "dea": -0.04, "histogram": -2.71 },
      "dmi": { "pdi": 16.23, "mdi": 24.18, "adx": 18.12 },
      "bollinger": { "upper": 243.30, "mid": 223.73, "lower": 204.15 },
      "volume": { "vol_ma5": 3728637.4, "vol_ma20": 6621546.05, "vol_ratio": 0.84, "vwap": 210.46 }
    }
  },
  "callbackUrl": "",
  "timestamp": "2026-02-05T14:30:22.123456"
}
```

### 回應格式

**成功時（無 Drive 模式，預設）**：
```json
{
  "status": "success",
  "message": "Analysis completed.",
  "reportId": "test_20260205_143022",
  "markdown_content": "# 📊 大量 (3167) 股票分析報告\n\n...",
  "drive_link": null
}
```

**成功時（Drive 儲存模式）**：
```json
{
  "status": "success",
  "message": "Analysis completed.",
  "reportId": "test_20260205_143022",
  "markdown_content": "# 📊 大量 (3167) 股票分析報告\n\n...",
  "drive_link": "https://drive.google.com/file/d/xxx"
}
```

**失敗時**：
```json
{
  "status": "error",
  "message": "錯誤訊息"
}
```

**回調格式（如有 callbackUrl）**：

成功時：
```json
{
  "status": "completed",
  "markdown_content": "# 分析報告...",
  "drive_link": "https://drive.google.com/file/d/xxx"
}
```

失敗時：
```json
{
  "status": "failed",
  "error_message": "錯誤訊息"
}
```

## 🔍 故障排除

### 問題：Script Properties 讀取為空

**解決方式**：
1. 確認 Script Properties 已正確設定
2. 重新部署 Web App
3. 確認執行身分設定為「我」

### 問題：Gemini API 回傳 403

**解決方式**：
1. 確認 API Key 有效
2. 確認 API Key 已啟用 Generative Language API
3. 檢查 API 配額是否用盡

### 問題：Drive 權限錯誤

**解決方式**：
1. 確認已授權 Drive 存取權限
2. 確認資料夾 ID 正確
3. 嘗試重新授權腳本

## 📝 開發注意事項

1. **不要**將 `config.gs` 提交到 Git
2. **不要**在程式碼中硬編碼 API Key
3. **務必**使用 Script Properties 或環境變數
4. **定期**更新 API Key 和密鑰
5. **監控** API 使用量和費用

## 🔗 相關資源

- [Google Apps Script 文檔](https://developers.google.com/apps-script)
- [Gemini API 文檔](https://ai.google.dev/docs)
- [Google Drive API](https://developers.google.com/drive)

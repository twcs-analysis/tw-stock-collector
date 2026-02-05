# 快速開始指南

## 🎯 目標

在 5 分鐘內完成 GAS Web App 的部署與測試。

---

## ⚡ 3 步驟快速部署

### 步驟 1：建立 GAS 專案（2 分鐘）

1. 前往 [Google Apps Script](https://script.google.com/)
2. 點選「新專案」
3. 將 [network-diagnostic-analyzer.gs](network-diagnostic-analyzer.gs) 的內容複製貼上
4. 點選「儲存」，命名為「台股分析 AI」

### 步驟 2：設定 API Key（2 分鐘）

1. 前往 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 點選「Create API Key」，複製產生的 Key
3. 回到 GAS 編輯器，點選左側「專案設定」⚙️
4. 在「指令碼屬性」新增：
   - 名稱：`GEMINI_API_KEY`
   - 值：貼上你的 API Key

**注意**：`SERVICE_SECRET` 和 `DRIVE_FOLDER_ID` 可暫不設定（預設模式不需要）

### 步驟 3：部署為 Web App（1 分鐘）

1. 點選「部署」→「新增部署作業」
2. 類型選擇「網頁應用程式」
3. 設定：
   - **執行身分**：我
   - **具有存取權的使用者**：所有人
4. 點選「部署」
5. 複製產生的 **Web App URL**（很重要！）

---

## 🧪 測試

### 安裝 Python 依賴

```bash
uv pip install requests
```

### 更新測試腳本的 URL

編輯 [gas_caller.py](gas_caller.py) 的第 16 行，將 URL 改為你的：

```python
GAS_WEB_APP_URL = "https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec"
```

### 執行測試

```bash
# 確保有技術分析資料
python scripts/data-transformer/transform.py --date 2026-02-04

# 測試 GAS Web App
python3.11 scripts/gas/gas_caller.py --stock-id 3167
```

**預期結果**：

```
============================================================
📊 GAS Web App 測試腳本
============================================================

🔍 載入股票資料: 3167 (2026-02-04)
✅ 成功載入: 大量

📋 建立報告資料...

📤 發送請求到 GAS Web App...
URL: https://script.google.com/macros/s/.../exec
Report ID: test_20260205_153620
Stock: 大量 (3167)

✅ HTTP 狀態碼: 200

============================================================
📥 GAS 回應結果
============================================================
{
  "status": "success",
  "message": "Analysis completed.",
  "reportId": "test_20260205_153620",
  "drive_link": null
}

✅ 測試成功！

============================================================
📄 AI 分析報告
============================================================
# 📊 大量 (3167) 股票分析報告

## 一、數據核實與即時市況
- 股票名稱 / 代號：大量 (3167)
...（完整分析內容）...

💡 此次測試未儲存到 Google Drive
```

---

## ✅ 成功！

恭喜！你已經成功部署並測試了 GAS Web App。

---

## 📚 下一步

### 選項 A：基本使用（推薦）

繼續使用預設的「無 Drive 模式」，適合日常分析：

```bash
# 測試不同股票
python3.11 scripts/gas/gas_caller.py --stock-id 2330  # 台積電
python3.11 scripts/gas/gas_caller.py --stock-id 0050  # 元大台灣50
```

### 選項 B：啟用 Drive 儲存（選用）

如需長期保存報告，請參考：
- [DRIVE_CONFIG.md](DRIVE_CONFIG.md) - Drive 儲存設定指南

### 選項 C：整合到應用程式

將 GAS Web App 整合到你的應用程式：

```python
import requests

response = requests.post(
    "https://script.google.com/macros/s/YOUR_ID/exec",
    json={
        "reportId": "app_001",
        "reportData": stock_data,
        "callbackUrl": "https://your-api.com/callback"
    }
)

result = response.json()
markdown_report = result['markdown_content']
```

---

## 🐛 故障排除

### Gemini API 配額用盡

**錯誤**：
```json
{
  "status": "error",
  "message": "Error: Gemini API 失敗 (429): quota exceeded"
}
```

**解決方式**：
1. 等待配額重置（通常幾分鐘到 1 小時）
2. 檢查 [API 使用量](https://ai.dev/rate-limit)
3. 升級到付費方案（如需要）

### 找不到股票資料

**錯誤**：
```
❌ 找不到股票 9999 的資料
```

**解決方式**：
```bash
# 查看可用的股票代號
python3.11 -c "
import json
data = json.load(open('data/raw/price/2026/02/2026-02-04.json'))
for s in data['data'][:20]:
    print(f\"{s['stock_id']}: {s['stock_name']}\")
"
```

### 其他問題

請參考：
- [USAGE.md](USAGE.md) - 詳細使用說明與常見問題
- [README.md](README.md) - 完整文檔

---

## 📞 需要協助？

1. 查看相關文檔
2. 檢查 GAS 執行日誌
3. 建立 GitHub Issue

---

**估計時間**：5-10 分鐘
**難度**：⭐⭐☆☆☆（簡單）
**最後更新**：2026-02-05

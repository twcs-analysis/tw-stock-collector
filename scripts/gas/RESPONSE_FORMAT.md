# GAS Web App 回應格式說明

## 📋 概述

本文件說明 GAS Web App 的完整回應格式與各欄位意義。

---

## 🎯 回應結構

### 成功回應（預設模式）

```json
{
  "status": "success",
  "message": "Analysis completed.",
  "reportId": "test_20260205_163415",
  "markdown_content": "完整的 Markdown 分析報告內容...",
  "drive_link": null
}
```

### 成功回應（Drive 儲存模式）

```json
{
  "status": "success",
  "message": "Analysis completed.",
  "reportId": "test_20260205_163415",
  "markdown_content": "完整的 Markdown 分析報告內容...",
  "drive_link": "https://drive.google.com/file/d/1Ab2Cd3Ef4Gh5Ij6Kl7Mn8Op9Qr0St1Uv/view"
}
```

### 錯誤回應

```json
{
  "status": "error",
  "message": "Error: Gemini API 失敗 (429): quota exceeded..."
}
```

---

## 📊 欄位說明

### 1. `status` (字串，必需)

**類型**: `"success"` | `"error"`

**說明**: 處理狀態

**可能值**:
- `"success"` - 處理成功，已生成分析報告
- `"error"` - 處理失敗，檢查 `message` 欄位了解錯誤原因

**範例**:
```json
"status": "success"
```

---

### 2. `message` (字串，必需)

**說明**: 處理訊息或錯誤描述

**成功時**:
```json
"message": "Analysis completed."
```

**失敗時**:
```json
"message": "Error: Gemini API 失敗 (429): Resource exhausted..."
```

---

### 3. `reportId` (字串，僅成功時)

**說明**: 報告識別碼，與請求時傳送的 `reportId` 相同

**用途**:
- 追蹤請求
- 關聯請求與回應
- 用於 callback 識別

**格式**: 自訂，建議格式 `{prefix}_{timestamp}`

**範例**:
```json
"reportId": "test_20260205_163415"
```

---

### 4. `markdown_content` (字串，僅成功時)

**說明**: AI 生成的完整 Markdown 格式分析報告

**內容結構**:
```markdown
好的，收到數據，我將以台股資深策略分析師的角色...

一、 數據核實與即時市況
- 股票名稱 / 代號：...
- 最後交易日股價：...

二、 技術面：趨勢結構分析
- 均線 (MA)：...
- 動能指標 (MACD/RSI)：...
🚩 技術總結：[偏多 / 中性 / 偏空]

三、 籌碼面：法人與主力行為
...

四、 基本面：產業與深度財報
...

五、 💰 殖利率分析與配息預估
...

六、 🔥 風險與出貨偵測
...

七、 🎯 綜合評等與行動建議
- 投資屬性：...
- 核心觀點：...
- 執行策略：
  1. 進場/觀察價：...
  2. 停損/重新評估點：...
```

**特性**:
- 格式：Markdown
- 長度：約 2,000 - 5,000 字元
- 編碼：UTF-8
- 包含：完整的七個分析章節

---

### 5. `drive_link` (字串 | null，僅成功時)

**說明**: Google Drive 儲存連結

**可能值**:
- `null` - 未啟用 Drive 儲存（預設）
- `"https://drive.google.com/file/d/..."` - Drive 檔案連結

**預設模式** (ENABLE_DRIVE_STORAGE = false):
```json
"drive_link": null
```

**Drive 儲存模式** (ENABLE_DRIVE_STORAGE = true):
```json
"drive_link": "https://drive.google.com/file/d/1Ab2Cd3Ef4Gh5Ij6Kl7Mn8Op9Qr0St1Uv/view"
```

**Drive 儲存失敗時**:
```json
"drive_link": null
```
（註：Drive 失敗不影響主流程，仍會回傳 `markdown_content`）

---

## 🔍 完整範例

### 範例 1：成功回應（無 Drive）

```json
{
  "status": "success",
  "message": "Analysis completed.",
  "reportId": "test_20260205_163415",
  "markdown_content": "好的，收到數據，我將以台股資深策略分析師的角色，為您深度解析大量 (3167) 的即時市況...\n\n一、 數據核實與即時市況\n- 股票名稱 / 代號：大量 / 3167\n- 最後交易日股價：212.5\n...\n\n七、 🎯 綜合評等與行動建議\n- 投資屬性：短線爆發\n- 核心觀點：目前不具備明顯進場優勢...\n- 執行策略：\n  1. 進場/觀察價：221.45\n  2. 停損/重新評估點：203.78\n",
  "drive_link": null
}
```

### 範例 2：錯誤回應（Gemini API 配額用盡）

```json
{
  "status": "error",
  "message": "Error: Gemini API 失敗 (429): {\n  \"error\": {\n    \"code\": 429,\n    \"message\": \"Resource exhausted. Please try again later.\",\n    \"status\": \"RESOURCE_EXHAUSTED\"\n  }\n}\n"
}
```

### 範例 3：錯誤回應（JSON 解析失敗）

```json
{
  "status": "error",
  "message": "SyntaxError: Unexpected token < in JSON at position 0"
}
```

---

## 📏 欄位大小參考

| 欄位 | 最小長度 | 典型長度 | 最大長度 |
|------|----------|----------|----------|
| `status` | 5 | 7 | 7 |
| `message` | 10 | 20 | 1,000 |
| `reportId` | 5 | 25 | 100 |
| `markdown_content` | 500 | 3,000 | 10,000 |
| `drive_link` | 4 (null) | 80 | 150 |

**總回應大小**: 通常 3-12 KB

---

## 🔄 回調格式（Callback）

如果請求時提供了 `callbackUrl`，GAS 會另外發送回調請求：

### 成功時

```json
{
  "status": "completed",
  "markdown_content": "完整的 Markdown 分析報告內容...",
  "drive_link": "https://drive.google.com/file/d/xxx"
}
```

### 失敗時

```json
{
  "status": "failed",
  "error_message": "錯誤訊息"
}
```

**注意**: 回調格式與主回應格式略有不同：
- 成功狀態: `"completed"` (回調) vs `"success"` (主回應)
- 欄位名稱: `error_message` (回調) vs `message` (主回應)

---

## 💡 使用建議

### 1. 解析回應

```python
import json
import requests

response = requests.post(gas_url, json=payload)
result = response.json()

if result['status'] == 'success':
    # 取得分析報告
    report = result['markdown_content']

    # 檢查是否有 Drive 連結
    if result.get('drive_link'):
        print(f"Drive 連結: {result['drive_link']}")

    # 處理報告內容
    process_report(report)
else:
    # 處理錯誤
    print(f"錯誤: {result['message']}")
```

### 2. 儲存報告

```python
# 儲存為 Markdown 檔案
if result['status'] == 'success':
    filename = f"report_{result['reportId']}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(result['markdown_content'])
```

### 3. 錯誤處理

```python
try:
    response = requests.post(gas_url, json=payload, timeout=60)
    response.raise_for_status()  # 檢查 HTTP 狀態碼

    result = response.json()

    if result['status'] == 'error':
        if '429' in result['message']:
            # API 配額用盡
            print("配額用盡，請稍後重試")
        else:
            # 其他錯誤
            print(f"處理失敗: {result['message']}")

except requests.exceptions.Timeout:
    print("請求逾時")
except requests.exceptions.RequestException as e:
    print(f"請求失敗: {e}")
```

---

## 🐛 常見錯誤訊息

### 1. Gemini API 配額用盡

```
Error: Gemini API 失敗 (429): Resource exhausted...
```

**解決方式**: 等待配額重置或使用新的 API Key

### 2. Gemini API 金鑰錯誤

```
Error: Gemini API 失敗 (401): Invalid API key...
```

**解決方式**: 檢查 Script Properties 中的 `GEMINI_API_KEY`

### 3. JSON 解析錯誤

```
SyntaxError: Unexpected token...
```

**解決方式**: 檢查請求的 JSON 格式是否正確

---

## 📚 相關文件

- **使用說明**: [USAGE.md](USAGE.md)
- **Drive 設定**: [DRIVE_CONFIG.md](DRIVE_CONFIG.md)
- **主文檔**: [README.md](README.md)

---

**最後更新**: 2026-02-05
**維護者**: Jason Huang

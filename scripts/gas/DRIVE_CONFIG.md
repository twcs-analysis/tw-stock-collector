# Google Drive 儲存設定

## 📋 概述

GAS Web App 現在支援兩種模式：

1. **無 Drive 模式**（預設）- 直接在回應中回傳 Markdown 內容
2. **Drive 儲存模式**（選用）- 額外儲存到 Google Drive

---

## 🎯 模式比較

| 功能 | 無 Drive 模式 | Drive 儲存模式 |
|------|--------------|---------------|
| **Markdown 回傳** | ✅ 直接回傳 | ✅ 直接回傳 |
| **Drive 儲存** | ❌ 不儲存 | ✅ 額外儲存 |
| **需要 Drive API** | ❌ 不需要 | ✅ 需要授權 |
| **回應速度** | ⚡ 快速 | 🐢 稍慢（需寫入 Drive） |
| **適用場景** | 一般使用 | 需要長期保存報告 |

---

## ⚙️ 設定方式

### 方法一：使用預設（無 Drive 模式）

**不需要任何設定**，開箱即用！

GAS 會直接在回應中回傳完整的 Markdown 內容：

```json
{
  "status": "success",
  "message": "Analysis completed.",
  "reportId": "test_20260205_143022",
  "markdown_content": "# 📊 大量 (3167) 股票分析報告\n\n...",
  "drive_link": null
}
```

---

### 方法二：啟用 Drive 儲存模式

如果需要將報告儲存到 Google Drive，請依照以下步驟：

#### 步驟 1：建立 Drive 資料夾

1. 前往 [Google Drive](https://drive.google.com)
2. 建立一個資料夾（如：「台股分析報告」）
3. 開啟該資料夾，從網址列複製資料夾 ID

**範例**：
```
https://drive.google.com/drive/folders/1JqcJCkuuqL_sHdE7Nm_l6z5a-iIH1Yzc
                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                        這就是資料夾 ID
```

#### 步驟 2：設定 Script Properties

在 Google Apps Script 編輯器中：

1. 點選左側「專案設定」（齒輪圖示）⚙️
2. 在「指令碼屬性」區段點選「新增指令碼屬性」
3. 新增以下屬性：

| 屬性名稱 | 屬性值 | 說明 |
|---------|--------|------|
| `DRIVE_FOLDER_ID` | `1JqcJC...` | Drive 資料夾 ID |
| `ENABLE_DRIVE_STORAGE` | `true` | 啟用 Drive 儲存 |

**重要**：`ENABLE_DRIVE_STORAGE` 必須設定為字串 `"true"`（含引號）

#### 步驟 3：授權 Drive 存取

首次執行時：

1. 在 GAS 編輯器中選擇 `testManualTrigger` 函式
2. 點選「執行」
3. 授權存取 Google Drive

#### 步驟 4：重新部署

1. 點選「部署」→「管理部署作業」
2. 點選「編輯」（鉛筆圖示）
3. 更新版本
4. 點選「部署」

---

## 🧪 測試驗證

### 測試無 Drive 模式（預設）

```bash
python3.11 scripts/gas/gas_caller.py --stock-id 3167
```

**預期結果**：
- ✅ 回應包含 `markdown_content`
- ✅ `drive_link` 為 `null`
- ✅ 直接顯示分析報告內容

---

### 測試 Drive 儲存模式

設定完成後執行：

```bash
python3.11 scripts/gas/gas_caller.py --stock-id 3167
```

**預期結果**：
- ✅ 回應包含 `markdown_content`
- ✅ `drive_link` 有實際連結
- ✅ Google Drive 中有新檔案
- ✅ 檔名格式：`diag_report_{股票代號}_{MMDDHHmm}.md`

---

## 📝 程式碼說明

### Drive 儲存邏輯

```javascript
// 檢查是否啟用 Drive 儲存
const enableDrive = CONFIG.ENABLE_DRIVE_STORAGE || false;

if (enableDrive && CONFIG.DRIVE_FOLDER_ID) {
  try {
    // 儲存到 Drive
    const driveFile = saveToDrive(aiMarkdown, ip, reportId);
    driveLink = driveFile.getUrl();
    console.log(`✅ 已儲存到 Drive: ${driveLink}`);
  } catch (driveError) {
    // Drive 失敗不影響主流程
    console.error(`⚠️ Drive 儲存失敗: ${driveError.toString()}`);
  }
}
```

**設計原則**：
- Drive 儲存是**額外功能**，失敗不影響主流程
- 即使 Drive 失敗，仍會回傳完整的 Markdown 內容
- 適合需要長期保存報告的場景

---

## 🔍 故障排除

### 問題 1：Drive 儲存失敗

**症狀**：
- 回應中 `drive_link` 為 `null`
- GAS 日誌顯示 Drive 錯誤

**檢查清單**：
- [ ] `ENABLE_DRIVE_STORAGE` 是否設定為 `"true"`（字串）
- [ ] `DRIVE_FOLDER_ID` 是否正確
- [ ] 是否已授權 Drive 存取權限
- [ ] Drive 資料夾是否存在且可存取

**解決方式**：
```bash
# 1. 檢查 Script Properties
# 在 GAS 編輯器中查看「專案設定」→「指令碼屬性」

# 2. 重新授權
# 執行 testManualTrigger 函式並授權

# 3. 測試 Drive API
# 在 GAS 編輯器中執行以下程式碼：
const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
console.log('資料夾名稱:', folder.getName());
```

---

### 問題 2：無法取得 Markdown 內容

**症狀**：
- 回應中沒有 `markdown_content` 欄位

**原因**：
- 使用舊版 GAS 程式碼

**解決方式**：
1. 更新 GAS 程式碼到最新版本
2. 重新部署 Web App
3. 清除瀏覽器快取

---

### 問題 3：Markdown 內容被截斷

**症狀**：
- 回應中的 Markdown 內容不完整

**原因**：
- Google Apps Script 回應大小限制（50 MB）

**解決方式**：
- 一般分析報告約 5-10 KB，不會超過限制
- 如果真的太大，建議只使用 Drive 儲存模式

---

## 💡 建議

### 何時使用無 Drive 模式？

✅ **推薦使用**：
- 一般日常分析
- 即時查詢需求
- 不需要長期保存
- 追求快速回應

### 何時使用 Drive 儲存模式？

✅ **推薦使用**：
- 需要長期保存報告
- 需要分享報告連結
- 需要建立報告資料庫
- 有合規或稽核需求

---

## 🔗 相關文件

- **主 README**: [scripts/gas/README.md](README.md)
- **使用說明**: [scripts/gas/USAGE.md](USAGE.md)
- **GAS 程式碼**: [network-diagnostic-analyzer.gs](network-diagnostic-analyzer.gs)

---

**最後更新**: 2026-02-05
**維護者**: Jason Huang

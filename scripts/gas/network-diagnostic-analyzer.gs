/**
 * 核心配置
 *
 * 注意：實際部署時，請使用 Google Apps Script 的 Properties Service
 * 來儲存敏感資訊，而非硬編碼在程式碼中。
 *
 * 設定方式：
 * 1. 在 Google Apps Script 編輯器中，點選「專案設定」
 * 2. 在「指令碼屬性」區段新增以下屬性：
 *    - GEMINI_API_KEY: 你的 Gemini API Key
 *    - DRIVE_FOLDER_ID: Google Drive 資料夾 ID
 *    - SERVICE_SECRET: 服務驗證密鑰
 * 3. 使用 PropertiesService.getScriptProperties().getProperty() 讀取
 *
 * 或者使用外部 config.gs 檔案（不提交到 Git）
 */

// 方法一：從 Script Properties 讀取（推薦用於生產環境）
const CONFIG = {
  GEMINI_API_KEY: PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY') || '',
  DRIVE_FOLDER_ID: PropertiesService.getScriptProperties().getProperty('DRIVE_FOLDER_ID') || '',
  SERVICE_SECRET: PropertiesService.getScriptProperties().getProperty('SERVICE_SECRET') || '',

  // 是否啟用 Google Drive 儲存（預設關閉）
  // 設定為 'true' 字串以啟用 Drive 儲存
  ENABLE_DRIVE_STORAGE: PropertiesService.getScriptProperties().getProperty('ENABLE_DRIVE_STORAGE') === 'true'
};

// 方法二：從外部 config.gs 檔案讀取（開發環境）
// 如果上面的 Script Properties 為空，且存在 config.gs，會自動載入
// 請確保 config.gs 已加入 .gitignore

/**
 * 接收來自 Admin API 的 POST 請求
 */
function doPost(e) {
  try {
    // 1. 解析後端傳來的數據
    const data = JSON.parse(e.postData.contents);

    const { reportId, reportData, callbackUrl, timestamp } = data;

    // 嘗試從 reportData 中提取 IP
    const ip = (reportData.clientInfo && reportData.clientInfo.ip)
      ? reportData.clientInfo.ip
      : (reportData.ip && reportData.ip.address)
        ? reportData.ip.address
        : "unknown_ip";

    console.log(`收到分析請求 | ID: ${reportId} | IP: ${ip}`);

    // 2. 呼叫 Gemini 進行診斷
    const aiMarkdown = callGeminiAI(reportData);

    // 3. 【選項】存入 Google Drive（預設關閉）
    let driveLink = null;
    const enableDrive = true; // 強制啟用 Drive 儲存（測試用）

    if (enableDrive && CONFIG.DRIVE_FOLDER_ID) {
      try {
        const driveFile = saveToDrive(aiMarkdown, ip, reportId);
        driveLink = driveFile.getUrl();
        console.log(`✅ 已儲存到 Drive: ${driveLink}`);
      } catch (driveError) {
        console.error(`⚠️ Drive 儲存失敗: ${driveError.toString()}`);
        // 繼續執行，不因 Drive 失敗而中斷
      }
    }

    // 4. 執行回調 (Callback) 通知後端 API
    if (callbackUrl) {
      sendCallbackToAdmin(callbackUrl, aiMarkdown, driveLink);
    }

    // 5. 回傳 GAS 分析結果（直接包含 Markdown）
    return ContentService.createTextOutput(JSON.stringify({
      status: 'success',
      message: 'Analysis completed.',
      reportId: reportId,
      markdown_content: aiMarkdown,
      drive_link: driveLink
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    console.error("❌ doPost 發生錯誤: " + error.toString());

    // 嘗試回調失敗狀態
    try {
      const data = JSON.parse(e.postData.contents);
      if (data.callbackUrl) {
        sendCallbackToAdminFailed(data.callbackUrl, error.toString());
      }
    } catch (callbackError) {
      console.error("❌ 回調失敗狀態也失敗: " + callbackError.toString());
    }

    return ContentService.createTextOutput(JSON.stringify({
      status: 'error',
      message: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * 呼叫 Gemini API
 */
function callGeminiAI(jsonContent) {
  const modelName = "gemini-2.0-flash";
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${CONFIG.GEMINI_API_KEY}`;

  const systemInstruction = `# Role
你是一位深耕台股市場 20 年的首席策略分析師，專長於「技術面、籌碼面、基本面」三位一體的診斷。你的目標是將數據轉化為具備實戰價值的投資決策建議。

# Background
使用者正在透過自動化系統追蹤台股動態。你將收到股票的**技術面完整數據**（價格、均線、技術指標）。

**重要說明**：
- ✅ 技術面資料：完整提供，請深入分析
- ⚠️ 籌碼面/基本面：**資料未提供**，請根據你的專業知識、產業經驗、市場慣例進行推測與建議
- 💡 分析策略：結合實際數據（技術面）+ 專業推論（其他面向）= 完整投資建議

# Task & Steps
請依據以下結構進行分析：

一、 數據核實與即時市況
- 股票名稱 / 代號：{確認結果}
- 最後交易日股價：{確認結果}
- [分析師修正]：主動檢核數據邏輯，若發現股價與均線位置有明顯矛盾，請先行指出。

二、 技術面：趨勢結構分析（✅ 基於實際數據）
- 均線 (MA)：判斷多空排列、乖離程度，標註支撐與反壓價位。
- 動能指標 (MACD/RSI)：判斷處於趨勢初期、末端或背離狀態。
- 波動與量價 (BB/VOL)：判斷布林通道收斂或擴張，偵測量價背離跡象。
- 成交量分析：評估量能變化、爆量或縮量的意義。
🚩 技術總結：[偏多 / 中性 / 偏空]

三、 籌碼面：法人與主力行為（💡 專業推論）
**說明**：由於缺乏即時籌碼數據，以下為基於技術面特徵的專業推論：

- 量價關係推測：
  * 若「價漲量增」→ 推測籌碼集中，法人可能進場
  * 若「價漲量縮」→ 警示籌碼鬆散，可能缺乏法人支撐
  * 若「價跌量增」→ 警示法人可能出貨

- 產業特性考量：
  * 根據股票代號/名稱判斷產業（電子、傳產、金融等）
  * 推測該產業常見的法人偏好與籌碼特性

- 價位推測：
  * 股價位於相對高點 → 提醒留意法人獲利了結風險
  * 股價位於相對低點 → 提醒關注法人逢低布局可能

🚩 籌碼總結：[基於技術面的合理推測 + 風險提示]

四、 基本面：產業與財報推論（💡 專業推論）
**說明**：由於缺乏財報數據，以下為基於產業經驗的合理推測：

- 產業識別與特性：
  * 根據公司名稱/代號判斷所屬產業
  * 說明該產業的景氣循環特性、毛利率水準、競爭態勢

- 評價水準推測：
  * 根據股價位階（相對 MA120/MA240）推測估值高低
  * 結合產業特性推測合理本益比區間

- 風險因子提示：
  * 產業面：該產業常見的風險（匯率、原料、競爭）
  * 總經面：利率、景氣、政策等外部因素

🚩 基本面總結：[產業推測 + 評價水準 + 風險提示]

五、 💰 殖利率與投資屬性（💡 專業推論）
**說明**：由於缺乏配息數據，以下為基於產業慣例的推測：

- 配息特性推測：
  * 根據產業特性推測配息政策（金融股高殖利率、成長股低配息）
  * 根據股價位階推測殖利率吸引力

- 投資屬性判斷：
  * 結合技術面+產業特性，判斷適合的投資策略
  * 短線：波段操作 / 中長線：價值投資或成長投資

六、 🔥 風險與出貨偵測（✅ 基於技術面數據）
- 技術面風險：
  * 量價背離：高檔量縮、低檔量增
  * 均線破位：跌破關鍵支撐
  * 動能轉弱：MACD/RSI 背離

- 推測性風險（基於經驗）：
  * 高檔風險：股價遠高於長期均線，推測法人可能獲利了結
  * 籌碼風險：連續上漲後量縮，推測追價意願不足

七、 🎯 綜合評等與行動建議
- 投資屬性：{短線爆發 / 波段操作 / 中長線價值投資}
- 核心觀點：
  * 技術面評價（基於數據）
  * 籌碼面推測（基於經驗）
  * 基本面考量（基於產業知識）
  * 整體結論：是否具備進場優勢

- 執行策略：
  1. 進場/觀察價：{具體數字，基於技術支撐/壓力}
  2. 停損/重新評估點：{具體觸發條件}
  3. 風險提示：{主要風險因子}

# Constraints
1. 語言：繁體中文
2. 語氣：專業、務實、明確
3. 格式：保留所有 Emoji 標籤與分段結構
4. 重要原則：
   - ✅ 有數據的部分（技術面）→ 深入分析
   - 💡 無數據的部分（籌碼/基本面）→ 明確標示「推測」，並說明推測依據
   - ⚠️ 絕不編造具體數字（不可虛構法人買賣張數、EPS 數據）
   - ✅ 可以提供合理的區間推測（如：「該產業毛利率通常在 20-30%」）
5. 透明度：在籌碼面/基本面章節開頭明確說明「由於缺乏數據，以下為專業推論」`;

  const payload = {
    contents: [{
      parts: [{
        text: `${systemInstruction}\n\n待分析數據如下：\n${typeof jsonContent === 'string' ? jsonContent : JSON.stringify(jsonContent)}`
      }]
    }],
    generationConfig: {
      temperature: 0.2,
      maxOutputTokens: 2048
    }
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(url, options);

  if (response.getResponseCode() !== 200) {
     throw new Error(`Gemini API 失敗 (${response.getResponseCode()}): ${response.getContentText()}`);
  }

  const result = JSON.parse(response.getContentText());

  if (result.candidates && result.candidates[0].content && result.candidates[0].content.parts) {
    return result.candidates[0].content.parts[0].text;
  } else {
    throw new Error('Gemini API 回傳格式異常');
  }
}

/**
 * 存入 Google Drive
 * 檔名格式修正為: diag_report_{IP}_{MMDDHHmm}.md
 */
function saveToDrive(markdown, ip, reportId) {
  const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);

  // 取得當前時間，並格式化為 MMddHHmm (月日時分)
  // 注意：Utilities.formatDate 的月份 MM 是大寫，分鐘 mm 是小寫
  const dateStr = Utilities.formatDate(new Date(), "GMT+8", "MMddHHmm");

  // 組合新檔名
  // 如果 IP 不存在或為 unknown_ip，可以考慮加個 fallback 處理，這裡直接使用傳入的 ip
  const fileName = `diag_report_${ip}_${dateStr}.md`;

  // 建立檔案
  const file = folder.createFile(fileName, markdown, MimeType.PLAIN_TEXT);

  // 設定權限為「任何知道連結的人皆可檢視」
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);

  return file;
}

/**
 * 【修正】回傳成功結果給 Admin API
 * - 使用 X-Service-Key header 驗證
 * - 欄位名稱對應 Admin API 期望的格式
 */
function sendCallbackToAdmin(callbackUrl, markdown, driveLink) {
  console.log(`準備回調至: ${callbackUrl}`);

  // 【修正】欄位名稱對應 Admin API 的 reports.js
  const payload = {
    status: 'completed',           // Admin API 需要 status 欄位
    markdown_content: markdown,    // Admin API 期望 markdown_content
    drive_link: driveLink || null  // Drive link（可能為 null）
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'X-Service-Key': CONFIG.SERVICE_SECRET  // 【修正】放在 header 中
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(callbackUrl, options);
    console.log(`回調結果 (${response.getResponseCode()}): ${response.getContentText()}`);
  } catch (e) {
    console.error("❌ 回調失敗: " + e.toString());
  }
}

/**
 * 【新增】回傳失敗狀態給 Admin API
 */
function sendCallbackToAdminFailed(callbackUrl, errorMessage) {
  console.log(`準備回調失敗狀態至: ${callbackUrl}`);

  const payload = {
    status: 'failed',
    error_message: errorMessage
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'X-Service-Key': CONFIG.SERVICE_SECRET
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(callbackUrl, options);
    console.log(`失敗回調結果 (${response.getResponseCode()}): ${response.getContentText()}`);
  } catch (e) {
    console.error("❌ 失敗回調也失敗: " + e.toString());
  }
}

// ------------------------------------
// 以下為手動測試區 (可保留用於 Debug)
// ------------------------------------
function testManualTrigger() {
  const mockData = {
    reportId: "manual_test_002",
    reportData: {
      "clientInfo": { "ip": "1.1.1.1" },
      "timestamp": "2026-01-27T00:00:00Z",
      "network": { "type": "4g", "downlink": 5.75 },
      "domainTests": [
        { "label": "Test API", "status": "success", "latency": 100 }
      ]
    },
    callbackUrl: ""
  };

  try {
    console.log("--- 開始手動測試 ---");
    const aiMarkdown = callGeminiAI(mockData.reportData);
    console.log("✅ Gemini 分析成功");
    const file = saveToDrive(aiMarkdown, "1.1.1.1", mockData.reportId);
    console.log("✅ 檔案連結: " + file.getUrl());
  } catch (error) {
    console.error("❌ 測試失敗: " + error.toString());
  }
}

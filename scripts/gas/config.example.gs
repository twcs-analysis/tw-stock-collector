/**
 * 配置範例檔案
 *
 * 使用方式：
 * 1. 將此檔案複製為 config.gs
 * 2. 填入你的實際 API Key 和設定
 * 3. config.gs 已被加入 .gitignore，不會被提交到 Git
 *
 * 注意：生產環境建議使用 Google Apps Script 的 Properties Service
 * 而非此檔案來儲存敏感資訊。
 */
const CONFIG = {
  GEMINI_API_KEY: 'YOUR_GEMINI_API_KEY_HERE',

  // Google Drive 儲存（選用）
  // 預設關閉，如需啟用請將 ENABLE_DRIVE_STORAGE 設為 true
  DRIVE_FOLDER_ID: 'YOUR_DRIVE_FOLDER_ID_HERE',
  ENABLE_DRIVE_STORAGE: false,  // 改為 true 以啟用 Drive 儲存

  SERVICE_SECRET: 'YOUR_SERVICE_SECRET_HERE'
};

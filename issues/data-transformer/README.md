# Data-Transformer Code Review 總覽

## 📊 問題統計

總計 **22 個問題**，按嚴重程度分類：

| 嚴重程度 | 數量 | 模組 |
|---------|------|------|
| **CRITICAL** ⭐⭐⭐⭐⭐ | 2 | indicators, technical_analysis_transformer |
| **HIGH** ⭐⭐⭐⭐ | 2 | technical_analysis_transformer, base_transformer |
| **MEDIUM** ⭐⭐⭐ | 14 | 所有模組 |
| **LOW** ⭐ | 4 | main, database_saver |

---

## 🔴 立即修復清單（CRITICAL + HIGH）

### 1. **indicators.py** - RSI 計算的除以零風險
- **文件**: `services/data-transformer/app/indicators.py` (Line 37-54)
- **問題**: 股票持續上漲時 `avg_loss` 為 0，導致 RSI 返回 NaN
- **優先級**: ⭐⭐⭐⭐⭐ CRITICAL
- **預計修復時間**: 30 分鐘

### 2. **technical_analysis_transformer.py** - 歷史數據日期遍歷邏輯
- **文件**: `services/data-transformer/app/technical_analysis_transformer.py` (Line 150-176)
- **問題**: 使用 `timedelta(days=1)` 逐日遍歷，浪費資源在周末/假期
- **優先級**: ⭐⭐⭐⭐⭐ CRITICAL
- **預計修復時間**: 45 分鐘

### 3. **technical_analysis_transformer.py** - 跳過股票的不可見性
- **文件**: `services/data-transformer/app/technical_analysis_transformer.py` (Line 74-82)
- **問題**: 數據不足的股票無聲地被跳過，用戶無法得知
- **優先級**: ⭐⭐⭐⭐ HIGH
- **預計修復時間**: 30 分鐘

### 4. **base_transformer.py** - 返回值語義不清晰
- **文件**: `services/data-transformer/app/base_transformer.py` (Line 257-270)
- **問題**: 無數據也返回 `True`，導致統計混亂
- **優先級**: ⭐⭐⭐⭐ HIGH
- **預計修復時間**: 40 分鐘

---

## 🟡 中等優先級問題（MEDIUM）

### 按模組分類

#### **indicators.py** (3 個問題)
1. ADX 計算中的 ATR 調用不當 (Line 167)
2. VWAP 累積求和邏輯 (Line 125-133) - *可選*

#### **technical_analysis_transformer.py** (5 個問題)
1. 數據類型轉換不一致 (Line 158, 193)
2. 指標計算中的 NaN 值未處理 (Line 115-144)
3. 缺少輸出列的容錯性 (Line 180-187)

#### **base_transformer.py** (3 個問題)
1. 批量轉換中的統計不準確 (Line 315-350)
2. 過於寬泛的異常捕獲 (Line 257-270)

#### **main.py** (3 個問題)
1. 參數驗證缺失
2. 日期範圍檢查不足
3. 錯誤處理中缺少恢復機制

#### **database_saver.py** (4 個問題)
1. 缺少數據庫連接復用
2. 批量插入配置不 optimal
3. 缺少數據驗證
4. 缺少事務管理

---

## 💡 解決方案優先順序

### 第一波（今天完成）- 修復 Critical 問題
```
1. indicators.py - RSI 除以零 (30 min)
2. technical_analysis_transformer.py - 日期遍歷 (45 min)
   預計耗時: 75 分鐘
```

### 第二波（明天）- 修復 High 問題
```
3. technical_analysis_transformer.py - 跳過股票 (30 min)
4. base_transformer.py - 返回值語義 (40 min)
   預計耗時: 70 分鐘
```

### 第三波（本週內）- 修復 Medium 問題
```
- 依優先級逐個修復
- 建議先修復影響數據質量的問題
- 預計耗時: 3-4 小時
```

### 第四波（可選）- 優化 Low 優先級
```
- 日誌優化
- 文檔完善
- 可在代碼審查後進行
```

---

## 📁 檔案結構

```
issues/data-transformer/
├── 01-indicators.md                      # 技術指標模組
├── 02-technical_analysis_transformer.md  # 技術分析轉換器
├── 03-base_transformer.md                # 基礎轉換器
├── 04-main.md                            # 主程式入口
├── 05-database_saver.md                  # 數據庫儲存
└── README.md                             # 此文件
```

---

## 🔍 驗證檢查清單

修復完成後，使用以下清單驗證：

- [ ] RSI 指標：測試持續上漲股票的 RSI 計算是否返回有效值（不是 NaN）
- [ ] 歷史數據加載：驗證周末/假期不再產生失敗日誌
- [ ] 跳過股票報告：運行轉換後，日誌中應顯示跳過股票的詳細列表
- [ ] 返回值統計：批量轉換的統計信息應準確反映成功/失敗的操作數
- [ ] ADX 指標：對比計算結果與預期值
- [ ] 數據庫連接：監控連接數是否保持穩定（不持續增加）
- [ ] 事務管理：模擬失敗場景，驗證數據是否被回滾

---

## 📝 相關文檔

- 架構文檔: [ARCHITECTURE.md](../../ARCHITECTURE.md)
- 技術方案: [TECHNICAL_ANALYSIS_TRANSFORM.md](../../docs/TECHNICAL_ANALYSIS_TRANSFORM.md)

---

## 👥 聯繫方式

如有問題，請參考各模組對應的 Issue 文件。


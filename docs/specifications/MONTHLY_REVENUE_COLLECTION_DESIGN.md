# 月營收收集功能 - 完整設計規範

**文件版本**: 1.0
**建立日期**: 2026-02-06
**設計者**: Claude Sonnet 4.5
**專案**: 台股資料收集與分析系統

---

## 📋 目錄

1. [功能概述](#功能概述)
2. [需求分析](#需求分析)
3. [架構設計](#架構設計)
4. [資料流程](#資料流程)
5. [API 策略](#api-策略)
6. [資料結構](#資料結構)
7. [驗證機制](#驗證機制)
8. [儲存策略](#儲存策略)
9. [資料庫設計](#資料庫設計)
10. [任務分解](#任務分解)
11. [風險評估](#風險評估)
12. [測試策略](#測試策略)

---

## 功能概述

### 目標

新增**月營收資料收集功能**，整合進現有的資料收集系統，支援：
- 自動收集所有上市櫃公司的月營收資料
- 支援即時收集（公司公告後立即可查）
- 支援歷史資料回補
- 整合進現有的 data-pipeline workflow

### 核心價值

1. **基本面分析基礎**：月營收是評估公司營運狀況的重要指標
2. **即時性**：相比其他財報資料（季報、年報），月營收更新最頻繁
3. **預警功能**：營收大幅變動可能預示股價波動
4. **完整性**：補足現有系統（價格、籌碼）缺少的財務面資料

### 與現有系統的整合

- 遵循現有的 Collector 架構模式
- 使用相同的儲存策略（JSON + PostgreSQL）
- 整合進 data-pipeline skill
- 支援相同的 CLI 執行方式

---

## 需求分析

### 功能性需求

#### FR1: 資料收集
- **FR1.1**: 支援收集所有上市公司月營收（TWSE）
- **FR1.2**: 支援收集所有上櫃公司月營收（TPEx）
- **FR1.3**: 支援指定單一公司查詢
- **FR1.4**: 支援指定年月查詢（歷史資料回補）
- **FR1.5**: 自動處理民國年/西元年轉換

#### FR2: 資料處理
- **FR2.1**: 資料清洗與格式化（移除逗號、轉換數值型別）
- **FR2.2**: 計算衍生欄位（月增率、年增率、累計營收等）
- **FR2.3**: 合併上市上櫃資料
- **FR2.4**: 處理特殊狀況（未公告、查無資料等）

#### FR3: 資料儲存
- **FR3.1**: 儲存為 JSON 檔案（與現有資料類型一致）
- **FR3.2**: 匯入到 PostgreSQL 資料庫
- **FR3.3**: 支援資料更新（覆蓋舊資料）
- **FR3.4**: 保留歷史版本（Git 版本控制）

#### FR4: 資料驗證
- **FR4.1**: 驗證必要欄位完整性
- **FR4.2**: 驗證數值合理性（營收不可為負數等）
- **FR4.3**: 驗證增減率計算正確性
- **FR4.4**: 偵測異常資料（營收暴增暴跌超過閾值）

### 非功能性需求

#### NFR1: 效能
- **NFR1.1**: 收集所有公司（~2,000 檔）月營收應在 **10 分鐘內**完成
- **NFR1.2**: 單一公司查詢應在 **3 秒內**完成
- **NFR1.3**: API 請求應有適當間隔（避免被封鎖）

#### NFR2: 可靠性
- **NFR2.1**: API 請求失敗應有重試機制（最多 3 次）
- **NFR2.2**: 部分失敗不應影響整體收集流程
- **NFR2.3**: 所有錯誤應有完整日誌記錄

#### NFR3: 可維護性
- **NFR3.1**: 程式碼遵循現有專案規範（BaseCollector 模式）
- **NFR3.2**: 完整的文檔與註解（繁體中文）
- **NFR3.3**: 模組化設計，易於測試與擴展

#### NFR4: 相容性
- **NFR4.1**: 與現有 data-pipeline 相容
- **NFR4.2**: 支援現有的執行腳本模式
- **NFR4.3**: 資料格式與現有資料類型一致

---

## 架構設計

### 系統架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                    月營收收集系統架構                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  執行層 (CLI)    │
│ ─────────────── │
│ • run_collection│  ← 整合進現有腳本
│ • backfill      │
│ • data-pipeline │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────┐
│              收集器層 (Collector Layer)                       │
│ ─────────────────────────────────────────────────────────── │
│  MonthlyRevenueCollector (繼承 BaseCollector)                │
│  • collect(date, year, month, stock_id)                     │
│  • get_data_type() → "revenue"                              │
│  • validate_and_save()                                      │
└────────┬────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────┐
│              資料源層 (DataSource Layer)                      │
│ ─────────────────────────────────────────────────────────── │
│  ┌──────────────────────┐    ┌──────────────────────┐      │
│  │ MOPSDataSource       │    │ OpenAPIDataSource    │      │
│  │ ───────────────────  │    │ ───────────────────  │      │
│  │ • POST API (即時)     │    │ • GET API (彙總)     │      │
│  │ • 單一公司查詢        │    │ • 批次下載           │      │
│  │ • 支援歷史年月        │    │ • 僅最新一期         │      │
│  └──────────────────────┘    └──────────────────────┘      │
└────────┬────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────┐
│               資料處理層 (Processing Layer)                   │
│ ─────────────────────────────────────────────────────────── │
│  • DataMerger: 合併上市上櫃資料                              │
│  • DataValidator: 驗證資料完整性與合理性                      │
│  • DataTransformer: 格式轉換與欄位對應                       │
└────────┬────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────┐
│               儲存層 (Storage Layer)                          │
│ ─────────────────────────────────────────────────────────── │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   JSON 檔案       │         │   PostgreSQL     │         │
│  │ ────────────────  │         │ ────────────────  │         │
│  │ data/raw/revenue/ │  ─────→ │ monthly_revenues │         │
│  │ YYYY/MM/*.json    │  匯入   │ (資料表)          │         │
│  └──────────────────┘         └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 模組設計

#### 1. MonthlyRevenueCollector（收集器）

**位置**: `services/common/collectors/revenue_collector.py`

**職責**:
- 繼承 `BaseCollector`
- 協調兩種資料源（MOPS 和 OpenAPI）
- 實作收集、驗證、儲存流程
- 提供統一的收集介面

**關鍵方法**:
```
- collect(date, year, month, stock_id) → DataFrame
  根據參數選擇適當的收集策略

- get_data_type() → str
  返回 "revenue"

- _collect_batch_mode(year, month) → DataFrame
  批次模式：使用 OpenAPI 一次取得所有公司

- _collect_single_mode(stock_id, year, month) → DataFrame
  單一模式：使用 MOPS API 查詢特定公司

- _should_use_mops(year, month) → bool
  判斷是否應使用 MOPS API（當前月份或未來月份）
```

#### 2. MOPSDataSource（MOPS 資料源）

**位置**: `services/common/datasources/mops_datasource.py`

**職責**:
- 封裝 MOPS POST API
- 處理民國年/西元年轉換
- 解析 MOPS API 的特殊 JSON 格式
- 錯誤處理與重試

**關鍵方法**:
```
- get_monthly_revenue(stock_id, year, month) → DataFrame
  查詢單一公司月營收

- _convert_to_roc_year(western_year) → int
  西元年轉民國年

- _parse_mops_response(response) → dict
  解析 MOPS API 回應格式

- _build_request_payload(stock_id, year, month) → dict
  建立 POST 請求的 payload
```

#### 3. MonthlyRevenueOpenAPISource（OpenAPI 資料源）

**位置**: `services/common/datasources/revenue_openapi_datasource.py`

**職責**:
- 封裝 OpenAPI GET 端點
- 批次取得所有公司資料
- 資料格式標準化

**關鍵方法**:
```
- get_all_revenues() → DataFrame
  取得最新一期所有公司月營收

- _parse_openapi_response(response) → DataFrame
  解析並標準化 OpenAPI 回應
```

#### 4. RevenueValidator（驗證器）

**位置**: `services/common/validators/revenue_validator.py`

**職責**:
- 繼承 `BaseValidator`
- 實作月營收特定的驗證規則
- 偵測異常營收變動

**驗證規則**:
```
必要欄位檢查:
- stock_id, stock_name, revenue_year, revenue_month
- current_month_revenue (當月營收)
- mom_change_pct (月增率)
- yoy_change_pct (年增率)

數值合理性檢查:
- 營收 >= 0
- -100% <= 月增率 <= 1000%
- -100% <= 年增率 <= 1000%

異常偵測:
- 營收變動超過 ±200% 發出警告
- 連續多月營收為 0 發出警告
```

#### 5. RevenueImporter（匯入器）

**位置**: `services/data-importer/app/importers/revenue_importer.py`

**職責**:
- 繼承 `BaseImporter`
- 讀取 JSON 檔案
- 匯入到 PostgreSQL
- 處理資料衝突（UPSERT）

---

## 資料流程

### 主要流程圖

```
開始
  │
  ↓
[判斷收集模式]
  │
  ├─→ 批次模式（收集當月所有公司）
  │   │
  │   ↓
  │   [檢查 OpenAPI 是否已更新]
  │   │
  │   ├─→ 是 → [使用 OpenAPI] → 一次取得所有公司
  │   │
  │   └─→ 否 → [使用 MOPS API] → 逐一查詢所有公司
  │                                  │
  │                                  ↓
  │                            [加入延遲避免被封鎖]
  │                                  │
  │   ↓                              │
  │   [合併資料] ←──────────────────┘
  │   │
  │   ↓
  │   [資料驗證]
  │   │
  │   ↓
  │   [儲存 JSON]
  │   │
  │   ↓
  │   [記錄日誌]
  │
  └─→ 單一模式（查詢特定公司）
      │
      ↓
      [使用 MOPS API 查詢]
      │
      ↓
      [資料驗證]
      │
      ↓
      [儲存 JSON]
      │
      ↓
      [記錄日誌]
  │
  ↓
結束
```

### 收集策略決策樹

```
                    [收集月營收]
                         │
                         ↓
              ┌──────────────────────┐
              │ 有指定 stock_id？     │
              └──────────┬───────────┘
                    是 ↙    ↘ 否
                      ↓        ↓
              [單一模式]    [批次模式]
                  │              │
                  ↓              ↓
            [MOPS API]   ┌─────────────────┐
             (即時)      │ 當月資料？         │
                         └──────┬──────────┘
                           是 ↙    ↘ 否
                             ↓        ↓
                    ┌────────────┐  [OpenAPI]
                    │ 超過 10 號？│   (歷史)
                    └─────┬──────┘
                     是 ↙   ↘ 否
                       ↓       ↓
                 [OpenAPI] [MOPS API]
                  (已彙整)  (逐一查詢)
```

### 時間序列處理邏輯

```
月營收公告時間軸:
────────────────────────────────────────────────────────

1/1-1/31          2/1-2/10              2/11 後
────────          ───────────           ─────────
1月營業活動      公司統計並公告         證交所彙整完成
                 (MOPS 即時更新)        (OpenAPI 更新)

系統收集策略:
────────────────────────────────────────────────────────

2/1-2/10: 使用 MOPS API 逐一查詢（慢但即時）
         ↓ 約 10-15 分鐘收集完成

2/11 後:  使用 OpenAPI 批次下載（快速且穩定）
         ↓ 約 1-2 秒收集完成
```

---

## API 策略

### 雙 API 策略比較

| 項目 | MOPS API | OpenAPI |
|------|----------|---------|
| **端點** | `POST mops.twse.com.tw/mops/api/t05st10_ifrs` | `GET openapi.twse.com.tw/v1/opendata/t187ap05_L` |
| **即時性** | ⭐⭐⭐⭐⭐ 即時（公司公告後立即可查） | ⭐⭐⭐ 延遲 1-2 天 |
| **查詢範圍** | 單一公司、指定年月 | 所有公司、最新一期 |
| **請求次數** | 1 請求/公司（~2,000 次） | 1 請求（全部） |
| **耗時** | ⏰ 約 10-15 分鐘（2,000 檔 × 0.5 秒延遲） | ⚡ 約 2-3 秒 |
| **彈性** | ✅ 可查任意歷史月份 | ❌ 僅最新一期 |
| **穩定性** | ⚠️ 需控制請求頻率 | ✅ 穩定 |
| **適用場景** | 當月即時收集、歷史回補 | 每月 11 號後批次收集 |

### 使用策略

#### 策略 A: 自動切換（推薦）

```
IF 指定 stock_id:
    使用 MOPS API（單一查詢）

ELSE IF 當前日期 <= 每月 10 號:
    使用 MOPS API（逐一查詢所有公司）
    加入 0.5 秒延遲避免被封鎖
    預估耗時: 10-15 分鐘

ELSE:
    使用 OpenAPI（批次下載）
    預估耗時: 2-3 秒
```

#### 策略 B: 混合模式（高級用法）

```
1. 每月 11 號後，使用 OpenAPI 批次收集
2. 發現有公司未公告時，使用 MOPS API 補充
3. 需要特定公司最新資料時，使用 MOPS API 單查
```

### API 請求規範

#### MOPS API 請求範例

```http
POST https://mops.twse.com.tw/mops/api/t05st10_ifrs
Content-Type: application/json
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15) AppleWebKit/537.36

{
  "companyId": "2330",
  "dataType": "2",
  "month": "1",
  "year": "115",
  "subsidiaryCompanyId": ""
}
```

**回應格式**:
```json
{
  "code": 200,
  "message": "查詢成功",
  "result": {
    "yymm": "11501",
    "companyAbbreviation": "台積電",
    "marketKindName": "上市公司",
    "data": [
      ["本月", "335,003,568"],
      ["去年同期", "278,163,107"],
      ["增減百分比", "20.43"]
    ]
  }
}
```

#### OpenAPI 請求範例

```http
GET https://openapi.twse.com.tw/v1/opendata/t187ap05_L
```

**回應格式**:
```json
[
  {
    "出表日期": "1150117",
    "資料年月": "11412",
    "公司代號": "2330",
    "公司名稱": "台積電",
    "營業收入-當月營收": "335003568",
    "營業收入-上月營收": "343613802",
    "營業收入-上月比較增減(%)": "-2.51",
    "營業收入-去年同月增減(%)": "20.43",
    "累計營業收入-當月累計營收": "3809054272"
  }
]
```

### 錯誤處理策略

```
API 錯誤類型處理:

1. HTTP 404/406（查無資料）
   → 正常情況（公司尚未公告）
   → 記錄日誌，不算失敗

2. HTTP 500（伺服器錯誤）
   → 重試 3 次，每次間隔 5 秒
   → 仍失敗則記錄錯誤並跳過

3. 連線逾時
   → 重試 3 次，增加 timeout 參數
   → 仍失敗則記錄錯誤並跳過

4. JSON 解析錯誤
   → 記錄原始回應內容
   → 標記為失敗，人工檢查

5. 被封鎖（429 Too Many Requests）
   → 立即停止收集
   → 等待 60 秒後重試
   → 建議增加請求間隔
```

---

## 資料結構

### JSON 檔案格式

**檔案路徑**: `data/raw/revenue/YYYY/MM/YYYY-MM.json`

**說明**:
- 月營收以「年月」為單位，不像其他資料以「日期」為單位
- 一個月份一個檔案，包含所有公司資料
- 檔案名稱格式: `YYYY-MM.json`（例如: `2026-01.json`）

**結構範例**:

```json
{
  "metadata": {
    "year": 2026,
    "month": 1,
    "revenue_year_month": "2026-01",
    "collected_at": "2026-02-06T19:15:20",
    "total_count": 1946,
    "twse_count": 1075,
    "tpex_count": 871,
    "source": "MOPS API + OpenAPI",
    "api_mode": "mops",
    "collection_duration_seconds": 865.3,
    "failed_count": 12,
    "notes": "部分公司尚未公告（已記錄於 failed_stocks）"
  },
  "data": [
    {
      "stock_id": "2330",
      "stock_name": "台積電",
      "market_type": "twse",
      "industry": "半導體業",

      "revenue_year": 2026,
      "revenue_month": 1,
      "revenue_year_month": "2026-01",

      "current_month_revenue": 335003568,
      "last_month_revenue": 343613802,
      "last_year_same_month_revenue": 278163107,

      "mom_change": -8610234,
      "mom_change_pct": -2.51,
      "yoy_change": 56840461,
      "yoy_change_pct": 20.43,

      "ytd_revenue": 3809054272,
      "ytd_revenue_last_year": 2894307699,
      "ytd_change_pct": 31.61,

      "note": "",
      "publish_date": "2026-02-10",
      "collected_at": "2026-02-10T18:30:15"
    }
  ],
  "failed_stocks": [
    {
      "stock_id": "1234",
      "stock_name": "某公司",
      "reason": "查無資料（尚未公告）",
      "error_code": 406,
      "attempted_at": "2026-02-06T18:25:10"
    }
  ]
}
```

### 欄位說明

#### Metadata 欄位

| 欄位名稱 | 型別 | 說明 | 範例 |
|---------|------|------|------|
| `year` | int | 西元年 | 2026 |
| `month` | int | 月份 | 1 |
| `revenue_year_month` | string | 年月字串 | "2026-01" |
| `collected_at` | string | 收集時間（ISO 8601） | "2026-02-06T19:15:20" |
| `total_count` | int | 總筆數 | 1946 |
| `twse_count` | int | 上市公司數 | 1075 |
| `tpex_count` | int | 上櫃公司數 | 871 |
| `source` | string | 資料來源 | "MOPS API" |
| `api_mode` | string | API 模式 | "mops" / "openapi" |
| `collection_duration_seconds` | float | 收集耗時（秒） | 865.3 |
| `failed_count` | int | 失敗筆數 | 12 |

#### Data 欄位

| 欄位名稱 | 型別 | 說明 | 單位 | 範例 |
|---------|------|------|------|------|
| `stock_id` | string | 股票代碼 | - | "2330" |
| `stock_name` | string | 股票名稱 | - | "台積電" |
| `market_type` | string | 市場類型 | - | "twse" / "tpex" |
| `industry` | string | 產業別 | - | "半導體業" |
| `revenue_year` | int | 營收年度 | 西元年 | 2026 |
| `revenue_month` | int | 營收月份 | 1-12 | 1 |
| `revenue_year_month` | string | 年月字串 | YYYY-MM | "2026-01" |
| `current_month_revenue` | int | 當月營收 | 千元 | 335003568 |
| `last_month_revenue` | int | 上月營收 | 千元 | 343613802 |
| `last_year_same_month_revenue` | int | 去年同月營收 | 千元 | 278163107 |
| `mom_change` | int | 月增金額 | 千元 | -8610234 |
| `mom_change_pct` | float | 月增率 | % | -2.51 |
| `yoy_change` | int | 年增金額 | 千元 | 56840461 |
| `yoy_change_pct` | float | 年增率 | % | 20.43 |
| `ytd_revenue` | int | 累計營收 | 千元 | 3809054272 |
| `ytd_revenue_last_year` | int | 去年累計營收 | 千元 | 2894307699 |
| `ytd_change_pct` | float | 累計年增率 | % | 31.61 |
| `note` | string | 備註說明 | - | "主係因客戶需求增加" |
| `publish_date` | string | 公告日期 | YYYY-MM-DD | "2026-02-10" |
| `collected_at` | string | 收集時間 | ISO 8601 | "2026-02-10T18:30:15" |

### 欄位對應表

#### MOPS API → 標準格式

| MOPS 欄位 | 標準欄位 | 轉換規則 |
|-----------|---------|---------|
| `公司代號` | `stock_id` | 直接對應 |
| `公司名稱` / `companyAbbreviation` | `stock_name` | 直接對應 |
| `產業別` | `industry` | 直接對應 |
| `data[0][1]` (本月) | `current_month_revenue` | 移除逗號，轉 int |
| `data[1][1]` (去年同期) | `last_year_same_month_revenue` | 移除逗號，轉 int |
| `data[3][1]` (增減百分比) | `yoy_change_pct` | 轉 float |
| `data[4][1]` (本年累計) | `ytd_revenue` | 移除逗號，轉 int |
| `data[8][1]` (備註) | `note` | 直接對應 |
| `yymm` | `revenue_year_month` | 轉換民國年為西元年 |

#### OpenAPI → 標準格式

| OpenAPI 欄位 | 標準欄位 | 轉換規則 |
|-------------|---------|---------|
| `公司代號` | `stock_id` | 直接對應 |
| `公司名稱` | `stock_name` | 直接對應 |
| `產業別` | `industry` | 直接對應 |
| `營業收入-當月營收` | `current_month_revenue` | 轉 int |
| `營業收入-上月營收` | `last_month_revenue` | 轉 int |
| `營業收入-去年當月營收` | `last_year_same_month_revenue` | 轉 int |
| `營業收入-上月比較增減(%)` | `mom_change_pct` | 轉 float |
| `營業收入-去年同月增減(%)` | `yoy_change_pct` | 轉 float |
| `累計營業收入-當月累計營收` | `ytd_revenue` | 轉 int |
| `累計營業收入-去年累計營收` | `ytd_revenue_last_year` | 轉 int |
| `備註` | `note` | 直接對應 |
| `資料年月` | `revenue_year_month` | 轉換民國年為西元年 |

---

## 驗證機制

### 三層驗證架構

```
┌─────────────────────────────────────────┐
│         第一層：結構驗證                  │
│  ─────────────────────────────────────  │
│  • JSON 格式正確                         │
│  • 必要欄位存在                          │
│  • 欄位型別正確                          │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│         第二層：數值驗證                  │
│  ─────────────────────────────────────  │
│  • 營收 >= 0                            │
│  • 增減率在合理範圍                      │
│  • 日期邏輯正確                          │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│         第三層：業務邏輯驗證               │
│  ─────────────────────────────────────  │
│  • 偵測異常波動                          │
│  • 交叉驗證計算結果                      │
│  • 歷史資料一致性                        │
└─────────────────────────────────────────┘
```

### 驗證規則詳細定義

#### 1. 結構驗證（Structure Validation）

**必要欄位清單**:
```yaml
必要欄位:
  - stock_id
  - stock_name
  - revenue_year
  - revenue_month
  - current_month_revenue
  - yoy_change_pct

可選欄位:
  - last_month_revenue
  - mom_change_pct
  - ytd_revenue
  - note
```

**型別檢查**:
```yaml
string 型別:
  - stock_id (長度 4-6)
  - stock_name (非空)
  - market_type (twse/tpex)
  - revenue_year_month (YYYY-MM 格式)

int 型別:
  - revenue_year (2000-2100)
  - revenue_month (1-12)
  - current_month_revenue (>= 0)
  - last_month_revenue (>= 0)
  - ytd_revenue (>= 0)

float 型別:
  - mom_change_pct (-100.0 ~ 999999.99)
  - yoy_change_pct (-100.0 ~ 999999.99)
```

#### 2. 數值驗證（Value Validation）

**範圍檢查**:
```yaml
營收檢查:
  - current_month_revenue >= 0
  - 如果 < 1000: 發出警告（可能單位錯誤）
  - 如果 > 10000000000: 發出警告（異常巨額）

增減率檢查:
  - -100% <= mom_change_pct <= 1000%
  - -100% <= yoy_change_pct <= 1000%
  - 如果 >= 999999.99: 視為無效值（分母為零）

日期檢查:
  - revenue_year: 2000 <= year <= 當前年度 + 1
  - revenue_month: 1 <= month <= 12
  - 組合合理性: 不能是未來月份（超過當前月份 1 個月以上）
```

**邏輯一致性檢查**:
```yaml
計算驗證:
  - mom_change = current_month_revenue - last_month_revenue
  - 驗證 mom_change_pct 計算正確（容許 0.1% 誤差）

  - yoy_change = current_month_revenue - last_year_same_month_revenue
  - 驗證 yoy_change_pct 計算正確（容許 0.1% 誤差）

  - ytd_change_pct = (ytd_revenue - ytd_revenue_last_year) / ytd_revenue_last_year * 100
  - 驗證計算正確（容許 0.1% 誤差）
```

#### 3. 業務邏輯驗證（Business Validation）

**異常偵測規則**:

```yaml
高風險警告（Critical）:
  - 營收年增率 >= 200% 或 <= -80%
    → 可能原因: 重大業務變動、合併、資料錯誤
    → 動作: 記錄警告、標記需人工複查

  - 連續 3 個月營收為 0
    → 可能原因: 停業、資料遺失
    → 動作: 記錄警告、標記需人工複查

  - 單月營收 > 累計營收 (對於非 1 月資料)
    → 明確錯誤
    → 動作: 拒絕儲存

中風險警告（Warning）:
  - 營收年增率 >= 100% 或 <= -50%
    → 記錄警告

  - 營收月增率 >= 50% 或 <= -50%
    → 記錄警告

  - 累計年增率與當月年增率差異 > 30%
    → 可能: 季節性因素、前期基期低
    → 記錄提示
```

**歷史資料一致性**:
```yaml
如果資料庫中有前期資料:
  - 驗證本月資料的 last_month_revenue 是否等於上月的 current_month_revenue
    容許誤差: 0（必須完全一致，除非有更正公告）

  - 驗證累計營收的連續性
    ytd_revenue(本月) 應 >= ytd_revenue(上月)
```

### 驗證失敗處理策略

```
┌─────────────────────────────────────────┐
│           驗證失敗處理流程                │
└─────────────────────────────────────────┘

結構驗證失敗:
  → 記錄錯誤日誌
  → 拒絕儲存該筆資料
  → 繼續處理其他資料

數值驗證失敗:
  → 記錄警告日誌
  → 根據配置決定:
    • strict 模式: 拒絕儲存
    • lenient 模式: 標記異常並儲存
  → 繼續處理其他資料

業務邏輯驗證失敗:
  → 記錄警告日誌
  → 標記為需人工複查
  → 仍然儲存資料（保留原始資料）
  → 繼續處理其他資料
```

### 驗證報告範例

```json
{
  "validation_summary": {
    "total_records": 1946,
    "passed": 1920,
    "failed": 14,
    "warnings": 12,
    "validation_time": "2026-02-06T19:20:15"
  },
  "failures": [
    {
      "stock_id": "1234",
      "stock_name": "某公司",
      "error_type": "MISSING_REQUIRED_FIELD",
      "error_message": "缺少必要欄位: current_month_revenue",
      "severity": "ERROR"
    }
  ],
  "warnings": [
    {
      "stock_id": "3167",
      "stock_name": "大量",
      "warning_type": "ABNORMAL_YOY_CHANGE",
      "warning_message": "年增率異常: 119.57% (超過 100%)",
      "severity": "WARNING",
      "value": 119.57,
      "threshold": 100.0
    }
  ]
}
```

---

## 儲存策略

### 雙層儲存架構

```
┌─────────────────────────────────────────┐
│              收集器輸出                   │
│         (DataFrame / Dict)               │
└────────────────┬────────────────────────┘
                 │
                 ↓
    ┌────────────────────────────┐
    │       第一層儲存              │
    │    JSON 檔案 (版本控制)      │
    │  ─────────────────────────  │
    │  • Git 追蹤所有變更          │
    │  • 人類可讀格式              │
    │  • 完整 metadata             │
    └────────┬───────────────────┘
             │
             ↓
    ┌────────────────────────────┐
    │       第二層儲存              │
    │    PostgreSQL (結構化)       │
    │  ─────────────────────────  │
    │  • 快速查詢                  │
    │  • 關聯分析                  │
    │  • 資料完整性約束            │
    └────────────────────────────┘
```

### JSON 檔案儲存策略

**目錄結構**:
```
data/raw/revenue/
├── 2024/
│   ├── 01/
│   │   └── 2024-01.json
│   ├── 02/
│   │   └── 2024-02.json
│   └── .../
├── 2025/
│   └── .../
└── 2026/
    ├── 01/
    │   └── 2026-01.json  ← 一個月份一個檔案
    └── 02/
        └── 2026-02.json
```

**檔案命名規範**:
- 格式: `YYYY-MM.json`
- 範例: `2026-01.json`（2026 年 1 月營收）
- 不包含日期（因為月營收是以月為單位）

**檔案合併策略**:
```
情況 1: 檔案不存在
  → 直接建立新檔案

情況 2: 檔案已存在（更新資料）
  → 讀取現有檔案
  → 合併新舊資料（以 stock_id 為 key）
  → 更新 metadata (collected_at, total_count 等)
  → 覆寫檔案

情況 3: 同一公司有多筆資料（異常）
  → 保留最新的一筆（以 collected_at 判斷）
  → 記錄警告日誌
```

**Git 版本控制**:
```
提交訊息格式:
  data(revenue): 收集 YYYY-MM 月營收資料

  - 總計: XXX 檔公司
  - 上市: XXX 檔
  - 上櫃: XXX 檔
  - 資料來源: MOPS API / OpenAPI

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### 檔案大小預估

```
單筆資料大小:
  - 平均每筆約 500 bytes（含欄位名稱與值）

單月檔案大小:
  - 2,000 檔公司 × 500 bytes = 1 MB
  - 加上 metadata 和格式化 ≈ 1.2 MB

年度儲存空間:
  - 12 個月 × 1.2 MB = 14.4 MB / 年

十年儲存空間:
  - 10 年 × 14.4 MB = 144 MB

結論: 儲存空間需求低，Git 可輕鬆管理
```

---

## 資料庫設計

### 資料表 Schema

**表名**: `monthly_revenues`

**欄位定義**:

```sql
CREATE TABLE monthly_revenues (
    -- 主鍵
    id SERIAL PRIMARY KEY,

    -- 基本資訊
    stock_id VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100) NOT NULL,
    market_type VARCHAR(10) NOT NULL,  -- 'twse' or 'tpex'
    industry VARCHAR(100),

    -- 營收期間
    revenue_year INTEGER NOT NULL,
    revenue_month INTEGER NOT NULL,
    revenue_year_month VARCHAR(7) NOT NULL,  -- 'YYYY-MM'

    -- 營收金額（千元）
    current_month_revenue BIGINT NOT NULL,
    last_month_revenue BIGINT,
    last_year_same_month_revenue BIGINT,

    -- 變動金額（千元）
    mom_change BIGINT,
    yoy_change BIGINT,

    -- 變動率（%）
    mom_change_pct DECIMAL(10, 2),
    yoy_change_pct DECIMAL(10, 2),

    -- 累計營收（千元）
    ytd_revenue BIGINT,
    ytd_revenue_last_year BIGINT,
    ytd_change_pct DECIMAL(10, 2),

    -- 其他資訊
    note TEXT,
    publish_date DATE,

    -- 系統欄位
    collected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 唯一約束
    UNIQUE(stock_id, revenue_year, revenue_month)
);
```

### 索引設計

```sql
-- 主要查詢索引
CREATE INDEX idx_revenue_stock_year_month
    ON monthly_revenues(stock_id, revenue_year DESC, revenue_month DESC);

-- 時間範圍查詢索引
CREATE INDEX idx_revenue_year_month
    ON monthly_revenues(revenue_year DESC, revenue_month DESC);

-- 產業分析索引
CREATE INDEX idx_revenue_industry_year_month
    ON monthly_revenues(industry, revenue_year DESC, revenue_month DESC);

-- 市場類型索引
CREATE INDEX idx_revenue_market_type
    ON monthly_revenues(market_type, revenue_year DESC, revenue_month DESC);

-- 異常偵測索引（年增率）
CREATE INDEX idx_revenue_yoy_change_pct
    ON monthly_revenues(yoy_change_pct DESC)
    WHERE yoy_change_pct IS NOT NULL;
```

### 資料匯入策略

**UPSERT 邏輯**:
```sql
INSERT INTO monthly_revenues (
    stock_id, stock_name, market_type, industry,
    revenue_year, revenue_month, revenue_year_month,
    current_month_revenue, last_month_revenue,
    last_year_same_month_revenue,
    mom_change, yoy_change,
    mom_change_pct, yoy_change_pct,
    ytd_revenue, ytd_revenue_last_year, ytd_change_pct,
    note, publish_date, collected_at
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT (stock_id, revenue_year, revenue_month)
DO UPDATE SET
    stock_name = EXCLUDED.stock_name,
    current_month_revenue = EXCLUDED.current_month_revenue,
    last_month_revenue = EXCLUDED.last_month_revenue,
    mom_change_pct = EXCLUDED.mom_change_pct,
    yoy_change_pct = EXCLUDED.yoy_change_pct,
    ytd_revenue = EXCLUDED.ytd_revenue,
    note = EXCLUDED.note,
    updated_at = CURRENT_TIMESTAMP;
```

**批次匯入優化**:
```
使用 COPY 命令加速:
  1. 將 DataFrame 轉為 CSV
  2. 使用 PostgreSQL COPY FROM 匯入
  3. 速度提升約 10-50 倍（vs 逐筆 INSERT）

預估效能:
  - 2,000 筆資料
  - COPY 方式: < 1 秒
  - INSERT 方式: 5-10 秒
```

### 資料完整性約束

```sql
-- 檢查約束
ALTER TABLE monthly_revenues ADD CONSTRAINT chk_revenue_positive
    CHECK (current_month_revenue >= 0);

ALTER TABLE monthly_revenues ADD CONSTRAINT chk_revenue_year_valid
    CHECK (revenue_year >= 2000 AND revenue_year <= 2100);

ALTER TABLE monthly_revenues ADD CONSTRAINT chk_revenue_month_valid
    CHECK (revenue_month >= 1 AND revenue_month <= 12);

ALTER TABLE monthly_revenues ADD CONSTRAINT chk_market_type_valid
    CHECK (market_type IN ('twse', 'tpex'));

-- 外鍵約束（如果有 stocks 主表的話）
-- ALTER TABLE monthly_revenues ADD CONSTRAINT fk_stock_id
--     FOREIGN KEY (stock_id) REFERENCES stocks(stock_id);
```

### 常用查詢範例

```sql
-- 1. 查詢特定公司的月營收歷史
SELECT
    revenue_year_month,
    current_month_revenue,
    yoy_change_pct
FROM monthly_revenues
WHERE stock_id = '2330'
ORDER BY revenue_year DESC, revenue_month DESC
LIMIT 12;

-- 2. 查詢當月營收年增率最高的前 20 名
SELECT
    stock_id,
    stock_name,
    current_month_revenue,
    yoy_change_pct
FROM monthly_revenues
WHERE revenue_year = 2026 AND revenue_month = 1
    AND yoy_change_pct IS NOT NULL
ORDER BY yoy_change_pct DESC
LIMIT 20;

-- 3. 產業營收統計
SELECT
    industry,
    COUNT(*) as company_count,
    SUM(current_month_revenue) as total_revenue,
    AVG(yoy_change_pct) as avg_yoy_change_pct
FROM monthly_revenues
WHERE revenue_year = 2026 AND revenue_month = 1
GROUP BY industry
ORDER BY total_revenue DESC;

-- 4. 偵測連續三個月營收衰退的公司
WITH monthly_changes AS (
    SELECT
        stock_id,
        revenue_year,
        revenue_month,
        yoy_change_pct,
        LAG(yoy_change_pct, 1) OVER (
            PARTITION BY stock_id
            ORDER BY revenue_year, revenue_month
        ) as prev_1_month_yoy,
        LAG(yoy_change_pct, 2) OVER (
            PARTITION BY stock_id
            ORDER BY revenue_year, revenue_month
        ) as prev_2_month_yoy
    FROM monthly_revenues
)
SELECT DISTINCT stock_id
FROM monthly_changes
WHERE yoy_change_pct < 0
    AND prev_1_month_yoy < 0
    AND prev_2_month_yoy < 0;
```

---

## 任務分解

### Phase 1: 基礎建設（預估 2-3 天）

#### Task 1.1: 建立資料源模組
**負責模組**: `MOPSDataSource`
**檔案**: `services/common/datasources/mops_datasource.py`

**子任務**:
- [ ] 建立 `MOPSDataSource` 類別骨架
- [ ] 實作 POST API 請求方法
- [ ] 實作民國年/西元年轉換函式
- [ ] 實作 MOPS API 回應解析器
- [ ] 加入重試機制（最多 3 次）
- [ ] 加入請求延遲控制（0.5 秒）
- [ ] 撰寫單元測試
- [ ] 撰寫 docstring（繁體中文）

**驗收標準**:
- 能成功查詢單一公司月營收
- 能正確處理「查無資料」情況
- 能正確轉換民國年/西元年
- 所有測試通過

**預估時間**: 6-8 小時

---

#### Task 1.2: 擴展 OpenAPI 資料源
**負責模組**: `MonthlyRevenueOpenAPISource`
**檔案**: `services/common/datasources/revenue_openapi_datasource.py`

**子任務**:
- [ ] 建立 `MonthlyRevenueOpenAPISource` 類別
- [ ] 實作 GET API 請求方法
- [ ] 實作 OpenAPI 回應解析器
- [ ] 實作資料格式標準化
- [ ] 撰寫單元測試
- [ ] 撰寫 docstring

**驗收標準**:
- 能成功取得所有公司月營收
- 資料格式與 MOPS API 一致
- 所有測試通過

**預估時間**: 4-6 小時

---

#### Task 1.3: 建立驗證器
**負責模組**: `RevenueValidator`
**檔案**: `services/common/validators/revenue_validator.py`

**子任務**:
- [ ] 繼承 `BaseValidator`
- [ ] 實作結構驗證規則
- [ ] 實作數值驗證規則
- [ ] 實作業務邏輯驗證規則
- [ ] 實作異常偵測規則
- [ ] 建立驗證報告生成器
- [ ] 撰寫驗證規則測試案例
- [ ] 撰寫 docstring

**驗收標準**:
- 能偵測所有定義的驗證規則
- 能生成完整的驗證報告
- 測試覆蓋率 > 90%

**預估時間**: 6-8 小時

---

### Phase 2: 收集器實作（預估 2-3 天）

#### Task 2.1: 建立月營收收集器
**負責模組**: `MonthlyRevenueCollector`
**檔案**: `services/common/collectors/revenue_collector.py`

**子任務**:
- [ ] 繼承 `BaseCollector`
- [ ] 實作 `get_data_type()` 返回 "revenue"
- [ ] 實作 `collect()` 方法（核心邏輯）
- [ ] 實作 API 選擇策略（MOPS vs OpenAPI）
- [ ] 實作批次收集模式（所有公司）
- [ ] 實作單一收集模式（指定公司）
- [ ] 整合驗證器
- [ ] 整合檔案儲存
- [ ] 加入進度顯示（進度條）
- [ ] 撰寫 docstring

**驗收標準**:
- 能自動選擇適當的 API
- 批次收集所有公司 < 15 分鐘
- 單一公司查詢 < 3 秒
- 資料通過驗證
- 成功儲存為 JSON

**預估時間**: 8-10 小時

---

#### Task 2.2: 整合資料合併器
**負責模組**: `DataMerger`（擴展現有）
**檔案**: `services/common/utils/data_merger.py`

**子任務**:
- [ ] 擴展 `DataMerger` 支援月營收資料
- [ ] 實作上市上櫃資料合併邏輯
- [ ] 處理重複資料（以最新為準）
- [ ] 撰寫測試案例

**驗收標準**:
- 能正確合併 TWSE 和 TPEx 資料
- 能處理重複股票代碼
- 測試通過

**預估時間**: 3-4 小時

---

### Phase 3: 儲存與匯入（預估 2 天）

#### Task 3.1: 設計 JSON 檔案格式
**負責**: 文檔與配置

**子任務**:
- [ ] 定義完整的 JSON Schema
- [ ] 建立範例檔案
- [ ] 更新 `.gitignore`（如需要）
- [ ] 撰寫格式說明文檔

**驗收標準**:
- JSON Schema 完整定義
- 有至少 3 個範例檔案
- 文檔清晰易懂

**預估時間**: 2-3 小時

---

#### Task 3.2: 實作 JSON 儲存邏輯
**負責模組**: `FileHandler`（擴展現有）
**檔案**: `services/common/utils/file_handler.py`

**子任務**:
- [ ] 擴展 `FileHandler` 支援月營收檔案路徑
- [ ] 實作檔案合併邏輯（同月份更新）
- [ ] 實作備份機制
- [ ] 撰寫測試案例

**驗收標準**:
- 能正確建立目錄結構
- 能正確合併更新資料
- 備份機制運作正常

**預估時間**: 4-5 小時

---

#### Task 3.3: 建立資料庫 Schema
**負責**: 資料庫遷移

**子任務**:
- [ ] 撰寫 CREATE TABLE SQL
- [ ] 建立所有必要索引
- [ ] 建立約束條件
- [ ] 撰寫資料庫遷移腳本
- [ ] 測試 Schema 建立

**驗收標準**:
- Schema 符合設計規範
- 所有索引建立成功
- 約束條件正確運作

**預估時間**: 3-4 小時

---

#### Task 3.4: 實作資料匯入器
**負責模組**: `RevenueImporter`
**檔案**: `services/data-importer/app/importers/revenue_importer.py`

**子任務**:
- [ ] 繼承 `BaseImporter`
- [ ] 實作 JSON 讀取邏輯
- [ ] 實作 UPSERT 邏輯
- [ ] 實作批次匯入優化（COPY）
- [ ] 加入錯誤處理
- [ ] 撰寫測試案例
- [ ] 撰寫 docstring

**驗收標準**:
- 能正確讀取 JSON 檔案
- UPSERT 邏輯正確（不重複插入）
- 2,000 筆資料匯入 < 5 秒
- 測試通過

**預估時間**: 6-8 小時

---

### Phase 4: CLI 與整合（預估 1-2 天）

#### Task 4.1: 整合進 run_collection 腳本
**負責**: 執行腳本
**檔案**: `scripts/run_collection.py`

**子任務**:
- [ ] 新增 `revenue` 資料類型支援
- [ ] 整合 `MonthlyRevenueCollector`
- [ ] 加入命令列參數（--year, --month）
- [ ] 更新 `--help` 說明
- [ ] 測試各種參數組合

**驗收標準**:
- `python scripts/run_collection.py --types revenue` 成功執行
- `python scripts/run_collection.py --types revenue --year 2026 --month 1` 成功執行
- 錯誤處理完善

**預估時間**: 3-4 小時

---

#### Task 4.2: 建立獨立執行腳本
**負責**: 新腳本
**檔案**: `scripts/data-collector/collect_revenue.sh`

**子任務**:
- [ ] 建立 Shell 腳本包裝器
- [ ] 加入參數解析
- [ ] 加入使用說明
- [ ] 測試各種執行情境

**腳本範例**:
```bash
#!/bin/bash
# 收集月營收資料

Usage:
  ./collect_revenue.sh [OPTIONS]

Options:
  --year YYYY          指定年度（預設：當前年度）
  --month MM           指定月份（預設：當前月份）
  --stock-id CODE      指定股票代碼（選用）
  --api-mode MODE      指定 API 模式: mops/openapi/auto（預設：auto）
  --help               顯示說明
```

**驗收標準**:
- 腳本能正確執行
- 參數解析正確
- 錯誤訊息清晰

**預估時間**: 2-3 小時

---

#### Task 4.3: 整合進 data-pipeline skill
**負責**: Skill 配置
**檔案**: `.claude/skills/data-pipeline/SKILL.md`

**子任務**:
- [ ] 更新 skill 說明加入月營收
- [ ] 修改 skill 執行流程包含 revenue
- [ ] 測試完整 pipeline（收集→匯入→轉換）
- [ ] 更新文檔

**驗收標準**:
- data-pipeline skill 包含月營收收集
- 完整流程測試通過
- 文檔更新完整

**預估時間**: 3-4 小時

---

### Phase 5: 文檔與測試（預估 1-2 天）

#### Task 5.1: 撰寫使用文檔
**負責**: 文檔
**檔案**: `docs/MONTHLY_REVENUE_USAGE.md`

**子任務**:
- [ ] 撰寫功能介紹
- [ ] 撰寫快速開始指南
- [ ] 撰寫完整使用範例
- [ ] 撰寫常見問題 FAQ
- [ ] 撰寫 API 參考
- [ ] 加入範例截圖/輸出

**驗收標準**:
- 文檔完整涵蓋所有功能
- 範例可執行且正確
- 繁體中文撰寫

**預估時間**: 4-6 小時

---

#### Task 5.2: 更新專案主文檔
**負責**: 文檔更新

**子任務**:
- [ ] 更新 `README.md` 加入月營收功能
- [ ] 更新 `CLAUDE.md` 加入架構說明
- [ ] 更新 `CHANGELOG.md` 記錄新功能
- [ ] 更新資料結構文檔

**驗收標準**:
- 所有相關文檔已更新
- 資訊一致且正確

**預估時間**: 2-3 小時

---

#### Task 5.3: 撰寫整合測試
**負責**: 測試
**檔案**: `tests/test_revenue_integration.py`

**子任務**:
- [ ] 建立端到端測試
- [ ] 測試完整收集流程
- [ ] 測試完整匯入流程
- [ ] 測試錯誤處理
- [ ] 測試邊界情況

**測試案例**:
```
測試案例清單:
1. 正常收集當月資料（所有公司）
2. 正常收集單一公司資料
3. 收集歷史資料（指定年月）
4. API 失敗重試機制
5. 驗證失敗處理
6. 檔案合併更新
7. 資料庫 UPSERT
8. 異常資料偵測
9. 非交易日處理
10. 未公告公司處理
```

**驗收標準**:
- 測試覆蓋率 > 80%
- 所有測試通過
- CI/CD 整合成功

**預估時間**: 6-8 小時

---

#### Task 5.4: 效能測試與優化
**負責**: 效能優化

**子任務**:
- [ ] 測試批次收集效能（2,000 檔）
- [ ] 測試資料庫匯入效能
- [ ] 識別效能瓶頸
- [ ] 實作優化（如需要）
- [ ] 撰寫效能測試報告

**效能目標**:
- 批次收集 2,000 檔 < 15 分鐘
- 資料庫匯入 2,000 筆 < 5 秒
- 單一公司查詢 < 3 秒

**驗收標準**:
- 達到效能目標
- 有效能測試報告
- 優化建議文檔

**預估時間**: 4-6 小時

---

### Phase 6: 部署與上線（預估 0.5-1 天）

#### Task 6.1: GitHub Actions 整合
**負責**: CI/CD
**檔案**: `.github/workflows/monthly-revenue-collection.yml`

**子任務**:
- [ ] 建立新的 workflow 檔案
- [ ] 設定排程（每月 11 號自動執行）
- [ ] 設定手動觸發選項
- [ ] 加入錯誤通知
- [ ] 測試 workflow

**Workflow 設計**:
```yaml
name: 月營收資料收集
on:
  schedule:
    # 每月 11 號 UTC 12:00 執行（台北時間 20:00）
    - cron: '0 12 11 * *'
  workflow_dispatch:
    inputs:
      year:
        description: '年度 (YYYY)'
        required: false
      month:
        description: '月份 (MM)'
        required: false
```

**驗收標準**:
- Workflow 建立成功
- 手動觸發測試成功
- 排程設定正確

**預估時間**: 3-4 小時

---

#### Task 6.2: 環境配置與部署
**負責**: 部署

**子任務**:
- [ ] 更新 `requirements.txt`（如有新套件）
- [ ] 更新環境變數設定
- [ ] 測試本地環境執行
- [ ] 測試 Docker 環境執行（如需要）
- [ ] 撰寫部署檢查清單

**驗收標準**:
- 所有環境正常運作
- 部署文檔完整

**預估時間**: 2-3 小時

---

### 任務總覽

| Phase | 任務數 | 預估時間 | 優先級 |
|-------|--------|---------|--------|
| Phase 1: 基礎建設 | 3 | 16-22 小時 | 🔴 高 |
| Phase 2: 收集器實作 | 2 | 11-14 小時 | 🔴 高 |
| Phase 3: 儲存與匯入 | 4 | 15-20 小時 | 🟡 中 |
| Phase 4: CLI 與整合 | 3 | 8-11 小時 | 🟡 中 |
| Phase 5: 文檔與測試 | 4 | 16-23 小時 | 🟢 中低 |
| Phase 6: 部署與上線 | 2 | 5-7 小時 | 🟢 低 |
| **總計** | **18** | **71-97 小時** | - |

**預估工作天數**: 9-12 天（以每天 8 小時計）

---

## 風險評估

### 技術風險

#### 風險 1: MOPS API 限流或封鎖
**機率**: 🟡 中
**影響**: 🔴 高

**說明**:
- 批次收集需要 2,000 次請求
- MOPS 可能有未公開的速率限制
- 可能觸發反爬蟲機制

**緩解策略**:
1. 加入請求延遲（0.5-1 秒）
2. 實作指數退避重試
3. 偵測到 429 錯誤時立即停止
4. 提供 OpenAPI 備用方案
5. 分批執行（例如每次 500 檔）

**應變計畫**:
- 如被封鎖，等待 24 小時後重試
- 改用 OpenAPI（等待資料更新）
- 聯絡 MOPS 了解正式 API 使用規範

---

#### 風險 2: API 回應格式變更
**機率**: 🟢 低
**影響**: 🟡 中

**說明**:
- MOPS API 為非官方文檔化 API
- 格式可能隨時變更

**緩解策略**:
1. 完整的單元測試
2. 加入 Schema 驗證
3. 詳細的錯誤日誌
4. 快速偵測機制（CI/CD）

**應變計畫**:
- 保留舊版解析器
- 快速適配新格式
- 回退到 OpenAPI

---

#### 風險 3: 資料一致性問題
**機率**: 🟡 中
**影響**: 🟡 中

**說明**:
- 公司可能更正前期營收
- 不同 API 資料可能不一致

**緩解策略**:
1. 三層驗證機制
2. 交叉驗證計算結果
3. 保留歷史版本（Git）
4. 標記異常資料

**應變計畫**:
- 定期重新收集歷史資料
- 人工複查異常案例
- 提供資料更正機制

---

### 業務風險

#### 風險 4: 收集時間過長
**機率**: 🟡 中
**影響**: 🟡 中

**說明**:
- MOPS API 模式需 10-15 分鐘
- 可能影響使用者體驗

**緩解策略**:
1. 優先使用 OpenAPI（每月 11 號後）
2. 提供進度顯示
3. 支援背景執行
4. 分批執行選項

**應變計畫**:
- 實作快取機制
- 僅收集有變動的公司
- 提供增量更新模式

---

#### 風險 5: 資料完整性不足
**機率**: 🟡 中
**影響**: 🟡 中

**說明**:
- 部分公司可能延遲公告
- 新上市公司無歷史資料

**緩解策略**:
1. 記錄未公告公司清單
2. 提供補充收集機制
3. 標記資料完整性狀態
4. 定期重新收集

**應變計畫**:
- 提供手動補充介面
- 設定公告延遲提醒
- 記錄資料缺口

---

### 合規風險

#### 風險 6: 資料使用合規性
**機率**: 🟢 低
**影響**: 🔴 高

**說明**:
- 大量爬取可能違反服務條款
- 商業使用可能有版權問題

**緩解策略**:
1. 僅用於個人研究
2. 合理的請求頻率
3. 標註資料來源
4. 不對外提供 API

**應變計畫**:
- 如收到警告立即停止
- 尋求官方授權
- 改用付費資料源

---

## 測試策略

### 測試金字塔

```
        ┌─────────────┐
        │  E2E 測試    │  ← 10% (整合流程測試)
        │   (少量)     │
        └─────────────┘
      ┌───────────────────┐
      │   整合測試          │  ← 30% (模組間互動)
      │   (適量)           │
      └───────────────────┘
  ┌───────────────────────────┐
  │      單元測試               │  ← 60% (個別函式)
  │      (大量)                │
  └───────────────────────────┘
```

### 測試範圍

#### 1. 單元測試（Unit Tests）

**MOPSDataSource 測試**:
```
測試案例:
- test_get_monthly_revenue_success()
  正常查詢成功情況

- test_get_monthly_revenue_not_found()
  公司未公告（406 錯誤）

- test_convert_roc_year()
  民國年轉換正確性

- test_parse_mops_response()
  解析 MOPS API 回應

- test_request_retry_on_failure()
  請求失敗重試機制

- test_invalid_stock_id()
  無效股票代碼處理
```

**RevenueValidator 測試**:
```
測試案例:
- test_validate_structure_success()
  結構驗證通過

- test_validate_missing_required_field()
  缺少必要欄位

- test_validate_negative_revenue()
  負數營收偵測

- test_validate_abnormal_yoy_change()
  異常年增率偵測

- test_validate_calculation_consistency()
  計算一致性驗證
```

**MonthlyRevenueCollector 測試**:
```
測試案例:
- test_collect_batch_mode()
  批次收集模式

- test_collect_single_mode()
  單一公司收集

- test_api_selection_strategy()
  API 選擇策略正確性

- test_data_merge()
  資料合併邏輯

- test_error_handling()
  錯誤處理機制
```

#### 2. 整合測試（Integration Tests）

**資料收集整合**:
```
測試案例:
- test_collect_and_save_flow()
  收集→驗證→儲存完整流程

- test_mops_and_openapi_integration()
  雙 API 整合測試

- test_database_import_flow()
  JSON→資料庫完整流程
```

**CLI 整合**:
```
測試案例:
- test_run_collection_revenue_type()
  執行腳本收集月營收

- test_backfill_historical_revenue()
  回補歷史資料

- test_data_pipeline_with_revenue()
  完整 pipeline 測試
```

#### 3. 端到端測試（E2E Tests）

```
測試案例:
- test_full_monthly_revenue_pipeline()
  完整流程：收集→驗證→儲存→匯入→查詢

- test_github_actions_workflow()
  GitHub Actions 自動化測試

- test_error_recovery()
  錯誤恢復測試
```

### 測試資料策略

**Mock 資料**:
```python
# 建立測試用的 MOPS API 回應
MOCK_MOPS_RESPONSE = {
    "code": 200,
    "result": {
        "data": [
            ["本月", "335,003,568"],
            ["去年同期", "278,163,107"],
            ...
        ]
    }
}

# 建立測試用的 DataFrame
TEST_REVENUE_DATA = pd.DataFrame([{
    "stock_id": "2330",
    "stock_name": "台積電",
    "current_month_revenue": 335003568,
    ...
}])
```

**測試資料庫**:
```
策略:
- 使用 SQLite 或獨立的 PostgreSQL 測試資料庫
- 每次測試前重建 Schema
- 測試後清理資料
- 不影響生產資料庫
```

### 效能測試

```
效能基準:
1. 批次收集 2,000 檔公司
   - 目標: < 15 分鐘
   - 測試: 實際執行並記錄時間

2. 資料庫匯入 2,000 筆
   - 目標: < 5 秒
   - 測試: 使用 pytest-benchmark

3. 單一公司查詢
   - 目標: < 3 秒
   - 測試: 平均 10 次查詢時間

4. 記憶體使用
   - 目標: < 500 MB
   - 測試: 使用 memory_profiler
```

### 測試執行

```bash
# 執行所有測試
pytest tests/

# 執行特定模組測試
pytest tests/test_mops_datasource.py

# 執行整合測試
pytest tests/integration/

# 執行效能測試
pytest tests/performance/ --benchmark-only

# 產生覆蓋率報告
pytest --cov=services/common/collectors --cov-report=html
```

### 持續整合

```yaml
# .github/workflows/test.yml
name: 測試
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: 設定 Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: 安裝相依套件
        run: pip install -r requirements.txt
      - name: 執行測試
        run: pytest tests/ --cov
      - name: 上傳覆蓋率報告
        uses: codecov/codecov-action@v2
```

---

## 附錄

### A. 參考資料

**API 文檔**:
- [MOPS 公開資訊觀測站](https://mops.twse.com.tw/)
- [TWSE OpenAPI](https://openapi.twse.com.tw/)
- [證交所月營收查詢](https://www.twse.com.tw/zh/trading/statistics/index04.html)

**程式參考**:
- [本專案現有 Collector 實作](../services/common/collectors/)
- [本專案 DataSource 實作](../services/common/datasources/)

**資料格式參考**:
- [現有 JSON 資料格式](../data/raw/price/)
- [資料庫 Schema](../services/common/database/models.py)

### B. 常見問題

**Q1: 為什麼不直接使用 OpenAPI？**

A: OpenAPI 有 1-2 天延遲，無法取得最新公告的月營收。使用 MOPS API 可以在公司公告後立即取得資料，對於即時分析很重要。

**Q2: 收集 2,000 檔需要 15 分鐘太久了？**

A: 這是使用 MOPS API 的情況（每月 1-10 號）。每月 11 號後可使用 OpenAPI，只需 2-3 秒即可完成。

**Q3: 月營收資料如何與股價資料關聯？**

A: 透過 `stock_id` 和時間範圍關聯。例如查詢某公司 2026 年 1 月營收對應的股價走勢。

**Q4: 如何處理公司更正前期營收？**

A: 系統會保留 Git 版本歷史，資料庫使用 UPSERT 更新最新資料。可透過 Git log 查看歷史版本。

**Q5: 資料可以商業使用嗎？**

A: 本系統僅供個人研究使用。商業使用請遵守證交所的資料使用條款，必要時購買官方資料授權。

### C. 版本歷史

| 版本 | 日期 | 變更內容 | 作者 |
|------|------|---------|------|
| 1.0 | 2026-02-06 | 初始版本 - 完整設計規範 | Claude Sonnet 4.5 |

---

**文件結束**

此設計文件提供完整的月營收收集功能架構與規範，包含需求分析、架構設計、資料流程、API 策略、驗證機制、儲存策略、資料庫設計、詳細任務分解、風險評估及測試策略。

所有設計遵循現有專案架構與規範，確保系統一致性與可維護性。

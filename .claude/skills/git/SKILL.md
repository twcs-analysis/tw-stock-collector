---
name: git
description: "Git 提交流程：分析變更、code review、更新文檔、提交並推送"
user-invocable: true
allowed-tools: Bash(git:*), Read, Write, Edit, Grep, Glob, Task
---

# Git 提交流程

執行完整的 Git 提交流程，包含 code review 與文檔更新。

## 檔案說明

- **README.md**: 專案說明文件
- **CHANGELOG.md**: 變更日誌（Keep a Changelog 格式）
- **deployment/README.md**: 部署說明
- **deployment/stock-data-collector/README.md**: 資料收集服務說明

## 執行步驟

### 1. 分析變更內容

```bash
# 查看變更狀態
git status

# 查看詳細變更
git diff
git diff --staged

# 查看最近 commit 格式
git log -5 --oneline
```

### 2. Code Review

**檢查項目**：
- 🔒 **安全性**：
  - 硬編碼密碼/token/API key
  - SQL injection、command injection
  - 敏感資訊外洩（.env、credentials）

- 🐛 **邏輯正確性**：
  - 空值處理、邊界條件
  - 錯誤處理機制
  - Race condition

- ⚡ **效能**：
  - N+1 查詢問題
  - 無限迴圈風險
  - 記憶體洩漏

- 📝 **程式碼品質**：
  - 命名一致性
  - 死碼（unused code）
  - 過度複雜的邏輯

**處理方式**：
- 小型變更（< 50 行）：直接檢查
- 中型變更（50-200 行）：逐檔案檢查
- 大型變更（> 200 行）：使用 Task tool 啟動獨立 review agent

**阻擋條件**（發現以下問題必須修復後才能提交）：
- ❌ 硬編碼的密碼、API key、token
- ❌ 明顯的安全漏洞
- ❌ 會導致服務中斷的邏輯錯誤

### 3. 更新相關文檔

根據變更類型更新對應文檔：

- **新功能或重大變更** → 更新 `README.md`
- **部署相關變更** → 更新 `deployment/README.md`
- **Docker 配置變更** → 更新 `deployment/stock-data-collector/README.md`
- **所有變更** → 更新 `CHANGELOG.md`

**CHANGELOG.md 格式**（Keep a Changelog）：
```markdown
## [Unreleased]

### Added
- 新增功能描述

### Changed
- 變更內容描述

### Fixed
- 修復問題描述

### Removed
- 移除項目描述
```

### 4. 建立 Git Commit

**Commit Message 格式**（Conventional Commits）：

```
<type>(<scope>): <subject>

<body>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Type 類型**：
- `feat`: 新功能
- `fix`: 修復 bug
- `docs`: 文檔更新
- `refactor`: 重構（不改變功能）
- `chore`: 雜項（建置、設定等）
- `test`: 測試相關
- `data`: 資料更新

**範例**：
```bash
git commit -m "$(cat <<'EOF'
feat: 新增成交量前 20 名資料收集器

- 新增 Top20VolumeCollector
- 從 TWSE OpenAPI 收集每日成交量前 20 名
- 新增對應的資料驗證器

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

### 5. 推送到遠端

```bash
git push
```

## 安全檢查清單

提交前確認：
- [ ] 沒有硬編碼的密碼或 API token
- [ ] `.env` 檔案在 `.gitignore` 中
- [ ] 沒有提交敏感設定檔
- [ ] 日誌檔案已在 `.gitignore` 中
- [ ] 測試資料已清理

## 注意事項

- ✅ Commit message 使用**繁體中文**描述變更內容
- ✅ CHANGELOG.md 遵循 Keep a Changelog 規範
- ✅ 每個 commit 應該是一個完整的邏輯單元
- ✅ 先 commit 後 push，不要跳過 commit
- ❌ 不要使用 `git commit --no-verify` 跳過檢查
- ❌ 不要提交包含密碼、token 等敏感資訊的檔案

## 常用 Git 指令

```bash
# 查看狀態
git status
git log --oneline -10

# 暫存變更
git add <file>
git add .

# 提交
git commit -m "訊息"

# 推送
git push

# 查看差異
git diff
git diff --staged
git diff HEAD~1

# 復原變更
git checkout <file>  # 復原未暫存的變更
git restore <file>   # 同上（新語法）
git reset HEAD <file> # 取消暫存
```

## Commit Message 範例

```bash
# 新功能
feat: 加入成交量前 20 名資料收集

# 修復 bug
fix: 修正 docker-compose.yml 的 command 參數格式

# 文檔更新
docs: 更新 deployment README 的使用說明

# 重構
refactor: 簡化 deployment 目錄結構

# 雜項
chore: 移除 docker-compose.yml 中過時的 version 屬性

# 資料更新
data: 補齊 2025 年 1-9 月完整歷史資料
```

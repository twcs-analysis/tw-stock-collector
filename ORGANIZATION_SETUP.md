# 組織 Repository 的 GitHub Actions 設定指南

由於此 repository 屬於組織 (`twcs-analysis`)，需要在**組織層級**進行 Actions 權限設定。

## 問題說明

在 repository 設定中無法選擇 "Read and write permissions" 是因為：
- 組織層級的 Actions 設定限制了個別 repository 的權限
- 需要組織管理員權限才能修改

## 解決方案

### 方案 1: 修改組織層級設定 (建議)

#### 步驟 1: 前往組織 Actions 設定

```
https://github.com/organizations/twcs-analysis/settings/actions
```

#### 步驟 2: 設定 Workflow permissions

找到 **"Workflow permissions"** 區塊，設定：

1. **選擇權限級別**:
   - ✅ 選擇 "**Read and write permissions**"
   - 這會套用到組織下所有 repositories

2. **允許創建 Pull Requests** (選用):
   - ✅ 勾選 "**Allow GitHub Actions to create and approve pull requests**"

3. **點擊 Save 儲存**

#### 步驟 3: 檢查 Fork pull request workflows

在同一個頁面，確認：
- ✅ "Allow GitHub Actions to run workflows from fork pull requests"
- 設定為適當的權限級別

---

### 方案 2: 為特定 Repository 設定例外

如果不想影響組織的其他 repositories：

#### 步驟 1: 組織設定允許覆寫

前往組織設定:
```
https://github.com/organizations/twcs-analysis/settings/actions
```

確認 **"Fork pull request workflows from outside collaborators"** 設定允許個別 repository 覆寫。

#### 步驟 2: Repository 設定

前往 repository 設定:
```
https://github.com/twcs-analysis/tw-stock-collector/settings/actions
```

現在應該可以選擇：
- ✅ "Read and write permissions"

---

### 方案 3: 使用 Personal Access Token (替代方案)

如果無法修改組織設定，可以使用 PAT：

#### 步驟 1: 建立 Personal Access Token

1. 前往 https://github.com/settings/tokens/new
2. 選擇權限:
   - ✅ `repo` (完整 repository 存取)
   - ✅ `write:packages` (推送 Docker 映像到 GHCR)
   - ✅ `workflow` (更新 workflow 檔案)
3. 設定 Token 名稱: `tw-stock-collector-ci`
4. 點擊 "**Generate token**"
5. **複製 Token** (只會顯示一次！)

#### 步驟 2: 新增 Repository Secret

前往:
```
https://github.com/twcs-analysis/tw-stock-collector/settings/secrets/actions
```

新增 Secret:
- Name: `PERSONAL_ACCESS_TOKEN`
- Secret: 貼上剛才複製的 Token

#### 步驟 3: 修改 Workflow

修改 [.github/workflows/ci.yml](.github/workflows/ci.yml):

```yaml
# 原本
- name: Log in to GitHub Container Registry
  if: github.event_name != 'pull_request'
  uses: docker/login-action@v3
  with:
    registry: ${{ env.REGISTRY }}
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}  # 改這行

# 改為
- name: Log in to GitHub Container Registry
  if: github.event_name != 'pull_request'
  uses: docker/login-action@v3
  with:
    registry: ${{ env.REGISTRY }}
    username: ${{ github.actor }}
    password: ${{ secrets.PERSONAL_ACCESS_TOKEN }}  # 使用 PAT
```

同樣修改 `daily-collection.yml` 和 `weekly-collection.yml`。

---

## 驗證設定

完成設定後，重新執行 GitHub Actions：

```bash
# 使用 GitHub CLI
gh run rerun 20542376282 --repo twcs-analysis/tw-stock-collector

# 或直接使用 workflow dispatch
gh workflow run ci.yml --repo twcs-analysis/tw-stock-collector
```

或在網頁上：
```
https://github.com/twcs-analysis/tw-stock-collector/actions
```

點擊失敗的 run → "Re-run all jobs"

---

## 確認清單

完成設定後，確認以下項目：

### 組織層級
- [ ] 組織 Actions 設定為 "Read and write permissions"
- [ ] 允許 GitHub Actions 創建 PR (如需要)

### Repository 層級
- [ ] Repository 可以覆寫組織設定 (如使用方案 2)
- [ ] Secrets 已設定:
  - [ ] `FINMIND_API_TOKEN` (選用)
  - [ ] `PERSONAL_ACCESS_TOKEN` (如使用方案 3)

### 測試 CI
- [ ] CI 工作流程成功執行
- [ ] Docker 映像成功建置
- [ ] Docker 映像成功推送到 GHCR

---

## 常見問題

### Q: 我沒有組織管理員權限怎麼辦？

A: 使用**方案 3** (Personal Access Token)，或聯繫組織管理員協助設定。

### Q: 設定後還是失敗？

A: 檢查以下項目：
1. Token 權限是否正確 (`repo`, `write:packages`, `workflow`)
2. Secret 名稱是否拼寫正確
3. Workflow 檔案是否正確引用 Secret
4. 組織是否有其他安全性限制

### Q: Docker 映像推送失敗？

A: 確認：
1. GHCR 是否啟用 (自動啟用)
2. Token 是否有 `write:packages` 權限
3. 映像名稱格式正確: `ghcr.io/twcs-analysis/tw-stock-collector`

---

## 快速連結

- **組織 Actions 設定**: https://github.com/organizations/twcs-analysis/settings/actions
- **Repository 設定**: https://github.com/twcs-analysis/tw-stock-collector/settings/actions
- **Secrets 管理**: https://github.com/twcs-analysis/tw-stock-collector/settings/secrets/actions
- **Actions 執行記錄**: https://github.com/twcs-analysis/tw-stock-collector/actions
- **建立 PAT**: https://github.com/settings/tokens/new

---

## 建議做法

**最佳方案**: 方案 1 (修改組織設定)
- 優點: 一次設定，適用所有 repositories
- 缺點: 需要組織管理員權限

**替代方案**: 方案 3 (使用 PAT)
- 優點: 不需要組織管理員權限
- 缺點: Token 需要定期更新，安全性較低

---

**最後更新**: 2025-12-28

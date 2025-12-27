#!/bin/bash
# GitHub Repository 自動設定腳本
# 需要安裝 GitHub CLI: brew install gh

set -e

REPO="twcs-analysis/tw-stock-collector"

echo "========================================"
echo "GitHub Repository 自動設定"
echo "========================================"
echo ""

# 檢查是否安裝 gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) 未安裝"
    echo ""
    echo "安裝方式："
    echo "  macOS: brew install gh"
    echo "  Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo ""
    exit 1
fi

# 檢查是否已登入
if ! gh auth status &> /dev/null; then
    echo "請先登入 GitHub CLI："
    echo "  gh auth login"
    exit 1
fi

echo "✅ GitHub CLI 已就緒"
echo ""

# 1. 設定 Workflow Permissions
echo "📝 設定 Workflow Permissions..."
echo "   (需要手動設定: Settings → Actions → General → Workflow permissions)"
echo "   選擇: Read and write permissions"
echo ""

# 2. 設定 Secret (如果有 Token)
echo "🔑 設定 Repository Secrets..."
read -p "是否要設定 FINMIND_API_TOKEN? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "請輸入 FinMind API Token: " -s FINMIND_TOKEN
    echo

    if [ -n "$FINMIND_TOKEN" ]; then
        gh secret set FINMIND_API_TOKEN --body "$FINMIND_TOKEN" --repo "$REPO"
        echo "✅ FINMIND_API_TOKEN 已設定"
    fi
else
    echo "⏭️  跳過 FINMIND_API_TOKEN 設定"
fi
echo ""

# 3. 啟用 GitHub Actions
echo "🚀 檢查 GitHub Actions 狀態..."
if gh api repos/$REPO/actions/permissions 2>&1 | grep -q "enabled"; then
    echo "✅ GitHub Actions 已啟用"
else
    echo "⚠️  請手動啟用 GitHub Actions:"
    echo "   1. 前往 https://github.com/$REPO/actions"
    echo "   2. 點擊 'I understand my workflows, go ahead and enable them'"
fi
echo ""

# 4. 設定 Package 權限
echo "📦 設定 GitHub Packages 權限..."
echo "   請確認以下設定："
echo "   1. Settings → Actions → General → Workflow permissions"
echo "   2. 選擇: Read and write permissions"
echo "   3. 勾選: Allow GitHub Actions to create and approve pull requests"
echo ""

# 5. 顯示當前 Actions 執行狀態
echo "📊 當前 GitHub Actions 執行狀態："
gh run list --repo "$REPO" --limit 5
echo ""

# 6. 生成設定檢查清單
echo "========================================"
echo "設定檢查清單"
echo "========================================"
echo ""
echo "請手動確認以下設定："
echo ""
echo "□ Workflow Permissions (Settings → Actions → General)"
echo "  └─ Read and write permissions ✓"
echo "  └─ Allow GitHub Actions to create and approve pull requests ✓"
echo ""
echo "□ GitHub Actions (Actions 頁面)"
echo "  └─ Workflows 已啟用 ✓"
echo ""
echo "□ Secrets (Settings → Secrets and variables → Actions)"
if gh secret list --repo "$REPO" 2>&1 | grep -q "FINMIND_API_TOKEN"; then
    echo "  └─ FINMIND_API_TOKEN ✓"
else
    echo "  └─ FINMIND_API_TOKEN (選用)"
fi
echo ""

# 7. 提供快速連結
echo "========================================"
echo "快速連結"
echo "========================================"
echo ""
echo "🔗 Repository: https://github.com/$REPO"
echo "🔗 Actions: https://github.com/$REPO/actions"
echo "🔗 Settings: https://github.com/$REPO/settings"
echo "🔗 Secrets: https://github.com/$REPO/settings/secrets/actions"
echo "🔗 Packages: https://github.com/orgs/twcs-analysis/packages?repo_name=tw-stock-collector"
echo ""

echo "✅ 設定腳本執行完成！"
echo ""
echo "接下來："
echo "1. 開啟上方的連結完成手動設定"
echo "2. 查看 Actions 頁面確認 CI 執行狀態"
echo "3. 等待 Docker 映像建置完成（約 5-8 分鐘）"

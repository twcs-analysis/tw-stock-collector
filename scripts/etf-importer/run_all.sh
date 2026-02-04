#!/bin/bash
# ============================================================================
# ETF 持股分析系統 - 一鍵執行腳本
# ============================================================================
#
# 功能:
# 1. 匯入 ETF 持股資料到資料庫
# 2. 產生 ETF 去重清單
# 3. 顯示統計資訊
#
# 使用方式:
#   bash scripts/etf-importer/run_all.sh
#   bash scripts/etf-importer/run_all.sh 2026-02-04
#
# ============================================================================

set -e  # 遇到錯誤立即停止

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 取得專案根目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 快照日期（預設為今天，或使用第一個參數）
SNAPSHOT_DATE="${1:-$(date +%Y-%m-%d)}"

echo ""
echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}ETF 持股分析系統 - 一鍵執行${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo -e "${YELLOW}快照日期: ${SNAPSHOT_DATE}${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# ============================================================================
# 步驟 1: 匯入 ETF 持股資料
# ============================================================================
echo -e "${GREEN}[1/2] 匯入 ETF 持股資料...${NC}"
echo ""

cd "$PROJECT_ROOT"

if python3.11 scripts/etf-importer/import_etf_holdings.py \
    --snapshot-date "$SNAPSHOT_DATE"; then
    echo ""
    echo -e "${GREEN}✅ ETF 持股資料匯入完成${NC}"
else
    echo ""
    echo -e "${RED}❌ ETF 持股資料匯入失敗${NC}"
    exit 1
fi

echo ""

# ============================================================================
# 步驟 2: 產生 ETF 去重清單
# ============================================================================
echo -e "${GREEN}[2/2] 產生 ETF 去重清單...${NC}"
echo ""

if python3.11 scripts/etf-importer/generate_etf_union.py \
    --snapshot-date "$SNAPSHOT_DATE"; then
    echo ""
    echo -e "${GREEN}✅ ETF 去重清單產生完成${NC}"
else
    echo ""
    echo -e "${RED}❌ ETF 去重清單產生失敗${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}============================================================================${NC}"
echo -e "${GREEN}🎉 所有步驟執行完成！${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""
echo -e "${YELLOW}接下來您可以:${NC}"
echo -e "  1. 執行選股策略 SQL (analysis/ETF持股篩選/*.sql)"
echo -e "  2. 查詢 ETF 持股: ${BLUE}SELECT * FROM etf_holdings;${NC}"
echo -e "  3. 查詢去重清單: ${BLUE}SELECT * FROM etf_stock_union;${NC}"
echo ""

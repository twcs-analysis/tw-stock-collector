#!/bin/bash

# ====================================
# 台股資料系統 - 一鍵建置所有微服務
# ====================================

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 設定映像檔標籤
TAG=${1:-latest}

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}台股資料系統 - 建置所有微服務${NC}"
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Tag: ${TAG}${NC}"
echo ""

# 服務列表
services=("data-collector" "data-importer" "api-service" "analyzer-service")

# 建置計數
success_count=0
failed_count=0

# 建置所有服務
for service in "${services[@]}"; do
    echo -e "${BLUE}[Building]${NC} $service..."

    docker build \
        -f build/$service/Dockerfile \
        -t tw-stock-$service:$TAG \
        . \
        2>&1 | tee build/$service/build.log

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✅ $service built successfully${NC}"
        ((success_count++))
    else
        echo -e "${RED}❌ $service build failed${NC}"
        echo -e "${YELLOW}Check build/$service/build.log for details${NC}"
        ((failed_count++))
    fi
    echo ""
done

# 顯示建置結果
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Build Summary${NC}"
echo -e "${BLUE}=====================================${NC}"
echo -e "${GREEN}✅ Success: $success_count${NC}"
echo -e "${RED}❌ Failed: $failed_count${NC}"
echo ""

# 列出建置的映像檔
if [ $success_count -gt 0 ]; then
    echo -e "${BLUE}Built images:${NC}"
    docker images | grep "tw-stock-" | grep "$TAG"
    echo ""
fi

# 檢查是否全部成功
if [ $failed_count -eq 0 ]; then
    echo -e "${GREEN}🎉 All services built successfully!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some services failed to build${NC}"
    exit 1
fi

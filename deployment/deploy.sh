#!/bin/bash

# ====================================
# 台股資料收集系統 - 部署腳本
# ====================================
#
# 用途: 選擇並部署不同的服務模組
#
# 使用方式:
#   ./deploy.sh                    # 互動式選擇
#   ./deploy.sh stock-data-collector  # 直接指定服務
#   ./deploy.sh --list             # 列出所有可用服務
#

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示標題
show_header() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}台股資料收集系統 - 部署腳本${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo ""
}

# 顯示錯誤訊息
error() {
    echo -e "${RED}❌ 錯誤: $1${NC}" >&2
}

# 顯示成功訊息
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 顯示警告訊息
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 顯示資訊訊息
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 列出所有可用服務
list_services() {
    echo -e "${GREEN}可用的服務:${NC}"
    echo ""

    for dir in */; do
        # 排除不是服務的目錄
        if [[ -d "$dir" && -f "${dir}docker-compose.yml" ]]; then
            service_name="${dir%/}"
            if [[ -f "${dir}README.md" ]]; then
                # 從 README 提取描述
                description=$(head -5 "${dir}README.md" | grep -E "^# |台股|資料" | head -1 | sed 's/^# //')
                echo -e "  ${GREEN}●${NC} ${BLUE}$service_name${NC}"
                echo -e "    $description"
            else
                echo -e "  ${GREEN}●${NC} ${BLUE}$service_name${NC}"
            fi
            echo ""
        fi
    done
}

# 檢查服務是否存在
check_service() {
    local service=$1

    if [[ ! -d "$service" ]]; then
        error "服務目錄不存在: $service"
        echo ""
        list_services
        return 1
    fi

    if [[ ! -f "$service/docker-compose.yml" ]]; then
        error "找不到 docker-compose.yml: $service/docker-compose.yml"
        return 1
    fi

    return 0
}

# 互動式選擇服務
interactive_select() {
    local services=()
    local i=1

    echo -e "${GREEN}請選擇要部署的服務:${NC}"
    echo ""

    for dir in */; do
        if [[ -d "$dir" && -f "${dir}docker-compose.yml" ]]; then
            service_name="${dir%/}"
            services+=("$service_name")

            if [[ -f "${dir}README.md" ]]; then
                description=$(head -5 "${dir}README.md" | grep -E "^# |台股|資料" | head -1 | sed 's/^# //')
                echo -e "  ${BLUE}[$i]${NC} $service_name"
                echo -e "      $description"
            else
                echo -e "  ${BLUE}[$i]${NC} $service_name"
            fi
            echo ""
            ((i++))
        fi
    done

    if [[ ${#services[@]} -eq 0 ]]; then
        error "找不到任何可用的服務"
        exit 1
    fi

    echo -n "請輸入數字 [1-${#services[@]}] 或按 Ctrl+C 取消: "
    read -r choice

    if [[ ! "$choice" =~ ^[0-9]+$ ]] || [[ $choice -lt 1 ]] || [[ $choice -gt ${#services[@]} ]]; then
        error "無效的選擇: $choice"
        exit 1
    fi

    echo "${services[$((choice-1))]}"
}

# 部署服務
deploy_service() {
    local service=$1
    local action=${2:-up}

    info "部署服務: $service"
    echo ""

    cd "$service" || exit 1

    # 檢查 .env 檔案
    if [[ ! -f .env ]]; then
        if [[ -f .env.example ]]; then
            warning ".env 檔案不存在，正在從 .env.example 複製..."
            cp .env.example .env
            success ".env 檔案已建立"
            echo ""
            warning "請檢查並修改 .env 設定後再繼續"
            echo ""
            echo -n "按 Enter 繼續或 Ctrl+C 取消..."
            read -r
        else
            warning ".env 和 .env.example 都不存在，使用預設設定"
        fi
    fi

    # 顯示操作選單
    echo -e "${GREEN}選擇操作:${NC}"
    echo "  [1] 啟動服務 (docker-compose up)"
    echo "  [2] 背景啟動 (docker-compose up -d)"
    echo "  [3] 停止服務 (docker-compose down)"
    echo "  [4] 查看日誌 (docker-compose logs)"
    echo "  [5] 重新建置 (docker-compose build)"
    echo "  [6] 查看狀態 (docker-compose ps)"
    echo "  [0] 返回"
    echo ""
    echo -n "請選擇 [0-6]: "
    read -r action_choice

    case $action_choice in
        1)
            info "啟動服務..."
            docker-compose up
            ;;
        2)
            info "背景啟動服務..."
            docker-compose up -d
            success "服務已在背景啟動"
            echo ""
            info "使用以下指令查看狀態:"
            echo "  cd $service && docker-compose logs -f"
            ;;
        3)
            info "停止服務..."
            docker-compose down
            success "服務已停止"
            ;;
        4)
            info "查看日誌..."
            docker-compose logs -f
            ;;
        5)
            info "重新建置..."
            docker-compose build --no-cache
            success "建置完成"
            ;;
        6)
            info "查看狀態..."
            docker-compose ps
            ;;
        0)
            info "返回"
            cd ..
            return
            ;;
        *)
            error "無效的選擇: $action_choice"
            cd ..
            exit 1
            ;;
    esac

    cd ..
}

# 主程式
main() {
    show_header

    # 檢查是否在 deployment 目錄
    if [[ ! -f "deploy.sh" ]]; then
        error "請在 deployment 目錄中執行此腳本"
        exit 1
    fi

    # 處理參數
    case "${1:-}" in
        --list|-l)
            list_services
            exit 0
            ;;
        --help|-h)
            echo "用法: $0 [服務名稱|選項]"
            echo ""
            echo "選項:"
            echo "  --list, -l     列出所有可用服務"
            echo "  --help, -h     顯示此說明"
            echo ""
            echo "範例:"
            echo "  $0                        # 互動式選擇"
            echo "  $0 stock-data-collector   # 直接部署指定服務"
            echo "  $0 --list                 # 列出所有服務"
            exit 0
            ;;
        "")
            # 互動式模式
            service=$(interactive_select)
            ;;
        *)
            # 直接指定服務
            service=$1
            ;;
    esac

    # 檢查服務
    if ! check_service "$service"; then
        exit 1
    fi

    # 部署服務
    deploy_service "$service"
}

# 執行主程式
main "$@"

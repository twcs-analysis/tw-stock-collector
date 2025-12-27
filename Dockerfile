# Phase 1 台股資料收集系統 - Docker Image
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY config/ ./config/
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY PHASE1_GUIDE.md README.md ./

# 建立必要的目錄
RUN mkdir -p data/raw/price data/raw/institutional data/raw/margin data/raw/lending \
    && mkdir -p logs \
    && mkdir -p cache

# 設定目錄權限
RUN chmod -R 755 /app

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# 預設執行測試
CMD ["python", "scripts/test_phase1.py", "--skip-api"]

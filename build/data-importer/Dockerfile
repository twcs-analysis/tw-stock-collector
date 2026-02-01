# ====================================
# Data Importer Service Dockerfile
# 台股資料匯入微服務
# ====================================
#
# 功能: 將 JSON 資料匯入到資料庫（PostgreSQL / SQLite）
# 用途: 從 data/raw/ 讀取 JSON 並寫入資料庫

FROM python:3.11-slim

LABEL maintainer="Jason Huang"
LABEL service="data-importer"
LABEL description="台股資料匯入服務 - 將 JSON 資料匯入資料庫"

WORKDIR /app

# ==========================================
# 1. 安裝系統依賴
# ==========================================
RUN apt-get update && apt-get install -y \
    postgresql-client \
    sqlite3 \
    git \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# 2. 安裝 Python 依賴
# ==========================================
COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir \
    -r requirements.txt \
    sqlalchemy>=2.0.0 \
    psycopg2-binary>=2.9.0 \
    alembic>=1.13.0 \
    pydantic>=2.0.0 \
    tqdm>=4.66.0

# ==========================================
# 3. 複製專案檔案
# ==========================================
COPY src /app/src
COPY scripts /app/scripts
COPY config /app/config

# ==========================================
# 4. 環境設定
# ==========================================
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV TZ=Asia/Taipei
ENV LOG_LEVEL=INFO

ENV DB_TYPE=postgresql
ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_NAME=tw_stock
ENV DB_USER=postgres

# ==========================================
# 5. 建立必要目錄
# ==========================================
RUN mkdir -p \
    /app/data/raw \
    /app/database/sqlite \
    /app/logs

# ==========================================
# 6. 執行入口（暫時）
# ==========================================
ENTRYPOINT ["python", "-c"]
CMD ["print('Data Importer Service - Ready to import data')"]

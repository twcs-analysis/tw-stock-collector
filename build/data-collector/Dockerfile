# Data Collector Service Dockerfile
# 台股資料收集微服務

FROM python:3.11-slim

LABEL maintainer="Jason Huang"
LABEL service="data-collector"
LABEL description="台股資料收集服務"

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt
COPY requirements.txt ./requirements.txt

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製共用程式庫
COPY services/common /app/common

# 複製服務程式碼
COPY services/data-collector/app /app/app

# 複製執行腳本
COPY scripts/run_collection.py /app/scripts/run_collection.py
COPY scripts/data-collector/ /app/scripts/data-collector/

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV TZ=Asia/Taipei
ENV LOG_LEVEL=INFO

# 建立資料目錄
RUN mkdir -p /app/data/raw /app/logs

# 設定執行權限
RUN chmod +x /app/scripts/run_collection.py

# 預設執行命令（使用舊的入口點保持向後相容）
ENTRYPOINT ["python", "/app/scripts/run_collection.py"]

# 預設參數
CMD ["--help"]

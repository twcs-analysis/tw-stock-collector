# Data Importer Service Dockerfile

FROM python:3.11-slim

LABEL maintainer="Jason Huang"
LABEL service="data-importer"
LABEL description="台股資料匯入服務"

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt
COPY services/data-importer/requirements.txt ./requirements.txt
COPY services/common /app/common

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製服務程式碼
COPY services/data-importer/app /app/app

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Taipei
ENV LOG_LEVEL=INFO

# 建立資料目錄
RUN mkdir -p /app/data

# 執行入口
ENTRYPOINT ["python", "/app/app/main.py"]

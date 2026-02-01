# Analyzer Service Dockerfile

FROM python:3.11-slim

LABEL maintainer="Jason Huang"
LABEL service="analyzer-service"
LABEL description="台股分析服務"

WORKDIR /app

# 安裝系統依賴（包含編譯工具for TA-Lib）
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安裝 TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# 複製 requirements.txt
COPY services/analyzer-service/requirements.txt ./requirements.txt
COPY services/common /app/common

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製服務程式碼
COPY services/analyzer-service/app /app/app

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Taipei
ENV LOG_LEVEL=INFO
ENV WORKER_THREADS=4

# 執行入口
ENTRYPOINT ["python", "/app/app/main.py"]

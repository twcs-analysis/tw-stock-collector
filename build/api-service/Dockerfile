# API Service Dockerfile

FROM python:3.11-slim

LABEL maintainer="Jason Huang"
LABEL service="api-service"
LABEL description="台股資料 API 服務"

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt
COPY services/api-service/requirements.txt ./requirements.txt
COPY services/common /app/common

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製服務程式碼
COPY services/api-service/app /app/app

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Taipei
ENV LOG_LEVEL=INFO
ENV API_PORT=8000

# 暴露 API 埠號
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 執行入口
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

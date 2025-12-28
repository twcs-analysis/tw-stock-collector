# Phase 1: 台股資料收集器 Docker Image
# 用於在 GitHub Actions 或本地執行資料收集

FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY src/ ./src/
COPY scripts/run_collection.py ./scripts/

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 建立資料目錄
RUN mkdir -p /app/data/raw

# 設定執行權限
RUN chmod +x /app/scripts/run_collection.py

# 預設執行命令
ENTRYPOINT ["python", "/app/scripts/run_collection.py"]

# 預設參數（可被覆寫）
CMD ["--help"]

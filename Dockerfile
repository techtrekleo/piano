FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements_simple.txt .

# 安裝Python依賴
RUN pip install --no-cache-dir -r requirements_simple.txt

# 複製應用代碼
COPY . .

# 創建上傳目錄
RUN mkdir -p uploads

# 設置環境變量
ENV FLASK_APP=app_simple.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 啟動命令
CMD ["python", "app_simple.py"]

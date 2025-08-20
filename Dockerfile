FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝Python依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建上傳目錄
RUN mkdir -p uploads

# 暴露端口
EXPOSE 5000

# 啟動命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

#!/bin/bash

echo "🚀 啟動音樂可視化器..."
echo "📁 當前目錄: $(pwd)"
echo "🐍 Python版本: $(python --version)"
echo "📦 安裝依賴..."

# 安裝依賴
pip install -r requirements_simple.txt

echo "🌐 啟動應用..."
echo "📍 端口: $PORT"
echo "🏥 健康檢查: /health"

# 啟動應用
python app_simple.py

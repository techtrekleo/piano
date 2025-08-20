# 🚀 部署到 Railway

這個音樂可視化器已經準備好部署到 Railway 平台。

## 📋 部署步驟

### 1. 創建 GitHub 倉庫

1. 前往 [GitHub](https://github.com) 創建新倉庫
2. 倉庫名稱建議：`music-visualizer` 或 `see-music`
3. 設置為 Public 倉庫
4. 不要初始化 README、.gitignore 或 license

### 2. 推送代碼到 GitHub

```bash
# 添加遠程倉庫（替換 YOUR_USERNAME 和 REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 推送代碼
git branch -M main
git push -u origin main
```

### 3. 部署到 Railway

1. 前往 [Railway](https://railway.app)
2. 使用 GitHub 帳號登入
3. 點擊 "New Project"
4. 選擇 "Deploy from GitHub repo"
5. 選擇你剛才創建的倉庫
6. 點擊 "Deploy Now"

### 4. 配置環境變量

Railway 會自動檢測 Python 項目並安裝依賴。

### 5. 等待部署完成

部署過程可能需要 5-10 分鐘，Railway 會：
- 安裝 Python 3.9+
- 安裝 requirements.txt 中的依賴
- 啟動 Flask 應用

## 🔧 部署後配置

### 檢查部署狀態

部署完成後，Railway 會提供一個 URL，例如：
`https://your-app-name.railway.app`

### 測試應用

1. 訪問你的 Railway URL
2. 上傳一個音頻文件測試
3. 檢查 `/health` 端點是否正常

## 📁 項目結構

```
TACOGOLD/
├── app.py                 # Flask 主應用
├── requirements.txt       # Python 依賴
├── railway.json          # Railway 配置
├── Procfile             # 部署配置
├── templates/            # HTML 模板
│   └── index.html       # 主頁面
├── .gitignore           # Git 忽略文件
└── README.md            # 項目說明
```

## 🐛 故障排除

### 常見問題

1. **構建失敗**
   - 檢查 requirements.txt 格式
   - 確保所有依賴版本兼容

2. **應用無法啟動**
   - 檢查 Railway 日誌
   - 確認 PORT 環境變量

3. **依賴安裝失敗**
   - 某些庫可能需要系統依賴
   - 考慮使用 Docker 部署

### 查看日誌

在 Railway 控制台：
1. 點擊你的項目
2. 選擇 "Deployments"
3. 點擊最新的部署
4. 查看 "Build Logs" 和 "Deploy Logs"

## 🌟 功能特點

- ✅ 支持多種音頻格式 (MP3, WAV, FLAC, M4A, OGG)
- ✅ 實時音頻分析
- ✅ 動態音樂可視化
- ✅ 響應式 Web 界面
- ✅ 拖拽上傳支持
- ✅ 鋼琴鍵盤可視化

## 🔗 相關鏈接

- [Railway 文檔](https://docs.railway.app/)
- [Flask 文檔](https://flask.palletsprojects.com/)
- [Librosa 文檔](https://librosa.org/)

---

部署完成後，你就可以在任何地方訪問你的音樂可視化器了！🎵✨

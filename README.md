referral-report/
│
├── app.py                  # Flask 主程式
├── requirements.txt        # 套件需求列表
├── .gitignore              # 忽略不需追蹤的檔案設定
│
├── templates/              # Flask 前端模板資料夾
│   └── index.html          # 主頁 HTML
│
├── static/                 # 前端靜態資源
│   ├── css/
│   │   └── style.css       # 頁面樣式
│   └── js/
│       └── referral-report.js  # JS 行為邏輯


# Referral Report API 專案

這是一個推薦人訂單查詢系統，使用者可透過推薦碼查詢專屬訂單、付款狀態、運費總額，並支援 CSV 匯出與視覺化圖表呈現。

## 🛠 技術堆疊
- Python + Flask
- EasyStore API
- HTML + JS (原生 JavaScript)
- Render 雲端部署

## 📂 專案結構
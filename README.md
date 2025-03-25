# 📋 Referral Report API 專案

推薦人專屬的訂單報表查詢系統，使用者可透過推薦碼查詢其推薦來源的 EasyStore 訂單，包含訂單狀態、金額、運費等資訊，並支援 CSV 匯出與統計視覺化呈現。

---

## 🌐 Demo 線上網址

👉 [https://referral-report-api.onrender.com](https://referral-report-api.onrender.com)

可直接帶入參數使用：

```
https://referral-report-api.onrender.com/?referral_code=LAVONS88&access_token=token_lavons88_123
```

---

## 🛠 技術堆疊

- Python 3 + Flask
- EasyStore API 串接
- HTML + 原生 JavaScript
- Render 雲端部署
- UTF-8 BOM 防亂碼 CSV 匯出

---

## ✨ 功能介紹

- ✅ 推薦人訂單查詢（依時間區段與推薦碼過濾）
- 📊 訂單總數 / 總金額 / 總運費 統計
- 📤 一鍵匯出對應訂單報表（CSV 格式）
- ⌛ 精準時間選擇（支援每半小時）
- 🔐 Token 權限驗證
- 🖥️ 可快速預覽推薦人查詢紀錄與結果

---

## 📦 安裝與使用

### 🔧 安裝套件

```bash
pip install -r requirements.txt
```

### 🚀 啟動伺服器

```bash
python app.py
```

開啟瀏覽器造訪：

```
http://localhost:5000
```

---

## 📁 專案結構

```
referral-report/
│
├── app.py                     # Flask 主程式
├── requirements.txt           # 套件需求列表
├── .gitignore                 # 忽略檔案設定
│
├── templates/
│   └── index.html             # 主頁 HTML 模板
│
├── static/
│   ├── css/
│   │   └── style.css          # 前端樣式
│   └── js/
│       └── referral-report.js # 前端邏輯與資料處理
```

---

## 🔑 推薦碼對照表

| 團主名稱 | 推薦碼 | Access Token | 專屬連結 |
|----------|--------|--------------|-----------|
| Lavon    | LAVONS88 | token_lavons88_123 | [點我查詢](https://referral-report-api.onrender.com/?referral_code=LAVONS88&access_token=token_lavons88_123) |
| Winnie   | LAVONS_WINNIE | token_winnie_456 | [點我查詢](https://referral-report-api.onrender.com/?referral_code=LAVONS_WINNIE&access_token=token_winnie_456) |
| 小杉     | LAVONS_XIAOSHAN | token_xiaoshan_789 | [點我查詢](https://referral-report-api.onrender.com/?referral_code=LAVONS_XIAOSHAN&access_token=token_xiaoshan_789) |

---

## 📤 匯出報表說明

- 點擊「📤 匯出報表」按鈕即可下載 CSV 檔案
- 匯出格式為 **UTF-8 with BOM**，避免 Excel 開啟時亂碼
- 欄位包含：
  - 訂單編號
  - 成立時間
  - 金額
  - 付款狀態
  - 出貨狀態
  - 是否取消
  - 備註

---

## 🔮 延伸功能規劃（未來）

- 📍 團主登入介面（帳號密碼）
- 📆 自動寄送週報 / 月報
- 📈 團購銷售圖表視覺化（折線圖 / 圓餅圖）
- 🔧 管理者後台（新增推薦碼、管理訂單）

---

## 🤝 貢獻與聯絡

如果你對本系統有任何建議或想法，歡迎發 Issue / PR 或與我聯絡 🙌

📬 Email：don1donshop@gmail.com

---

🎉 感謝使用本推薦人訂單查詢系統，希望幫助你更高效地追蹤推廣成果！

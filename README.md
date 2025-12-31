# My Vuetify3 App — 環境與啟動說明 

本文檔說明如何：
- 安裝前端（Vue + Vuetify）相依套件
- 將資料（`api/test_2.sql`）匯入 MySQL 資料庫
- 使用 Python venv 啟動 `api.py`（後端 API）
- 啟動前端開發伺服器 (`npm run dev -- --host`)

---

## 先決條件 
- Node.js（建議 Node 18+）與 npm
- Python 3.10+
- MySQL（或 MariaDB）可執行，且有權限建立資料庫
- 在 Windows 下使用 PowerShell 示例指令（若使用 cmd 或 WSL，指令稍有差別）

---

## 1) 前端：安裝與啟動（Vue/Vuetify）
1. 在專案根目錄（含 `package.json` 的資料夾）執行：

```powershell
npm install
```

2. 啟動開發伺服器（允許從本機網路存取）：

```powershell
npm run dev -- --host
```

- 若要 build 成 production bundle：

```powershell
npm run build
```

---

## 2) 資料庫：建立資料庫並匯入 `api/test_2.sql`
> 預設 DB 設定位於 `api/config.json`：
> ```json
> "db": {
>   "username": "root",
>   "password": "",
>   "host": "localhost",
>   "port": 3306,
>   "database": "test",
>   "charset": "utf8mb4"
> }
> ```

1. 若尚未建立資料庫，可用 MySQL CLI（PowerShell 範例）：

```powershell
mysql -u root -p -e "CREATE DATABASE test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

2. 匯入 SQL 檔（範例）：

```powershell
mysql -u root -p test < api/test_2.sql
```

- 如果您偏好 GUI（MySQL Workbench / phpMyAdmin），也可以用匯入功能將 `api/test_2.sql` 匯入 `test` 資料庫。
- 如果想用 Python 匯入（不需直接使用 MySQL CLI），請參考下面的「使用 Python 匯入」小節。

---

## 3) 後端：使用 venv 啟動 `api.py`（Flask）
1. 建議在 `api/` 目錄下建立虛擬環境並安裝相依套件：

```powershell
cd api
python -m venv .venv
# PowerShell 啟用
.\.venv\Scripts\Activate.ps1
# pip 更新
python -m pip install --upgrade pip
# 安裝套件
pip install -r requirements.txt
```

2. 啟動 API：

```powershell
python api.py
```

- 啟動後預設會監聽在 `0.0.0.0:5000`（可由前端以 `http://localhost:5000` 或機器 IP 存取）。
- 若要更改資料庫帳號、密碼或資料庫名稱，編輯 `api/config.json`。

---


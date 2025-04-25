# Earthquake-Event-Dispatcher

使用 Docker + docker-compose 整合開發模組，包括：

- backend : fastAPI
- frontend : React
- prometheus
- grafana

## QuickStart

為了避免資料庫密碼進入 git，用 `cp .env.example .env` 複製一份環境變數檔案後，在自己的開發環境自行修改密碼 `.env` 
```
cp .env.example .env

docker-compose build
docker-compose --env-file .env up -d
```

## Port 對應表

| 服務名稱       | 容器內部 Port | 對外對應 Port（本機） |
|----------------|----------------|------------------------|
| `backend`      | 8000           | 8000                   |
| `frontend`     | 3000           | 3000                   |
| `prometheus`   | 9090           | 9090                   |
| `grafana`      | 3000           | 3000                   |

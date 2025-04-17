# Earthquake-Event-Dispatcher

使用 Docker + docker-compose 整合多個開發模組，包括：

- FastAPI backend
- React frontend
- Simulation UI
- Prometheus（資料收集）
- Grafana（視覺化分析）

目前已啟用 **Prometheus 與 Grafana**

## Port 對應表

| 服務名稱       | 功能說明           | 容器內部 Port | 對外對應 Port（本機） |
|----------------|--------------------|----------------|------------------------|
| `backend`      | FastAPI 後端 API   | 8000           | 8000                   |
| `frontend`     | 使用者 UI（React） | 3000           | 3000                   |
| `simulation-ui`| 地震模擬前端       | 3000           | 3001                   |
| `prometheus`   | 時序資料收集服務   | 9090           | 9090                   |
| `grafana`      | 圖表視覺化工具     | 3000           | 4000（避免與 frontend 衝突） |
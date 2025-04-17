# Earthquake-Event-Dispatcher

使用 Docker + docker-compose 整合多個開發模組，包括：

- FastAPI backend
- React frontend
- Simulation UI
- Prometheus（資料收集）
- Grafana（視覺化分析）

目前已啟用 **Prometheus 與 Grafana**

## Port 對應表

| 服務名稱       | 容器內部 Port | 對外對應 Port（本機） |
|----------------|----------------|------------------------|
| `backend`      | 8000           | 8000                   |
| `frontend`     | 3000           | 3000                   |
| `prometheus`   | 9090           | 9090                   |
| `grafana`      | 3000           | 4000                   |

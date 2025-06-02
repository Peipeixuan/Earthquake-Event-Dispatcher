# Earthquake Event Dispatcher

地震事件調度系統 - 用於地震監測、模擬和事件管理的專案。

## 系統架構

- **Frontend**: React 服務，提供地震模擬和警報管理界面
- **Backend**: FastAPI 後端服務，處理 API 請求和業務邏輯
- **Data Ingestion**: 資料擷取服務，從中央氣象局 API 獲取地震數據
- **Database**: MySQL 8.0 資料庫
- **Earthquake Monitoring**: Prometheus + Grafana 
- **Reverse Proxy**: Nginx 反向代理

- **System Monitoring & logging** : [See this repo](https://github.com/Peipeixuan/Earthquake-Event-Dispatcher-Monitor)
### 系統架構圖
![infra_overview](https://github.com/user-attachments/assets/6eaa7141-88d7-476c-b84c-f8bfb4ac62af)
![infra_detail](https://github.com/user-attachments/assets/b5a69da8-bba3-47e7-b46e-5285ec0ad89a)

### CICD 流程圖
![cicd_flow](https://github.com/user-attachments/assets/61c6917b-3c0e-433d-8c0b-3745f6b68247)

## Quick Start

### 開發環境

1. **Clone Project**
   ```bash
   git clone https://github.com/Peipeixuan/Earthquake-Event-Dispatcher.git
   cd Earthquake-Event-Dispatcher
   ```

2. **配置環境變數**
   ```bash
   cp .env.example .env
   # 編輯 .env 文件，設置資料庫和其他設定
   ```

3. **啟動開發環境**
   ```bash
   docker compose up -d
   ```

### 生產環境

生產環境會使用預構建的 Docker image（Artifact Registry），透過 GitHub Actions 自動部署：

```bash
docker compose -f docker-compose.prod.yml up -d
```

## 功能特性

### 前端應用

React 有兩個主要頁面： 

- **地震模擬** (`/simulation`): 模擬地震參數設置，設定地震抑制時間
- **事件管理** (`/alert`): 地震警報處理和狀態管理

### 地震模擬系統

用戶可在模擬系統設定地震參數：

- 地震時間、震級、深度
- 震央位置（縣市）
- 各地區震度設置

### 事件管理工作流

事件管理系統實現四階段工作流：
1. **未接收**: 新地震事件等待確認
2. **待處理**: 已確認事件等待評估
3. **維修中**: 正在處理的事件
4. **已完成**: 處理完成的事件

## 部署和維運

### CI/CD 流水線

系統使用 GitHub Actions 實現自動化 CI/CD：

**開發分支** (`develop`):  
- 自動構建 Docker 鏡像
- 運行測試套件
- 推送到 GCP Artifact Registry

**主分支** (`main`): 
- 將 develop 鏡像重新標記為 main
- 自動部署到生產環境
- 執行健康檢查

### 服務端口配置

| 服務 | 內部 port | 外部訪問 | 用途 |
|------|----------|----------|------|
| nginx | 80 | Port 80 | 反向代理 |
| backend | 8000 | `/api/*` | API 服務 |
| frontend | 5173 | `/*` | Web 界面 |
| prometheus | 9090 | `/prometheus/*` | 監控指標 |
| grafana | 3000 | `/grafana/*` | 監控面板 |
| mysql | 3306 | 內部 | 數據庫 |

### 監控和日誌

- **Prometheus**: 收集系統指標和性能數據
- **Grafana**: 提供可視化地震監控面板

## 開發指南

### 專案結構

```
├── frontend/           # React 前端應用
│   ├── src/pages/     # 頁面組件
│   └── src/components/ # 共用組件
├── backend/           # FastAPI 後端服務
├── data_ingestion/    # 數據攝取服務
├── prometheus/        # 監控配置
├── grafana/          # 面板配置
└── nginx.conf        # 反向代理配置
```


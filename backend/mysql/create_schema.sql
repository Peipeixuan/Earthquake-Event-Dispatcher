CREATE TABLE IF NOT EXISTS earthquake (
    id INT PRIMARY KEY,
    origin_time TIMESTAMP NOT NULL,     -- 發生日期時間
    location VARCHAR(255),              -- 地點名稱
    latitude FLOAT,                     -- 緯度
    longitude FLOAT,                    -- 經度
    richter_scale FLOAT,                -- 芮氏規模
    focal_depth FLOAT,                  -- 震源深度（公里）
    is_demo BOOLEAN                     -- 是否為 demo 地震（T/F）
);

CREATE TABLE IF NOT EXISTS earthquake_location (
    id INT AUTO_INCREMENT PRIMARY KEY,
    earthquake_id INT,                    -- 對應 earthquake.id
    location VARCHAR(255),                 -- 地點名稱
    magnitude_value FLOAT,                 -- 各地震度值
    FOREIGN KEY (earthquake_id) REFERENCES earthquake(id)
);

CREATE TABLE IF NOT EXISTS event (
    id VARCHAR(20) PRIMARY KEY,
    location_eq_id INT,                  -- 對應 location_eq_id
    create_at TIMESTAMP NOT NULL,         -- 發生日期時間
    region VARCHAR(255),                  -- 區域
    level ENUM('NA', 'L1', 'L2'),          -- 等級
    trigger_alert BOOLEAN,                -- 是否觸發警報（T/F）
    ack BOOLEAN,                          -- 是否接收ack（T/F）
    ack_time TIMESTAMP NULL,              -- 接收時間
    is_damage BOOLEAN,                    -- 是否損毀（T/F）
    is_operation_active BOOLEAN,          -- 是否正在處理（T/F）
    is_done BOOLEAN,                      -- 是否處理完成（T/F）
    report_at TIMESTAMP NULL,             -- 回報時間
    closed_at TIMESTAMP NULL,             -- 確認修復完成時間
    FOREIGN KEY (location_eq_id) REFERENCES earthquake_location(id)
);

CREATE TABLE IF NOT EXISTS alert (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id VARCHAR(20),                         -- 對應 event.id
    create_at TIMESTAMP NOT NULL,          -- 發生日期時間
    factory VARCHAR(255),                  -- 廠名
    FOREIGN KEY (event_id) REFERENCES event(id)
);

-- cooldown_time
CREATE TABLE IF NOT EXISTS settings (
    name VARCHAR(255) PRIMARY KEY,
    value VARCHAR(255)
);
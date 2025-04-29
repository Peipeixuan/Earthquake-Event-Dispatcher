from fastapi import APIRouter, Query
import pymysql
from app.db import get_mysql_connection

router = APIRouter(
    prefix="/settings",
    tags=["Settings"]
)

@router.post("/alert_suppress")
def set_alert_suppress_time(alert_suppress_time: int = Query(..., description="設定警報抑制時間（單位：分鐘）")):
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "REPLACE INTO settings (name, value) VALUES (%s, %s)",
                ("alert_suppress_time", str(alert_suppress_time))
            )
        conn.commit()
        return {"message": "alert suppress time updated", "alert_suppress_time": alert_suppress_time}
    finally:
        conn.close()

@router.get("/alert_suppress")
def get_alert_suppress_time():
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT value FROM settings WHERE name = %s", ("alert_suppress_time",))
            result = cursor.fetchone()
            if result:
                return {"alert_suppress_time": int(result["value"])}
            return {"alert_suppress_time": 30}  # fallback
    finally:
        conn.close()
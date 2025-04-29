from fastapi import APIRouter, Query
import pymysql
from app.db import get_mysql_connection

router = APIRouter(
    prefix="/settings",
    tags=["Settings"]
)

@router.post("/alert_cooldown")
def set_alert_cooldown(cooldown_minutes: int = Query(..., description="設定警報抑制時間（單位：分鐘）")):
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "REPLACE INTO settings (name, value) VALUES (%s, %s)",
                ("cooldown_minutes", str(cooldown_minutes))
            )
        conn.commit()
        return {"message": "Cooldown time updated", "cooldown_minutes": cooldown_minutes}
    finally:
        conn.close()

@router.get("/alert_cooldown")
def get_alert_cooldown():
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT value FROM settings WHERE name = %s", ("cooldown_minutes",))
            result = cursor.fetchone()
            if result:
                return {"cooldown_minutes": int(result["value"])}
            return {"cooldown_minutes": 30}  # fallback
    finally:
        conn.close()
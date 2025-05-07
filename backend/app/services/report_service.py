from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.db import get_mysql_connection

location_suffix_map = {
    "Taipei": "-tp",
    "Hsinchu": "-hc",
    "Taichung": "-tc",
    "Tainan": "-tn"
}


def fetch_unacknowledged_events(location: str):
    """ report/unacknowledged
    Fetch unacknowledged events
    """
    suffix = location_suffix_map.get(location)
    if not suffix and location.lower() != "all":
        return {"message": "Invalid location"}

    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT e.id AS event_id, eq.earthquake_time, e.create_at AS alert_time, 
                       eq.magnitude, el.intensity, e.level, e.region 
                FROM event e
                JOIN earthquake_location el ON e.location_eq_id = el.id
                JOIN earthquake eq ON el.earthquake_id = eq.id
                WHERE e.ack = FALSE
            """
            if suffix:
                sql += " AND e.id LIKE %s"
                cursor.execute(sql, [f"%{suffix}"])
            else:
                cursor.execute(sql)

            return cursor.fetchall()
    finally:
        conn.close()


def acknowledge_event_by_id(event_id: str) -> bool:
    """ report/acknowledge
    Acknowledge event by ID
    """
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            # 先檢查事件是否存在
            cursor.execute("SELECT id FROM event WHERE id = %s", (event_id,))
            if not cursor.fetchone():
                return False

            # 更新 ack 與 ack_time
            cursor.execute("""
                UPDATE event
                SET ack = TRUE, ack_time = %s
                WHERE id = %s
            """, (datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S"), event_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"[ERROR] Acknowledge event failed: {e}")
        return False
    finally:
        conn.close()

def fetch_acknowledged_events(location: str):
    """ report/acknowledged
    Fetch acknowledged events
    """
    suffix = location_suffix_map.get(location)
    if not suffix and location.lower() != "all":
        return {"message": "Invalid location"}

    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT e.id AS event_id, eq.earthquake_time, e.create_at AS alert_time, 
                       eq.magnitude, el.intensity, e.level, e.region, e.ack_time
                FROM event e
                JOIN earthquake_location el ON e.location_eq_id = el.id
                JOIN earthquake eq ON el.earthquake_id = eq.id
                WHERE e.ack = TRUE AND e.is_damage IS NULL
            """
            if suffix:
                sql += " AND e.id LIKE %s"
                cursor.execute(sql, [f"%{suffix}"])
            else:
                cursor.execute(sql)

            return cursor.fetchall()
    finally:
        conn.close()

def update_event_status(event_id: str, damage: bool, operation_active: bool):
    """ report/submit
    Update event status
    """
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            now = datetime.now(ZoneInfo("Asia/Taipei"))
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")

            if not damage:
                # 查 create_at 並計算處理時間（分鐘）
                cursor.execute(
                    "SELECT create_at FROM event WHERE id = %s", (event_id,))
                result = cursor.fetchone()
                print(result)
                if result:
                    create_at = result["create_at"]
                    create_at = create_at.replace(tzinfo=ZoneInfo("Asia/Taipei"))
                    process_minutes = int(
                        (now - create_at).total_seconds() // 60)

                sql = """
                    UPDATE event
                    SET is_damage = %s,
                        is_operation_active = %s,
                        report_at = %s,
                        is_done = TRUE,
                        closed_at = %s,
                        process_time = %s
                    WHERE id = %s
                """
                cursor.execute(sql, (damage, operation_active, now_str, now_str, process_minutes, event_id))
            else:
                sql = """
                    UPDATE event
                    SET is_damage = %s,
                        is_operation_active = %s,
                        report_at = %s
                    WHERE id = %s
                """
                cursor.execute(sql, (damage, operation_active, now_str, event_id))

            if cursor.rowcount == 0:
                return False

        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to update event status: {e}")
        return False
    finally:
        conn.close()

def fetch_in_process_events(location: str):
    """ report/in_process
    Fetch events where is_damage=True and is_done=False, with optional location filter
    """
    suffix = location_suffix_map.get(location)
    if not suffix and location.lower() != "all":
        return {"message": "Invalid location"}

    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT e.id AS event_id, eq.earthquake_time, e.create_at AS alert_time,
                       eq.magnitude, el.intensity, e.level, e.region, e.ack_time, e.is_operation_active
                FROM event e
                JOIN earthquake_location el ON e.location_eq_id = el.id
                JOIN earthquake eq ON el.earthquake_id = eq.id
                WHERE e.is_damage = TRUE AND e.is_done = FALSE
            """
            if suffix:
                sql += " AND e.id LIKE %s"
                cursor.execute(sql, [f"%{suffix}"])
            else:
                cursor.execute(sql)

            return cursor.fetchall()
    finally:
        conn.close()

def mark_event_as_repaired(event_id: str):
    """ report/repair
    Repair event by ID
    """
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            closed_at = datetime.now(ZoneInfo("Asia/Taipei"))
            closed_str = closed_at.strftime("%Y-%m-%d %H:%M:%S")

            # 更新 is_done 與 closed_at
            cursor.execute("""
                UPDATE event
                SET is_done = %s,
                    closed_at = %s
                WHERE id = %s
            """, (True, closed_str, event_id))

            # 查 create_at 並計算處理時間（分鐘）
            cursor.execute(
                "SELECT create_at FROM event WHERE id = %s", (event_id,))
            result = cursor.fetchone()
            print(result)
            if result:
                create_at = result["create_at"]
                create_at = create_at.replace(tzinfo=ZoneInfo("Asia/Taipei"))
                process_minutes = int(
                    (closed_at - create_at).total_seconds() // 60)

                cursor.execute(
                    "UPDATE event SET process_time = %s WHERE id = %s",
                    (process_minutes, event_id)
                )

        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to mark event as repaired: {e}")
        return False
    finally:
        conn.close()

def fetch_closed_events(location: str):
    """ report/closed
    Fetch closed events with optional location filter
    """
    suffix = location_suffix_map.get(location)
    if not suffix and location.lower() != "all":
        return {"message": "Invalid location"}

    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT e.id AS event_id, eq.earthquake_time, e.create_at AS alert_time,
                       eq.magnitude, el.intensity, e.level, e.region, 
                       e.ack_time, e.is_damage, e.is_operation_active, e.process_time
                FROM event e
                JOIN earthquake_location el ON e.location_eq_id = el.id
                JOIN earthquake eq ON el.earthquake_id = eq.id
                WHERE e.is_done = TRUE
            """
            if suffix:
                sql += " AND e.id LIKE %s"
                cursor.execute(sql, [f"%{suffix}"])
            else:
                cursor.execute(sql)

            rows = cursor.fetchall()
            for row in rows:
                if row["process_time"] == -1:
                    row["process_time"] = "未處理"
            return rows

    finally:
        conn.close()

def auto_close_unprocessed_events():
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            print('hi')
            # 台灣現在時間
            now = datetime.now(ZoneInfo("Asia/Taipei"))
            one_hour_ago = now - timedelta(hours=1)

            # 找出條件符合的 event
            sql_select = """
                SELECT id FROM event
                WHERE ack = TRUE
                  AND is_damage = TRUE
                  AND is_done = FALSE
                  AND create_at <= %s
            """
            cursor.execute(sql_select, (one_hour_ago.strftime("%Y-%m-%d %H:%M:%S"),))
            to_close = cursor.fetchall()
            
            for row in to_close:
                event_id = row['id']
                sql_update = """
                    UPDATE event
                    SET is_done = TRUE,
                        closed_at = %s,
                        process_time = %s
                    WHERE id = %s
                """
                cursor.execute(sql_update, (
                    now.strftime("%Y-%m-%d %H:%M:%S"),
                    -1,  # -1 表示未處理
                    event_id
                ))

        conn.commit()
        print(f"[INFO] Auto-closed {len(to_close)}")
        return len(to_close)
    except Exception as e:
        print(f"[ERROR] Failed to auto-close events: {e}")
        return 0
    finally:
        conn.close()

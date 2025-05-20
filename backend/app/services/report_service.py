from datetime import datetime, timedelta
import logging
from zoneinfo import ZoneInfo

from app.db import get_mysql_connection

logger = logging.getLogger(__name__)

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
        # TODO: indicate in return code
        return []

    conn = get_mysql_connection()
    if not conn:
        # TODO indicate in return code
        return []
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT e.id AS event_id, eq.earthquake_time, e.create_at AS alert_time, 
                       eq.magnitude, el.intensity, e.level, e.region 
                FROM event e
                JOIN earthquake_location el ON e.location_eq_id = el.id
                JOIN earthquake eq ON el.earthquake_id = eq.id
                WHERE e.ack = FALSE AND e.is_done = FALSE
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
    if not conn:
        return False
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
        logger.error("Acknowledge event failed")
        logger.exception(e)
        return False
    finally:
        conn.close()


def fetch_acknowledged_events(location: str):
    """ report/acknowledged
    Fetch acknowledged events
    """
    suffix = location_suffix_map.get(location)
    if not suffix and location.lower() != "all":
        # TODO: indicate in return code
        return []

    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT e.id AS event_id, eq.earthquake_time, e.create_at AS alert_time, 
                       eq.magnitude, el.intensity, e.level, e.region, e.ack_time
                FROM event e
                JOIN earthquake_location el ON e.location_eq_id = el.id
                JOIN earthquake eq ON el.earthquake_id = eq.id
                WHERE e.ack = TRUE AND e.is_damage IS NULL AND e.is_done = FALSE
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
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            now = datetime.now(ZoneInfo("Asia/Taipei"))
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")

            if not damage:
                # 查 create_at 並計算處理時間（分鐘）
                cursor.execute(
                    "SELECT create_at FROM event WHERE id = %s", (event_id,))
                result = cursor.fetchone()
                logger.debug(f"Fetching event {event_id} returns: {result}")
                if result:
                    create_at = result["create_at"]
                    create_at = create_at.replace(
                        tzinfo=ZoneInfo("Asia/Taipei"))
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
                cursor.execute(sql, (damage, operation_active,
                               now_str, now_str, process_minutes, event_id))
            else:
                sql = """
                    UPDATE event
                    SET is_damage = %s,
                        is_operation_active = %s,
                        report_at = %s
                    WHERE id = %s
                """
                cursor.execute(
                    sql, (damage, operation_active, now_str, event_id))

            if cursor.rowcount == 0:
                return False

        conn.commit()
        return True
    except Exception as e:
        logger.error("Failed to update event status")
        logger.exception(e)
        return False
    finally:
        conn.close()


def fetch_in_process_events(location: str):
    """ report/in_process
    Fetch events where is_damage=True and is_done=False, with optional location filter
    """
    suffix = location_suffix_map.get(location)
    if not suffix and location.lower() != "all":
        # TODO: indicate in return code
        return []

    conn = get_mysql_connection()
    if not conn:
        return []
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
    if not conn:
        return False
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
            logger.debug(f"Fetching event {event_id} returns: {result}")
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
        logger.error("Failed to mark event as repaired")
        logger.exception(e)
        return False
    finally:
        conn.close()


def fetch_closed_events(location: str):
    """ report/closed
    Fetch the 10 most recent closed events with optional location filter
    """
    suffix = location_suffix_map.get(location)
    if not suffix and location.lower() != "all":
        # TODO: indicate in return code
        return []

    if not conn:
        return []
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
            params: list[str] = []
            if suffix:
                sql += " AND e.id LIKE %s"
                params.append(f"%{suffix}")

            sql += " ORDER BY e.create_at DESC LIMIT 10"
            cursor.execute(sql, params)

            rows = cursor.fetchall()
            for row in rows:
                if row["process_time"] == -1:
                    row["process_time"] = "未處理"
            return rows

    finally:
        conn.close()


def auto_close_unprocessed_events():
    conn = get_mysql_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            # 台灣現在時間
            now = datetime.now(ZoneInfo("Asia/Taipei"))
            one_hour_ago = now - timedelta(minutes=1)

            # 條件 1
            sql1 = """
                SELECT id FROM event
                WHERE ack_time IS NULL
                  AND create_at <= %s
                  AND closed_at IS NULL
            """
            cursor.execute(sql1, (one_hour_ago.strftime("%Y-%m-%d %H:%M:%S"),))
            to_close_1 = cursor.fetchall()

            # 條件 2
            sql2 = """
                SELECT id FROM event
                WHERE report_at IS NULL
                  AND ack_time IS NOT NULL
                  AND ack_time <= %s
                  AND closed_at IS NULL
            """
            cursor.execute(sql2, (one_hour_ago.strftime("%Y-%m-%d %H:%M:%S"),))
            to_close_2 = cursor.fetchall()

            # 條件 3
            sql3 = """
                SELECT id FROM event
                WHERE report_at IS NOT NULL
                  AND report_at <= %s
                  AND closed_at IS NULL
            """
            cursor.execute(sql3, (one_hour_ago.strftime("%Y-%m-%d %H:%M:%S"),))
            to_close_3 = cursor.fetchall()

            to_close = list(to_close_1) + list(to_close_2) + list(to_close_3)
            logger.info(f"Auto-close events: {to_close}")

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
        logger.info(f"Auto-closed {len(to_close)} events successfully")
        return len(to_close)
    except Exception as e:
        logger.error("Failed to auto-close events")
        logger.exception(e)
        return 0
    finally:
        conn.close()

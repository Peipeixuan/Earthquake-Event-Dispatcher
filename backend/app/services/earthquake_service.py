from datetime import datetime, timedelta
import logging
from zoneinfo import ZoneInfo
from app.db import get_mysql_connection

logger = logging.getLogger(__name__)

location_suffix_map = {
    "臺北南港": "-tp",
    "新竹寶山": "-hc",
    "臺中大雅": "-tc",
    "臺南善化": "-tn"
}


def determine_level(intensity, magnitude):
    if intensity in ["3級", "4級", "5弱", "5強", "6弱", "6強", "7級"] or magnitude >= 5:
        return 'L2'
    elif intensity in ["1級", "2級"]:
        return 'L1'
    else:
        return 'NA'


def get_alert_suppress_time_from_db():
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT value FROM settings WHERE name = %s", ("alert_suppress_time",))
            result = cursor.fetchone()
            if result:
                return int(result["value"])
            return 30
    finally:
        conn.close()


def generate_simulated_earthquake_id(conn):
    """
    generate ID from 100,000,000
    """
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT MAX(id) as max_id FROM earthquake WHERE id >= 100000000
        """)
        result = cursor.fetchone()
        max_sim_id = result['max_id'] or 100000000
        return max_sim_id + 1


def process_earthquake_and_locations(req, alert_suppress_time=None):
    if alert_suppress_time is None:
        alert_suppress_time = get_alert_suppress_time_from_db()

    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                # === Insert earthquake ===
                eq = req.earthquake

                # generate id
                if eq.earthquake_id is None:
                    eq.earthquake_id = generate_simulated_earthquake_id(conn)

                eq_time_str = eq.earthquake_time.replace("T", " ")
                eq_time = datetime.strptime(
                    eq_time_str, "%Y-%m-%d %H:%M:%S")  # 轉成 datetime

                sql_insert_eq = """
                INSERT INTO earthquake (id, earthquake_time, center, latitude, longitude, magnitude, depth, is_demo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_insert_eq, (
                    eq.earthquake_id, eq_time_str, eq.center, eq.latitude, eq.longitude, eq.magnitude, eq.depth, eq.is_demo
                ))

                # === Insert earthquake_location ===
                sql_insert_loc = """
                INSERT INTO earthquake_location (earthquake_id, location, intensity)
                VALUES (%s, %s, %s)
                """
                location_ids = []

                for loc in req.locations:
                    cursor.execute(
                        sql_insert_loc, (eq.earthquake_id, loc.location, loc.intensity))
                    location_ids.append(
                        (loc.location, cursor.lastrowid, loc.intensity))

                # === Insert event for each location ===
                sql_insert_event = """
                INSERT INTO event (id, location_eq_id, create_at, region, level, trigger_alert, ack, is_damage, is_operation_active, is_done)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                for loc_name, location_eq_id, intensity in location_ids:
                    suffix = None
                    for keyword, sfx in location_suffix_map.items():
                        if keyword in loc_name:
                            suffix = sfx
                            break

                    if suffix:
                        event_id = f"{eq.earthquake_id}{suffix}"
                        level = determine_level(intensity, eq.magnitude)

                        alert_suppress_threshold = (
                            eq_time - timedelta(minutes=alert_suppress_time)).strftime("%Y-%m-%d %H:%M:%S")

                        level_order = {"L1": 1, "L2": 2}
                        this_level_score = level_order.get(level, 0)

                        # 查詢 suppress 時間內、同地區發出的警報等級
                        sql_check_alert = """
                        SELECT level FROM event
                        WHERE region = %s AND trigger_alert = 1
                        AND create_at BETWEEN %s AND %s
                        """
                        cursor.execute(
                            sql_check_alert, (loc_name, alert_suppress_threshold, eq_time_str))
                        past_levels = cursor.fetchall()

                        # 比較是否有等級 >= 本次的事件
                        suppress = any(level_order.get(
                            row["level"], 0) >= this_level_score for row in past_levels)

                        # 決定是否觸發
                        trigger_alert = 0
                        if level in ['L1', 'L2'] and not suppress:
                            trigger_alert = 1

                        # 插入 event
                        cursor.execute(sql_insert_event, (
                            event_id,
                            location_eq_id,
                            datetime.now(ZoneInfo("Asia/Taipei")
                                         ).strftime("%Y-%m-%d %H:%M:%S"),
                            loc_name,  # region 填入地點名稱
                            level,
                            trigger_alert,
                            False,  # ack
                            None,  # is_damage
                            None,  # is_operation_active
                            False   # is_done
                        ))

                conn.commit()
                return True

        except Exception as e:
            logger.exception(f"Failed to insert earthquake and events")
        finally:
            conn.close()
    return False


def fetch_all_simulated_earthquakes():
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            # 取出模擬地震
            cursor.execute("""
                SELECT * FROM earthquake
                WHERE is_demo = TRUE
                ORDER BY earthquake_time DESC
            """)
            earthquakes = cursor.fetchall()

            result = []
            for eq in earthquakes:
                cursor.execute("""
                    SELECT location, intensity
                    FROM earthquake_location
                    WHERE earthquake_id = %s
                """, (eq["id"],))
                locations = cursor.fetchall()

                result.append({
                    "earthquake": {
                        "earthquake_time": eq["earthquake_time"].strftime("%Y-%m-%dT%H:%M:%S"),
                        "center": eq["center"],
                        "latitude": eq["latitude"],
                        "longitude": eq["longitude"],
                        "magnitude": eq["magnitude"],
                        "depth": eq["depth"]
                    },
                    "locations": locations
                })

            return result
    finally:
        conn.close()

from datetime import datetime, timedelta
from app.db import get_mysql_connection

location_suffix_map = {
    "台北南港": "-tp",
    "新竹寶山": "-hc",
    "台中大雅": "-tc",
    "台南善化": "-tn"
}

def determine_level(magnitude_value, richter_scale):
    if magnitude_value >= 3 or richter_scale >= 5:
        return 'L2'
    elif magnitude_value >= 1:
        return 'L1'
    else:
        return 'NA'

def get_cooldown_minutes_from_db():
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT value FROM settings WHERE name = %s", ("cooldown_minutes",))
            result = cursor.fetchone()
            if result:
                return int(result["value"])
            return 30
    finally:
        conn.close()

def process_earthquake_and_locations(req, cooldown_minutes=None):
    if cooldown_minutes is None:
        cooldown_minutes = get_cooldown_minutes_from_db()
    
    print("cooldown_minutes", cooldown_minutes)

    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                # === Insert earthquake ===
                eq = req.earthquake
                origin_time_str = eq.origin_time
                origin_time = datetime.strptime(origin_time_str, "%Y-%m-%d %H:%M:%S")  # 轉成 datetime

                sql_insert_eq = """
                INSERT INTO earthquake (id, origin_time, location, latitude, longitude, richter_scale, focal_depth, is_demo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_insert_eq, (
                    eq.earthquake_id, origin_time_str, eq.location,
                    eq.latitude, eq.longitude, eq.richter_scale,
                    eq.focal_depth, eq.is_demo
                ))

                # === Insert earthquake_location ===
                sql_insert_loc = """
                INSERT INTO earthquake_location (earthquake_id, location, magnitude_value)
                VALUES (%s, %s, %s)
                """
                location_ids = []

                for loc in req.locations:
                    cursor.execute(sql_insert_loc, (eq.earthquake_id, loc.location, loc.magnitude_value))
                    location_ids.append((loc.location, cursor.lastrowid, loc.magnitude_value))

                # === Insert event for each location ===
                sql_insert_event = """
                INSERT INTO event (id, location_eq_id, create_at, region, level, trigger_alert, ack, is_damage, is_operation_active, is_done)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                for loc_name, location_eq_id, magnitude_value in location_ids:
                    suffix = None
                    for keyword, sfx in location_suffix_map.items():
                        if keyword in loc_name:
                            suffix = sfx
                            break

                    if suffix:
                        event_id = f"{eq.earthquake_id}{suffix}"
                        level = determine_level(magnitude_value, eq.richter_scale)

                        # cooldown 基準改用 origin_time
                        cooldown_threshold = (origin_time - timedelta(minutes=cooldown_minutes)).strftime("%Y-%m-%d %H:%M:%S")
                        
                        sql_check_alert = """
                        SELECT COUNT(*) as count FROM event
                        WHERE level = %s AND region = %s AND trigger_alert = 1 
                        AND create_at BETWEEN %s AND %s
                        """
                        cursor.execute(sql_check_alert, (level, loc_name, cooldown_threshold, origin_time_str))
                        result = cursor.fetchone()
                        existing_alert_count = result['count']

                        trigger_alert = 0
                        if level in ['L1', 'L2'] and existing_alert_count == 0:
                            trigger_alert = 1

                        # 插入 event
                        cursor.execute(sql_insert_event, (
                            event_id,
                            location_eq_id,
                            origin_time_str,
                            loc_name,  # region 填入地點名稱
                            level,
                            trigger_alert,
                            0,  # ack
                            0,  # is_damage
                            0,  # is_operation_active
                            0   # is_done
                        ))

                conn.commit()
                return True

        except Exception as e:
            print(f"[ERROR] Failed to insert earthquake and events: {e}")
        finally:
            conn.close()
    return False
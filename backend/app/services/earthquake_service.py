from datetime import datetime
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

def process_earthquake_and_locations(req):
    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                # === Insert earthquake ===
                eq = req.earthquake
                origin_time_str = eq.origin_time.replace("T", " ").replace("Z", "")

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
                location_ids = []  # 記錄下每一個 location_eq_id

                for loc in req.locations:
                    cursor.execute(sql_insert_loc, (eq.earthquake_id, loc.location, loc.magnitude_value))
                    location_ids.append((loc.location, cursor.lastrowid, loc.magnitude_value))  # 抓剛插入的 id

                # === Insert event for each location ===
                sql_insert_event = """
                INSERT INTO event (id, location_eq_id, create_at, region, level, trigger_alert, ack, is_damage, is_operation_active, is_done)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

                for loc_name, location_eq_id, magnitude_value in location_ids:
                    suffix = None
                    for keyword, sfx in location_suffix_map.items():
                        if keyword in loc_name:
                            suffix = sfx
                            break

                    if suffix:
                        event_id = f"{eq.earthquake_id}{suffix}"
                        level = determine_level(magnitude_value, eq.richter_scale)
                        trigger_alert = 1 if level in ['L1', 'L2'] else 0

                        cursor.execute(sql_insert_event, (
                            event_id,
                            location_eq_id,
                            now,
                            loc_name,            # region 暫時留空
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
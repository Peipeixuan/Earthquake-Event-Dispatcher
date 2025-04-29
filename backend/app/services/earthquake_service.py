from app.db import get_mysql_connection

def process_earthquake_and_locations(req):
    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                # Insert earthquake
                sql_insert_eq = """
                INSERT INTO earthquake (id, origin_time, location, latitude, longitude, richter_scale, focal_depth, is_demo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                eq = req.earthquake
                cursor.execute(sql_insert_eq, (
                    eq.earthquake_id, eq.origin_time, eq.location,
                    eq.latitude, eq.longitude, eq.richter_scale,
                    eq.focal_depth, eq.is_demo
                ))

                # Insert locations 地點資料
                sql_insert_loc = """
                INSERT INTO earthquake_location (earthquake_id, location, magnitude_value)
                VALUES (%s, %s, %s)
                """
                for loc in req.locations:
                    cursor.execute(sql_insert_loc, (eq.earthquake_id, loc.location, loc.magnitude_value))

                conn.commit()
                return True
        finally:
            conn.close()
    return False

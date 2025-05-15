import pymysql
import os


def get_mysql_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", ""),
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.OperationalError as e:
        print(f"MySQL connection error: {e}")
        return None

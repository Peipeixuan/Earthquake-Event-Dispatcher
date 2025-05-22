import logging
import os
import pymysql
from pymysql.err import OperationalError

logger = logging.getLogger(__name__)


def get_mysql_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST", ""),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", ""),
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute("SET time_zone = '+08:00'")
        
        return conn
    except OperationalError as e:
        logger.error("MySQL connection error")
        logger.exception(e)
        return None


def check_mysql_connection():
    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        finally:
            conn.close()
    return False

from datetime import datetime, timedelta
import json
from typing import Dict, List
from zoneinfo import ZoneInfo
from pydantic import BaseModel
import pymysql
import requests
import os

import logging

from db import get_mysql_connection

logger = logging.getLogger(__name__)

API_KEY = os.getenv('API_KEY')
if API_KEY == None:
    raise EnvironmentError('API_KEY not set')
# 顯著有感地震報告資料-顯著有感地震報告
URL = 'https://opendata.cwa.gov.tw/api//v1/rest/datastore/E-A0015-001'


class Earthquake(BaseModel):
    earthquake_id: int
    timestamp: str  # YYYY-MM-DD HH:MM:SS
    magnitude: float
    center: str
    depth: float
    longitude: float
    latitude: float
    intensity: Dict[str, float] = {}


def intensity_to_float(intensity: str) -> float:
    return {
        '0級': 0.0,
        '1級': 1.0,
        '2級': 2.0,
        '3級': 3.0,
        '4級': 4.0,
        '5弱': 5.0,
        '5強': 5.5,
        '6弱': 6.0,
        '6強': 6.5,
        '7級': 7.0,
    }[intensity]


def parse_earthquake(data) -> Earthquake:
    parsed_earthquake = Earthquake(
        earthquake_id=data['EarthquakeNo'],
        timestamp=data['EarthquakeInfo']['OriginTime'],
        magnitude=data['EarthquakeInfo']['EarthquakeMagnitude']['MagnitudeValue'],
        center=data['EarthquakeInfo']['Epicenter']['Location'],
        depth=data['EarthquakeInfo']['FocalDepth'],
        longitude=data['EarthquakeInfo']['Epicenter']['EpicenterLongitude'],
        latitude=data['EarthquakeInfo']['Epicenter']['EpicenterLatitude'],
    )

    areaNameMapper = {
        '臺北市': 'Taipei',
        '新竹市': 'Hsinchu',
        '臺中市': 'Taichung',
        '臺南市': 'Tainan',
    }

    # Initialize every area with level 0
    for area in areaNameMapper.keys():
        parsed_earthquake.intensity[areaNameMapper[area]] = intensity_to_float('0級')

    # Assign each found area
    for area in data['Intensity']['ShakingArea']:
        county_name = area['CountyName']
        if county_name in areaNameMapper.keys():
            parsed_earthquake.intensity[areaNameMapper[county_name]
                                        ] = intensity_to_float(area['AreaIntensity'])

    return parsed_earthquake


def crawl_new_earthquakes() -> List[Earthquake]:
    res = requests.get(URL, {
        'Authorization': API_KEY,
        'limit': 100,
    })

    if res.status_code != 200:
        logger.error('API error')
        exit(1)

    earthquakes = res.json()['records']['Earthquake']
    return list(map(parse_earthquake, earthquakes))


location_suffix_map = {
    "Taipei": "-tp",
    "Hsinchu": "-hc",
    "Taichung": "-tc",
    "Tainan": "-tn",
}


def determine_level(intensity: float, magnitude: float) -> str:
    if intensity >= 3 or magnitude >= 5:
        return 'L2'
    elif intensity >= 1:
        return 'L1'
    else:
        return 'NA'


def get_alert_suppress_time_from_db() -> int:
    conn = get_mysql_connection()
    if not conn:
        logger.error("Failed to connect to the database.")
        return 30
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


def insert_earthquake(eq: Earthquake, conn: pymysql.Connection, alert_suppress_time: int):
    with conn.cursor() as cursor:
        sql_check_eq = """
        SELECT id FROM earthquake WHERE id = %s
        """
        cursor.execute(sql_check_eq, (eq.earthquake_id))
        result = cursor.fetchone()
        if result:
            return False

        eq_time_str = eq.timestamp
        eq_time = datetime.strptime(
            eq_time_str, "%Y-%m-%d %H:%M:%S")

        sql_insert_eq = """
        INSERT INTO earthquake (id, earthquake_time, center, latitude, longitude, magnitude, depth, is_demo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert_eq, (
            eq.earthquake_id, eq_time_str, eq.center, eq.latitude, eq.longitude, eq.magnitude, eq.depth, False
        ))

        # === Insert earthquake_location ===
        sql_insert_loc = """
        INSERT INTO earthquake_location (earthquake_id, location, intensity)
        VALUES (%s, %s, %s)
        """
        location_ids = []

        for (loc, intensity) in eq.intensity.items():
            cursor.execute(
                sql_insert_loc, (eq.earthquake_id, loc, intensity))
            location_ids.append(
                (loc, cursor.lastrowid, intensity))

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
            else:
                raise ValueError(
                    'Location name not found in location_suffix_map')

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
    return False


def batch_insert_earthquake(data: List[Earthquake]):
    alert_suppress_time = get_alert_suppress_time_from_db()

    conn = get_mysql_connection()
    if not conn:
        logger.error("Failed to connect to the database.")
        return
    logger.info(f'Fetched {len(data)} earthquakes...')
    try:
        for eq in data:
            if insert_earthquake(eq, conn, alert_suppress_time):
                logger.info(
                    f"Inserted earthquake {eq.earthquake_id} successfully.")
        logger.info("All earthquakes inserted successfully.")
    except Exception as e:
        logger.exception(f"[ERROR] Failed to insert earthquake: {e}")
    finally:
        conn.close()


def update_new_data():
    data = crawl_new_earthquakes()
    batch_insert_earthquake(data)

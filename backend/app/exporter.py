from ast import parse
from calendar import c
import sched
from datetime import datetime
import threading
import time
from typing import Dict
from prometheus_client import Gauge
from pydantic import BaseModel

import logging

from app.db import get_mysql_connection

logger = logging.getLogger('uvicorn')

UPDATE_INTERVAL = 3

earthquake_time = Gauge(
    'earthquake_time', 'Unix timestamp of the last earthquake')
earthquake_scale = Gauge(
    'earthquake_scale', 'Magnitude of the last earthquake')
earthquake_depth = Gauge(
    'earthquake_depth', 'Depth of the last earthquake in km')
earthquake_longitude = Gauge(
    'earthquake_longitude', 'Longitude of the last earthquake')
earthquake_latitude = Gauge('earthquake_latitude',
                            'Latitude of the last earthquake')
earthquake_intensity = Gauge(
    'earthquake_intensity', 'Intensity of the last earthquake by location', ['location'])


def intensity_str_to_float(intensity: str):
    return {
        '0級': 0,
        '1級': 1,
        '2級': 2,
        '3級': 3,
        '4級': 4,
        '5弱': 5,
        '5強': 5.5,
        '6弱': 6,
        '6強': 6.5,
        '7級': 7,
    }[intensity]


class Earthquake(BaseModel):
    earthquake_id: int = 0
    timestamp: int = 0  # Unix timestamp
    scale: float = 0.0
    depth: float = 0.0
    longitude: float = 0.0
    latitude: float = 0.0
    intensity: Dict[str, float] = {}


last_earthquake = Earthquake()
my_scheduler = sched.scheduler(time.time, time.sleep)


def update_metric(data: Earthquake):
    earthquake_time.set(data.timestamp)
    earthquake_scale.set(data.scale)
    earthquake_depth.set(data.depth)
    earthquake_longitude.set(data.longitude)
    earthquake_latitude.set(data.latitude)

    for location in ["臺北南港", "新竹寶山", "臺中大雅", "臺南善化"]:
        earthquake_intensity.labels(location=location).set(
            data.intensity.get(location, '0'))


def parse_earthquake(result) -> Earthquake:
    parsed_earthquake = Earthquake(
        earthquake_id=result['id'],
        timestamp=int(result['earthquake_time'].timestamp()),
        scale=result['magnitude'],
        depth=result['depth'],
        longitude=result['longitude'],
        latitude=result['latitude'],
    )
    return parsed_earthquake


def update_new_data():
    conn = get_mysql_connection()
    if conn is None:
        logger.error('MySQL connection error')
        my_scheduler.enter(UPDATE_INTERVAL, 1, update_new_data)
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM earthquake ORDER BY earthquake_time DESC LIMIT 1")
            result = cursor.fetchone()

            if result:
                earthquake = parse_earthquake(result)

                for area in ["臺北南港", "新竹寶山", "臺中大雅", "臺南善化"]:
                    cursor.execute(
                        "SELECT intensity FROM earthquake_location WHERE earthquake_id = %s AND location = %s",
                        (earthquake.earthquake_id, area))
                    result = cursor.fetchone()
                    if result:
                        earthquake.intensity[area] = intensity_str_to_float(
                            result["intensity"])

                if earthquake.earthquake_id != last_earthquake.earthquake_id:
                    update_metric(earthquake)
    except Exception as e:
        logger.error(f"Error fetching last earthquake: {e}")
        return
    finally:
        conn.close()

    my_scheduler.enter(UPDATE_INTERVAL, 1, update_new_data)


def setup_scheduler():
    my_scheduler.enter(0, 1, update_new_data)
    my_scheduler.run()


def setup_exporter():
    update_metric(last_earthquake)

    thread = threading.Thread(target=setup_scheduler, daemon=True)
    thread.start()

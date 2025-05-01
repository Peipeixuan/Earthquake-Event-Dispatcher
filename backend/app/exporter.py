from dataclasses import dataclass, field
import sched
from datetime import datetime
import threading
import time
from typing import Dict
from prometheus_client import Gauge
import requests
import os

from dotenv import load_dotenv
load_dotenv()

# TODO: 10sec for production
UPDATE_INTERVAL = 10
API_KEY = os.getenv('API_KEY')
if API_KEY == None:
    raise EnvironmentError('API_KEY not set')
# 顯著有感地震報告資料-顯著有感地震報告
URL = 'https://opendata.cwa.gov.tw/api//v1/rest/datastore/E-A0015-001'

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


def intensity_to_int(intensity: str):
    return {
        '0級': 0,
        '1級': 1,
        '2級': 2,
        '3級': 3,
        '4級': 4,
        '5弱': 5,
        '5強': 5,
        '6弱': 6,
        '6強': 6,
        '7級': 7,
    }[intensity]


@dataclass
class Earthquake:
    earthquake_id: int = 0
    timestamp: int = field(
        default_factory=lambda: int(datetime.now().timestamp()))
    scale: float = 6.4
    depth: float = 30
    longitude: float = 122.4
    latitude: float = 22.5
    intensity: Dict[str, int] = field(
        default_factory=lambda: {
            'Taipei': 0,
            'Hsinchu': 0,
            'Taichung': 0,
            'Tainan': 0
        })


last_earthquake = Earthquake()
my_scheduler = sched.scheduler(time.time, time.sleep)


def update_metric(data: Earthquake):
    earthquake_time.set(data.timestamp)
    earthquake_scale.set(data.scale)
    earthquake_depth.set(data.depth)
    earthquake_longitude.set(data.longitude)
    earthquake_latitude.set(data.latitude)

    for location, intensity in data.intensity.items():
        earthquake_intensity.labels(location=location).set(intensity)


def parse_earthquake(data) -> Earthquake:
    parsed_earthquake = Earthquake(
        earthquake_id=data['EarthquakeNo'],
        timestamp=int(datetime.strptime(data['EarthquakeInfo']
                                        ['OriginTime'], '%Y-%m-%d %H:%M:%S').timestamp()),
        scale=data['EarthquakeInfo']['EarthquakeMagnitude']['MagnitudeValue'],
        depth=data['EarthquakeInfo']['FocalDepth'],
        longitude=data['EarthquakeInfo']['Epicenter']['EpicenterLongitude'],
        latitude=data['EarthquakeInfo']['Epicenter']['EpicenterLatitude'],
    )

    for area in data['Intensity']['ShakingArea']:
        areaNameMapper = {
            '臺北市': 'Taipei',
            '新竹市': 'Hsinchu',
            '臺中市': 'Taichung',
            '臺南市': 'Tainan'
        }
        for name, code in areaNameMapper.items():
            # TODO: refactor this when wake up
            if name in area['CountyName']:
                parsed_earthquake.intensity[code] = intensity_to_int(
                    area['AreaIntensity'])
    return parsed_earthquake


def crawl_new_earthquakes() -> Earthquake:
    res = requests.get(URL, {
        'Authorization': API_KEY,
        'limit': 1,
    })

    if res.status_code != 200:
        print('API error')
        exit(1)

    earthquakes = res.json()['records']['Earthquake']
    if len(earthquakes) == 0:
        return Earthquake()

    return parse_earthquake(earthquakes)


def update_new_data():
    data = crawl_new_earthquakes()

    # TODO: batch update
    if data.earthquake_id != last_earthquake.earthquake_id:
        update_metric(data)

    my_scheduler.enter(UPDATE_INTERVAL, 1, update_new_data)


def setup_scheduler():
    my_scheduler.enter(0, 1, update_new_data)
    my_scheduler.run()


def setup_exporter():
    update_metric(last_earthquake)

    thread = threading.Thread(target=setup_scheduler, daemon=True)
    thread.start()

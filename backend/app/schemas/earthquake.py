from pydantic import BaseModel
from typing import List

class EarthquakeIn(BaseModel):
    earthquake_id: int
    origin_time: str
    location: str
    latitude: float
    longitude: float
    richter_scale: float
    focal_depth: float
    is_demo: bool

class EarthquakeLocationIn(BaseModel):
    location: str
    magnitude_value: float

class EarthquakeIngestRequest(BaseModel):
    earthquake: EarthquakeIn
    locations: List[EarthquakeLocationIn]
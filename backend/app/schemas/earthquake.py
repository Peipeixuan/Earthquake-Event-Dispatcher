from pydantic import BaseModel
from typing import List

class EarthquakeIn(BaseModel):
    earthquake_id: int
    earthquake_time: str
    center: str
    latitude: str
    longitude: str
    magnitude: float
    depth: float
    is_demo: bool

class EarthquakeLocationIn(BaseModel):
    location: str
    intensity: str

class EarthquakeIngestRequest(BaseModel):
    earthquake: EarthquakeIn
    locations: List[EarthquakeLocationIn]
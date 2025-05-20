from typing import Optional
from pydantic import BaseModel
from typing import List


class EarthquakeIn(BaseModel):
    earthquake_id: Optional[int] = None
    earthquake_time: str
    center: str
    latitude: str
    longitude: str
    magnitude: float
    depth: float
    is_demo: bool


class EarthquakeLocationIn(BaseModel):
    location: str
    intensity: float


class EarthquakeIngestRequest(BaseModel):
    earthquake: EarthquakeIn
    locations: List[EarthquakeLocationIn]


class EarthquakeBaseOut(BaseModel):
    earthquake_time: str
    center: str
    latitude: str
    longitude: str
    magnitude: float
    depth: float


class EarthquakeLocationOut(BaseModel):
    location: str
    intensity: float


class EarthquakeSimulationOut(BaseModel):
    earthquake: EarthquakeBaseOut
    locations: List[EarthquakeLocationOut]

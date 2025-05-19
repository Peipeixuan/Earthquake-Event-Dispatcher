from fastapi import APIRouter
from typing import List
from app.schemas.earthquake import EarthquakeIngestRequest, EarthquakeSimulationOut
from app.services.earthquake_service import process_earthquake_and_locations, fetch_all_simulated_earthquakes

router = APIRouter(
    prefix="/earthquake",
    tags=["Earthquake"]
)


@router.post("/simulate")
def ingest_earthquake(req: EarthquakeIngestRequest):
    success = process_earthquake_and_locations(req)
    if success:
        return {"message": "Earthquake and locations ingested successfully"}
    else:
        return {"message": "Error occurred"}, 500


@router.get("/simulation", response_model=List[EarthquakeSimulationOut])
def get_simulated_earthquakes():
    return fetch_all_simulated_earthquakes()

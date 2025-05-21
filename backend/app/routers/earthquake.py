from fastapi import APIRouter, HTTPException
from typing import List

from fastapi.responses import JSONResponse
from app.schemas.earthquake import EarthquakeIngestRequest, EarthquakeSimulationOut
from app.services.earthquake_service import process_earthquake_and_locations, fetch_all_simulated_earthquakes

router = APIRouter(
    prefix="/earthquake",
    tags=["Earthquake"]
)


@router.post("/simulate")
def ingest_earthquake(req: EarthquakeIngestRequest):
    success = process_earthquake_and_locations(req)
    
    if success == 400:
        raise HTTPException(status_code=400, detail="Cannot simulate earthquake earlier than 1 hour ago")
    if success == 500:
        raise HTTPException(status_code=500, detail="Error occurred")
    if success:
        return {"message": "Earthquake and locations ingested successfully"}
    else:
        return JSONResponse(
            status_code=500,
            content={"message": "Error occurred"}
        )


@router.get("/simulation", response_model=List[EarthquakeSimulationOut])
def get_simulated_earthquakes():
    results = fetch_all_simulated_earthquakes()

    if results == 500:
        raise HTTPException(status_code=500, detail="Error occurred")

    return results

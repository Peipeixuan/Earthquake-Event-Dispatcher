from fastapi import APIRouter
from app.schemas.earthquake import EarthquakeIngestRequest
from app.services.earthquake_service import process_earthquake_and_locations

router = APIRouter(
    prefix="/earthquake",
    tags=["Earthquake"]
)

@router.post("/ingest")
def ingest_earthquake(req: EarthquakeIngestRequest):
    success = process_earthquake_and_locations(req)
    if success:
        return {"message": "Earthquake and locations ingested successfully"}
    else:
        return {"message": "Error occurred"}, 500
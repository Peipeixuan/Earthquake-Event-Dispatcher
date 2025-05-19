from fastapi import APIRouter, Query, HTTPException
from app.schemas.report import AcknowledgeRequest, SubmitReportRequest, RepairEventRequest
from app.services.report_service import fetch_unacknowledged_events, acknowledge_event_by_id, fetch_acknowledged_events, update_event_status, fetch_in_process_events, mark_event_as_repaired, fetch_closed_events

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/unacknowledged")
def get_unacknowledged_events(location: str = Query(..., description="Taipei / Hsinchu / Taichung / Tainan / all")):
    return fetch_unacknowledged_events(location)


@router.post("/acknowledge")
def acknowledge_event(payload: AcknowledgeRequest):
    success = acknowledge_event_by_id(payload.event_id)
    if success:
        return {"message": f"Event {payload.event_id} acknowledged successfully"}
    raise HTTPException(status_code=404, detail="Event not found")


@router.get("/pending")
def get_acknowledged_events(location: str = Query(..., description="Taipei / Hsinchu / Taichung / Tainan / all")):
    return fetch_acknowledged_events(location)


@router.post("/submit")
def submit_report(request: SubmitReportRequest):
    success = update_event_status(
        request.event_id, request.damage, request.operation_active)
    if success:
        return {"message": "Event status updated"}
    raise HTTPException(status_code=404, detail="Event not found")


@router.get("/in_process")
def get_in_process_events(location: str = Query(..., description="Taipei / Hsinchu / Taichung / Tainan / all")):
    return fetch_in_process_events(location)


@router.post("/repair")
def repair_event(request: RepairEventRequest):
    success = mark_event_as_repaired(request.event_id)
    if success:
        return {"message": "Event marked as repaired"}
    raise HTTPException(status_code=404, detail="Event not found")


@router.get("/closed")
def get_closed_events(location: str = Query(..., description="Taipei / Hsinchu / Taichung / Tainan / all")):
    return fetch_closed_events(location)

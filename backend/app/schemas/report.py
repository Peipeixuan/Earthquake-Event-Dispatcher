from pydantic import BaseModel


class AcknowledgeRequest(BaseModel):
    event_id: str


class SubmitReportRequest(BaseModel):
    event_id: str
    damage: bool
    operation_active: bool


class RepairEventRequest(BaseModel):
    event_id: str

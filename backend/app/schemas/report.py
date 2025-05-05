from pydantic import BaseModel

# report/acknowledge
class AcknowledgeRequest(BaseModel):
    event_id: str

# report/submit
class SubmitReportRequest(BaseModel):
    event_id: str
    damage: bool
    operation_active: bool

# report/repair
class RepairEventRequest(BaseModel):
    event_id: str
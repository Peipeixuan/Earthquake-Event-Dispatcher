from pydantic import BaseModel


class AcknowledgeRequest(BaseModel):
    """ report/acknowledge
    """
    event_id: str


class SubmitReportRequest(BaseModel):
    """ report/submit
    """
    event_id: str
    damage: bool
    operation_active: bool


class RepairEventRequest(BaseModel):
    """ report/repair
    """
    event_id: str

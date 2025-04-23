from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RoleBase(BaseModel):
    role_name: str


class RoleResponse(RoleBase):
    role_id: int

    class Config:
        from_attributes = True


class CountyBase(BaseModel):
    county_name: str
    county_code: str


class CountyResponse(CountyBase):
    county_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    password: str
    county_id: int
    role_id: int


class UserResponse(UserBase):
    user_id: int

    class Config:
        from_attributes = True


class EarthquakeBase(BaseModel):
    origin_time: datetime
    report_content: str
    focal_depth: float
    location: str
    epicenter_latitude: float
    epicenter_longitude: float
    magnitude_type: str
    magnitude_value: str
    is_demo: bool


class EarthquakeResponse(EarthquakeBase):
    earthquake_no: int

    class Config:
        from_attributes = True


class EarthquakeEventBase(BaseModel):
    earthquake_no: int
    county_id: int
    area_intensity: float
    event_severity: str
    alert: bool
    alert_start_time: datetime | None
    is_damage: bool
    is_operations_center_active: bool
    status: str
    last_update: datetime


class EarthquakeEventResponse(EarthquakeEventBase):
    event_id: str

    class Config:
        from_attributes = True


class PendingResponseUpdate(BaseModel):
    is_damage: bool
    is_operations_center_active: bool


class InProgressUpdate(BaseModel):
    is_damage: bool
    is_operations_center_active: bool

class DemoEarthquakeEvent(BaseModel):
    county_id: int
    area_intensity: float
    alert: Optional[bool] = True
    is_damage: Optional[bool] = False
    is_operations_center_active: Optional[bool] = False
    status: Optional[str] = "unacknowledged"
    alert_start_time: Optional[datetime] = None


class DemoEarthquakeRequest(BaseModel):
    earthquake_no: int
    report_content: str
    origin_time: datetime
    focal_depth: float
    location: str
    epicenter_latitude: float
    epicenter_longitude: float
    magnitude_type: str
    magnitude_value: float
    events: List[DemoEarthquakeEvent]

class UpdateAlertRequest(BaseModel):
    alert: bool
import asyncio
from datetime import datetime

import httpx
from backend import database, models, schemas
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

# Define the API URL
API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization=CWA-0D5559F3-F35F-4B30-8A11-B532CA021040&limit=1&AreaName=%E8%87%BA%E5%8C%97%E5%B8%82,%E8%87%BA%E4%B8%AD%E5%B8%82,%E8%87%BA%E5%8D%97%E5%B8%82,%E6%96%B0%E7%AB%B9%E5%B8%82"

# Define the target counties for earthquake events
TARGET_COUNTIES = ["臺北市", "新竹市", "臺中市", "臺南市"]

# Initialize the database
models.Base.metadata.create_all(bind=database.engine)


# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_event_severity(magnitude_value: float, area_intensity: float) -> str:
    if magnitude_value < 1:
        return "NA"
    elif magnitude_value >= 5 or area_intensity >= 3:
        return "L2"
    elif magnitude_value >= 1:
        return "L1"
    return "NA"

# Background task to fetch and process earthquake data
async def fetch_and_process_earthquake_data():
    while True:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL)
            if response.status_code == 200:
                data = response.json()
                process_earthquake_data(data)
        await asyncio.sleep(60)  # Wait for 1 minute before fetching again


# Define the lifespan context
async def lifespan(app: FastAPI):
    db = next(get_db())
    create_default_roles(db)
    create_default_counties(db)
    asyncio.create_task(fetch_and_process_earthquake_data())
    yield  # This is required to indicate the lifespan context
    # Add any cleanup logic here if needed


# Create the FastAPI app with the lifespan context
app = FastAPI(lifespan=lifespan)


def create_default_roles(db: Session):
    default_roles = [
        {"role_id": 1, "role_name": "主管"},
        {"role_id": 2, "role_name": "中控人員"},
        {"role_id": 3, "role_name": "一線人員"},
    ]
    for role in default_roles:
        existing_role = (
            db.query(models.Role).filter(models.Role.role_id == role["role_id"]).first()
        )
        if not existing_role:
            db_role = models.Role(role_id=role["role_id"], role_name=role["role_name"])
            db.add(db_role)
    db.commit()


def create_default_counties(db: Session):
    default_counties = [
        {"county_id": 1, "county_name": "臺北市", "county_code": "tp"},
        {"county_id": 2, "county_name": "新竹市", "county_code": "hc"},
        {"county_id": 3, "county_name": "臺中市", "county_code": "tc"},
        {"county_id": 4, "county_name": "臺南市", "county_code": "tn"},
    ]
    for county in default_counties:
        existing_county = (
            db.query(models.County)
            .filter(models.County.county_id == county["county_id"])
            .first()
        )
        if not existing_county:
            db_county = models.County(
                county_id=county["county_id"],
                county_name=county["county_name"],
                county_code=county["county_code"],
            )
            db.add(db_county)
    db.commit()


# Background task to fetch and process earthquake data
def process_earthquake_data(data: dict):
    db = next(get_db())
    try:
        # Extract earthquake data
        earthquakes = data.get("records", {}).get("Earthquake", [])
        for eq in earthquakes:
            earthquake_no = eq["EarthquakeNo"]
            report_content = eq["ReportContent"]
            origin_time = datetime.strptime(
                eq["EarthquakeInfo"]["OriginTime"], "%Y-%m-%d %H:%M:%S"
            )  # Convert to datetime
            focal_depth = eq["EarthquakeInfo"]["FocalDepth"]
            location = eq["EarthquakeInfo"]["Epicenter"]["Location"]
            epicenter_latitude = eq["EarthquakeInfo"]["Epicenter"]["EpicenterLatitude"]
            epicenter_longitude = eq["EarthquakeInfo"]["Epicenter"][
                "EpicenterLongitude"
            ]
            magnitude_type = eq["EarthquakeInfo"]["EarthquakeMagnitude"][
                "MagnitudeType"
            ]
            magnitude_value = eq["EarthquakeInfo"]["EarthquakeMagnitude"][
                "MagnitudeValue"
            ]

            # Check if the earthquake already exists
            db_earthquake = (
                db.query(models.Earthquake)
                .filter(models.Earthquake.earthquake_no == earthquake_no)
                .first()
            )
            if db_earthquake:
                # Update existing earthquake
                db_earthquake.report_content = report_content
                db_earthquake.origin_time = origin_time
                db_earthquake.focal_depth = focal_depth
                db_earthquake.location = location
                db_earthquake.epicenter_latitude = epicenter_latitude
                db_earthquake.epicenter_longitude = epicenter_longitude
                db_earthquake.magnitude_type = magnitude_type
                db_earthquake.magnitude_value = magnitude_value
            else:
                # Create a new earthquake record
                db_earthquake = models.Earthquake(
                    earthquake_no=earthquake_no,
                    report_content=report_content,
                    origin_time=origin_time,
                    focal_depth=focal_depth,
                    location=location,
                    epicenter_latitude=epicenter_latitude,
                    epicenter_longitude=epicenter_longitude,
                    magnitude_type=magnitude_type,
                    magnitude_value=magnitude_value,
                )
                db.add(db_earthquake)

            db.commit()
            db.refresh(db_earthquake)

            # Process earthquake events for target counties
            intensity_data = eq.get("Intensity", {}).get("ShakingArea", [])
            for area in intensity_data:
                county_name = area["CountyName"]
                if county_name in TARGET_COUNTIES:
                    area_intensity = float(area["AreaIntensity"].replace("級", ""))  # Convert intensity to float
                    county = (
                        db.query(models.County)
                        .filter(models.County.county_name == county_name)
                        .first()
                    )
                    if not county:
                        continue  # Skip if the county is not found

                    event_id = f"{earthquake_no}-{county.county_code}"  # Use county_code instead of county_name

                    # Calculate event_severity
                    event_severity = calculate_event_severity(magnitude_value, area_intensity)

                    # Check if the earthquake event already exists
                    db_event = (
                        db.query(models.EarthquakeEvent)
                        .filter(models.EarthquakeEvent.event_id == event_id)
                        .first()
                    )
                    if db_event:
                        # Update existing earthquake event
                        db_event.area_intensity = area_intensity
                        db_event.event_severity = event_severity
                        db_event.last_update = datetime.utcnow()
                    else:
                        # Create a new earthquake event
                        db_event = models.EarthquakeEvent(
                            event_id=event_id,
                            earthquake_no=earthquake_no,
                            county_id=county.county_id,
                            area_intensity=area_intensity,
                            event_severity=event_severity,  # Set calculated event_severity
                            alert=True,  # Default to True
                            is_damage=False,  # Default to False
                            is_operations_center_active=False,  # Default to False
                            status="unacknowledged",
                            alert_start_time=datetime.utcnow(),
                            last_update=datetime.utcnow(),
                        )
                        db.add(db_event)

                    db.commit()
                    db.refresh(db_event)
    finally:
        db.close()


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")


@app.get("/roles/", response_model=list[schemas.RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(models.Role).all()
    return roles


@app.post("/roles/", response_model=schemas.RoleResponse)
def create_role(role: schemas.RoleBase, db: Session = Depends(get_db)):
    db_role = models.Role(role_name=role.role_name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


@app.get("/roles/{role_id}", response_model=schemas.RoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(models.Role).filter(models.Role.role_id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@app.put("/roles/{role_id}", response_model=schemas.RoleResponse)
def update_role(role_id: int, role: schemas.RoleBase, db: Session = Depends(get_db)):
    db_role = db.query(models.Role).filter(models.Role.role_id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    db_role.role_name = role.role_name
    db.commit()
    db.refresh(db_role)
    return db_role


@app.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    db_role = db.query(models.Role).filter(models.Role.role_id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(db_role)
    db.commit()
    return {"message": "Role deleted successfully"}


@app.post("/counties/", response_model=schemas.CountyResponse)
def create_county(county: schemas.CountyBase, db: Session = Depends(get_db)):
    db_county = models.County(
        county_name=county.county_name, county_code=county.county_code
    )
    db.add(db_county)
    db.commit()
    db.refresh(db_county)
    return db_county


@app.get("/counties/", response_model=list[schemas.CountyResponse])
def get_counties(db: Session = Depends(get_db)):
    counties = db.query(models.County).all()
    return counties


@app.get("/counties/{county_id}", response_model=schemas.CountyResponse)
def get_county(county_id: int, db: Session = Depends(get_db)):
    county = (
        db.query(models.County).filter(models.County.county_id == county_id).first()
    )
    if not county:
        raise HTTPException(status_code=404, detail="County not found")
    return county


@app.put("/counties/{county_id}", response_model=schemas.CountyResponse)
def update_county(
    county_id: int, county: schemas.CountyBase, db: Session = Depends(get_db)
):
    db_county = (
        db.query(models.County).filter(models.County.county_id == county_id).first()
    )
    if not db_county:
        raise HTTPException(status_code=404, detail="County not found")
    db_county.county_name = county.county_name
    db_county.county_code = county.county_code
    db.commit()
    db.refresh(db_county)
    return db_county


@app.delete("/counties/{county_id}")
def delete_county(county_id: int, db: Session = Depends(get_db)):
    db_county = (
        db.query(models.County).filter(models.County.county_id == county_id).first()
    )
    if not db_county:
        raise HTTPException(status_code=404, detail="County not found")
    db.delete(db_county)
    db.commit()
    return {"message": "County deleted successfully"}


@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = models.User(
        username=user.username,
        password=user.password,
        county_id=user.county_id,
        role_id=user.role_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user.username
    db_user.password = user.password
    db_user.county_id = user.county_id
    db_user.role_id = user.role_id
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}


@app.get("/earthquakes/", response_model=list[schemas.EarthquakeResponse])
def get_earthquakes(db: Session = Depends(get_db)):
    earthquakes = db.query(models.Earthquake).all()
    return earthquakes


@app.post("/earthquakes/", response_model=schemas.EarthquakeResponse)
def create_earthquake(
    earthquake: schemas.EarthquakeBase, db: Session = Depends(get_db)
):
    db_earthquake = models.Earthquake(**earthquake.dict())
    db.add(db_earthquake)
    db.commit()
    db.refresh(db_earthquake)
    return db_earthquake


@app.get("/earthquakes/{earthquake_no}", response_model=schemas.EarthquakeResponse)
def get_earthquake(earthquake_no: int, db: Session = Depends(get_db)):
    earthquake = (
        db.query(models.Earthquake)
        .filter(models.Earthquake.earthquake_no == earthquake_no)
        .first()
    )
    if not earthquake:
        raise HTTPException(status_code=404, detail="Earthquake not found")
    return earthquake


@app.put("/earthquakes/{earthquake_no}", response_model=schemas.EarthquakeResponse)
def update_earthquake(
    earthquake_no: int,
    earthquake: schemas.EarthquakeBase,
    db: Session = Depends(get_db),
):
    db_earthquake = (
        db.query(models.Earthquake)
        .filter(models.Earthquake.earthquake_no == earthquake_no)
        .first()
    )
    if not db_earthquake:
        raise HTTPException(status_code=404, detail="Earthquake not found")

    # Update the earthquake fields
    for key, value in earthquake.dict().items():
        setattr(db_earthquake, key, value)

    db.commit()
    db.refresh(db_earthquake)

    # Update related earthquake events' area_intensity
    related_events = (
        db.query(models.EarthquakeEvent)
        .filter(models.EarthquakeEvent.earthquake_no == earthquake_no)
        .all()
    )
    for event in related_events:
        event.area_intensity = earthquake.area_intensity  # Update area_intensity
        event.last_update = datetime.utcnow()  # Update the last_update timestamp
        db.commit()
        db.refresh(event)

    return db_earthquake


@app.delete("/earthquakes/{earthquake_no}")
def delete_earthquake(earthquake_no: int, db: Session = Depends(get_db)):
    db_earthquake = (
        db.query(models.Earthquake)
        .filter(models.Earthquake.earthquake_no == earthquake_no)
        .first()
    )
    if not db_earthquake:
        raise HTTPException(status_code=404, detail="Earthquake not found")
    db.delete(db_earthquake)
    db.commit()
    return {"message": "Earthquake deleted successfully"}


@app.get("/earthquake_events/", response_model=list[schemas.EarthquakeEventResponse])
def get_earthquake_events(db: Session = Depends(get_db)):
    events = db.query(models.EarthquakeEvent).all()
    return events


@app.post("/earthquake_events/", response_model=schemas.EarthquakeEventResponse)
def create_earthquake_event(
    event: schemas.EarthquakeEventBase, db: Session = Depends(get_db)
):
    county = (
        db.query(models.County)
        .filter(models.County.county_id == event.county_id)
        .first()
    )
    if not county:
        raise HTTPException(status_code=404, detail="County not found")

    # Generate event_id using county_code
    event_id = f"{event.earthquake_no}-{county.county_code}"

    # Calculate event_severity
    event_severity = calculate_event_severity(event.magnitude_value, event.area_intensity)

    # Set default values for fields if not provided
    current_time = datetime.utcnow()  # Use UTC time for consistency
    db_event = models.EarthquakeEvent(
        event_id=event_id,
        earthquake_no=event.earthquake_no,
        county_id=event.county_id,
        area_intensity=event.area_intensity,
        event_severity=event_severity,  # Set calculated event_severity
        alert=event.alert if event.alert is not None else True,  # Default to True
        is_damage=event.is_damage if event.is_damage is not None else False,  # Default to False
        is_operations_center_active=event.is_operations_center_active if event.is_operations_center_active is not None else False,  # Default to False
        status="unacknowledged",
        alert_start_time=event.alert_start_time or current_time,  # Default to current time
        last_update=event.last_update or current_time,  # Default to current time
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.get(
    "/earthquake_events/{event_id}", response_model=schemas.EarthquakeEventResponse
)
def get_earthquake_event(event_id: str, db: Session = Depends(get_db)):
    event = (
        db.query(models.EarthquakeEvent)
        .filter(models.EarthquakeEvent.event_id == event_id)
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="Earthquake event not found")
    return event


@app.put(
    "/earthquake_events/{event_id}", response_model=schemas.EarthquakeEventResponse
)
def update_earthquake_event(
    event_id: str, event: schemas.EarthquakeEventBase, db: Session = Depends(get_db)
):
    db_event = (
        db.query(models.EarthquakeEvent)
        .filter(models.EarthquakeEvent.event_id == event_id)
        .first()
    )
    if not db_event:
        raise HTTPException(status_code=404, detail="Earthquake event not found")

    # Update fields
    for key, value in event.dict().items():
        setattr(db_event, key, value)

    # Recalculate event_severity
    db_event.event_severity = calculate_event_severity(
        event.magnitude_value, event.area_intensity
    )
    db_event.last_update = datetime.utcnow()

    db.commit()
    db.refresh(db_event)
    return db_event


@app.delete("/earthquake_events/{event_id}")
def delete_earthquake_event(event_id: str, db: Session = Depends(get_db)):
    db_event = (
        db.query(models.EarthquakeEvent)
        .filter(models.EarthquakeEvent.event_id == event_id)
        .first()
    )
    if not db_event:
        raise HTTPException(status_code=404, detail="Earthquake event not found")
    db.delete(db_event)
    db.commit()
    return {"message": "Earthquake event deleted successfully"}


@app.get("/events/unacknowledged", response_model=list[schemas.EarthquakeEventResponse])
def get_unacknowledged_events(db: Session = Depends(get_db)):
    events = (
        db.query(models.EarthquakeEvent)
        .filter(models.EarthquakeEvent.status == "unacknowledged")
        .all()
    )
    return events


@app.put(
    "/events/unacknowledged/{event_id}", response_model=schemas.EarthquakeEventResponse
)
def update_unacknowledged_event(event_id: str, db: Session = Depends(get_db)):
    event = (
        db.query(models.EarthquakeEvent)
        .filter(models.EarthquakeEvent.event_id == event_id)
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status != "unacknowledged":
        raise HTTPException(
            status_code=400, detail="Event is not in 'unacknowledged' status"
        )

    event.status = "pending_response"
    event.last_update = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return event


@app.get(
    "/events/pending_response", response_model=list[schemas.EarthquakeEventResponse]
)
def get_pending_response_events(db: Session = Depends(get_db)):
    events = (
        db.query(models.EarthquakeEvent)
        .filter(models.EarthquakeEvent.status == "pending_response")
        .all()
    )
    return events


@app.put(
    "/events/pending_response/{event_id}",
    response_model=schemas.EarthquakeEventResponse,
)
def update_pending_response_event(
    event_id: str,
    update_data: schemas.PendingResponseUpdate,
    db: Session = Depends(get_db),
):
    event = (
        db.query(models.EarthquakeEvent)
        .filter(models.EarthquakeEvent.event_id == event_id)
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status != "pending_response":
        raise HTTPException(
            status_code=400, detail="Event is not in 'pending_response' status"
        )

    event.is_damage = update_data.is_damage
    event.is_operations_center_active = update_data.is_operations_center_active
    event.status = "in_progress"
    event.last_update = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return event


@app.get("/events/in_progress", response_model=list[schemas.EarthquakeEventResponse])
def get_in_progress_events(db: Session = Depends(get_db)):
    events = (
        db.query(models.EarthquakeEvent)
        .filter(models.EarthquakeEvent.status == "in_progress")
        .all()
    )
    return events


@app.put(
    "/events/in_progress/{event_id}", response_model=schemas.EarthquakeEventResponse
)
def update_in_progress_event(
    event_id: str, update_data: schemas.InProgressUpdate, db: Session = Depends(get_db)
):
    event = (
        db.query(models.EarthquakeEvent)
        .filter(models.EarthquakeEvent.event_id == event_id)
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status != "in_progress":
        raise HTTPException(
            status_code=400, detail="Event is not in 'in_progress' status"
        )

    event.is_damage = update_data.is_damage
    event.is_operations_center_active = update_data.is_operations_center_active
    event.status = "closed"
    event.last_update = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return event


@app.get("/events/closed", response_model=list[schemas.EarthquakeEventResponse])
def get_closed_events(db: Session = Depends(get_db)):
    events = (
        db.query(models.EarthquakeEvent)
        .filter(models.EarthquakeEvent.status == "closed")
        .all()
    )
    return events

@app.post("/earthquakes/demo", response_model=schemas.EarthquakeResponse)
def create_demo_earthquake_with_events(
    earthquake_data: schemas.DemoEarthquakeRequest, db: Session = Depends(get_db)
):
    # Create the earthquake
    db_earthquake = models.Earthquake(
        earthquake_no=earthquake_data.earthquake_no,
        report_content=earthquake_data.report_content,
        origin_time=earthquake_data.origin_time,
        focal_depth=earthquake_data.focal_depth,
        location=earthquake_data.location,
        epicenter_latitude=earthquake_data.epicenter_latitude,
        epicenter_longitude=earthquake_data.epicenter_longitude,
        magnitude_type=earthquake_data.magnitude_type,
        magnitude_value=earthquake_data.magnitude_value,
        is_demo=True,  # Set is_demo to True
    )
    db.add(db_earthquake)
    db.commit()
    db.refresh(db_earthquake)

    # Create associated earthquake events
    for event_data in earthquake_data.events:
        county = (
            db.query(models.County)
            .filter(models.County.county_id == event_data.county_id)
            .first()
        )
        if not county:
            raise HTTPException(status_code=404, detail=f"County with ID {event_data.county_id} not found")

        # Generate event_id using earthquake_no and county_code
        event_id = f"{earthquake_data.earthquake_no}-{county.county_code}"

        # Calculate event_severity
        event_severity = calculate_event_severity(
            earthquake_data.magnitude_value, event_data.area_intensity
        )

        db_event = models.EarthquakeEvent(
            event_id=event_id,
            earthquake_no=earthquake_data.earthquake_no,
            county_id=event_data.county_id,
            area_intensity=event_data.area_intensity,
            event_severity=event_severity,
            alert=event_data.alert if event_data.alert is not None else True,
            is_damage=event_data.is_damage if event_data.is_damage is not None else False,
            is_operations_center_active=event_data.is_operations_center_active
            if event_data.is_operations_center_active is not None
            else False,
            status=event_data.status or "unacknowledged",
            alert_start_time=event_data.alert_start_time or datetime.utcnow(),
            last_update=datetime.utcnow(),
            is_demo=True,  # Set is_demo to True
        )
        db.add(db_event)

    db.commit()
    return db_earthquake

@app.put("/earthquake_events/{event_id}/alert", response_model=schemas.EarthquakeEventResponse)
def update_event_alert(event_id: str, alert_data: schemas.UpdateAlertRequest, db: Session = Depends(get_db)):
    # Fetch the event by event_id
    db_event = (
        db.query(models.EarthquakeEvent)
        .filter(models.EarthquakeEvent.event_id == event_id)
        .first()
    )
    if not db_event:
        raise HTTPException(status_code=404, detail="Earthquake event not found")

    # Update the alert field
    db_event.alert = alert_data.alert
    db_event.last_update = datetime.utcnow()  # Update the last_update timestamp

    db.commit()
    db.refresh(db_event)
    return db_event
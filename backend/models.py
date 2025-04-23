from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, nullable=False)


class County(Base):
    __tablename__ = "counties"

    county_id = Column(Integer, primary_key=True, index=True)
    county_name = Column(String, nullable=False)
    county_code = Column(String, nullable=False, unique=True)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    county_id = Column(Integer, ForeignKey("counties.county_id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    county = relationship("County", back_populates="users")
    role = relationship("Role", back_populates="users")


County.users = relationship("User", back_populates="county")
Role.users = relationship("User", back_populates="role")


class Earthquake(Base):
    __tablename__ = "earthquakes"

    earthquake_no = Column(Integer, primary_key=True, index=True)
    origin_time = Column(DateTime, nullable=False)
    report_content = Column(String, nullable=True)
    focal_depth = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    epicenter_latitude = Column(Float, nullable=False)
    epicenter_longitude = Column(Float, nullable=False)
    magnitude_type = Column(String, nullable=False)
    magnitude_value = Column(String, nullable=False)
    is_demo = Column(Boolean, default=False)


class EarthquakeEvent(Base):
    __tablename__ = "earthquake_events"

    event_id = Column(String, primary_key=True, index=True)  # earthquake_no + county_code
    earthquake_no = Column(Integer, ForeignKey("earthquakes.earthquake_no"), nullable=False)
    county_id = Column(Integer, ForeignKey("counties.county_id"), nullable=False)
    area_intensity = Column(Float, nullable=False)
    event_severity = Column(String, nullable=False)
    alert = Column(Boolean, default=False)
    alert_start_time = Column(DateTime, nullable=True)
    is_damage = Column(Boolean, default=False)
    is_operations_center_active = Column(Boolean, default=False)
    status = Column(String, nullable=False)
    last_update = Column(DateTime, default=func.now(), onupdate=func.now())

    county = relationship("County", back_populates="earthquake_events")
    earthquake = relationship("Earthquake", back_populates="earthquake_events")


County.earthquake_events = relationship("EarthquakeEvent", back_populates="county")
Earthquake.earthquake_events = relationship("EarthquakeEvent", back_populates="earthquake")
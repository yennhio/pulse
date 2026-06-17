from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class SiteCheck(Base):
    __tablename__ = "site_checks"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, nullable=False)
    is_up = Column(Boolean, nullable=False)
    response_time_ms = Column(Integer)
    status_code = Column(Integer)
    checked_at = Column(DateTime, server_default=func.now())
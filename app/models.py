from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base

# SQLAlchemy model — this is the actual database table
class NodeDB(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_operational = Column(Boolean, default=True)

# Pydantic model — this is for API validation
class NodeType(str):
    HOSPITAL = "hospital"
    POWER_STATION = "power_station"
    ROAD = "road"
    WATER_SUPPLY = "water_supply"
    COMMUNICATION_TOWER = "communication_tower"
    SHELTER = "shelter"

class Node(BaseModel):
    id: int
    name: str
    type: str
    latitude: float
    longitude: float
    is_operational: bool = True

    class Config:
        from_attributes = True
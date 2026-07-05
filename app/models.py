from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base

# SQLAlchemy model — nodes table
class NodeDB(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_operational = Column(Boolean, default=True)

# SQLAlchemy model — users table
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# SQLAlchemy model — edges table
class EdgeDB(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, index=True)
    from_node = Column(Integer, nullable=False)
    to_node = Column(Integer, nullable=False)
    weight = Column(Float, default=1.0)

# SQLAlchemy model — simulation history table
class SimulationHistoryDB(Base):
    __tablename__ = "simulation_history"

    id = Column(Integer, primary_key=True, index=True)
    disaster_type = Column(String, nullable=False)
    affected_node_ids = Column(String, nullable=False)
    failed_count = Column(Integer, nullable=False)
    operational_count = Column(Integer, nullable=False)
    timestamp = Column(String, nullable=False)

# Pydantic models — API validation
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

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class EdgeCreate(BaseModel):
    from_node: int
    to_node: int
    weight: float = 1.0

class Edge(BaseModel):
    id: int
    from_node: int
    to_node: int
    weight: float

    class Config:
        from_attributes = True
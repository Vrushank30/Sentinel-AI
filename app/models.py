from pydantic import BaseModel
from typing import Optional
class NodeType(str):
    HOSPITAL = "hospital"
    POWER_STATION = "power_station"
    ROAD = "road"
    WATER_SUPPLY = "water_supply"
    COMMUNICATION_TOWER = "communication_tower"
    SHELTER = "shelter"

class Node(BaseModel):
    id: int
    name:str
    type : str
    latitude: float
    longitude: float
    is_operational: bool=True
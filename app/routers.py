from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Node, NodeDB, UserDB, UserCreate, UserResponse, EdgeDB, EdgeCreate, Edge, SimulationHistoryDB
from app.database import get_db
from app.auth import hash_password, verify_password, create_access_token, verify_token
from app.simulation import build_city_graph, simulate_disaster
from typing import List
from datetime import datetime
from app.osm import get_all_infrastructure

router = APIRouter()

# --- Node endpoints ---

@router.post("/nodes", response_model=Node)
def create_node(node: Node, db: Session = Depends(get_db)):
    db_node = NodeDB(
        id=node.id,
        name=node.name,
        type=node.type,
        latitude=node.latitude,
        longitude=node.longitude,
        is_operational=node.is_operational
    )
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

@router.get("/nodes", response_model=List[Node])
def get_all_nodes(db: Session = Depends(get_db)):
    return db.query(NodeDB).all()

@router.get("/nodes/{node_id}", response_model=Node)
def get_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(NodeDB).filter(NodeDB.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@router.delete("/nodes/cleanup")
def cleanup_fake_nodes(db: Session = Depends(get_db)):
    fake_ids = [1, 2, 3, 4]
    for id in fake_ids:
        node = db.query(NodeDB).filter(NodeDB.id == id).first()
        if node:
            db.delete(node)
    db.commit()
    return {"message": "Fake nodes removed. Only real OSM data remains."}

# --- Edge endpoints ---

@router.post("/edges", response_model=Edge)
def create_edge(edge: EdgeCreate, db: Session = Depends(get_db)):
    db_edge = EdgeDB(
        from_node=edge.from_node,
        to_node=edge.to_node,
        weight=edge.weight
    )
    db.add(db_edge)
    db.commit()
    db.refresh(db_edge)
    return db_edge

@router.get("/edges", response_model=List[Edge])
def get_all_edges(db: Session = Depends(get_db)):
    return db.query(EdgeDB).all()

# --- Simulation endpoint ---

@router.post("/simulate")
def run_simulation(disaster: dict, db: Session = Depends(get_db), current_user: str = Depends(verify_token)):
    nodes = db.query(NodeDB).all()
    edges = db.query(EdgeDB).all()

    if not nodes:
        raise HTTPException(status_code=400, detail="No nodes found. Add nodes first.")

    edge_list = [{"from_node": e.from_node, "to_node": e.to_node} for e in edges]
    affected_node_ids = disaster.get("affected_node_ids", [])
    disaster_type = disaster.get("disaster_type", "unknown")

    G = build_city_graph(nodes, edge_list)
    result = simulate_disaster(G, affected_node_ids)

    history = SimulationHistoryDB(
        disaster_type=disaster_type,
        affected_node_ids=str(affected_node_ids),
        failed_count=result["failed_count"],
        operational_count=result["operational_count"],
        timestamp=datetime.utcnow().isoformat()
    )
    db.add(history)
    db.commit()

    return result

# --- Simulation history endpoint ---

@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    history = db.query(SimulationHistoryDB).order_by(SimulationHistoryDB.id.desc()).all()
    return history

# --- Auth endpoints ---

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = UserDB(
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

# --- OSM import endpoint ---

@router.post("/import-osm")
def import_osm_data(db: Session = Depends(get_db)):
    nodes = get_all_infrastructure("Bengaluru, India")

    if not nodes:
        raise HTTPException(status_code=404, detail="No data fetched from OpenStreetMap")

    added = 0
    for node in nodes:
        existing = db.query(NodeDB).filter(NodeDB.id == node["id"]).first()
        if not existing:
            db_node = NodeDB(
                id=node["id"],
                name=node["name"],
                type=node["type"],
                latitude=node["latitude"],
                longitude=node["longitude"],
                is_operational=True
            )
            db.add(db_node)
            added += 1

    db.commit()
    return {"message": f"Imported {added} real infrastructure nodes from OpenStreetMap"}
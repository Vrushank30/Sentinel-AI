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

@router.post("/auto-edges")
def auto_generate_edges(db: Session = Depends(get_db)):
    db.query(EdgeDB).delete()
    all_nodes = db.query(NodeDB).all()
    hospitals = [n for n in all_nodes if n.type == "hospital"]
    water = [n for n in all_nodes if n.type == "water_supply"]

    added = 0
    for h in hospitals:
        for w in water:
            db.add(EdgeDB(from_node=h.id, to_node=w.id, weight=1.0))
            added += 1

    for i in range(len(hospitals)):
        for j in range(i+1, min(i+3, len(hospitals))):
            db.add(EdgeDB(from_node=hospitals[i].id, to_node=hospitals[j].id, weight=0.8))
            added += 1

    db.commit()
    return {"message": f"Auto-generated {added} edges between real infrastructure nodes"}

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

    # Clear existing nodes and edges
    db.query(EdgeDB).delete()
    db.query(NodeDB).delete()
    db.commit()

    for node in nodes:
        db_node = NodeDB(
            id=node["id"],
            name=node["name"],
            type=node["type"],
            latitude=node["latitude"],
            longitude=node["longitude"],
            is_operational=True
        )
        db.add(db_node)
    db.commit()

    # Auto generate edges
    all_nodes = db.query(NodeDB).all()
    hospitals = [n for n in all_nodes if n.type == "hospital"]
    water = [n for n in all_nodes if n.type == "water_supply"]

    for h in hospitals:
        for w in water:
            db.add(EdgeDB(from_node=h.id, to_node=w.id, weight=1.0))

    for i in range(len(hospitals)):
        for j in range(i+1, min(i+3, len(hospitals))):
            db.add(EdgeDB(from_node=hospitals[i].id, to_node=hospitals[j].id, weight=0.8))

    db.commit()

    return {"message": f"Imported {len(nodes)} real nodes and auto-generated edges from OpenStreetMap"}
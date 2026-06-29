from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Node, NodeDB
from app.database import get_db
from typing import List

router = APIRouter()

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
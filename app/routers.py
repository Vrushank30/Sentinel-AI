from fastapi import APIRouter,HTTPException
from app.models import Node
from typing import List
router = APIRouter()
nodes_db: List[Node] = []
@router.post("/nodes", response_model=Node)
def create_node(node: Node):
    for existing_node in nodes_db:
        if existing_node.id == node.id:
            raise HTTPException(status_code=400, detail="Node with this ID already exists")
    nodes_db.append(node)
    return node
@router.get("/nodes",response_model = List[Node])
def get_all_nodes():
    return nodes_db
@router.get("/nodes/{node_id}", response_model=Node)
def get_node(node_id: int):
    for node in nodes_db:
        if node.id == node_id:
            return node
    raise HTTPException(status_code=404, detail="Node not found")

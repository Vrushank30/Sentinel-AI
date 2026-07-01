import networkx as nx
from typing import List, Dict

def build_city_graph(nodes: list, edges: list) -> nx.Graph:
    G = nx.Graph()
    
    for node in nodes:
        G.add_node(node.id, name=node.name, type=node.type, 
                   is_operational=node.is_operational)
    
    for edge in edges:
        G.add_edge(edge["from_node"], edge["to_node"])
    
    return G

def simulate_disaster(G: nx.Graph, affected_node_ids: List[int]) -> Dict:
    failed_nodes = set(affected_node_ids)
    
    for node_id in affected_node_ids:
        if node_id in G.nodes:
            neighbors = list(G.neighbors(node_id))
            for neighbor in neighbors:
                node_data = G.nodes[neighbor]
                if node_data.get("type") in ["hospital", "shelter"]:
                    failed_nodes.add(neighbor)
    
    operational_nodes = [
        {"id": n, **G.nodes[n]} 
        for n in G.nodes 
        if n not in failed_nodes
    ]
    
    failed_nodes_list = [
        {"id": n, **G.nodes[n]} 
        for n in G.nodes 
        if n in failed_nodes
    ]
    
    return {
        "failed_nodes": failed_nodes_list,
        "operational_nodes": operational_nodes,
        "total_nodes": len(G.nodes),
        "failed_count": len(failed_nodes_list),
        "operational_count": len(operational_nodes)
    }
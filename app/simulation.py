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

def simulate_disaster(G: nx.Graph, affected_node_ids: List[int], severity: int = 5) -> Dict:
    failed_nodes = set(affected_node_ids)
    
    cascade_depth = severity // 3
    
    current_wave = set(affected_node_ids)
    for _ in range(cascade_depth):
        next_wave = set()
        for node_id in current_wave:
            if node_id in G.nodes:
                neighbors = list(G.neighbors(node_id))
                for neighbor in neighbors:
                    node_data = G.nodes[neighbor]
                    if node_data.get("type") in ["hospital", "shelter", "water_supply"]:
                        next_wave.add(neighbor)
        failed_nodes.update(next_wave)
        current_wave = next_wave

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

    recovery_times = {
        "hospital": "6 hours",
        "power_station": "48 hours",
        "water_supply": "24 hours",
        "communication_tower": "12 hours",
        "road": "72 hours",
        "shelter": "3 hours"
    }

    for node in failed_nodes_list:
        node["recovery_time"] = recovery_times.get(node.get("type"), "24 hours")

    return {
        "failed_nodes": failed_nodes_list,
        "operational_nodes": operational_nodes,
        "total_nodes": len(G.nodes),
        "failed_count": len(failed_nodes_list),
        "operational_count": len(operational_nodes),
        "severity": severity,
        "cascade_depth": cascade_depth
    }
"""Routing Protocols Adapter: Dijkstra's Shortest Path & Distance Vector.

Simulates Network Layer routing across hospital clinical subnetworks:
- Hospital Topology Graph (Nodes: ICU, Cardiology, Radiology, Pharmacy, Emergency, Core, Server)
- Dijkstra's Algorithm (Link-State Shortest Path with path reconstruction)
- Distance Vector Routing (Bellman-Ford matrix exchange)
"""

import heapq
from typing import Dict, List, Tuple, Any, Optional

try:
    from modules.base_adapter import BaseProtocolAdapter, AdapterStatus
except (ImportError, ValueError):
    try:
        from .base_adapter import BaseProtocolAdapter, AdapterStatus
    except (ImportError, ValueError):
        from base_adapter import BaseProtocolAdapter, AdapterStatus

# Hospital network topology adjacency graph with link latencies (in milliseconds)
HOSPITAL_TOPOLOGY: Dict[str, Dict[str, float]] = {
    "ICU Ward": {
        "Core Router": 4.0,
        "Emergency Unit": 8.0
    },
    "Emergency Unit": {
        "ICU Ward": 8.0,
        "Core Router": 5.0,
        "Radiology": 7.0
    },
    "Cardiology": {
        "Core Router": 6.0,
        "Central Pharmacy": 9.0
    },
    "Radiology": {
        "Emergency Unit": 7.0,
        "Core Router": 10.0,
        "Central Server": 12.0
    },
    "Central Pharmacy": {
        "Cardiology": 9.0,
        "Core Router": 5.0,
        "Central Server": 6.0
    },
    "Core Router": {
        "ICU Ward": 4.0,
        "Emergency Unit": 5.0,
        "Cardiology": 6.0,
        "Radiology": 10.0,
        "Central Pharmacy": 5.0,
        "Central Server": 3.0
    },
    "Central Server": {
        "Core Router": 3.0,
        "Radiology": 12.0,
        "Central Pharmacy": 6.0
    }
}


class RoutingAdapter(BaseProtocolAdapter):
    """Adapter for hospital network routing algorithms."""

    def __init__(self):
        super().__init__(
            protocol_name="Routing Protocols (Dijkstra & Distance Vector)",
            candidate_modules=["routing.dijkstra", "modules.routing", "routing"]
        )
        self.topology = HOSPITAL_TOPOLOGY

    def get_nodes(self) -> List[str]:
        """Return list of all network nodes/departments."""
        return list(self.topology.keys())

    # -------------------------------------------------------------
    # Dijkstra's Shortest Path Algorithm
    # -------------------------------------------------------------
    def run_dijkstra(self, source: str, destination: str) -> Dict[str, Any]:
        """
        Compute shortest path from source to destination using Dijkstra's algorithm.
        Returns:
            Dict containing shortest path list, total latency cost, and node distance map.
        """
        if source not in self.topology or destination not in self.topology:
            return {
                "path": [source, destination],
                "total_cost_ms": 0.0,
                "error": "Source or destination not found in topology."
            }

        distances: Dict[str, float] = {node: float("inf") for node in self.topology}
        predecessors: Dict[str, Optional[str]] = {node: None for node in self.topology}
        distances[source] = 0.0

        # Priority queue stores (cost, node)
        pq: List[Tuple[float, str]] = [(0.0, source)]
        visited = set()
        relaxation_log = []

        while pq:
            curr_dist, curr_node = heapq.heappop(pq)
            if curr_node in visited:
                continue
            visited.add(curr_node)

            if curr_node == destination:
                break

            for neighbor, weight in self.topology[curr_node].items():
                if neighbor in visited:
                    continue
                new_dist = curr_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = curr_node
                    heapq.heappush(pq, (new_dist, neighbor))
                    relaxation_log.append(
                        f"Relaxed edge ({curr_node} -> {neighbor}): New dist = {new_dist:.1f} ms"
                    )

        # Reconstruct path
        path = []
        curr = destination
        while curr is not None:
            path.append(curr)
            curr = predecessors[curr]
        path.reverse()

        return {
            "source": source,
            "destination": destination,
            "path": path,
            "total_cost_ms": round(distances[destination], 2),
            "hop_count": max(len(path) - 1, 0),
            "relaxation_log": relaxation_log,
            "all_distances": {k: round(v, 2) for k, v in distances.items() if v != float("inf")}
        }

    # -------------------------------------------------------------
    # Distance Vector Routing (Bellman-Ford)
    # -------------------------------------------------------------
    def run_distance_vector(self) -> Dict[str, Dict[str, Tuple[float, str]]]:
        """
        Computes Distance Vector routing table for every node in hospital network.
        Returns:
            Dict mapping: node -> { destination: (cost, next_hop) }
        """
        nodes = list(self.topology.keys())
        # distance_table[u][v] = cost
        dist = {u: {v: float("inf") for v in nodes} for u in nodes}
        next_hop = {u: {v: v for v in nodes} for u in nodes}

        # Initialize direct link costs
        for u in nodes:
            dist[u][u] = 0.0
            for v, w in self.topology[u].items():
                dist[u][v] = w
                next_hop[u][v] = v

        # Bellman-Ford relaxation across network |V| - 1 iterations
        for _ in range(len(nodes) - 1):
            updated = False
            for u in nodes:
                for v in nodes:
                    for neighbor, w in self.topology[u].items():
                        if dist[neighbor][v] + w < dist[u][v]:
                            dist[u][v] = dist[neighbor][v] + w
                            next_hop[u][v] = neighbor
                            updated = True
            if not updated:
                break

        # Format clean output table
        routing_tables: Dict[str, List[Dict[str, Any]]] = {}
        for u in nodes:
            routing_tables[u] = []
            for v in nodes:
                cost = dist[u][v]
                nh = next_hop[u][v] if cost != float("inf") else "None"
                routing_tables[u].append({
                    "destination": v,
                    "cost_ms": round(cost, 1) if cost != float("inf") else 999.0,
                    "next_hop": nh
                })

        return routing_tables

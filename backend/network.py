"""Network topology model for the reliability monitoring simulator."""

from dataclasses import dataclass
import heapq
from typing import Dict, List


@dataclass
class Node:
    id: str
    label: str
    role: str
    status: str = "active"
    reading: float | None = None
    unit: str = ""
    fail_count: int = 0
    repair_count: int = 0
    uptime_seconds: int = 0
    downtime_seconds: int = 0


@dataclass
class Link:
    source: str
    target: str
    active: bool = True
    latency_ms: int = 30
    loss_rate: float = 0.002
    protocol: str = "Industrial Ethernet"


class NetworkState:
    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {
            "A": Node(id="A", label="Temperature Sensor A", role="Sensor", reading=72.0, unit="C"),
            "B": Node(id="B", label="PLC B", role="PLC"),
            "C": Node(id="C", label="SIS Controller C", role="Controller"),
            "D": Node(id="D", label="Backup Gateway D", role="Redundant Path"),
            "E": Node(id="E", label="Control Room E", role="SCADA"),
        }
        self.links: List[Link] = [
            Link("A", "B", latency_ms=22, loss_rate=0.001, protocol="Modbus TCP"),
            Link("B", "C", latency_ms=28, loss_rate=0.002, protocol="Profinet"),
            Link("C", "E", latency_ms=35, loss_rate=0.002, protocol="OPC UA"),
            Link("A", "D", latency_ms=38, loss_rate=0.004, protocol="MQTT"),
            Link("D", "C", latency_ms=42, loss_rate=0.004, protocol="Industrial Ethernet"),
            Link("D", "E", latency_ms=48, loss_rate=0.005, protocol="OPC UA"),
        ]

    def get_nodes(self) -> List[Dict[str, str | int | float | None]]:
        return [vars(node) for node in self.nodes.values()]

    def get_links(self) -> List[Dict[str, str | bool | int | float]]:
        return [{**vars(link), "id": self.link_id(link.source, link.target)} for link in self.links]

    def fail_node(self, node_id: str) -> bool:
        node = self.nodes.get(node_id)
        if node is None:
            return False
        if node.status != "failed":
            node.fail_count += 1
        node.status = "failed"
        for link in self.links:
            if link.source == node_id or link.target == node_id:
                link.active = False
        return True

    def restore_node(self, node_id: str) -> bool:
        node = self.nodes.get(node_id)
        if node is None:
            return False
        if node.status == "failed":
            node.repair_count += 1
        node.status = "active"
        for link in self.links:
            if link.source == node_id or link.target == node_id:
                other = link.target if link.source == node_id else link.source
                if self.nodes[other].status == "active":
                    link.active = True
        return True

    def reset(self) -> None:
        for node in self.nodes.values():
            node.status = "active"
            node.reading = 72.0 if node.id == "A" else node.reading
            node.fail_count = 0
            node.repair_count = 0
            node.uptime_seconds = 0
            node.downtime_seconds = 0
        for link in self.links:
            link.active = True
            if link.source == "A" and link.target == "B":
                link.latency_ms = 22
                link.loss_rate = 0.001
            elif link.source == "B" and link.target == "C":
                link.latency_ms = 28
                link.loss_rate = 0.002
            elif link.source == "C" and link.target == "E":
                link.latency_ms = 35
                link.loss_rate = 0.002
            elif link.source == "A" and link.target == "D":
                link.latency_ms = 38
                link.loss_rate = 0.004
            elif link.source == "D" and link.target == "C":
                link.latency_ms = 42
                link.loss_rate = 0.004
            elif link.source == "D" and link.target == "E":
                link.latency_ms = 48
                link.loss_rate = 0.005

    def fail_link(self, source: str, target: str) -> bool:
        link = self.find_link(source, target)
        if link is None:
            return False
        link.active = False
        return True

    def restore_link(self, source: str, target: str) -> bool:
        link = self.find_link(source, target)
        if link is None:
            return False
        if self.nodes[link.source].status == "active" and self.nodes[link.target].status == "active":
            link.active = True
        return True

    def set_link_conditions(self, loss_rate: float | None = None, latency_ms: int | None = None) -> None:
        for link in self.links:
            if loss_rate is not None:
                link.loss_rate = max(0.0, min(loss_rate, 1.0))
            if latency_ms is not None:
                link.latency_ms = max(0, latency_ms)

    def update_node_timers(self) -> None:
        for node in self.nodes.values():
            if node.status == "active":
                node.uptime_seconds += 1
            else:
                node.downtime_seconds += 1

    def shortest_path(self, src: str, dst: str) -> List[str]:
        if src not in self.nodes or dst not in self.nodes:
            return []
        if self.nodes[src].status != "active" or self.nodes[dst].status != "active":
            return []
        if src == dst:
            return [src]

        adjacency: Dict[str, List[tuple[str, float]]] = {node_id: [] for node_id in self.nodes}
        for link in self.links:
            if not link.active:
                continue
            if self.nodes[link.source].status != "active" or self.nodes[link.target].status != "active":
                continue
            weight = float(link.latency_ms) + (link.loss_rate * 1000.0)
            adjacency[link.source].append((link.target, weight))
            adjacency[link.target].append((link.source, weight))

        queue: list[tuple[float, str]] = [(0.0, src)]
        parent: Dict[str, str | None] = {src: None}
        best_cost: Dict[str, float] = {src: 0.0}
        while queue:
            cost, current = heapq.heappop(queue)
            if cost > best_cost[current]:
                continue
            if current == dst:
                path = []
                probe: str | None = dst
                while probe is not None:
                    path.append(probe)
                    probe = parent[probe]
                return list(reversed(path))
            for neighbor, edge_weight in adjacency[current]:
                new_cost = cost + edge_weight
                if new_cost < best_cost.get(neighbor, float("inf")):
                    best_cost[neighbor] = new_cost
                    parent[neighbor] = current
                    heapq.heappush(queue, (new_cost, neighbor))
        return []

    def is_connected(self, src: str, dst: str) -> bool:
        return len(self.shortest_path(src, dst)) > 0

    def path_links(self, path: List[str]) -> List[Link]:
        links: List[Link] = []
        for index in range(len(path) - 1):
            link = self.find_link(path[index], path[index + 1])
            if link is not None:
                links.append(link)
        return links

    def find_link(self, source: str, target: str) -> Link | None:
        for link in self.links:
            if {link.source, link.target} == {source, target}:
                return link
        return None

    @staticmethod
    def link_id(source: str, target: str) -> str:
        return "-".join(sorted([source, target]))

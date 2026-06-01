"""Network topology model for the reliability monitoring simulator."""

from dataclasses import dataclass
from collections import deque
from typing import Dict, List


@dataclass
class Node:
    id: str
    label: str
    role: str
    status: str = "active"


@dataclass
class Link:
    source: str
    target: str
    active: bool = True


class NetworkState:
    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {
            "A": Node(id="A", label="Sensor A", role="Sensor"),
            "B": Node(id="B", label="PLC B", role="PLC"),
            "C": Node(id="C", label="Controller C", role="Controller"),
            "D": Node(id="D", label="Backup Node D", role="Redundant Path"),
            "E": Node(id="E", label="Control Room E", role="SCADA"),
        }
        self.links: List[Link] = [
            Link("A", "B"),
            Link("B", "C"),
            Link("C", "E"),
            Link("A", "D"),
            Link("D", "C"),
            Link("D", "E"),
        ]

    def get_nodes(self) -> List[Dict[str, str]]:
        return [vars(node) for node in self.nodes.values()]

    def get_links(self) -> List[Dict[str, str | bool]]:
        return [vars(link) for link in self.links]

    def fail_node(self, node_id: str) -> bool:
        node = self.nodes.get(node_id)
        if node is None:
            return False
        node.status = "failed"
        for link in self.links:
            if link.source == node_id or link.target == node_id:
                link.active = False
        return True

    def restore_node(self, node_id: str) -> bool:
        node = self.nodes.get(node_id)
        if node is None:
            return False
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
        for link in self.links:
            link.active = True

    def shortest_path(self, src: str, dst: str) -> List[str]:
        if src not in self.nodes or dst not in self.nodes:
            return []
        if self.nodes[src].status != "active" or self.nodes[dst].status != "active":
            return []
        if src == dst:
            return [src]

        adjacency: Dict[str, List[str]] = {node_id: [] for node_id in self.nodes}
        for link in self.links:
            if not link.active:
                continue
            if self.nodes[link.source].status != "active" or self.nodes[link.target].status != "active":
                continue
            adjacency[link.source].append(link.target)
            adjacency[link.target].append(link.source)

        queue = deque([src])
        parent: Dict[str, str | None] = {src: None}
        while queue:
            current = queue.popleft()
            if current == dst:
                path = []
                probe: str | None = dst
                while probe is not None:
                    path.append(probe)
                    probe = parent[probe]
                return list(reversed(path))
            for neighbor in adjacency[current]:
                if neighbor not in parent:
                    parent[neighbor] = current
                    queue.append(neighbor)
        return []

    def is_connected(self, src: str, dst: str) -> bool:
        return len(self.shortest_path(src, dst)) > 0

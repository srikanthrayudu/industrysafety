"""
Simple in-memory network model for the simulator.

Defines Node and Link representations and helpers to inspect connectivity.
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Node:
    id: str
    label: str
    status: str = "active"  # "active" or "failed"


@dataclass
class Link:
    source: str
    target: str
    active: bool = True


class NetworkState:
    def __init__(self):
        # initialize a small example topology
        self.nodes: Dict[str, Node] = {
            "A": Node(id="A", label="Sensor A"),
            "B": Node(id="B", label="PLC B"),
            "C": Node(id="C", label="Controller C"),
            "D": Node(id="D", label="Sensor D"),
        }

        # undirected links
        self.links: List[Link] = [
            Link("A", "B"),
            Link("B", "C"),
            Link("C", "D"),
            Link("A", "D"),
            # extra cross link to create alternate route
            Link("B", "D"),
        ]

    def get_nodes(self):
        return [vars(n) for n in self.nodes.values()]

    def get_links(self):
        return [vars(l) for l in self.links]

    def fail_node(self, node_id: str) -> bool:
        n = self.nodes.get(node_id)
        if not n:
            return False
        n.status = "failed"
        # deactivate links incident to failed node
        for l in self.links:
            if l.source == node_id or l.target == node_id:
                l.active = False
        return True

    def restore_node(self, node_id: str) -> bool:
        n = self.nodes.get(node_id)
        if not n:
            return False
        n.status = "active"
        # reactivate links incident to restored node
        for l in self.links:
            if l.source == node_id or l.target == node_id:
                l.active = True
        return True

    def reset(self):
        for n in self.nodes.values():
            n.status = "active"
        for l in self.links:
            l.active = True

    def is_connected(self, src: str, dst: str) -> bool:
        # simple BFS over active links and active nodes
        if src == dst:
            return True
        if src not in self.nodes or dst not in self.nodes:
            return False
        if self.nodes[src].status != "active" or self.nodes[dst].status != "active":
            return False

        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for l in self.links:
            if not l.active:
                continue
            # skip links whose endpoints are failed
            if self.nodes[l.source].status != "active" or self.nodes[l.target].status != "active":
                continue
            adj[l.source].append(l.target)
            adj[l.target].append(l.source)

        visited = set()
        queue = [src]
        while queue:
            cur = queue.pop(0)
            if cur == dst:
                return True
            if cur in visited:
                continue
            visited.add(cur)
            for nb in adj.get(cur, []):
                if nb not in visited:
                    queue.append(nb)
        return False

    def shortest_path(self, src: str, dst: str):
        """Return shortest path as list of node ids (including src and dst) or [] if no path."""
        if src == dst:
            return [src]
        if src not in self.nodes or dst not in self.nodes:
            return []
        if self.nodes[src].status != "active" or self.nodes[dst].status != "active":
            return []

        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for l in self.links:
            if not l.active:
                continue
            if self.nodes[l.source].status != "active" or self.nodes[l.target].status != "active":
                continue
            adj[l.source].append(l.target)
            adj[l.target].append(l.source)

        from collections import deque

        q = deque([src])
        parent = {src: None}
        while q:
            cur = q.popleft()
            if cur == dst:
                # reconstruct path
                path = []
                node = dst
                while node is not None:
                    path.append(node)
                    node = parent.get(node)
                return list(reversed(path))
            for nb in adj.get(cur, []):
                if nb not in parent:
                    parent[nb] = cur
                    q.append(nb)
        return []

    def links_from_path(self, path: List[str]):
        """Given a node path [A,B,C], return list of link tuples [(A,B),(B,C)] in the same order."""
        res = []
        for i in range(len(path) - 1):
            res.append((path[i], path[i + 1]))
        return res

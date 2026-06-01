"""Simulation engine for industrial communication reliability monitoring."""

from __future__ import annotations

import random
import threading
import time
from datetime import datetime
from typing import Any, Dict, List

from network import NetworkState


class Simulator:
    def __init__(self, network: NetworkState, tick_interval: float = 1.0) -> None:
        self.network = network
        self.tick_interval = tick_interval
        self.random_fail_probability = 0.08
        self.monitored_flow = ("A", "E")
        self.primary_route = self.network.shortest_path(*self.monitored_flow)

        self.metrics: Dict[str, float | int] = {}
        self.history: List[Dict[str, float | str]] = []
        self.alerts: List[Dict[str, str]] = []
        self.logs: List[Dict[str, str]] = []
        self.backup_route_active = False

        self._running = False
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._reset_counters()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _loop(self) -> None:
        while self._running:
            self.step()
            time.sleep(self.tick_interval)

    def step(self) -> None:
        with self._lock:
            self._inject_random_failure()
            packet_burst = random.randint(8, 15)
            self.metrics["packetsSent"] += packet_burst

            path = self.network.shortest_path(*self.monitored_flow)
            if not path:
                lost = packet_burst
                delay = random.randint(220, 320)
            else:
                path_penalty = max(0, len(path) - len(self.primary_route)) * 35
                baseline = random.randint(65, 110)
                delay = baseline + path_penalty
                link_loss = random.randint(0, 2 if path == self.primary_route else 4)
                lost = min(packet_burst, link_loss)

            self.metrics["packetsLost"] += lost
            self.metrics["packetsReceived"] = self.metrics["packetsSent"] - self.metrics["packetsLost"]
            self.metrics["packetLossPercent"] = self._to_percent(
                self.metrics["packetsLost"], self.metrics["packetsSent"]
            )
            self.metrics["reliability"] = self._to_percent(
                self.metrics["packetsReceived"], self.metrics["packetsSent"]
            )
            self.metrics["delayMs"] = delay

            active_nodes = sum(1 for node in self.network.nodes.values() if node.status == "active")
            failed_nodes = len(self.network.nodes) - active_nodes
            self.metrics["activeNodes"] = active_nodes
            self.metrics["failedNodes"] = failed_nodes

            self.backup_route_active = bool(path) and path != self.primary_route
            if self.backup_route_active:
                self._create_alert("warning", "Backup route activated")

            self._append_history()
            self._trim_buffers()

    def inject_failure(self, node_id: str) -> bool:
        with self._lock:
            ok = self.network.fail_node(node_id)
            if not ok:
                return False
            self.metrics["packetsLost"] += random.randint(3, 7)
            self._create_alert("critical", f"Node {node_id} failure detected")
            self._log_event(f"Fault Injection: node {node_id} failed")
            return True

    def restore_node(self, node_id: str) -> bool:
        with self._lock:
            ok = self.network.restore_node(node_id)
            if not ok:
                return False
            self._create_alert("success", f"Node {node_id} restored")
            self._log_event(f"Recovery: node {node_id} restored")
            return True

    def reset(self) -> None:
        with self._lock:
            self.network.reset()
            self._reset_counters()
            self._log_event("Network reset requested")
            self._create_alert("success", "Network reset complete")

    def set_random_failure_probability(self, probability: float) -> None:
        with self._lock:
            self.random_fail_probability = probability
            self._log_event(f"Random fault probability updated to {probability:.2f}")

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            current_path = self.network.shortest_path(*self.monitored_flow)
            return {
                "nodes": self.network.get_nodes(),
                "links": self.network.get_links(),
                "metrics": dict(self.metrics),
                "routes": {
                    "monitoredFlow": {"from": self.monitored_flow[0], "to": self.monitored_flow[1]},
                    "primary": self.primary_route,
                    "current": current_path,
                    "backupActive": self.backup_route_active,
                },
                "alerts": list(self.alerts),
                "logs": list(self.logs),
                "history": list(self.history),
            }

    def get_history(self, limit: int = 60) -> List[Dict[str, float | str]]:
        with self._lock:
            return list(self.history[-limit:])

    def get_logs(self, limit: int = 120) -> List[Dict[str, str]]:
        with self._lock:
            return list(self.logs[-limit:])

    def get_alerts(self, limit: int = 50) -> List[Dict[str, str]]:
        with self._lock:
            return list(self.alerts[-limit:])

    def _inject_random_failure(self) -> None:
        for node in self.network.nodes.values():
            if node.status != "active":
                continue
            if random.random() < self.random_fail_probability:
                self.network.fail_node(node.id)
                self._create_alert("critical", f"Random failure on node {node.id}")
                self._log_event(f"Random fault: node {node.id} failed")
                break

    def _reset_counters(self) -> None:
        self.metrics = {
            "packetsSent": 0,
            "packetsReceived": 0,
            "packetsLost": 0,
            "packetLossPercent": 0.0,
            "reliability": 100.0,
            "delayMs": 80,
            "activeNodes": len(self.network.nodes),
            "failedNodes": 0,
        }
        self.history = []
        self.alerts = []
        self.logs = []
        self.backup_route_active = False

    def _append_history(self) -> None:
        self.history.append(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "reliability": float(self.metrics["reliability"]),
                "packetLossPercent": float(self.metrics["packetLossPercent"]),
                "delayMs": float(self.metrics["delayMs"]),
            }
        )

    def _trim_buffers(self) -> None:
        if len(self.history) > 240:
            self.history = self.history[-240:]
        if len(self.alerts) > 120:
            self.alerts = self.alerts[-120:]
        if len(self.logs) > 300:
            self.logs = self.logs[-300:]

    def _create_alert(self, level: str, message: str) -> None:
        alert = {"time": datetime.now().strftime("%H:%M:%S"), "level": level, "message": message}
        self.alerts.append(alert)

    def _log_event(self, message: str) -> None:
        self.logs.append({"time": datetime.now().strftime("%H:%M:%S"), "event": message})

    @staticmethod
    def _to_percent(part: int | float, whole: int | float) -> float:
        if whole <= 0:
            return 0.0
        return round((float(part) / float(whole)) * 100.0, 2)

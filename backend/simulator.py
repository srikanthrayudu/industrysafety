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
        self.random_fail_probability = 0.0
        self.monitored_flow = ("A", "E")
        self.primary_route = self.network.shortest_path(*self.monitored_flow)

        self.metrics: Dict[str, float | int] = {}
        self.history: List[Dict[str, float | str]] = []
        self.alerts: List[Dict[str, str]] = []
        self.logs: List[Dict[str, str]] = []
        self.backup_route_active = False
        self.alarm_suppressed = False
        self.false_data_active = False
        self.dos_ticks_remaining = 0
        self.esd_failures = 0
        self.esd_successes = 0
        self._was_backup_route_active = False

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
            self._update_sensor_reading()
            self.network.update_node_timers()

            packet_burst = random.randint(8, 15)
            dos_active = self.dos_ticks_remaining > 0
            if dos_active:
                packet_burst += random.randint(35, 55)
                self.dos_ticks_remaining -= 1
            self.metrics["packetsSent"] += packet_burst

            path = self.network.shortest_path(*self.monitored_flow)
            if not path:
                lost = packet_burst
                delay = random.randint(220, 320)
            else:
                path_links = self.network.path_links(path)
                baseline = sum(link.latency_ms for link in path_links) + random.randint(4, 18)
                path_penalty = max(0, len(path) - len(self.primary_route)) * 12
                delay = baseline + path_penalty
                combined_loss_rate = min(1.0, sum(link.loss_rate for link in path_links))
                if dos_active:
                    combined_loss_rate = min(1.0, combined_loss_rate + 0.22)
                    delay += random.randint(120, 180)
                link_loss = sum(1 for _ in range(packet_burst) if random.random() < combined_loss_rate)
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
            delivered = packet_burst - lost
            self.metrics["throughputPps"] = delivered
            self.metrics["uptimeSeconds"] += 1

            active_nodes = sum(1 for node in self.network.nodes.values() if node.status == "active")
            failed_nodes = len(self.network.nodes) - active_nodes
            self.metrics["activeNodes"] = active_nodes
            self.metrics["failedNodes"] = failed_nodes
            self.metrics["mtbfSec"] = self._mean_time_between_failures()
            self.metrics["mttrSec"] = self._mean_time_to_repair()
            self.metrics["esdSuccesses"] = self.esd_successes
            self.metrics["esdFailures"] = self.esd_failures

            self.backup_route_active = bool(path) and path != self.primary_route
            if self.backup_route_active and not self._was_backup_route_active:
                self._create_alert("warning", "Backup route activated")
                self._log_event(f"Failover: active route changed to {' -> '.join(path)}")
            if not self.backup_route_active and self._was_backup_route_active and path:
                self._create_alert("success", "Primary route restored")
                self._log_event("Recovery: primary communication route restored")
            self._was_backup_route_active = self.backup_route_active

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

    def inject_link_failure(self, source: str, target: str) -> bool:
        with self._lock:
            ok = self.network.fail_link(source, target)
            if not ok:
                return False
            self._create_alert("critical", f"Link {source}-{target} failure detected")
            self._log_event(f"Fault Injection: link {source}-{target} failed")
            return True

    def restore_link(self, source: str, target: str) -> bool:
        with self._lock:
            ok = self.network.restore_link(source, target)
            if not ok:
                return False
            self._create_alert("success", f"Link {source}-{target} restored")
            self._log_event(f"Recovery: link {source}-{target} restored")
            return True

    def inject_event(self, event: str, payload: Dict[str, Any]) -> bool:
        event = event.strip().lower()
        if event == "fail_node":
            return self.inject_failure(str(payload.get("nodeId") or payload.get("node_id") or ""))
        if event == "restore_node":
            return self.restore_node(str(payload.get("nodeId") or payload.get("node_id") or ""))
        if event == "fail_link":
            source = str(payload.get("source") or "")
            target = str(payload.get("target") or "")
            return self.inject_link_failure(source, target)
        if event == "restore_link":
            source = str(payload.get("source") or "")
            target = str(payload.get("target") or "")
            return self.restore_link(source, target)

        with self._lock:
            if event == "packet_loss":
                rate = float(payload.get("rate", 0.05))
                self.network.set_link_conditions(loss_rate=max(0.0, min(rate, 1.0)))
                self._create_alert("warning", f"Packet loss set to {rate * 100:.1f}%")
                self._log_event(f"Network condition: packet loss set to {rate * 100:.1f}%")
                return True
            if event == "latency":
                latency_ms = int(payload.get("latencyMs", payload.get("latency_ms", 120)))
                self.network.set_link_conditions(latency_ms=latency_ms)
                self._create_alert("warning", f"Latency increased to {latency_ms} ms per link")
                self._log_event(f"Network condition: latency increased to {latency_ms} ms per link")
                return True
            if event == "dos":
                self.dos_ticks_remaining = int(payload.get("durationTicks", 12))
                self._create_alert("critical", "DoS flood simulation started")
                self._log_event("Cyber Scenario: DoS flood increased traffic and packet loss")
                return True
            if event == "alarm_suppression":
                self.alarm_suppressed = bool(payload.get("enabled", True))
                state = "enabled" if self.alarm_suppressed else "disabled"
                self._log_event(f"Cyber Scenario: alarm suppression {state}")
                if not self.alarm_suppressed:
                    self._create_alert("success", "Alarm channel restored")
                return True
            if event == "false_data":
                value = float(payload.get("value", 41.0))
                sensor = self.network.nodes.get("A")
                if sensor is None:
                    return False
                sensor.reading = value
                self.false_data_active = True
                self._create_alert("warning", f"Sensor A reports suspicious value {value:.1f} C")
                self._log_event(f"Cyber Scenario: false data injected on Sensor A ({value:.1f} C)")
                return True
            if event == "esd_failure":
                self._simulate_esd(force_failure=True)
                return True
            if event == "esd_command":
                self._simulate_esd(force_failure=False)
                return True
            if event == "sensor_loss_scenario":
                self.network.fail_node("B")
                self._create_alert("critical", "Sensor path interrupted at PLC B")
                self._log_event("Demo Scenario: sensor communication loss triggered")
                return True
            if event == "reset_conditions":
                self.network.reset()
                self.alarm_suppressed = False
                self.false_data_active = False
                self.dos_ticks_remaining = 0
                self._create_alert("success", "Network conditions normalized")
                self._log_event("Network condition reset requested")
                return True
        return False

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
                "scenario": {
                    "alarmSuppressed": self.alarm_suppressed,
                    "falseDataActive": self.false_data_active,
                    "dosActive": self.dos_ticks_remaining > 0,
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
            "throughputPps": 0,
            "uptimeSeconds": 0,
            "mtbfSec": 0.0,
            "mttrSec": 0.0,
            "esdSuccesses": 0,
            "esdFailures": 0,
            "activeNodes": len(self.network.nodes),
            "failedNodes": 0,
        }
        self.history = []
        self.alerts = []
        self.logs = []
        self.backup_route_active = False
        self.alarm_suppressed = False
        self.false_data_active = False
        self.dos_ticks_remaining = 0
        self.esd_failures = 0
        self.esd_successes = 0
        self._was_backup_route_active = False

    def _append_history(self) -> None:
        self.history.append(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "reliability": float(self.metrics["reliability"]),
                "packetLossPercent": float(self.metrics["packetLossPercent"]),
                "delayMs": float(self.metrics["delayMs"]),
                "throughputPps": float(self.metrics["throughputPps"]),
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
        if self.alarm_suppressed and level in {"critical", "warning"}:
            self._log_event(f"Suppressed Alert: {message}")
            return
        alert = {"time": datetime.now().strftime("%H:%M:%S"), "level": level, "message": message}
        self.alerts.append(alert)

    def _log_event(self, message: str) -> None:
        self.logs.append({"time": datetime.now().strftime("%H:%M:%S"), "event": message})

    def _simulate_esd(self, force_failure: bool) -> None:
        path = self.network.shortest_path("C", "E")
        failed = force_failure or not path
        if failed:
            self.esd_failures += 1
            self.metrics["packetsSent"] += 1
            self.metrics["packetsLost"] += 1
            self._create_alert("critical", "ESD command failed to reach Control Room E")
            self._log_event("Safety Scenario: emergency shutdown command delivery failed")
            return
        self.esd_successes += 1
        self.metrics["packetsSent"] += 1
        self.metrics["packetsReceived"] += 1
        self._create_alert("success", "ESD command delivered on active route")
        self._log_event(f"Safety Scenario: ESD command delivered through {' -> '.join(path)}")

    def _update_sensor_reading(self) -> None:
        sensor = self.network.nodes.get("A")
        if sensor is None or sensor.status != "active" or self.false_data_active:
            return
        sensor.reading = round(72.0 + random.uniform(-1.5, 1.5), 1)

    def _mean_time_between_failures(self) -> float:
        failures = sum(node.fail_count for node in self.network.nodes.values())
        if failures == 0:
            return 0.0
        uptime = sum(node.uptime_seconds for node in self.network.nodes.values())
        return round(uptime / failures, 2)

    def _mean_time_to_repair(self) -> float:
        repairs = sum(node.repair_count for node in self.network.nodes.values())
        if repairs == 0:
            return 0.0
        downtime = sum(node.downtime_seconds for node in self.network.nodes.values())
        return round(downtime / repairs, 2)

    @staticmethod
    def _to_percent(part: int | float, whole: int | float) -> float:
        if whole <= 0:
            return 0.0
        return round((float(part) / float(whole)) * 100.0, 2)

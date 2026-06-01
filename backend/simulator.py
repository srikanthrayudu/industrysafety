"""Simulation engine for the smart industrial safety monitoring system."""

from __future__ import annotations

import random
import threading
import time
from datetime import datetime
from typing import Any, Dict, List

from network import NetworkState


class Simulator:
    """SCADA-inspired safety simulator with communication reliability as one layer."""

    SAFETY_THRESHOLDS = {
        "minReliability": 99.0,
        "maxDelayMs": 150.0,
        "maxPacketLossPercent": 1.0,
    }

    RISK_ORDER = {"GREEN": 0, "YELLOW": 1, "ORANGE": 2, "RED": 3, "BLACK": 4}

    SENSOR_CONFIGS: List[Dict[str, Any]] = [
        {
            "id": "temperature",
            "label": "Reactor Temperature",
            "domain": "Chemical / Nuclear",
            "unit": "degC",
            "min": 20.0,
            "max": 350.0,
            "baseline": 82.0,
            "jitter": 1.8,
            "direction": "high",
            "thresholds": {"YELLOW": 150.0, "ORANGE": 210.0, "RED": 250.0, "BLACK": 320.0},
            "normalRange": "20-140 degC",
            "actions": ["Start cooling loop", "Reduce feed rate", "Trip reactor if escalation continues"],
        },
        {
            "id": "pressure",
            "label": "Pressure Vessel",
            "domain": "Process Industry",
            "unit": "bar",
            "min": 1.0,
            "max": 100.0,
            "baseline": 18.0,
            "jitter": 0.9,
            "direction": "high",
            "thresholds": {"YELLOW": 35.0, "ORANGE": 55.0, "RED": 75.0, "BLACK": 90.0},
            "normalRange": "1-30 bar",
            "actions": ["Open relief path", "Close inlet valve", "Notify pressure safety officer"],
        },
        {
            "id": "toxic_gas",
            "label": "Toxic Gas",
            "domain": "Chemical Plant",
            "unit": "ppm",
            "min": 0.0,
            "max": 500.0,
            "baseline": 12.0,
            "jitter": 2.2,
            "direction": "high",
            "thresholds": {"YELLOW": 50.0, "ORANGE": 120.0, "RED": 220.0, "BLACK": 360.0},
            "normalRange": "0-40 ppm",
            "actions": ["Trigger siren", "Close isolation valve", "Start scrubber fans", "Evacuate affected zone"],
        },
        {
            "id": "radiation",
            "label": "Radiation Field",
            "domain": "Nuclear Safety",
            "unit": "mSv",
            "min": 0.0,
            "max": 1000.0,
            "baseline": 5.0,
            "jitter": 1.5,
            "direction": "high",
            "thresholds": {"YELLOW": 80.0, "ORANGE": 180.0, "RED": 420.0, "BLACK": 700.0},
            "normalRange": "0-50 mSv",
            "actions": ["Trigger reactor shutdown", "Activate containment", "Dispatch radiation response team"],
        },
        {
            "id": "methane",
            "label": "Methane Concentration",
            "domain": "Mining Safety",
            "unit": "%",
            "min": 0.0,
            "max": 100.0,
            "baseline": 3.0,
            "jitter": 0.8,
            "direction": "high",
            "thresholds": {"YELLOW": 20.0, "ORANGE": 45.0, "RED": 70.0, "BLACK": 82.0},
            "normalRange": "0-10%",
            "actions": ["Start ventilation", "Cut ignition sources", "Evacuate workers"],
        },
        {
            "id": "smoke",
            "label": "Smoke Density",
            "domain": "Plant / Mine Fire",
            "unit": "%",
            "min": 0.0,
            "max": 100.0,
            "baseline": 2.0,
            "jitter": 0.8,
            "direction": "high",
            "thresholds": {"YELLOW": 15.0, "ORANGE": 35.0, "RED": 65.0, "BLACK": 85.0},
            "normalRange": "0-10%",
            "actions": ["Trigger fire alarm", "Start suppression", "Open evacuation route"],
        },
        {
            "id": "oxygen",
            "label": "Oxygen Level",
            "domain": "Confined Space / Mine",
            "unit": "%",
            "min": 0.0,
            "max": 25.0,
            "baseline": 20.9,
            "jitter": 0.15,
            "direction": "low",
            "thresholds": {"YELLOW": 19.5, "ORANGE": 18.0, "RED": 16.0, "BLACK": 14.0},
            "normalRange": "19.5-23.5%",
            "actions": ["Increase ventilation", "Block worker entry", "Evacuate confined zone"],
        },
        {
            "id": "humidity",
            "label": "Humidity",
            "domain": "Environmental Monitoring",
            "unit": "%RH",
            "min": 0.0,
            "max": 100.0,
            "baseline": 48.0,
            "jitter": 1.2,
            "direction": "high",
            "thresholds": {"YELLOW": 70.0, "ORANGE": 82.0, "RED": 92.0, "BLACK": 98.0},
            "normalRange": "30-65%RH",
            "actions": ["Inspect condensation risk", "Increase ventilation", "Protect control cabinets"],
        },
    ]

    SCENARIO_LIBRARY: Dict[str, Dict[str, Any]] = {
        "chemical_leak": {
            "label": "Chemical Leak",
            "environment": "Chemical Processing Plant",
            "processArea": "Reactor Train 2",
            "description": "Toxic gas release with rising vessel pressure.",
            "targets": {"toxic_gas": 280.0, "pressure": 64.0, "humidity": 76.0},
            "durationTicks": 120,
        },
        "radiation_spike": {
            "label": "Radiation Spike",
            "environment": "Nuclear Power Facility",
            "processArea": "Reactor Containment",
            "description": "Radiation field rises while reactor temperature trends upward.",
            "targets": {"radiation": 780.0, "temperature": 265.0},
            "durationTicks": 120,
        },
        "methane_explosion": {
            "label": "Methane Explosion Risk",
            "environment": "Underground Mining Operation",
            "processArea": "North Tunnel Ventilation District",
            "description": "Methane accumulates and oxygen falls, creating ignition risk.",
            "targets": {"methane": 86.0, "oxygen": 15.4},
            "durationTicks": 120,
        },
        "reactor_overheat": {
            "label": "Reactor Overheating",
            "environment": "Chemical Processing Plant",
            "processArea": "Exothermic Reactor Vessel",
            "description": "Thermal runaway precursor with elevated vessel pressure.",
            "targets": {"temperature": 302.0, "pressure": 72.0},
            "durationTicks": 120,
        },
        "cooling_failure": {
            "label": "Cooling System Failure",
            "environment": "Nuclear Power Facility",
            "processArea": "Primary Cooling Loop",
            "description": "Cooling degradation drives reactor heat toward shutdown threshold.",
            "targets": {"temperature": 335.0, "radiation": 160.0, "pressure": 58.0},
            "durationTicks": 120,
        },
        "tunnel_fire": {
            "label": "Tunnel Fire",
            "environment": "Underground Mining Operation",
            "processArea": "Conveyor Transfer Tunnel",
            "description": "Smoke and heat rise while oxygen drops in a confined tunnel.",
            "targets": {"smoke": 88.0, "temperature": 190.0, "oxygen": 16.8},
            "durationTicks": 120,
        },
        "oxygen_deficiency": {
            "label": "Oxygen Deficiency",
            "environment": "Hazardous Manufacturing Plant",
            "processArea": "Confined Maintenance Bay",
            "description": "Oxygen depletion threatens worker safety.",
            "targets": {"oxygen": 13.6, "toxic_gas": 70.0},
            "durationTicks": 120,
        },
        "pipeline_failure": {
            "label": "Pipeline Failure",
            "environment": "Oil & Gas Facility",
            "processArea": "High Pressure Transfer Line",
            "description": "Pipeline pressure excursion with gas release signature.",
            "targets": {"pressure": 92.0, "toxic_gas": 180.0},
            "durationTicks": 120,
        },
        "plc_failure_emergency": {
            "label": "PLC Failure During Emergency",
            "environment": "Chemical Processing Plant",
            "processArea": "Reactor Train 2",
            "description": "Hazard occurs while the PLC path is lost.",
            "targets": {"toxic_gas": 240.0, "pressure": 70.0},
            "durationTicks": 120,
            "failNode": "B",
        },
        "communication_loss_shutdown": {
            "label": "Communication Loss During Shutdown",
            "environment": "Nuclear Power Facility",
            "processArea": "Reactor Containment",
            "description": "Critical condition coincides with delayed shutdown communication.",
            "targets": {"radiation": 760.0, "temperature": 310.0},
            "durationTicks": 120,
            "lossRate": 0.18,
            "latencyMs": 190,
            "forceShutdownFailure": True,
        },
    }

    HAZARD_LABELS = {
        "temperature": "Reactor Overheating",
        "pressure": "Pressure Vessel Overstress",
        "toxic_gas": "Toxic Gas Release",
        "radiation": "Radiation Leak",
        "methane": "Methane Explosion Risk",
        "smoke": "Fire / Smoke Event",
        "oxygen": "Oxygen Deficiency",
        "humidity": "Environmental Control Risk",
    }

    def __init__(self, network: NetworkState, tick_interval: float = 1.0) -> None:
        self.network = network
        self.tick_interval = tick_interval
        self.random_fail_probability = 0.0
        self.monitored_flow = ("A", "E")
        self.primary_route = self.network.shortest_path(*self.monitored_flow)

        self.sensor_configs = {config["id"]: config for config in self.SENSOR_CONFIGS}
        self.sensor_values = {
            sensor_id: float(config["baseline"]) for sensor_id, config in self.sensor_configs.items()
        }
        self.plant_profile = self._default_plant_profile()
        self.active_scenario: str | None = None
        self.scenario_ticks_remaining = 0
        self.hazards: List[Dict[str, Any]] = []
        self.risk_state: Dict[str, Any] = self._default_risk_state()
        self.emergency_actions: List[Dict[str, Any]] = []
        self.shutdown_active = False
        self.last_shutdown_status = "standby"

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
        self.alarm_attempts = 0
        self.alarm_deliveries = 0
        self.shutdown_attempts = 0
        self.shutdown_successes = 0
        self.shutdown_failures = 0
        self._announced_hazards: set[str] = set()
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
            self._update_sensor_readings()
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
            self.metrics["communicationReliability"] = self.metrics["reliability"]
            self.metrics["safetyCommunicationReliability"] = self.metrics["reliability"]
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

            self.backup_route_active = bool(path) and path != self.primary_route
            if self.backup_route_active and not self._was_backup_route_active:
                self._create_alert("warning", "Backup safety communication route activated")
                self._log_event(f"Failover: active route changed to {' -> '.join(path)}")
            if not self.backup_route_active and self._was_backup_route_active and path:
                self._create_alert("success", "Primary safety communication route restored")
                self._log_event("Recovery: primary communication route restored")
            self._was_backup_route_active = self.backup_route_active

            self._evaluate_safety_cycle()
            self._append_history()
            self._trim_buffers()

    def inject_failure(self, node_id: str) -> bool:
        with self._lock:
            ok = self.network.fail_node(node_id)
            if not ok:
                return False
            self.metrics["packetsLost"] += random.randint(3, 7)
            self._create_alert("critical", f"{self._node_label(node_id)} failure detected")
            self._log_event(f"Fault Injection: {self._node_label(node_id)} failed")
            self._evaluate_safety_cycle()
            return True

    def restore_node(self, node_id: str) -> bool:
        with self._lock:
            ok = self.network.restore_node(node_id)
            if not ok:
                return False
            self._create_alert("success", f"{self._node_label(node_id)} restored")
            self._log_event(f"Recovery: {self._node_label(node_id)} restored")
            self._evaluate_safety_cycle()
            return True

    def inject_link_failure(self, source: str, target: str) -> bool:
        with self._lock:
            ok = self.network.fail_link(source, target)
            if not ok:
                return False
            self._create_alert("critical", f"Safety link {source}-{target} failure detected")
            self._log_event(f"Fault Injection: safety communication link {source}-{target} failed")
            self._evaluate_safety_cycle()
            return True

    def restore_link(self, source: str, target: str) -> bool:
        with self._lock:
            ok = self.network.restore_link(source, target)
            if not ok:
                return False
            self._create_alert("success", f"Safety link {source}-{target} restored")
            self._log_event(f"Recovery: safety communication link {source}-{target} restored")
            self._evaluate_safety_cycle()
            return True

    def inject_event(self, event: str, payload: Dict[str, Any]) -> bool:
        event = event.strip().lower()
        if event in self.SCENARIO_LIBRARY:
            with self._lock:
                self._activate_safety_scenario(event)
                return True
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
                self._create_alert("warning", f"Sensor alarm packet loss set to {rate * 100:.1f}%")
                self._log_event(f"Communication condition: packet loss set to {rate * 100:.1f}%")
                self._evaluate_safety_cycle()
                return True
            if event == "latency":
                latency_ms = int(payload.get("latencyMs", payload.get("latency_ms", 120)))
                self.network.set_link_conditions(latency_ms=latency_ms)
                self._create_alert("warning", f"Emergency response delay increased to {latency_ms} ms per link")
                self._log_event(f"Communication condition: latency increased to {latency_ms} ms per link")
                self._evaluate_safety_cycle()
                return True
            if event == "dos":
                self.dos_ticks_remaining = int(payload.get("durationTicks", 12))
                self._create_alert("critical", "DoS flood simulation started against safety network")
                self._log_event("Cyber Scenario: DoS flood increased alarm traffic and packet loss")
                self._evaluate_safety_cycle()
                return True
            if event == "alarm_suppression":
                self.alarm_suppressed = bool(payload.get("enabled", True))
                state = "enabled" if self.alarm_suppressed else "disabled"
                self._log_event(f"Cyber Scenario: alarm suppression {state}")
                if not self.alarm_suppressed:
                    self._create_alert("success", "Alarm channel restored")
                self._evaluate_safety_cycle()
                return True
            if event == "false_data":
                value = float(payload.get("value", 41.0))
                self.sensor_values["temperature"] = value
                sensor = self.network.nodes.get("A")
                if sensor is None:
                    return False
                sensor.reading = value
                self.false_data_active = True
                self._create_alert("warning", f"Temperature sensor reports suspicious value {value:.1f} degC")
                self._log_event(f"Cyber Scenario: false data injected on temperature sensor ({value:.1f} degC)")
                self._evaluate_safety_cycle()
                return True
            if event == "esd_failure":
                self._simulate_esd(force_failure=True, reason="Manual emergency shutdown failure drill")
                self._evaluate_safety_cycle()
                return True
            if event == "esd_command":
                self._simulate_esd(force_failure=False, reason="Manual emergency shutdown command")
                self._evaluate_safety_cycle()
                return True
            if event == "sensor_loss_scenario":
                self.network.fail_node("B")
                self._create_alert("critical", "Sensor path interrupted at PLC / RTU B")
                self._log_event("Demo Scenario: sensor communication loss triggered")
                self._evaluate_safety_cycle()
                return True
            if event == "reset_conditions":
                self._normalize_conditions(reset_network=True)
                self._create_alert("success", "Plant and communication conditions normalized")
                self._log_event("Safety condition reset requested")
                self._evaluate_safety_cycle()
                return True
        return False

    def reset(self) -> None:
        with self._lock:
            self.network.reset()
            self._reset_counters()
            self._log_event("Simulator reset requested")
            self._create_alert("success", "Safety simulator reset complete")

    def set_random_failure_probability(self, probability: float) -> None:
        with self._lock:
            self.random_fail_probability = probability
            self._log_event(f"Random fault probability updated to {probability:.2f}")

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            self._refresh_node_counts()
            current_path = self.network.shortest_path(*self.monitored_flow)
            self.backup_route_active = bool(current_path) and current_path != self.primary_route
            safety_metrics = self._safety_metrics()
            return {
                "project": {
                    "name": "Smart Industrial Safety Monitoring and Emergency Response Simulator",
                    "focus": "Industrial Safety Engineering",
                    "communicationRole": "Communication reliability is modeled as a safety support layer.",
                },
                "plant": dict(self.plant_profile),
                "sensors": self._sensor_payload(),
                "hazards": list(self.hazards),
                "risk": dict(self.risk_state),
                "emergency": {
                    "actions": list(self.emergency_actions),
                    "shutdownActive": self.shutdown_active,
                    "lastShutdownStatus": self.last_shutdown_status,
                    "responseMode": "Automatic SIS response with operator visibility",
                },
                "communication": self._communication_payload(current_path),
                "safetyMetrics": safety_metrics,
                "scenarioCatalog": self._scenario_catalog(),
                "nodes": self.network.get_nodes(),
                "links": self.network.get_links(),
                "metrics": dict(self.metrics),
                "routes": {
                    "monitoredFlow": {"from": self.monitored_flow[0], "to": self.monitored_flow[1]},
                    "primary": self.primary_route,
                    "current": current_path,
                    "backupActive": self.backup_route_active,
                },
                "scenario": self._scenario_payload(),
                "safety": self._safety_status(),
                "thresholds": dict(self.SAFETY_THRESHOLDS),
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

    def _activate_safety_scenario(self, scenario_id: str) -> None:
        scenario = self.SCENARIO_LIBRARY[scenario_id]
        self.active_scenario = scenario_id
        self.scenario_ticks_remaining = int(scenario.get("durationTicks", 90))
        self.shutdown_active = False
        self.last_shutdown_status = "standby"
        self.plant_profile = {
            "name": scenario["environment"],
            "processArea": scenario["processArea"],
            "mode": "Emergency Simulation",
            "activeScenario": scenario["label"],
            "description": scenario["description"],
        }

        fail_node = scenario.get("failNode")
        if fail_node:
            self.network.fail_node(str(fail_node))
        if "lossRate" in scenario or "latencyMs" in scenario:
            self.network.set_link_conditions(
                loss_rate=scenario.get("lossRate"),
                latency_ms=scenario.get("latencyMs"),
            )

        for sensor_id, target in scenario["targets"].items():
            self.sensor_values[sensor_id] = self._move_toward(
                self.sensor_values[sensor_id],
                float(target),
                ratio=0.65,
            )

        self._create_alert("critical", f"Scenario started: {scenario['label']}")
        self._log_event(f"Safety Scenario: {scenario['label']} started - {scenario['description']}")
        if scenario.get("forceShutdownFailure"):
            self._simulate_esd(force_failure=True, reason="Shutdown attempted during communication loss")
        self._evaluate_safety_cycle()

    def _inject_random_failure(self) -> None:
        for node in self.network.nodes.values():
            if node.status != "active":
                continue
            if random.random() < self.random_fail_probability:
                self.network.fail_node(node.id)
                self._create_alert("critical", f"Random failure on {node.label}")
                self._log_event(f"Random fault: {node.label} failed")
                break

    def _reset_counters(self) -> None:
        self.metrics = {
            "packetsSent": 0,
            "packetsReceived": 0,
            "packetsLost": 0,
            "packetLossPercent": 0.0,
            "reliability": 100.0,
            "communicationReliability": 100.0,
            "safetyCommunicationReliability": 100.0,
            "delayMs": 80,
            "throughputPps": 0,
            "uptimeSeconds": 0,
            "mtbfSec": 0.0,
            "mttrSec": 0.0,
            "esdSuccesses": 0,
            "esdFailures": 0,
            "activeNodes": len(self.network.nodes),
            "failedNodes": 0,
            "alarmDeliverySuccessRate": 100.0,
            "emergencyShutdownSuccessRate": 100.0,
            "plantSafetyScore": 100.0,
            "sensorAvailability": 100.0,
            "hazardDetectionAccuracy": 98.5,
            "emergencyResponseTimeSec": 0.8,
            "activeHazards": 0,
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
        self.alarm_attempts = 0
        self.alarm_deliveries = 0
        self.shutdown_attempts = 0
        self.shutdown_successes = 0
        self.shutdown_failures = 0
        self._announced_hazards = set()
        self._was_backup_route_active = False
        self._normalize_conditions(reset_network=False)
        self._evaluate_safety_cycle()

    def _normalize_conditions(self, reset_network: bool) -> None:
        if reset_network:
            self.network.reset()
        self.sensor_values = {
            sensor_id: float(config["baseline"]) for sensor_id, config in self.sensor_configs.items()
        }
        sensor = self.network.nodes.get("A")
        if sensor is not None:
            sensor.reading = self.sensor_values["temperature"]
        self.plant_profile = self._default_plant_profile()
        self.active_scenario = None
        self.scenario_ticks_remaining = 0
        self.hazards = []
        self.risk_state = self._default_risk_state()
        self.emergency_actions = []
        self.shutdown_active = False
        self.last_shutdown_status = "standby"
        self.alarm_suppressed = False
        self.false_data_active = False
        self.dos_ticks_remaining = 0
        self._announced_hazards.clear()

    def _update_sensor_readings(self) -> None:
        scenario_targets: Dict[str, float] = {}
        if self.active_scenario and self.scenario_ticks_remaining > 0:
            scenario_targets = self.SCENARIO_LIBRARY[self.active_scenario]["targets"]
            self.scenario_ticks_remaining -= 1
        elif self.active_scenario and self.scenario_ticks_remaining <= 0:
            self.active_scenario = None
            self.plant_profile = self._default_plant_profile()
            self._log_event("Safety Scenario: active hazard drifted back toward normal")

        sensor_array_active = self.network.nodes.get("A") is not None and self.network.nodes["A"].status == "active"
        for sensor_id, config in self.sensor_configs.items():
            if sensor_id == "temperature" and self.false_data_active:
                continue
            if not sensor_array_active:
                continue
            target = float(scenario_targets.get(sensor_id, config["baseline"]))
            drift = self._move_toward(self.sensor_values[sensor_id], target, ratio=0.28)
            jitter = random.uniform(-float(config["jitter"]), float(config["jitter"]))
            self.sensor_values[sensor_id] = self._clamp(drift + jitter, float(config["min"]), float(config["max"]))

        sensor = self.network.nodes.get("A")
        if sensor is not None and sensor_array_active and not self.false_data_active:
            sensor.reading = round(self.sensor_values["temperature"], 1)

    def _evaluate_safety_cycle(self) -> None:
        self.hazards = self._detect_hazards()
        self.risk_state = self._calculate_risk(self.hazards)
        self._process_new_hazard_alarms()

        if self.risk_state["level"] == "BLACK" and not self.shutdown_active and self.last_shutdown_status != "failed":
            force_failure = not self._shutdown_channel_available()
            self._simulate_esd(force_failure=force_failure, reason="Automatic SIS shutdown for BLACK risk")

        self.emergency_actions = self._plan_emergency_actions(self.hazards, self.risk_state)
        safety_metrics = self._safety_metrics()
        self.metrics["alarmDeliverySuccessRate"] = safety_metrics["alarmDeliveryRate"]
        self.metrics["emergencyShutdownSuccessRate"] = safety_metrics["emergencyShutdownSuccessRate"]
        self.metrics["plantSafetyScore"] = safety_metrics["overallPlantSafetyScore"]
        self.metrics["sensorAvailability"] = safety_metrics["sensorAvailability"]
        self.metrics["hazardDetectionAccuracy"] = safety_metrics["hazardDetectionAccuracy"]
        self.metrics["emergencyResponseTimeSec"] = safety_metrics["emergencyResponseTimeSec"]
        self.metrics["activeHazards"] = len(self.hazards)
        self.metrics["esdSuccesses"] = self.esd_successes
        self.metrics["esdFailures"] = self.esd_failures

    def _process_new_hazard_alarms(self) -> None:
        for hazard in self.hazards:
            key = f"{hazard['id']}:{hazard['level']}"
            if key in self._announced_hazards:
                continue
            self._announced_hazards.add(key)
            self.alarm_attempts += 1
            delivered = self._alarm_channel_available()
            if delivered:
                self.alarm_deliveries += 1
                self._create_alert(self._alert_level_for_risk(hazard["level"]), hazard["name"])
                self._log_event(f"Hazard Detected: {hazard['name']} ({hazard['level']})")
            else:
                self._log_event(f"Alarm Delivery Failed: {hazard['name']} ({hazard['level']})")

    def _detect_hazards(self) -> List[Dict[str, Any]]:
        hazards: List[Dict[str, Any]] = []
        for sensor in self._sensor_payload():
            if self.RISK_ORDER[sensor["riskLevel"]] < self.RISK_ORDER["YELLOW"]:
                continue
            sensor_id = str(sensor["id"])
            config = self.sensor_configs[sensor_id]
            hazards.append(
                {
                    "id": f"hazard-{sensor_id}",
                    "name": self.HAZARD_LABELS[sensor_id],
                    "domain": config["domain"],
                    "level": sensor["riskLevel"],
                    "sensorId": sensor_id,
                    "reading": sensor["value"],
                    "unit": config["unit"],
                    "threshold": sensor["threshold"],
                    "description": self._hazard_description(sensor_id, sensor["riskLevel"]),
                    "recommendedActions": list(config["actions"]),
                    "detectedAt": datetime.now().strftime("%H:%M:%S"),
                }
            )

        reliability = float(self.metrics.get("reliability", 100.0))
        delay = float(self.metrics.get("delayMs", 0.0))
        packet_loss = float(self.metrics.get("packetLossPercent", 0.0))
        path = self.network.shortest_path(*self.monitored_flow)
        if not path or reliability < 97.0 or delay > self.SAFETY_THRESHOLDS["maxDelayMs"] or packet_loss > 1.0:
            if not path or reliability < 85.0:
                level = "RED"
            elif delay > 220 or packet_loss > 8.0:
                level = "ORANGE"
            else:
                level = "YELLOW"
            hazards.append(
                {
                    "id": "hazard-communication",
                    "name": "Delayed Alarm / Shutdown Communication",
                    "domain": "Industrial Automation",
                    "level": level,
                    "sensorId": "communication",
                    "reading": round(reliability, 2),
                    "unit": "%",
                    "threshold": f">= {self.SAFETY_THRESHOLDS['minReliability']}% reliability",
                    "description": "Communication degradation can delay operator alarms or emergency shutdown commands.",
                    "recommendedActions": [
                        "Switch to redundant path",
                        "Notify control room",
                        "Verify alarm and shutdown acknowledgement",
                    ],
                    "detectedAt": datetime.now().strftime("%H:%M:%S"),
                }
            )

        for node in self.network.nodes.values():
            if node.status != "failed":
                continue
            level = "RED" if node.id in {"B", "C", "E"} else "ORANGE"
            hazards.append(
                {
                    "id": f"hazard-node-{node.id}",
                    "name": f"{node.role} Failure",
                    "domain": "Safety Instrumented System",
                    "level": level,
                    "sensorId": node.id,
                    "reading": "failed",
                    "unit": "",
                    "threshold": "Node must remain active during emergencies",
                    "description": f"{node.label} is unavailable, reducing safety function availability.",
                    "recommendedActions": ["Restore node", "Verify redundant route", "Dispatch maintenance team"],
                    "detectedAt": datetime.now().strftime("%H:%M:%S"),
                }
            )
        return hazards

    def _calculate_risk(self, hazards: List[Dict[str, Any]]) -> Dict[str, Any]:
        level = "GREEN"
        drivers: List[str] = []
        for hazard in hazards:
            hazard_level = str(hazard["level"])
            if self.RISK_ORDER[hazard_level] > self.RISK_ORDER[level]:
                level = hazard_level
            drivers.append(str(hazard["name"]))

        reliability = float(self.metrics.get("reliability", 100.0))
        delay = float(self.metrics.get("delayMs", 0.0))
        packet_loss = float(self.metrics.get("packetLossPercent", 0.0))
        if reliability < 90.0 and self.RISK_ORDER[level] < self.RISK_ORDER["RED"]:
            level = "RED"
            drivers.append("Communication reliability below 90%")
        elif delay > 220.0 and self.RISK_ORDER[level] < self.RISK_ORDER["ORANGE"]:
            level = "ORANGE"
            drivers.append("Emergency response delay above 220 ms")
        elif packet_loss > 1.0 and self.RISK_ORDER[level] < self.RISK_ORDER["YELLOW"]:
            level = "YELLOW"
            drivers.append("Alarm packet loss above safety threshold")

        severe_process_hazard = any(
            hazard["level"] in {"RED", "BLACK"} and hazard["id"] != "hazard-communication" for hazard in hazards
        )
        communication_degraded = reliability < 95.0 or delay > 180.0 or packet_loss > 5.0
        if severe_process_hazard and communication_degraded:
            level = "BLACK"
            drivers.append("Critical process hazard with degraded communication")

        if any(hazard["level"] == "BLACK" for hazard in hazards):
            level = "BLACK"
        if self.last_shutdown_status == "failed":
            level = "BLACK"
            drivers.append("Emergency shutdown delivery failure")
        if self.alarm_suppressed and hazards and self.RISK_ORDER[level] < self.RISK_ORDER["RED"]:
            level = "RED"
            drivers.append("Alarm channel suppressed during hazard")

        score_by_level = {"GREEN": 96.0, "YELLOW": 82.0, "ORANGE": 62.0, "RED": 34.0, "BLACK": 6.0}
        communication_penalty = max(0.0, 99.0 - reliability) * 0.45
        delay_penalty = max(0.0, delay - 150.0) * 0.03
        failed_node_penalty = float(self.metrics.get("failedNodes", 0)) * 4.0
        score = max(0.0, min(100.0, score_by_level[level] - communication_penalty - delay_penalty - failed_node_penalty))
        return {
            "level": level,
            "label": self._risk_label(level),
            "score": round(score, 1),
            "drivers": drivers[:6],
            "hazardCount": len(hazards),
            "shutdownRequired": level == "BLACK",
            "color": self._risk_color(level),
        }

    def _plan_emergency_actions(self, hazards: List[Dict[str, Any]], risk: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not hazards:
            return [
                {
                    "id": "action-monitoring",
                    "name": "Continuous safety monitoring",
                    "target": self.plant_profile["processArea"],
                    "status": "ready",
                    "priority": "GREEN",
                    "owner": "SCADA",
                    "etaSeconds": 0,
                    "reason": "No active hazards",
                }
            ]

        unique_actions: Dict[str, Dict[str, Any]] = {}
        for hazard in hazards:
            for action_name in hazard["recommendedActions"]:
                key = action_name.lower()
                if key in unique_actions:
                    continue
                unique_actions[key] = {
                    "id": f"action-{len(unique_actions) + 1}",
                    "name": action_name,
                    "target": hazard["domain"],
                    "status": self._action_status(action_name, hazard["level"]),
                    "priority": hazard["level"],
                    "owner": self._action_owner(action_name),
                    "etaSeconds": self._estimated_response_seconds(hazard["level"]),
                    "reason": hazard["name"],
                }

        if risk["shutdownRequired"]:
            unique_actions["emergency shutdown command"] = {
                "id": "action-shutdown",
                "name": "Emergency shutdown command",
                "target": "SIS Controller C to SCADA E",
                "status": "completed" if self.shutdown_active else self.last_shutdown_status,
                "priority": "BLACK",
                "owner": "SIS",
                "etaSeconds": self._estimated_response_seconds("BLACK"),
                "reason": "BLACK risk level requires shutdown",
            }
        return list(unique_actions.values())[:10]

    def _simulate_esd(self, force_failure: bool, reason: str) -> None:
        path = self.network.shortest_path("C", "E")
        failed = force_failure or not path
        self.shutdown_attempts += 1
        if failed:
            self.esd_failures += 1
            self.shutdown_failures += 1
            self.metrics["esdFailures"] = self.esd_failures
            self.metrics["packetsSent"] += 1
            self.metrics["packetsLost"] += 1
            self.last_shutdown_status = "failed"
            self.shutdown_active = False
            self._create_alert("critical", "Emergency shutdown command failed to reach SCADA / EOC")
            self._log_event(f"Safety Response: shutdown failed - {reason}")
            return
        self.esd_successes += 1
        self.shutdown_successes += 1
        self.metrics["esdSuccesses"] = self.esd_successes
        self.metrics["packetsSent"] += 1
        self.metrics["packetsReceived"] += 1
        self.last_shutdown_status = "completed"
        self.shutdown_active = True
        self._create_alert("success", "Emergency shutdown command delivered on active route")
        self._log_event(f"Safety Response: shutdown delivered through {' -> '.join(path)}")

    def _safety_status(self) -> Dict[str, Any]:
        reliability = float(self.metrics["reliability"])
        delay = float(self.metrics["delayMs"])
        packet_loss = float(self.metrics["packetLossPercent"])
        violations = list(self.risk_state.get("drivers", []))

        if reliability < self.SAFETY_THRESHOLDS["minReliability"]:
            violations.append("Reliability below safety threshold")
        if delay > self.SAFETY_THRESHOLDS["maxDelayMs"]:
            violations.append("Communication delay above safety threshold")
        if packet_loss > self.SAFETY_THRESHOLDS["maxPacketLossPercent"]:
            violations.append("Packet loss above safety threshold")
        if self.esd_failures > 0:
            violations.append("Emergency shutdown delivery failure recorded")
        if self.alarm_suppressed:
            violations.append("Alarm channel is suppressed")
        if self.false_data_active:
            violations.append("False sensor data scenario is active")
        if self.dos_ticks_remaining > 0:
            violations.append("DoS traffic scenario is active")

        risk_level = self.risk_state.get("level", "GREEN")
        if risk_level in {"RED", "BLACK"}:
            level = "critical"
        elif risk_level in {"YELLOW", "ORANGE"} or violations:
            level = "degraded"
        else:
            level = "normal"

        return {
            "level": level,
            "violations": list(dict.fromkeys(violations))[:8],
            "thresholdsMet": len(violations) == 0 and risk_level == "GREEN",
        }

    def _sensor_payload(self) -> List[Dict[str, Any]]:
        sensor_array_active = self.network.nodes.get("A") is not None and self.network.nodes["A"].status == "active"
        sensors = []
        for sensor_id, config in self.sensor_configs.items():
            value = round(self.sensor_values[sensor_id], 1)
            risk_level = self._sensor_risk_level(sensor_id, value)
            sensors.append(
                {
                    "id": sensor_id,
                    "label": config["label"],
                    "domain": config["domain"],
                    "value": value,
                    "unit": config["unit"],
                    "status": "online" if sensor_array_active else "offline",
                    "riskLevel": risk_level,
                    "normalRange": config["normalRange"],
                    "threshold": self._threshold_label(sensor_id, risk_level),
                    "min": config["min"],
                    "max": config["max"],
                }
            )
        return sensors

    def _scenario_payload(self) -> Dict[str, Any]:
        return {
            "alarmSuppressed": self.alarm_suppressed,
            "falseDataActive": self.false_data_active,
            "dosActive": self.dos_ticks_remaining > 0,
            "activeSafetyScenario": self.active_scenario,
            "activeScenarioLabel": self.SCENARIO_LIBRARY[self.active_scenario]["label"] if self.active_scenario else "Normal Operation",
            "scenarioTicksRemaining": self.scenario_ticks_remaining,
            "shutdownActive": self.shutdown_active,
        }

    def _communication_payload(self, current_path: List[str]) -> Dict[str, Any]:
        alarm_delivery = self._to_percent(self.alarm_deliveries, self.alarm_attempts) if self.alarm_attempts else 100.0
        shutdown_success = self._to_percent(self.shutdown_successes, self.shutdown_attempts) if self.shutdown_attempts else 100.0
        return {
            "safetyCommunicationReliability": round(float(self.metrics.get("reliability", 100.0)), 2),
            "alarmDeliverySuccessRate": alarm_delivery,
            "emergencyShutdownSuccessRate": shutdown_success,
            "averageResponseDelayMs": float(self.metrics.get("delayMs", 0.0)),
            "missedSensorReadings": int(self.metrics.get("packetsLost", 0)),
            "currentPath": current_path,
            "backupRouteActive": self.backup_route_active,
            "alarmChannelSuppressed": self.alarm_suppressed,
        }

    def _safety_metrics(self) -> Dict[str, float]:
        alarm_delivery = self._to_percent(self.alarm_deliveries, self.alarm_attempts) if self.alarm_attempts else 100.0
        shutdown_success = self._to_percent(self.shutdown_successes, self.shutdown_attempts) if self.shutdown_attempts else 100.0
        sensor_availability = 100.0 if self.network.nodes["A"].status == "active" else 0.0
        detection_accuracy = 98.5
        if self.false_data_active:
            detection_accuracy -= 18.0
        if self.alarm_suppressed:
            detection_accuracy -= 12.0
        if float(self.metrics.get("reliability", 100.0)) < 95.0:
            detection_accuracy -= 8.0
        response_time = round(max(0.5, float(self.metrics.get("delayMs", 80.0)) / 1000.0 + len(self.hazards) * 0.22), 2)
        return {
            "overallPlantSafetyScore": float(self.risk_state.get("score", 100.0)),
            "hazardDetectionAccuracy": round(max(0.0, detection_accuracy), 1),
            "alarmDeliveryRate": alarm_delivery,
            "emergencyResponseTimeSec": response_time,
            "emergencyShutdownSuccessRate": shutdown_success,
            "sensorAvailability": sensor_availability,
            "communicationReliability": round(float(self.metrics.get("reliability", 100.0)), 2),
            "meanTimeBetweenFailuresSec": float(self.metrics.get("mtbfSec", 0.0)),
            "meanTimeToRecoverySec": float(self.metrics.get("mttrSec", 0.0)),
        }

    def _scenario_catalog(self) -> List[Dict[str, str]]:
        return [
            {
                "id": scenario_id,
                "label": scenario["label"],
                "environment": scenario["environment"],
                "description": scenario["description"],
            }
            for scenario_id, scenario in self.SCENARIO_LIBRARY.items()
        ]

    def _append_history(self) -> None:
        self.history.append(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "reliability": float(self.metrics["reliability"]),
                "packetLossPercent": float(self.metrics["packetLossPercent"]),
                "delayMs": float(self.metrics["delayMs"]),
                "throughputPps": float(self.metrics["throughputPps"]),
                "riskScore": float(self.risk_state.get("score", 100.0)),
                "riskLevel": str(self.risk_state.get("level", "GREEN")),
                "activeHazards": float(len(self.hazards)),
                "alarmDeliveryRate": float(self.metrics.get("alarmDeliverySuccessRate", 100.0)),
                "shutdownSuccessRate": float(self.metrics.get("emergencyShutdownSuccessRate", 100.0)),
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

    def _sensor_risk_level(self, sensor_id: str, value: float) -> str:
        config = self.sensor_configs[sensor_id]
        thresholds = config["thresholds"]
        if config["direction"] == "low":
            if value <= thresholds["BLACK"]:
                return "BLACK"
            if value <= thresholds["RED"]:
                return "RED"
            if value <= thresholds["ORANGE"]:
                return "ORANGE"
            if value <= thresholds["YELLOW"]:
                return "YELLOW"
            return "GREEN"
        if value >= thresholds["BLACK"]:
            return "BLACK"
        if value >= thresholds["RED"]:
            return "RED"
        if value >= thresholds["ORANGE"]:
            return "ORANGE"
        if value >= thresholds["YELLOW"]:
            return "YELLOW"
        return "GREEN"

    def _threshold_label(self, sensor_id: str, level: str) -> str:
        config = self.sensor_configs[sensor_id]
        if level == "GREEN":
            return config["normalRange"]
        threshold = config["thresholds"][level]
        operator = "<=" if config["direction"] == "low" else ">="
        return f"{operator} {threshold:g} {config['unit']}"

    def _hazard_description(self, sensor_id: str, level: str) -> str:
        descriptions = {
            "temperature": "Temperature is trending beyond safe operating limits.",
            "pressure": "Pressure excursion may challenge containment and relief systems.",
            "toxic_gas": "Gas concentration suggests a chemical leak or toxic release.",
            "radiation": "Radiation level exceeds normal monitoring range.",
            "methane": "Methane concentration is approaching explosive range.",
            "smoke": "Smoke density indicates fire or combustion products.",
            "oxygen": "Oxygen level is unsafe for personnel in the monitored area.",
            "humidity": "Humidity may affect instrumentation or process quality.",
        }
        return f"{descriptions[sensor_id]} Current risk is {level}."

    def _action_status(self, action_name: str, risk_level: str) -> str:
        lowered = action_name.lower()
        if "alarm" in lowered or "siren" in lowered or "notify" in lowered:
            if self.alarm_suppressed:
                return "suppressed"
            if self._alarm_channel_available():
                return "completed" if self.RISK_ORDER[risk_level] >= self.RISK_ORDER["ORANGE"] else "ready"
            return "delayed"
        if "shutdown" in lowered or "trip" in lowered:
            if self.shutdown_active:
                return "completed"
            if self.last_shutdown_status == "failed":
                return "failed"
            return "armed"
        if self.RISK_ORDER[risk_level] >= self.RISK_ORDER["RED"]:
            return "in_progress"
        return "queued"

    def _action_owner(self, action_name: str) -> str:
        lowered = action_name.lower()
        if "shutdown" in lowered or "trip" in lowered:
            return "SIS"
        if "notify" in lowered or "evacuate" in lowered:
            return "Operator"
        if "ventilation" in lowered or "scrubber" in lowered or "suppression" in lowered:
            return "Emergency Response"
        return "PLC"

    def _estimated_response_seconds(self, risk_level: str) -> float:
        base = float(self.metrics.get("delayMs", 80.0)) / 1000.0
        urgency = {"GREEN": 1.5, "YELLOW": 3.0, "ORANGE": 2.0, "RED": 1.2, "BLACK": 0.6}
        return round(base + urgency.get(risk_level, 2.0), 2)

    def _alarm_channel_available(self) -> bool:
        if self.alarm_suppressed:
            return False
        return bool(self.network.shortest_path(*self.monitored_flow)) and float(self.metrics.get("reliability", 100.0)) >= 75.0

    def _shutdown_channel_available(self) -> bool:
        return bool(self.network.shortest_path("C", "E")) and float(self.metrics.get("reliability", 100.0)) >= 80.0

    def _mean_time_between_failures(self) -> float:
        failures = sum(node.fail_count for node in self.network.nodes.values())
        if failures == 0:
            return 0.0
        uptime = sum(node.uptime_seconds for node in self.network.nodes.values())
        return round(uptime / failures, 2)

    def _refresh_node_counts(self) -> None:
        active_nodes = sum(1 for node in self.network.nodes.values() if node.status == "active")
        self.metrics["activeNodes"] = active_nodes
        self.metrics["failedNodes"] = len(self.network.nodes) - active_nodes

    def _mean_time_to_repair(self) -> float:
        repairs = sum(node.repair_count for node in self.network.nodes.values())
        if repairs == 0:
            return 0.0
        downtime = sum(node.downtime_seconds for node in self.network.nodes.values())
        return round(downtime / repairs, 2)

    def _default_plant_profile(self) -> Dict[str, str]:
        return {
            "name": "Integrated Hazardous Process Facility",
            "processArea": "Multi-domain training simulator",
            "mode": "Normal Operation",
            "activeScenario": "Normal Operation",
            "description": "Chemical, nuclear, mining, oil and gas, and hazardous manufacturing safety training.",
        }

    def _default_risk_state(self) -> Dict[str, Any]:
        return {
            "level": "GREEN",
            "label": "Normal",
            "score": 100.0,
            "drivers": [],
            "hazardCount": 0,
            "shutdownRequired": False,
            "color": self._risk_color("GREEN"),
        }

    def _node_label(self, node_id: str) -> str:
        node = self.network.nodes.get(node_id)
        return node.label if node else f"Node {node_id}"

    @staticmethod
    def _risk_label(level: str) -> str:
        return {
            "GREEN": "Normal",
            "YELLOW": "Warning",
            "ORANGE": "Danger",
            "RED": "Critical",
            "BLACK": "Emergency Shutdown Required",
        }[level]

    @staticmethod
    def _risk_color(level: str) -> str:
        return {
            "GREEN": "#10b981",
            "YELLOW": "#eab308",
            "ORANGE": "#f97316",
            "RED": "#ef4444",
            "BLACK": "#020617",
        }[level]

    @staticmethod
    def _alert_level_for_risk(level: str) -> str:
        if level in {"RED", "BLACK"}:
            return "critical"
        if level in {"YELLOW", "ORANGE"}:
            return "warning"
        return "success"

    @staticmethod
    def _move_toward(current: float, target: float, ratio: float) -> float:
        return current + ((target - current) * ratio)

    @staticmethod
    def _clamp(value: float, min_value: float, max_value: float) -> float:
        return max(min_value, min(max_value, value))

    @staticmethod
    def _to_percent(part: int | float, whole: int | float) -> float:
        if whole <= 0:
            return 0.0
        return round((float(part) / float(whole)) * 100.0, 2)

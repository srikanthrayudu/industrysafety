"""
Simulator engine for the industrial network reliability demo.

Provides a Simulator class that runs a background loop to simulate packet
transmission, inject random failures, and compute basic metrics.
"""
import threading
import time
import random
import sqlite3
from typing import Dict, Any, Tuple
import os

from network_model import NetworkState
from mqtt_sim import SimBroker
try:
    import paho.mqtt.client as mqtt
except Exception:
    mqtt = None


class Simulator:
    def __init__(self, net: NetworkState, tick_interval: float = 1.0):
        self.net = net
        self.tick = tick_interval
        self.metrics: Dict[str, Any] = {
            "packetsSent": 0,
            "packetsLost": 0,
            "reliability": 100.0,
        }
        self._running = False
        self._thread = None
        # probability of random failure per tick for each node
        self.random_fail_prob = 0.05
        # persistence (sqlite) setup
        self.db_path = "metrics.db"
        self._ensure_db()

        # routing: store initial primary routes for monitored pairs
        self.monitored_pairs = [("A", "C"), ("B", "D"), ("A", "D")]
        self.primary_routes: Dict[Tuple[str, str], Tuple[str, ...]] = {}
        self._compute_primary_routes()

        # simple in-memory MQTT broker (simulated)
        self.mqtt_mode = False
        self.broker = SimBroker()
        # recent mqtt messages for SSE/UI (list of dicts)
        self.mqtt_messages = []
        self._mqtt_lock = threading.Lock()
        # subscribed topics set (start with sim/metrics)
        self.subscribed_topics = set()
        self.subscribe_topic('sim/metrics')
        # subscribe to simulated broker so incoming messages are captured
        self.broker.subscribe('sim/metrics', self._handle_incoming_mqtt)
        # optional external MQTT broker client
        self.mqtt_client = None
        self.mqtt_broker = os.environ.get("MQTT_BROKER")
        self.mqtt_port = int(os.environ.get("MQTT_BROKER_PORT", "1883"))
        if self.mqtt_broker and mqtt:
            try:
                client = mqtt.Client()
                client.connect(self.mqtt_broker, self.mqtt_port)
                # subscribe to all topics and forward incoming messages into simulated broker
                def _on_message(c, userdata, msg):
                    try:
                        payload = msg.payload.decode('utf-8')
                    except Exception:
                        payload = str(msg.payload)
                    # publish into sim broker which will notify subscribers including _handle_incoming_mqtt
                    try:
                        self.broker.publish(msg.topic, payload)
                    except Exception:
                        pass

                client.on_message = _on_message
                client.subscribe('#')
                client.loop_start()
                self.mqtt_client = client
            except Exception:
                self.mqtt_client = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _run_loop(self):
        while self._running:
            try:
                self.step()
            except Exception:
                # keep the loop alive even if one step fails
                pass
            time.sleep(self.tick)

    def step(self):
        # simulate one time-step: send a few packets between random pairs
        pairs = [("A", "C"), ("B", "D"), ("A", "D")]
        for src, dst in pairs:
            self.metrics["packetsSent"] += 1
            if not self.net.is_connected(src, dst):
                # if no path exists, packet is lost
                self.metrics["packetsLost"] += 1
            else:
                # minor chance of packet loss even on up path
                if random.random() < 0.01:
                    self.metrics["packetsLost"] += 1

        # possibility to inject random node failures
        for nid, node in list(self.net.nodes.items()):
            if node.status == "active" and random.random() < self.random_fail_prob:
                self.net.fail_node(nid)
                # count some immediate packet loss when node fails
                self.metrics["packetsLost"] += 2

        # recompute reliability
        sent = self.metrics.get("packetsSent", 0)
        lost = self.metrics.get("packetsLost", 0)
        if sent > 0:
            self.metrics["reliability"] = 100.0 * (1 - lost / sent)
        else:
            self.metrics["reliability"] = 100.0

        # store metric snapshot in sqlite
        try:
            self._insert_metrics_snapshot()
        except Exception:
            pass

        # publish metrics over MQTT simulation if enabled
        if self.mqtt_mode:
            try:
                self.broker.publish("sim/metrics", dict(self.metrics))
            except Exception:
                pass
        # also publish to external broker if configured
        if self.mqtt_client:
            try:
                self.mqtt_client.publish("sim/metrics", payload=str(dict(self.metrics)))
            except Exception:
                pass

    def inject_failure(self, node_id: str) -> bool:
        ok = self.net.fail_node(node_id)
        if ok:
            # attribute some lost packets when manual failure occurs
            self.metrics["packetsLost"] += 3
        return ok

    def restore(self, node_id: str) -> bool:
        return self.net.restore_node(node_id)

    def reset(self):
        self.net.reset()
        self.metrics = {"packetsSent": 0, "packetsLost": 0, "reliability": 100.0}

    def get_state(self):
        # include routing info: current path for monitored pairs and whether rerouted
        routes = {}
        for a, b in self.monitored_pairs:
            primary = list(self.primary_routes.get((a, b), []))
            current = self.net.shortest_path(a, b)
            rerouted = False
            if primary and current and primary != current:
                rerouted = True
            routes[f"{a}-{b}"] = {"primary": primary, "current": current, "rerouted": rerouted}

        return {
            "nodes": self.net.get_nodes(),
            "links": self.net.get_links(),
            "metrics": self.metrics,
            "routes": routes,
        }

    def enable_mqtt_mode(self, enabled: bool = True):
        self.mqtt_mode = bool(enabled)

    # ---- persistence helpers ----
    def _ensure_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    ts REAL PRIMARY KEY,
                    packetsSent INTEGER,
                    packetsLost INTEGER,
                    reliability REAL
                )
                """
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def _insert_metrics_snapshot(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        ts = time.time()
        cur.execute(
            "INSERT OR REPLACE INTO metrics (ts, packetsSent, packetsLost, reliability) VALUES (?, ?, ?, ?)",
            (ts, int(self.metrics.get("packetsSent", 0)), int(self.metrics.get("packetsLost", 0)), float(self.metrics.get("reliability", 100.0))),
        )
        conn.commit()
        conn.close()

    def query_metrics(self, limit: int = 200):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT ts, packetsSent, packetsLost, reliability FROM metrics ORDER BY ts DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return [ {"ts": r[0], "packetsSent": r[1], "packetsLost": r[2], "reliability": r[3]} for r in rows[::-1] ]

    # ---- routing helpers ----
    def _compute_primary_routes(self):
        for a, b in self.monitored_pairs:
            path = self.net.shortest_path(a, b)
            if path:
                self.primary_routes[(a, b)] = tuple(path)
            else:
                self.primary_routes[(a, b)] = tuple()

    def _handle_incoming_mqtt(self, topic: str, message: any):
        # called when a message is published into the simulated broker
        with self._mqtt_lock:
            self.mqtt_messages.append({"ts": time.time(), "topic": topic, "message": message})
            # keep last 200 messages
            if len(self.mqtt_messages) > 200:
                self.mqtt_messages = self.mqtt_messages[-200:]

    def pop_mqtt_messages(self):
        with self._mqtt_lock:
            msgs = list(self.mqtt_messages)
            self.mqtt_messages = []
        return msgs

    # dynamic topic subscription management
    def subscribe_topic(self, topic: str):
        try:
            if topic in self.subscribed_topics:
                return True
            # subscribe in simulated broker
            self.broker.subscribe(topic, self._handle_incoming_mqtt)
            # if external client exists, subscribe there as well
            if self.mqtt_client:
                try:
                    self.mqtt_client.subscribe(topic)
                except Exception:
                    pass
            self.subscribed_topics.add(topic)
            return True
        except Exception:
            return False

    def unsubscribe_topic(self, topic: str):
        try:
            if topic not in self.subscribed_topics:
                return True
            try:
                self.broker.unsubscribe(topic, self._handle_incoming_mqtt)
            except Exception:
                pass
            if self.mqtt_client:
                try:
                    self.mqtt_client.unsubscribe(topic)
                except Exception:
                    pass
            try:
                self.subscribed_topics.remove(topic)
            except KeyError:
                pass
            return True
        except Exception:
            return False

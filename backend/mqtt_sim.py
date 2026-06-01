"""Simple in-memory MQTT-like broker simulation for demo purposes.

This provides a SimBroker that allows publish(topic, message) and subscription
callbacks (in-process). It is NOT a real MQTT broker; it's a simulation for the
educational demo and for driving UI behavior.
"""
from typing import Callable, Dict, List, Any
import threading


class SimBroker:
    def __init__(self):
        self.topics: Dict[str, List[Dict[str, Any]]] = {}
        self.subscribers: Dict[str, List[Callable[[str, Any], None]]] = {}
        self.lock = threading.Lock()

    def publish(self, topic: str, message: Any):
        with self.lock:
            self.topics.setdefault(topic, []).append({"message": message})
            # keep only recent 100 messages per topic
            if len(self.topics[topic]) > 100:
                self.topics[topic] = self.topics[topic][-100:]
            # notify subscribers
            for cb in self.subscribers.get(topic, []):
                try:
                    cb(topic, message)
                except Exception:
                    pass

    def get_messages(self, topic: str, limit: int = 50):
        with self.lock:
            msgs = self.topics.get(topic, [])
            return msgs[-limit:]

    def subscribe(self, topic: str, callback: Callable[[str, Any], None]):
        with self.lock:
            self.subscribers.setdefault(topic, []).append(callback)

    def unsubscribe(self, topic: str, callback: Callable[[str, Any], None]):
        with self.lock:
            subs = self.subscribers.get(topic)
            if not subs:
                return
            try:
                subs.remove(callback)
            except ValueError:
                pass


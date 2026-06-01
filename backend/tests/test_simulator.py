from network import NetworkState
from simulator import Simulator


def test_fail_restore_reset():
    network = NetworkState()
    simulator = Simulator(network, tick_interval=0.01)

    assert network.is_connected("A", "E")

    assert network.fail_node("B")
    assert network.nodes["B"].status == "failed"
    assert network.is_connected("A", "E")

    assert network.restore_node("B")
    assert network.nodes["B"].status == "active"
    assert network.is_connected("A", "E")

    network.fail_node("D")
    simulator.reset()
    assert all(node.status == "active" for node in network.nodes.values())
    assert simulator.metrics["packetsSent"] == 0


def test_step_updates_metrics():
    network = NetworkState()
    simulator = Simulator(network, tick_interval=0.01)

    simulator.step()
    simulator.step()

    assert simulator.metrics["packetsSent"] > 0
    assert "reliability" in simulator.metrics
    assert len(simulator.get_history()) >= 1


def test_safety_and_cyber_scenarios_update_state():
    network = NetworkState()
    simulator = Simulator(network, tick_interval=0.01)

    assert simulator.inject_event("false_data", {"value": 41.0})
    state = simulator.get_state()
    sensor = next(node for node in state["nodes"] if node["id"] == "A")
    assert sensor["reading"] == 41.0
    assert state["scenario"]["falseDataActive"] is True

    assert simulator.inject_event("alarm_suppression", {"enabled": True})
    assert simulator.get_state()["scenario"]["alarmSuppressed"] is True

    assert simulator.inject_event("dos", {"durationTicks": 2})
    simulator.step()
    assert simulator.get_state()["scenario"]["dosActive"] is True

    assert simulator.inject_event("esd_command", {})
    assert simulator.metrics["esdSuccesses"] == 1


def test_link_failure_activates_backup_route():
    network = NetworkState()
    simulator = Simulator(network, tick_interval=0.01)

    assert simulator.inject_link_failure("B", "C")
    simulator.step()
    state = simulator.get_state()

    assert state["routes"]["backupActive"] is True
    assert state["routes"]["current"] != state["routes"]["primary"]


def test_state_includes_protocols_and_safety_thresholds():
    network = NetworkState()
    simulator = Simulator(network, tick_interval=0.01)
    state = simulator.get_state()

    assert all("protocol" in link for link in state["links"])
    assert state["thresholds"]["minReliability"] == 99.0
    assert state["safety"]["level"] == "normal"


def test_chemical_leak_creates_hazards_and_actions():
    network = NetworkState()
    simulator = Simulator(network, tick_interval=0.01)

    assert simulator.inject_event("chemical_leak", {})
    state = simulator.get_state()

    assert state["project"]["name"] == "Smart Industrial Safety Monitoring and Emergency Response Simulator"
    assert state["scenario"]["activeSafetyScenario"] == "chemical_leak"
    assert any(sensor["id"] == "toxic_gas" for sensor in state["sensors"])
    assert len(state["hazards"]) >= 1
    assert state["risk"]["level"] in {"YELLOW", "ORANGE", "RED", "BLACK"}
    assert len(state["emergency"]["actions"]) >= 1


def test_communication_loss_shutdown_tracks_shutdown_failure():
    network = NetworkState()
    simulator = Simulator(network, tick_interval=0.01)

    assert simulator.inject_event("communication_loss_shutdown", {})
    state = simulator.get_state()

    assert state["emergency"]["lastShutdownStatus"] == "failed"
    assert state["metrics"]["esdFailures"] == 1
    assert state["risk"]["level"] == "BLACK"

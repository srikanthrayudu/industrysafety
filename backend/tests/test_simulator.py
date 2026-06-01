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

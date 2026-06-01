import pytest
from network_model import NetworkState
from simulator import Simulator


def test_fail_restore_reset():
    net = NetworkState()
    sim = Simulator(net, tick_interval=0.01)

    # initial connectivity A->C should be True
    assert net.is_connected('A', 'C')

    # fail node B and ensure links deactivated
    assert net.fail_node('B')
    assert net.nodes['B'].status == 'failed'
    for l in net.links:
        if l.source == 'B' or l.target == 'B':
            assert not l.active

    # restore B
    assert net.restore_node('B')
    assert net.nodes['B'].status == 'active'
    for l in net.links:
        if l.source == 'B' or l.target == 'B':
            assert l.active

    # reset
    net.fail_node('A')
    sim.reset()
    for n in net.nodes.values():
        assert n.status == 'active'


def test_simulator_metrics():
    net = NetworkState()
    sim = Simulator(net, tick_interval=0.01)
    # run a few steps
    sim.step()
    sim.step()
    assert sim.metrics['packetsSent'] >= 2
    assert 'reliability' in sim.metrics


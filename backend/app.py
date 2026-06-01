"""Flask API for the Industrial Communication Reliability Simulator."""
from flask import Flask, jsonify, request
from flask_cors import CORS
import atexit

from network_model import NetworkState
from simulator import Simulator
import json
import time
from flask import Response


app = Flask(__name__)
CORS(app)

net = NetworkState()
sim = Simulator(net)


@app.route("/network/status", methods=["GET"])
def get_status():
    return jsonify(sim.get_state())


@app.route("/simulate/failure", methods=["POST"])
def simulate_failure():
    data = request.get_json() or {}
    node_id = data.get("nodeId")
    if not node_id:
        return jsonify({"error": "nodeId is required"}), 400
    ok = sim.inject_failure(node_id)
    if not ok:
        return jsonify({"error": "Invalid nodeId"}), 400
    return jsonify({"message": f"Node {node_id} failed", **sim.get_state()})


@app.route("/simulate/restore", methods=["POST"])
def simulate_restore():
    data = request.get_json() or {}
    node_id = data.get("nodeId")
    if not node_id:
        return jsonify({"error": "nodeId is required"}), 400
    ok = sim.restore(node_id)
    if not ok:
        return jsonify({"error": "Invalid nodeId"}), 400
    return jsonify({"message": f"Node {node_id} restored", **sim.get_state()})


@app.route("/reset", methods=["POST"])
def reset():
    sim.reset()
    return jsonify({"message": "Network reset", **sim.get_state()})


@app.route("/simulate/random", methods=["POST"])
def set_random_failure():
    data = request.get_json() or {}
    prob = data.get("probability")
    if prob is None:
        return jsonify({"error": "probability is required (0.0-1.0)"}), 400
    try:
        p = float(prob)
    except Exception:
        return jsonify({"error": "invalid probability value"}), 400
    if p < 0 or p > 1:
        return jsonify({"error": "probability must be between 0 and 1"}), 400
    sim.random_fail_prob = p
    return jsonify({"message": "random failure probability set", "probability": p})


@app.route('/events')
def stream_events():
    """Server-Sent Events endpoint that streams the simulator state every tick.

    Frontend can connect to `/events` and receive `data: <json>\n\n` messages.
    """
    def event_stream():
                while True:
                    try:
                        # First, yield any pending mqtt messages as named events
                        try:
                            mqtt_msgs = sim.pop_mqtt_messages()
                            for m in mqtt_msgs:
                                yield f"event: mqtt\n"
                                yield f"data: {json.dumps(m)}\n\n"
                        except Exception:
                            pass

                        # Then yield the current state as a 'state' event
                        payload = json.dumps(sim.get_state())
                        yield f"event: state\n"
                        yield f"data: {payload}\n\n"
                        time.sleep(sim.tick)
                    except GeneratorExit:
                        break

    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/metrics/history', methods=['GET'])
def metrics_history():
    try:
        limit = int(request.args.get('limit', '200'))
    except Exception:
        limit = 200
    data = sim.query_metrics(limit=limit)
    return jsonify({"history": data})


@app.route('/mqtt/publish', methods=['POST'])
def mqtt_publish():
    data = request.get_json() or {}
    topic = data.get('topic')
    msg = data.get('message')
    if not topic:
        return jsonify({'error': 'topic is required'}), 400
    sim.broker.publish(topic, msg)
    return jsonify({'message': 'published', 'topic': topic})


@app.route('/mqtt/messages', methods=['GET'])
def mqtt_messages():
    topic = request.args.get('topic')
    if not topic:
        return jsonify({'error': 'topic is required'}), 400
    limit = int(request.args.get('limit', '50'))
    msgs = sim.broker.get_messages(topic, limit=limit)
    return jsonify({'topic': topic, 'messages': msgs})


@app.route('/mqtt/mode', methods=['POST'])
def mqtt_mode():
    data = request.get_json() or {}
    enabled = bool(data.get('enabled', True))
    sim.enable_mqtt_mode(enabled)
    return jsonify({'mqtt_mode': sim.mqtt_mode})


@app.route('/mqtt/subscribe', methods=['POST'])
def mqtt_subscribe():
    data = request.get_json() or {}
    topic = data.get('topic')
    if not topic:
        return jsonify({'error': 'topic is required'}), 400
    ok = sim.subscribe_topic(topic)
    if not ok:
        return jsonify({'error': 'failed to subscribe'}), 500
    return jsonify({'message': 'subscribed', 'topic': topic})


@app.route('/mqtt/unsubscribe', methods=['POST'])
def mqtt_unsubscribe():
    data = request.get_json() or {}
    topic = data.get('topic')
    if not topic:
        return jsonify({'error': 'topic is required'}), 400
    ok = sim.unsubscribe_topic(topic)
    if not ok:
        return jsonify({'error': 'failed to unsubscribe'}), 500
    return jsonify({'message': 'unsubscribed', 'topic': topic})


def _shutdown():
    try:
        sim.stop()
    except Exception:
        pass


if __name__ == "__main__":
    # start simulator background loop
    sim.start()
    atexit.register(_shutdown)
    # run flask dev server on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)

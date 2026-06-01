"""HTTP routes for simulator controls and monitoring data."""

from flask import Blueprint, jsonify, request

from simulator import Simulator


def create_api_blueprint(simulator: Simulator) -> Blueprint:
    api = Blueprint("api", __name__)

    @api.get("/network/status")
    def network_status():
        return jsonify(simulator.get_state())

    @api.post("/simulate/failure")
    def simulate_failure():
        payload = request.get_json(silent=True) or {}
        node_id = payload.get("nodeId")
        if not node_id:
            return jsonify({"error": "nodeId is required"}), 400
        if not simulator.inject_failure(str(node_id)):
            return jsonify({"error": "Invalid nodeId"}), 400
        return jsonify(simulator.get_state())

    @api.post("/simulate/restore")
    def simulate_restore():
        payload = request.get_json(silent=True) or {}
        node_id = payload.get("nodeId")
        if not node_id:
            return jsonify({"error": "nodeId is required"}), 400
        if not simulator.restore_node(str(node_id)):
            return jsonify({"error": "Invalid nodeId"}), 400
        return jsonify(simulator.get_state())

    @api.post("/simulate/random")
    def set_random_failure():
        payload = request.get_json(silent=True) or {}
        probability = payload.get("probability")
        if probability is None:
            return jsonify({"error": "probability is required"}), 400
        try:
            parsed = float(probability)
        except (TypeError, ValueError):
            return jsonify({"error": "probability must be numeric"}), 400
        if parsed < 0.0 or parsed > 1.0:
            return jsonify({"error": "probability must be between 0 and 1"}), 400
        simulator.set_random_failure_probability(parsed)
        return jsonify({"probability": parsed})

    @api.post("/reset")
    def reset():
        simulator.reset()
        return jsonify(simulator.get_state())

    @api.get("/metrics/history")
    def metrics_history():
        limit = request.args.get("limit", default=60, type=int)
        limit = max(1, min(limit, 500))
        return jsonify({"history": simulator.get_history(limit)})

    @api.get("/alerts")
    def alerts():
        limit = request.args.get("limit", default=40, type=int)
        limit = max(1, min(limit, 500))
        return jsonify({"alerts": simulator.get_alerts(limit)})

    @api.get("/logs")
    def logs():
        limit = request.args.get("limit", default=100, type=int)
        limit = max(1, min(limit, 1000))
        return jsonify({"logs": simulator.get_logs(limit)})

    return api

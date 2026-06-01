"""Flask app entrypoint for Industrial Communication Reliability Monitoring System."""

from __future__ import annotations

import atexit
import os

from flask import Flask
from flask_cors import CORS

from network import NetworkState
from routes import create_api_blueprint
from simulator import Simulator


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    network = NetworkState()
    simulator = Simulator(network)
    simulator.start()
    atexit.register(simulator.stop)

    app.config["simulator"] = simulator
    app.register_blueprint(create_api_blueprint(simulator))
    return app


app = create_app()


if __name__ == "__main__":
    debug_enabled = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug_enabled, use_reloader=False)

import os
from flask import Flask, jsonify, Response
import config
import json
import time
from blueprints.activities import activities


def create_app():
    app = Flask(__name__)
    app.register_blueprint(activities)

    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify(error=str(e)), 404

    @app.errorhandler(405)
    def resource_not_found(e):
        return jsonify(error=str(e)), 405

    @app.errorhandler(401)
    def custom_401(error):
        return Response("API Key required.", 401)

    @app.route("/version", methods=["GET"], strict_slashes=False)
    def version():
        response_body = {
            "success": 1,
        }
        return jsonify(response_body)

    @app.route("/ping")
    def hello_world():
        response_body = {
            "success": 1,
            "payload": "pong"
        }
        return jsonify(response_body)

    @app.after_request
    def after_request(response):
        if response and response.get_json():
            data = response.get_json()
            data["time_request"] = int(time.time())
            data["version"] = config.VERSION

            response.set_data(json.dumps(data))

            return response

    return app


app = create_app()

if __name__ == "__main__":
    print(" Starting app...")
    app.run(debug=True, host="0.0.0.0", port=5555)

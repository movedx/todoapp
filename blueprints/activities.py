import config
import json

from flask import Blueprint, jsonify, request
from utils.utils import generic_api_requests

activities = Blueprint(
    name="activities", import_name=__name__, url_prefix="/api/v1/activities")


# That Blueprint’s mission is only to receive an API call, call an external API and respond to the initial caller.
# curl -X POST -H 'Content-Type: application/json' 127.0.0.1:5555/api/v1/activities -d '{"test": "1"}'
@activities.route("/", methods=["POST"], strict_slashes=False)
def create_activity():
    try:

        request_body = request.get_json()

        is_success, response = generic_api_requests(
            "POST", config.URL_ACTIVITIES, request_body
        )

        response_body = {
            "success": is_success,
            "data": response["json"] if is_success else {"message": str(response)},
        }

        return jsonify(response_body)

    except Exception as error:

        response_body = {
            "success": 0,
            "data": {"message": "Error : {}".format(error)},
        }

        return jsonify(response_body), 400

import config
from flask import Blueprint, jsonify, request, Response, g, redirect, render_template, url_for
from utils.utils import generic_api_requests, hash_password
import json
import time
import uuid
from database import db, User


activities = Blueprint(
    name="activities", import_name=__name__, url_prefix="")


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


@activities.before_request
def before_request_func():
    execution_id = uuid.uuid4()
    g.start_time = time.time()
    g.execution_id = execution_id

    print(g.execution_id, "ROUTE CALLED", request.url)


@activities.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@activities.errorhandler(405)
def resource_not_found(e):
    return jsonify(error=str(e)), 405


@activities.errorhandler(401)
def custom_401(error):
    return Response("API Key required.", 401)


@activities.route("/version", methods=["GET"], strict_slashes=False)
def version():
    response_body = {
        "success": 1,
    }
    return jsonify(response_body)


@activities.route("/ping")
def pong():
    response_body = {
        "success": 1,
        "payload": "pong"
    }
    return jsonify(response_body)


@activities.route("/users")
def user_list():
    users = db.session.execute(
        db.select(User).order_by(User.username)).scalars()
    return render_template("user/list.html", users=users)


@activities.route("/users/create", methods=["GET", "POST"])
def user_create():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            email=request.form["email"],
            password=hash_password(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("activities.user_detail", id=user.id))

    return render_template("user/create.html")


@activities.route("/user/<int:id>")
def user_detail(id):
    user = db.get_or_404(User, id)
    return render_template("user/detail.html", user=user)


@activities.route("/user/<int:id>/delete", methods=["GET", "POST"])
def user_delete(id):
    user = db.get_or_404(User, id)

    if request.method == "POST":
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("activities.user_list"))

    return render_template("user/delete.html", user=user)


@activities.after_request
def after_request(response):
    if response.headers.get('Content-Type').startswith('activitieslication/json'):
        data = response.get_json()
        data["time_request"] = int(time.time())
        data["version"] = config.VERSION

        response.set_data(json.dumps(data))

        return response
    return response

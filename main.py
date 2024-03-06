import os
from flask import Flask, jsonify, Response, g, redirect, render_template, request, url_for
import config
import json
import time
from blueprints.activities import activities
import uuid
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy


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

    @app.before_request
    def before_request_func():
        execution_id = uuid.uuid4()
        g.start_time = time.time()
        g.execution_id = execution_id

        print(g.execution_id, "ROUTE CALLED", request.url)


    @app.route("/users")
    def user_list():
        users = db.session.execute(db.select(User).order_by(User.username)).scalars()
        return render_template("user/list.html", users=users)
    

    @app.route("/users/create", methods=["GET", "POST"])
    def user_create():
        if request.method == "POST":
            user = User(
                username=request.form["username"],
                email=request.form["email"],
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("user_detail", id=user.id))

        return render_template("user/create.html")
    

    @app.route("/user/<int:id>")
    def user_detail(id):
        user = db.get_or_404(User, id)
        return render_template("user/detail.html", user=user)
    

    @app.route("/user/<int:id>/delete", methods=["GET", "POST"])
    def user_delete(id):
        user = db.get_or_404(User, id)

        if request.method == "POST":
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for("user_list"))

        return render_template("user/delete.html", user=user)
    
    
    @app.after_request
    def after_request(response):
        if response.headers.get('Content-Type').startswith('application/json'):
            data = response.get_json()
            data["time_request"] = int(time.time())
            data["version"] = config.VERSION

            response.set_data(json.dumps(data))

            return response
        return response

    return app


load_dotenv()


def create_db(app):
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PW = os.getenv("POSTGRES_PW")
    POSTGRES_DB = os.getenv("POSTGRES_DB")

    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

    db = SQLAlchemy(app)
    return db


app = create_app()
db = create_db(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    print(" Starting app...")
    app.run(debug=True, host="0.0.0.0", port=5555)

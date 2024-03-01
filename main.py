import os
from flask import Flask, jsonify, Response

def create_app():
  app = Flask(__name__)

  @app.errorhandler(404)
  def resource_not_found(e):
    return jsonify(error=str(e)), 404

  @app.errorhandler(405)
  def resource_not_found(e):
    return jsonify(error=str(e)), 405

  @app.errorhandler(401)
  def custom_401(error):
    return Response("API Key required.", 401)
  
  @app.route("/ping")
  def hello_world():
     return "pong"
  
  return app
  
app = create_app()

if __name__ == "__main__":
  #    app = create_app()
  print(" Starting app...")
  app.run(host="0.0.0.0", port=5555)
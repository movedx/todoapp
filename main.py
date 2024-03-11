from flask import Flask

app = Flask(__name__)

from blueprints.activities import activities
app.register_blueprint(activities)

if __name__ == "__main__":
    print(" Starting app...")
    app.run(debug=True, host="0.0.0.0", port=5555)

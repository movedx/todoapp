import config
import json
import time
import uuid
from flask import Flask, Response, g, jsonify, request
# from flask_talisman import Talisman

import ssl
ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
ctx.load_cert_chain('cert.pem', 'key.pem')

app = Flask(__name__)

# Talisman(app)

from blueprints.routes_non_auth import routes_non_auth
app.register_blueprint(routes_non_auth)

from blueprints.routes_auth import routes_auth
app.register_blueprint(routes_auth)


@app.before_request
def before_request_func():
    execution_id = uuid.uuid4()
    g.start_time = time.time()
    g.execution_id = execution_id

    print(g.execution_id, 'ROUTE CALLED', request.url)


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(405)
def resource_not_found(e):
    return jsonify(error=str(e)), 405


@app.errorhandler(401)
def custom_401(error):
    return Response('API Key required.', 401)


@app.after_request
def after_request(response):
    if response.headers.get('Content-Type').startswith('application/json'):
        data = response.get_json()
        data['time_request'] = int(time.time())
        data['version'] = config.VERSION

        response.set_data(json.dumps(data))

        return response
    return response


if __name__ == '__main__':
    print(' Starting app...')
    app.run(host='0.0.0.0', port=443, ssl_context=ctx)

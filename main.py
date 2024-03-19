import config
import json
import time
import uuid
from flask import Flask, Response, g, jsonify, request
from flask_talisman import Talisman

import ssl
ctx = ssl.create_default_context()
ctx.load_cert_chain('cert.pem', 'key.pem')

app = Flask(__name__)

csp = {
    'default-src': [
        '\'self\'',
    ],
    'script-src': [
        '\'self\'',
        '\'unsafe-inline\'',  # Allows the use of inline scripts
        # '\'unsafe-eval\'',    # Allows the use of eval()
        # 'https://js.example.com',  # Allow JS from this source
    ],
    'style-src': [
        '\'self\'',
        '\'unsafe-inline\'',  # Allows the use of inline styles
        'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.2/css/bulma.min.css',  # Allow CSS from this source
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',

    ],
}

Talisman(app, content_security_policy=csp)

Talisman(app)

from blueprints.routes import routes
app.register_blueprint(routes)


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

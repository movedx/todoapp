from flask_login import logout_user
import config
from flask import Blueprint, jsonify, request, redirect, render_template, url_for
from utils.utils import generic_api_requests
from database import db, User
from werkzeug.security import generate_password_hash


routes_non_auth = Blueprint(
    name='routes_non_auth', import_name=__name__, url_prefix='/')


# That Blueprint’s mission is only to receive an API call, call an external API and respond to the initial caller.
# curl -X POST -H 'Content-Type: application/json' 127.0.0.1:5555/api/v1/routes_non_auth -d '{'test': '1'}'
@routes_non_auth.route('/', methods=['POST'], strict_slashes=False)
def create_activity():
    try:

        request_body = request.get_json()

        is_success, response = generic_api_requests('POST', config.URL_routes_non_auth, request_body)

        response_body = {
            'success': is_success,
            'data': response['json'] if is_success else {'message': str(response)},
        }

        return jsonify(response_body)

    except Exception as error:

        response_body = {
            'success': 0,
            'data': {'message': 'Error : {}'.format(error)},
        }

        return jsonify(response_body), 400


@routes_non_auth.route('/version', methods=['GET'], strict_slashes=False)
def version():
    response_body = {
        'success': 1,
    }
    return jsonify(response_body)


@routes_non_auth.route('/')
def index():
    return render_template('index.html')


@routes_non_auth.route('/ping')
def pong():
    response_body = {
        'success': 1,
        'payload': 'pong'
    }
    return jsonify(response_body)


@routes_non_auth.route('/users')
def user_list():
    users = db.session.execute(db.select(User).order_by(User.username)).scalars()
    return render_template('user/list.html', users=users)


@routes_non_auth.route('/users/create', methods=['GET', 'POST'])
def user_create():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password'])
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('routes_non_auth.user_detail', id=user.id))

    return render_template('user/create.html')


@routes_non_auth.route('/user/<int:id>')
def user_detail(id):
    user = db.get_or_404(User, id)
    return render_template('user/detail.html', user=user)


@routes_non_auth.route('/user/<int:id>/delete', methods=['GET', 'POST'])
def user_delete(id):
    user = db.get_or_404(User, id)

    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('routes_non_auth.user_list'))

    return render_template('user/delete.html', user=user)

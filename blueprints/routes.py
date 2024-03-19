from flask import Blueprint, json, jsonify, redirect, render_template, request, url_for, flash
import requests
from database import db, User, Todo, get_google_provider_cfg, client, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required, login_user, logout_user
import secrets
import config

from utils.utils import generic_api_requests


routes = Blueprint(name='routes', import_name=__name__)


@routes.route('/login_google', methods=['GET', 'POST'])
def login_google():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="https://localhost/login/callback",
        scope=["email"],
        prompt="consent",
    )
    return redirect(request_uri)


@routes.route('/login/callback')
def authorized():

    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        # unique_id = userinfo_response.json()["sub"]
        users_email: str = userinfo_response.json()["email"]
        # picture = userinfo_response.json()["picture"]
        # users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User.query.filter_by(email=users_email).first()
    if not user:
        # Create a new user with information from Google
        # The resulting password will have password length of password_length * 1.3.
        # The text is Base64 encoded, so on average each byte results in approximately 1.3 characters.
        password_length = 14
        user = User(email=users_email, username=users_email.split("@")[0],
                    password=generate_password_hash(secrets.token_urlsafe(password_length), method='scrypt'))
        db.session.add(user)
        db.session.commit()

    login_user(user)

    return redirect(url_for('routes.profile'))


@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again')
            return redirect(url_for('routes.login'))

        login_user(user, remember=remember)
        return redirect(url_for('routes.profile'))

    return render_template('login.html')


@routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('routes.signup'))

        new_user = User(email=email, username=username, password=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('routes.login'))

    return render_template('signup.html')


@routes.route('/profile')
@login_required
def profile():
    user = User.query.get(current_user.id)
    todos = user.todos.all()
    return render_template('user/profile.html', username=current_user.username, todos=todos)


@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))


@routes.route('/create_todo', methods=['POST'])
@login_required
def create_toodo():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        new_todo = Todo(title=title, description=description, user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('routes.profile'))


@routes.route('/delete_todo', methods=['POST'])
@login_required
def delete_todo():
    if request.method == 'POST':
        todo_id = request.form.get('todo_id')

        todo_to_delete = Todo.query.get(todo_id)

        if todo_to_delete and todo_to_delete.user_id == current_user.id:
            db.session.delete(todo_to_delete)
            db.session.commit()
            flash('Todo deleted successfully', 'success')
        else:
            flash('Todo not found or you do not have permission to delete it', 'error')

        return redirect(url_for('routes.profile'))


@routes.route('/complete_todo', methods=['POST'])
@login_required
def complete_todo():
    if request.method == 'POST':
        todo_id = request.form.get('todo_id')

        todo_to_complete = Todo.query.get(todo_id)
        if todo_to_complete.is_completed == True:
            todo_to_complete.is_completed = False
            db.session.commit()

            return redirect(url_for('routes.profile'))
        if todo_to_complete and todo_to_complete.user_id == current_user.id:
            todo_to_complete.is_completed = True
            db.session.commit()
        else:
            flash('Todo not found or you do not have permission to mark it as completed', 'error')

    return redirect(url_for('routes.profile'))


# That Blueprint’s mission is only to receive an API call, call an external API and respond to the initial caller.
# curl -X POST -H 'Content-Type: application/json' 127.0.0.1:5555/api/v1/routes -d '{'test': '1'}'
@routes.route('/', methods=['POST'], strict_slashes=False)
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


@routes.route('/version', methods=['GET'], strict_slashes=False)
def version():
    response_body = {
        'success': 1,
    }
    return jsonify(response_body)


@routes.route('/')
def index():
    return render_template('index.html')


@routes.route('/ping')
def pong():
    response_body = {
        'success': 1,
        'payload': 'pong'
    }
    return jsonify(response_body)

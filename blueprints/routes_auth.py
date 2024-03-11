from flask import Blueprint, redirect, render_template, request, url_for, flash
from database import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required, login_user, logout_user

routes_auth = Blueprint(name='routes_auth', import_name=__name__)


@routes_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again')
            return redirect(url_for('routes_auth.login'))

        login_user(user, remember=remember)
        return redirect(url_for('routes_auth.profile'))

    return render_template('login.html')


@routes_auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('routes_auth.signup'))

        new_user = User(email=email, username=username, password=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('routes_auth.login'))

    return render_template('signup.html')


@routes_auth.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', username=current_user.username)


@routes_auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes_non_auth.index'))

from flask import Blueprint, redirect, render_template, request, url_for, flash
from database import db, User, Todo
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
    user = User.query.get(current_user.id)
    todos = user.todos.all()
    return render_template('user/profile.html', username=current_user.username, todos=todos)


@routes_auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes_non_auth.index'))


@routes_auth.route('/create_todo', methods=['POST'])
@login_required
def create_toodo():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        new_todo = Todo(title=title, description=description, user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('routes_auth.profile'))



@routes_auth.route('/delete_todo', methods=['POST'])
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
    
            return redirect(url_for('routes_auth.profile'))
        
@routes_auth.route('/complete_todo', methods=['POST'])
@login_required
def complete_todo():
    if request.method == 'POST':
        todo_id = request.form.get('todo_id')

        todo_to_complete = Todo.query.get(todo_id)
        if todo_to_complete.is_completed == True:
            todo_to_complete.is_completed = False
            db.session.commit()
            flash('Todo marked as completed', 'success')

            return redirect(url_for('routes_auth.profile'))
        if todo_to_complete and todo_to_complete.user_id == current_user.id:
            todo_to_complete.is_completed = True
            db.session.commit()
            flash('Todo marked as completed', 'success')
        else:
            flash('Todo not found or you do not have permission to mark it as completed', 'error')
    
    return redirect(url_for('routes_auth.profile'))
    
from flask_sqlalchemy import SQLAlchemy
from main import app
import os
from flask_login import UserMixin, LoginManager
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

POSTGRES_URL = os.getenv('POSTGRES_URL')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PW = os.getenv('POSTGRES_PW')
POSTGRES_DB = os.getenv('POSTGRES_DB')

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL, db=POSTGRES_DB)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
# silence the deprecation warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = False
app.config['LOGIN_DISABLED'] = False

app.secret_key = os.getenv('APP_SECRET_KEY')

db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String)
    password = db.Column(db.String(200), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy='dynamic')


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=1)


login_manager = LoginManager()
login_manager.login_view = 'routes_auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


with app.app_context():
    db.create_all()

    # user1 = User(email='user1@example.com', username='username1', password=generate_password_hash('username1', method='scrypt'))
    # user2 = User(email='user2@example.com', username='username2', password=generate_password_hash('username2', method='scrypt'))
    # user3 = User(email='user3@example.com', username='username3', password=generate_password_hash('username3', method='scrypt'))

    # db.session.add_all([user1, user2, user3])
    # db.session.commit()

    # todo1 = Todo(title='Title 1', description='Description todo 1', user_id=str(User.query.filter_by(email='user1@example.com').first().id))
    # todo2 = Todo(title='Title 2', description='Description todo 2', user_id=str(
    #     User.query.filter_by(email='user1@example.com').first().id), is_completed=True)
    # todo3 = Todo(title='Title 3', description='Description todo 3', user_id=str(User.query.filter_by(email='user2@example.com').first().id))
    # todo4 = Todo(title='Title 4', description='Description todo 4', user_id=str(
    #     User.query.filter_by(email='user3@example.com').first().id), priority=10)

    # db.session.add_all([todo1, todo2, todo3, todo4])
    # db.session.commit()

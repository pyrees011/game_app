from flask import Flask
import os
from flask_login import LoginManager, current_user
from .events import socketio

def create_app():
    app = Flask(__name__)
    app.secret_key = 'secret'
    app.config['secret_key'] = os.getenv("Secret_key")
    app.config['DEBUG'] = True

    from .views import views
    from .auth import auth
    from .mongo import mongo

    socketio.init_app(app)
    app.register_blueprint(auth, url_prefix = "/")
    app.register_blueprint(views, url_prefix = "/")
    app.register_blueprint(mongo, url_prefix = "/")

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User
    from .sqlite import getUserById

    @login_manager.user_loader
    def load_user(id):
        data = getUserById(id)
        if data:
            cur_user = User(id=data[0][0], username=data[0][1], password=data[0][2], email=data[0][3])
            return cur_user

    return app


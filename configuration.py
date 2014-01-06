import flask
from app import app
from models import User

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'LTjzysF0RfSPmmBd'
app.config['FORBID_MODIFY_PAST']=True

import flask_wtf
csrf_protector =flask_wtf.csrf.CsrfProtect(app)
@csrf_protector.error_handler
def csrf_error(reason):
    return "Bad CSRF token: "+reason, 400

from flask.ext.login import LoginManager
login_manager = flask.ext.login.LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

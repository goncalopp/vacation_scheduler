from flask import Flask, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, current_user

import flask_wtf
from flask_wtf import Form
import wtforms
from wtforms.validators import ValidationError, required
from wtforms.fields import TextField, PasswordField
import datetime
import json

DATE_FORMAT="%Y-%m-%dT%H:%M:%SZ"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'LTjzysF0RfSPmmBd'

db = SQLAlchemy(app)

csrf=flask_wtf.csrf.CsrfProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)

@csrf.error_handler
def csrf_error(reason):
    return "Bad CSRF token: "+reason, 400

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


class NewVacationForm(Form):
    def validate_date(form, date_field):
        try:
            datetime.datetime.strptime(date_field.data, DATE_FORMAT)
        except ValueError:
            raise ValidationError('Bad date format')
    date = TextField('date', [required(message="date missing"), validate_date])

class LoginForm(Form):
    username = TextField('Username', [required(message="No username provided"), wtforms.validators.Length(max=30)])
    password = PasswordField('Password', [required(message="No password provided"), wtforms.validators.Length(max=30)])
    

class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date= db.Column(db.Date)

    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return str(self.date)
        
def vacations_to_json(vacations):
    def craft_dict(vacation, title="my_user"):
        return {"start":vacation.date.strftime(DATE_FORMAT), "title": "my event"}
    return json.dumps(map(craft_dict, vacations))

class User(db.Model):
    username= db.Column(db.String(30), primary_key=True)
    password= db.Column(db.String(30))
    
    def __init__(self, username, password):
        self.username= username
        self.password= password
    
    def is_anonymous(self):     #flask-login
        return False
    
    def is_authenticated(self): #flask-login
        return True
    
    def is_active(self):        #flask-login
        return True

    def get_id(self):           #flask-login
        return unicode(self.username)

@app.route('/')
def index():
    return render_template('index.html', login_form=LoginForm())

@app.route('/events', methods=['GET','POST'])
def events():
    if request.method=='GET':
        vs= Vacation.query.all()
        return vacations_to_json( vs )
    else:
        form= NewVacationForm()
        if form.validate():
            date= datetime.datetime.strptime(form.date.data, DATE_FORMAT)
            v= Vacation(date)
            db.session.add(v)
            db.session.commit()
            return ""
        return form_errors_as_text(form),400

def form_errors_as_text( form ):
    return ", ".join([", ".join(x) for x in form.errors.values()])

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    else:
        form= LoginForm()
        print "LOGIN",form.username, form.password
        if form.validate():
            user= User.query.get(form.username.data)
            if user is None:
                return "No such user", 404
            if user.password!=form.password.data:
                return "Bad password", 400
            login_user(user)
            return ""
        return form_errors_as_text(form),400





if __name__ == '__main__':
    app.run(host='0.0.0.0', use_reloader=True)

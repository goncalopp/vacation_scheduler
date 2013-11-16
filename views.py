from app import app
from models import *
from forms import *
from misc import vacations_to_json, form_errors_as_text, DATE_FORMAT

from flask import request, render_template
from flask.ext.login import login_user, current_user

@app.route('/')
def index():
    return render_template('index.html', login_form=LoginForm())

@app.route('/events', methods=['GET','POST'])
def events():
    if request.method=='GET':
        vs= Vacation.query.all()
        return vacations_to_json( vs )
    else:
        if not current_user.is_authenticated():
            return "You need to login to add events", 403
        form= NewVacationForm()
        if form.validate():
            date= string_to_date(form.date.data)
            v= Vacation(date, current_user)
            db.session.add(v)
            db.session.commit()
            return ""
        return form_errors_as_text(form),400

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


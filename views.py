from app import app
from models import *
from forms import *
from misc import vacations_to_json, form_errors_as_text, DATE_FORMAT

from flask import request, render_template
from flask.ext.login import login_user, current_user

@app.route('/')
def index():
    au= current_user.is_authenticated()
    available_days= UserYearlyArchive.getOrCreate(current_user).getAvailableVacations() if au else 0
    scheduled_days= UserYearlyArchive.getOrCreate(current_user).getScheduledVacations() if au else 0
    used_days= UserYearlyArchive.getOrCreate(current_user).getUsedVacations() if au else 0
    
    event_types= Vacation.readable_types.items()
    return render_template('index.html', login_form=LoginForm(), 
        current_user=current_user, available_days= available_days, scheduled_days= scheduled_days,
        used_days= used_days, event_types=event_types)

@app.route('/events', methods=['GET','POST'])
def events():
    if request.method=='GET':
        vs= Vacation.query.all()
        return vacations_to_json( vs, current_user )
    if not current_user.is_authenticated():
        return "You need to login to add events", 403
    form= NewVacationForm()
    if not form.validate():
        return form_errors_as_text(form),400
    date= string_to_date(form.date.data).date()
    vtype= form.type.data
    sameday_events= Vacation.query.filter( Vacation.date == date ).filter( Vacation.user == current_user ).all()
    if form.delete.data:
        if len(sameday_events)!=1:
            return "Tried to delete inexistent event (or more than one event on same day)", 400
        delete_vacation(sameday_events[0])
    else:
        if len(sameday_events)!=0:
            return "Tried to add an event to a day with a event already in it.",400
        add_vacation(date, current_user, vtype)
    return ""


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    else:
        form= LoginForm()
        if form.validate():
            user= User.query.get(form.username.data)
            if user is None:
                return "No such user", 404
            if user.password!=form.password.data:
                return "Bad password", 400
            login_user(user)
            return ""
        return form_errors_as_text(form),400


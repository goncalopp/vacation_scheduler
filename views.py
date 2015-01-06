from app import app
from models import *
from forms import *
from misc import vacations_to_json, form_errors_as_text, DATE_FORMAT

from flask import request, render_template
from flask.ext.login import login_user, current_user

from app_log import get_logger
log= get_logger(__name__)

@app.route('/')
def index():
    log.info("GET index for %s", current_user)
    event_types= Vacation.readable_types.items()
    return render_template('index.html', login_form=LoginForm(), 
        current_user=current_user, event_types=event_types, 
        **statistics(getDict=True) )

@app.route('/statistics')
def statistics(getDict=False):
    log.info("GET statistics for %s", current_user)
    try:
        if not current_user.is_authenticated():
            raise ArchiveBeforeJoin
        ar= UserYearlyArchive.getOrCreate(current_user)
        available_days= getAvailableVacations( ar )
        scheduled_days= getScheduledVacations( ar )
        used_days=      getUsedVacations( current_user )
    except ArchiveBeforeJoin:
        available_days=0
        scheduled_days=0
        used_days=0
    d= { "available_days":  available_days, 
        "scheduled_days":   scheduled_days,
        "used_days":        used_days,
        }
    if getDict:
        return d
    else:
        return render_template('statistics.html', **d)



@app.route('/events', methods=['GET','POST'])
def events():
    if request.method=='GET':
        log.info("GET events for %s", current_user)
        vs= Vacation.query.all()
        return vacations_to_json( vs, current_user )
    log.info("POST events for %s", current_user)
    if not current_user.is_authenticated():
        log.warn("User tried to add events without loggin")
        return "You need to login to add events", 403
    form= NewVacationForm()
    if not form.validate():
        log.warn("Form validation error for %s", current_user)
        return form_errors_as_text(form),400
    date= string_to_date(form.date.data).date()
    vtype= form.type.data
    sameday_events= Vacation.query.filter( Vacation.date == date ).filter( Vacation.user == current_user ).all()
    if form.delete.data:
        if len(sameday_events)!=1:
            log.warn("Bad deletion for %s", current_user)
            return "Tried to delete inexistent event (or more than one event on same day)", 400
        try:
            delete_vacation(sameday_events[0])
        except ModifyPast as e:
            log.warn("Tried to change events in the past: %s (%s)", current_user, e)
            return "Can't change events in the past ({0})".format(e), 400
    else:
        if len(sameday_events)!=0:
            log.warn("Add event to day with events already : %s", current_user)
            return "Tried to add an event to a day with a event already in it.",400
        try:
            add_vacation(date, current_user, vtype)
        except ModifyPast as e:
            log.warn("Tried to change events in the past: %s (%s)", current_user, e)
            return "Can't change events in the past ({0})".format(e), 400
    return ""


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='GET':
        log.info("GET login")
        return render_template('login.html')
    else:
        log.info("POST login")
        form= LoginForm()
        if form.validate():
            username= form.username.data
            user= User.query.get(username)
            if user is None:
                log.info("Tried to login inexistent user: %s", username)
                return "No such user", 404
            if user.password!=form.password.data:
                log.info("Got bad password for %s", username)
                return "Bad password", 400
            log.info(unicode(user)+" logged in")
            login_user(user)
            return ""
        log.warn("Login form validation error")
        return form_errors_as_text(form),400


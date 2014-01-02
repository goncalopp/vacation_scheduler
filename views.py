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
    au= current_user.is_authenticated()
    try:
        if not au:
            raise ArchiveBeforeJoin
        a= UserYearlyArchive.getOrCreate(current_user)
        available_days= a.getAvailableVacations()
        scheduled_days= a.getScheduledVacations()
        used_days= a.getUsedVacations()
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
        try:
            delete_vacation(sameday_events[0])
        except ModifyPast:
            return "Can't change events in the past", 400
    else:
        if len(sameday_events)!=0:
            return "Tried to add an event to a day with a event already in it.",400
        try:
            add_vacation(date, current_user, vtype)
        except ModifyPast:
            return "Can't change events in the past", 400
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
            user= User.query.get(form.username.data)
            if user is None:
                return "No such user", 404
            if user.password!=form.password.data:
                return "Bad password", 400
            log.info(unicode(user)+" logged in")
            login_user(user)
            return ""
        return form_errors_as_text(form),400


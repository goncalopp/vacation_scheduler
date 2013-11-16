import datetime
import json


def vacations_to_json(vacations, current_user):
    def craft_dict(vacation):
        return {
            "start": date_to_string(vacation.date), 
            "title": vacation.user.username,
            "color": "#aa0000" if current_user==vacation.user else "#0000aa"
            }
    return json.dumps(map(craft_dict, vacations))

DATETIME_FORMAT="%Y-%m-%dT%H:%M:%SZ"
DATE_FORMAT="%Y-%m-%d"


def form_errors_as_text( form ):
    return ", ".join([", ".join(x) for x in form.errors.values()])

def date_to_string( date ):
    return date.strftime(DATETIME_FORMAT)
    
def string_to_date( s ):
    try: 
        return datetime.datetime.strptime(s, DATETIME_FORMAT)
    except ValueError:
        return datetime.datetime.strptime(s, DATE_FORMAT).date()

def calculate_vacation_days_since(join_date):
    '''given the date a employee joined the company,
    gives the total days of vacations that should be
    available to him, if he had used none.'''
    d1, d2= join_date, datetime.datetime.now()
    months= (d2.year-d1.year)*12 + (d2.month-d1.month)
    return months*2
    
    

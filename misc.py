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

DATE_FORMAT="%Y-%m-%dT%H:%M:%SZ"

def form_errors_as_text( form ):
    return ", ".join([", ".join(x) for x in form.errors.values()])

def date_to_string( date ):
    return date.strftime(DATE_FORMAT)
    
def string_to_date( s ):
    return datetime.datetime.strptime(s, DATE_FORMAT)

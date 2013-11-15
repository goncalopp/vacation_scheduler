import datetime
import json


def vacations_to_json(vacations):
    def craft_dict(vacation, title="my_user"):
        return {"start":date_to_string(vacation.date), "title": "my event"}
    return json.dumps(map(craft_dict, vacations))

DATE_FORMAT="%Y-%m-%dT%H:%M:%SZ"

def form_errors_as_text( form ):
    return ", ".join([", ".join(x) for x in form.errors.values()])

def date_to_string( date ):
    return date.strftime(DATE_FORMAT)
    
def string_to_date( s ):
    return datetime.datetime.strptime(s, DATE_FORMAT)

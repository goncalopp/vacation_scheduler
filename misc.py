import datetime
import json
import unicodedata


def vacations_to_json(vacations, current_user):
    def craft_dict(vacation):
        vtype= vacation.getReadableType()
        return {
            "start": date_to_string(vacation.date), 
            "title": vacation.user.username + (" ("+vtype+")" if vtype else ""),
            "color": "#aa0000" if current_user==vacation.user else "#0000aa",
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

def unisafe(s):
    '''unicode to ascii string'''
    return unicodedata.normalize('NFKD',unicode(s)).encode('ascii','ignore')

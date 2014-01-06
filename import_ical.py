from icalendar import Calendar #icalendar module
import urllib
from datetime import datetime

from vacation_scheduler import User, Vacation, add_vacation, app, db
app.config['FORBID_MODIFY_PAST']=False

URL="https://www.google.com/calendar/ical/en.portuguese%23holiday%40group.v.calendar.google.com/public/basic.ics"
USER= User.query.filter(User.username=="feriado").first()
if not USER:
    raise Exception("no such user")

def main():
    cal_str= urllib.urlopen(URL).read()
    c= Calendar.from_ical(cal_str )
    for x in c.walk():
        if x.name=="VEVENT":
            date= x['DTSTART'].dt
            add_date(date)

def add_date(date):
    if date.year!=datetime.now().year:
        print "ignoring event with different year",date
        return
    print "adding date",date
    add_vacation(date, USER) 

def delete_all_user_events():
    existing= Vacation.query.filter(Vacation.user==USER).all()
    for e in existing:
        db.session.delete(e)
    db.session.commit()

if __name__=="__main__":
    main()

from datetime import date
from vacation_scheduler import db, Vacation, User


db.create_all()

dates= [
    date(2013, 11, 14),
    ]

for d in dates:
    v=Vacation(d)
    db.session.add(v)

db.session.add( User("user","pass") )

db.session.commit()

from datetime import date
from vacation_scheduler import db, Vacation


db.create_all()

dates= [
    date(2013, 11, 14),
    ]

for d in dates:
    v=Vacation(d)
    db.session.add(v)

db.session.commit()

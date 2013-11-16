from datetime import date
from vacation_scheduler import db, Vacation, User


db.create_all()

user= User("user","pass")
db.session.add( user )


dates= [
    date(2013, 11, 14),
    ]

for d in dates:
    v=Vacation(d, user)
    db.session.add(v)



db.session.commit()

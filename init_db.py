from datetime import date
from vacation_scheduler import db, Vacation, User, UserInfo
from misc import string_to_date

db.create_all()

alice= User("alice", "alice")
bob= User("bob", "bob")
db.session.add( alice )
db.session.add( bob )

v1=Vacation(date(2013, 11, 14), alice)
v2=Vacation(date(2013, 11, 15), bob)
db.session.add(v1)
db.session.add(v2)

#the UserInfo creation must occur AFTER adding vacations
#otherwise available days are calculated wrongly
alice_info= UserInfo(alice, "2013-03-23")
bob_info= UserInfo(bob, "2013-05-12")
db.session.add( alice_info )
db.session.add( bob_info )

db.session.commit()

from datetime import date
from vacation_scheduler import db, Vacation, User, UserVacationInfo, add_vacation
from misc import string_to_date

db.create_all()

alice= User("alice", "alice")
bob= User("bob", "bob")
db.session.add( alice )
db.session.add( bob )

alice_info= UserVacationInfo(alice, "2013-03-23",  22, 2)
bob_info= UserVacationInfo(bob, "2013-05-12",  22, 2)
db.session.add( alice_info )
db.session.add( bob_info )

add_vacation(date(2013, 11, 14), alice)
add_vacation(date(2013, 11, 15), bob)

db.session.commit()

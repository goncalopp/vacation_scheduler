from db import db
from misc import string_to_date, calculate_vacation_days_since

class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date= db.Column(db.Date)
    username = db.Column(db.String(30), db.ForeignKey('user.username'))
    user = db.relationship('User', backref=db.backref('vacations', lazy='dynamic'))
    def __init__(self, date, user):
        self.date = date
        self.user= user

    def __repr__(self):
        return str(self.date)


class User(db.Model):
    username= db.Column(db.String(30), primary_key=True)
    password= db.Column(db.String(30))
    
    def __init__(self, username, password):
        self.username= username
        self.password= password
    
    def is_anonymous(self):     #flask-login
        return False
    
    def is_authenticated(self): #flask-login
        return True
    
    def is_active(self):        #flask-login
        return True

    def get_id(self):           #flask-login
        return unicode(self.username)

class UserInfo(db.Model):
    username = db.Column(db.String(30), db.ForeignKey('user.username'), primary_key=True)
    user = db.relationship('User', backref=db.backref('info', uselist=False))
    join_date= db.Column(db.Date) #when did the user join the company
    available_vacation_days= db.Column(db.Integer) #cache, must be update on even add/remove
    
    def __init__(self, user, join_date):
        self.join_date= string_to_date(join_date)
        self.user= user
        total= calculate_vacation_days_since(self.join_date)
        used= user.vacations.count()
        self.available_vacation_days= total-used
    

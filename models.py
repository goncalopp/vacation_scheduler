from db import db

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

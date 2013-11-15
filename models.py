from db import db

class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date= db.Column(db.Date)

    def __init__(self, date):
        self.date = date

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

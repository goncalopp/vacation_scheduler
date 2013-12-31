# coding=utf-8

from db import db
from misc import string_to_date
from datetime import datetime,date

class Vacation(db.Model):
    types= {
        "vacation":     0, 
        "sick_leave":   1, 
        "child_birth":  2, 
        "training":     3, 
        "other":        99,
        }
    readable_types= {
        0:u"",
        1:u"baixa",
        2:u"parto",
        3:u"formação",
        99:u"outro",
        }
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    date= db.Column(db.Date)
    username = db.Column(db.String(30), db.ForeignKey('user.username'))
    user = db.relationship('User', backref=db.backref('vacations', lazy='dynamic'))
    def __init__(self, date, user, type):
        self.date = date
        self.user= user
        self.type=type

    def __repr__(self):
        return str(self.date)
    
    def getReadableType(self):
        '''returns the human-readable type of this vacation'''
        return Vacation.readable_types.get(self.type, "")

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

class UserVacationInfo(db.Model):
    username = db.Column(db.String(30), db.ForeignKey('user.username'), primary_key=True)
    user = db.relationship('User', backref=db.backref('info', uselist=False))
    join_date= db.Column(db.Date) #when did the user join the company
    vacations_per_year= db.Column(db.Integer)
    vacations_per_month= db.Column(db.Integer) #for first year
    
    def __init__(self, user, join_date, vacations_per_year, vacations_per_month):
        self.join_date= string_to_date(join_date)
        self.user= user
        self.vacations_per_year= vacations_per_year
        self.vacations_per_month= vacations_per_month 

class UserYearlyArchive(db.Model):
    username = db.Column(db.String(30), db.ForeignKey('user.username'), primary_key=True)
    user = db.relationship('User')
    year= db.Column(db.Integer, primary_key=True)
    total_vacations= db.Column(db.Integer) #number of vacations available in this year
    used_vacations= db.Column(db.Integer)
    
    def __init__(self, user, year):
        self.username= user.username
        self.year= year
        self.used_vacations= 0
        self.total_vacations= UserYearlyArchive.totalVacations(user, year)
    
    @staticmethod
    def totalVacations(user, year):
        if year>user.info.join_date.year:
            return user.info.vacations_per_year
        elif year==user.info.join_date.year:
            n_months= 12 - user.info.join_date.month #n of months of work. don't count join month
            return n_months * user.info.vacations_per_month
        else:
            #year before user join date
            return 0
    
    @staticmethod
    def getOrCreate(user, year=datetime.now().year, commit=True):
        q= UserYearlyArchive.query.filter( UserYearlyArchive.username == user.username ).filter( UserYearlyArchive.year == year ).all()
        if len(q)==0:
            info= UserYearlyArchive(user, year)
            db.session.add(info)
            if commit:
                db.session.commit()
        else:
            info= q[0]
        return info
    
    def getAvailableVacations(self):
        '''get the number of vacations the user has available (left) this year'''
        if self.user.info.join_date.year==self.year:
            #user joined the company this year. We want to display
            #available vacations only up to the current date, not at the
            #end of current year
            n_months= (datetime.now().month-self.user.info.join_date.month)
            return n_months*self.user.info.vacations_per_month - self.used_vacations
        else:
            return self.total_vacations - self.used_vacations
    
    def getScheduledVacations(self):
        '''get the number of user scheduled vacations this year'''
        start_date, end_date= date(year=self.year, month=1, day=1), date(year=self.year+1, month=1, day=1)
        return Vacation.query.filter( Vacation.user == self.user ).filter( Vacation.date >= start_date ).filter( Vacation.date < end_date ).filter( Vacation.type==0 ).count()
    
    def getUsedVacations(self):
        '''gets the number of user scheduled vacations this year that
        have already occurred'''
        return self.used_vacations

def delete_vacation(vacation, commit=True):
    uyc= UserYearlyArchive.getOrCreate(vacation.user, vacation.date.year, commit=False)
    if vacation.type==0:
        uyc.used_vacations-=1
    db.session.delete(vacation)
    if commit:
        db.session.commit()

def add_vacation(date, user, vtype=0, commit=True):
    v= Vacation(date, user, vtype)
    db.session.add(v)
    uyc= UserYearlyArchive.getOrCreate(user, date.year, commit=False)
    if vtype==0:
        uyc.used_vacations+=1
    db.session.add(uyc)
    if commit:
        db.session.commit()

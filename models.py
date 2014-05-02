# coding=utf-8

from db import db
from misc import string_to_date, unisafe
from datetime import datetime,date
from app import app

from app_log import get_logger
log= get_logger(__name__)

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
        log.debug("Created %s", self)

    
    def getReadableType(self):
        '''returns the human-readable type of this vacation'''
        return Vacation.readable_types.get(self.type, "")
    
    def __repr__(self):
        return "Vacation<"+",".join(map(str,(self.user, self.date, self.type)))+">"

class User(db.Model):
    username= db.Column(db.String(30), primary_key=True)
    password= db.Column(db.String(30))
    email=    db.Column(db.String(50))
    
    def __init__(self, username, password, email=None):
        self.username= username
        self.password= password
        self.email=    email
        log.info("Created %s", self)
    
    def is_anonymous(self):     #flask-login
        return False
    
    def is_authenticated(self): #flask-login
        return True
    
    def is_active(self):        #flask-login
        return True

    def get_id(self):           #flask-login
        return unicode(self.username)
    
    def __repr__(self):
        return unisafe("User<"+self.username+">")

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
        log.info("Created %s: %s", self, ", ".join(map(str,(
            vacations_per_year, 
            vacations_per_month,
            ))))
    
    def __repr__(self):
        return "UserVacationInfo<"+str(self.user)+">"

class UserYearlyArchive(db.Model):
    username = db.Column(db.String(30), db.ForeignKey('user.username'), primary_key=True)
    user = db.relationship('User', backref=db.backref('archives', lazy='dynamic'))
    year= db.Column(db.Integer, primary_key=True)
    total_vacations= db.Column(db.Integer) #number of vacations available in this year
    used_vacations= db.Column(db.Integer) #vacations scheduled this year
    inherited_vacations= db.Column(db.Integer) #vacations inherited from last year
    
    def __init__(self, user, year, override_inherited=None):
        self.username= user.username
        self.year= year
        self.used_vacations=  UserYearlyArchive.getScheduledVacationsFor(user, year)
        self.total_vacations= UserYearlyArchive.totalVacations(user, year)
        self.inherited_vacations= override_inherited or UserYearlyArchive.inheritedVacations(user, year)
        log.info("Created %s: %s", self, ", ".join(map(str,(
            self.used_vacations, 
            self.total_vacations, 
            self.inherited_vacations,
            ))))
    
    @staticmethod
    def totalVacations(user, year):
        '''number of vacations the user is given this year, counted at end of year'''
        if year>user.info.join_date.year:
            return user.info.vacations_per_year
        elif year==user.info.join_date.year:
            n_months= 12 - user.info.join_date.month #n of months of work. don't count join month
            return n_months * user.info.vacations_per_month
        else:
            #year before user join date
            return 0
    
    @staticmethod
    def inheritedVacations(user, year):
        try:
            last= UserYearlyArchive.getOrCreate(user, year-1)
            return last.getAvailableVacations()
        except ArchiveBeforeJoin:
            return 0
    
    @staticmethod
    def getOrCreate(user, year=datetime.now().year, commit=True):
        if year<user.info.join_date.year:
            raise ArchiveBeforeJoin
        q= UserYearlyArchive.query.filter( UserYearlyArchive.username == user.username ).filter( UserYearlyArchive.year == year ).all()
        if len(q)==0:
            info= UserYearlyArchive(user, year)
            db.session.add(info)
            if commit:
                db.session.commit()
        else:
            assert len(q)==1 #at most 1 archive per user-year
            info= q[0]
        return info

    @staticmethod
    def getScheduledVacationsFor(user, year):
        '''get the number of user scheduled vacations this year'''
        start_date, end_date= date(year=year, month=1, day=1), date(year=year+1, month=1, day=1)
        return Vacation.query.filter( Vacation.user == user ).filter( Vacation.date >= start_date ).filter( Vacation.date < end_date ).filter( Vacation.type==0 ).count()
    
    
    def getAvailableVacations(self):
        '''get the number of vacations the user has available (left) this year'''
        if self.user.info.join_date.year==self.year:
            #user joined the company this year. We want to display
            #available vacations only up to the current date, not at the
            #end of current year
            n=datetime.now().date()
            if n.year!=self.year:
                #we are querying a yearly archive in the past
                n=date(year=self.year, month=12, day=31)
            n_months= (n.month-self.user.info.join_date.month)
            return n_months*self.user.info.vacations_per_month - self.used_vacations
        else:
            return self.inherited_vacations + self.total_vacations - self.used_vacations
    
    def getScheduledVacations(self):
        '''get the number of user scheduled vacations this year'''
        return UserYearlyArchive.getScheduledVacationsFor(self.user, datetime.now().year)

    def getUsedVacations(self):
        '''gets the number of user scheduled vacations this year that
        have already occurred'''
        #this currently returns a fake result, since there's no way
        #to efficiently calculate this without additional structures.
        return self.used_vacations 
    
    def __repr__(self):
        return "UserYearlyArchive<"+",".join(map(str, (self.user, self.year)))+">"

class ArchiveBeforeJoin( Exception ):
    '''Tried to get or create archive from year before user joined the company'''
    pass

class ModifyPast(Exception):
    '''Tried to modify vacations in the past'''
    pass

def update_used_vacations(vacation, commit=True, add=False, delete=False):
    now= datetime.now().date()
    if app.config['FORBID_MODIFY_PAST']:
        if vacation.date<=now:
            raise ModifyPast
    if vacation.type!=0:
        return
    if vacation.date.year > now.year:
        return #Don't generate archives in the future
    uyc= UserYearlyArchive.getOrCreate(vacation.user, vacation.date.year, commit=False)
    db.session.add(uyc)
    if add:
        uyc.used_vacations+=1
    if delete:
        uyc.used_vacations-=1
    if commit and (add or delete):
        db.session.commit()

def delete_vacation(vacation, commit=True):
    now= datetime.now().date()
    update_used_vacations(vacation, commit=False, delete=True)
    db.session.delete(vacation)
    log.info("deleted %s", vacation)
    if commit:
        db.session.commit()

def add_vacation(date, user, vtype=0, commit=True):
    v= Vacation(date, user, vtype)
    update_used_vacations(v, commit=False, add=True)
    db.session.add(v)
    if commit:
        db.session.commit()
    log.info("created %s", v)

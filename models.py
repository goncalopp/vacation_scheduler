# coding=utf-8

from db import db
from misc import string_to_date, unisafe
from datetime import datetime,date,timedelta
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
    vacations_per_month= db.Column(db.Integer) #for first year. OBSOLETE, see vacationsGivenUntil
    
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
    
    def vacationsGivenUntil(self, date, closed_interval=True):
        '''number of vacations the user is given in the period from the
        beggining of date.year up to (and including, iff 
        closed_interval) date'''
        if date.year > self.join_date.year:
            return self.vacations_per_year
        elif date.year < self.join_date.year:
            return 0
        else: #year==self.join_date.year
            if closed_interval: #remaining of code assumes open_interval
                year= date.year
                date+= timedelta( days=1 )
                year_overflow= date.year!=year
            else:
                year_overflow=False
            
            current_month= 13 if year_overflow else date.month
            n_months= max(0,current_month - self.join_date.month-1) #n of COMPLETE months of work (don't count join and current month)
            n_months_vacations= n_months * 2
            if date.month==self.join_date.month and not year_overflow:
                n_joinmonth_vacations=0
            else:
                n_joinmonth_vacations= 2 if self.join_date.day <=1 else 1 if self.join_date.day <=15 else 0
            n_currentmonth_vacations= 0
            result= n_months_vacations + n_joinmonth_vacations + n_currentmonth_vacations
            return min( self.vacations_per_year, result )
    
    def vacationsGivenOnYear( self, year ):
        return self.vacationsGivenUntil( datetime(year=year, month=12, day=31), closed_interval=True )

class UserYearlyArchive(db.Model):
    username = db.Column(db.String(30), db.ForeignKey('user.username'), primary_key=True)
    user = db.relationship('User', backref=db.backref('archives', lazy='dynamic'))
    year= db.Column(db.Integer, primary_key=True)
    total_vacations= db.Column(db.Integer) #number of vacations made available to the user, measured at year's end
    used_vacations= db.Column(db.Integer)  #vacations scheduled this year
    inherited_vacations= db.Column(db.Integer) #vacations inherited from last year
    
    def __init__(self, user, year, override_inherited=None, override_total=None):
        self.user= user #this is done in order to make the field available in this method
        self.username= user.username
        self.year= year
        self.regenerateArchive( creation=True, override_inherited=override_inherited, override_total=override_total )
        log.info("Created {}".format(self))
    
    def regenerateArchive(self, override_inherited=None, override_total=None, creation=False, commit=True):
        '''recalculate cached values'''
        if not creation:
            log.info("Regenerating archive. Old: {}".format(self))
        self.used_vacations=  queryYearlyVacations( self.user, self.year).count()
        self.total_vacations= self.user.info.vacationsGivenOnYear( self.year ) if override_total is None else override_total
        self.inherited_vacations= UserYearlyArchive.calculateInheritedVacations(self.user, self.year) if override_inherited is None else override_inherited
        if not creation:
            log.info("Regenerating archive. New: {}".format(self))
        if commit and not creation:
            db.session.commit()

    @staticmethod
    def calculateInheritedVacations(user, year):
        try:
            last_archive= UserYearlyArchive.getOrCreate(user, year-1) # this line makes this function indirectly recursive
            return getAvailableVacations( last_archive )
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
    
    def __str__(self):
        a= ",".join(map(str, (self.username, self.year)))
        b= ", ".join(map(str,(
            self.used_vacations, 
            self.total_vacations, 
            self.inherited_vacations,
            )))
        return "UserYearlyArchive<{}|{}>".format(a,b)
    def __repr__(self):
        return "UserYearlyArchive<"+",".join(map(str, (self.username, self.year)))+">"

class InvalidArchiveAccessDate( Exception ):
    '''Tried to get data from a archive that is not yet available'''
    pass
    
class ArchiveBeforeJoin( Exception ):
    '''Tried to get or create archive from year before user joined the company'''
    pass

class ModifyPast(Exception):
    '''Tried to modify vacations in the past'''
    def __init__(self):
        super(Exception, self).__init__( self.__class__.__name__ )

class ModifyPastYear( ModifyPast ):
    pass


def queryYearlyVacations(user, year, end_date=None):
    '''get the (query representing) user scheduled vacations this year'''
    start_date= date(year=year, month=1, day=1)
    if end_date is None:
        end_date= date(year=year+1, month=1, day=1)
    else:
        assert end_date.year == year
        end_date+=timedelta(days=1)
    return Vacation.query.filter( Vacation.user == user ).filter( Vacation.date >= start_date ).filter( Vacation.date < end_date ).filter( Vacation.type==0 )
        
def getScheduledVacations( archive ):
    return archive.used_vacations

def getUsedVacations(user):
    n=datetime.now().date()
    return queryYearlyVacations(user, n.year, n).count()
    
def getAvailableVacations( archive ):
    inherited=  archive.inherited_vacations
    given=  vacations( archive )
    used=       archive.used_vacations
    return inherited + given - used

def vacations( archive ):
    '''vacations given in the archive's year. 
    If the archive is for the current year, will only return vacations
    available up to the current day (i.e.: not counted at end of year)'''
    if archive.year < datetime.now().year:
        return archive.total_vacations  
    else: 
        return archive.user.info.vacationsGivenUntil( datetime.now() )

def update_used_vacations(vacation, commit=True, add=False, delete=False):
    now= datetime.now().date()
    if app.config['FORBID_MODIFY_PAST_YEAR']:
        if vacation.date.year<now.year:
            raise ModifyPastYear
    if app.config['FORBID_MODIFY_PAST']:
        if vacation.date<now:
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

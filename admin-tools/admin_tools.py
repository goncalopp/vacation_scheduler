from io import open
from datetime import date
import vacation_scheduler
from models import Vacation, User, UserVacationInfo, UserYearlyArchive 
from misc import string_to_date, unisafe

from mail_user import mail_user

import random
import string
from time import sleep

USER_INFO_FILE 'data/users.txt' #TSV, each line is (name, mail, leftover)
EMAIL_DOMAIN= "domain.tld"
NO_JOIN_DATE= "2013-12-31"


def random_password():
    return "".join([random.choice(string.lowercase+string.digits) for x in range(8)])

def user_from_name(name):
    result= unisafe(name).lower().replace(" ","_")
    return result


user_message='''Username: {username}
Password: {password}
'''

def mail_user_info(user):
    print "Emailing info to",user
    username= user.username
    password= user.password
    mail_user(user, user_message.format(**locals()))
    sleep(1)

def get_user(username):
    u= User.query.filter(User.username==username).all()
    assert len(u)==1
    return u[0]


def create_db():
    db.create_all()
    for line in open(USER_INFO_FILE, 'r', encoding='utf-8').read().splitlines():
        name, mail, leftover= line.split("\t")
        username= user_from_name(name)
        password= random_password()
        user= User(username, password, email= mail)
        db.session.add( user )
    
        user_info= UserVacationInfo(user, NO_JOIN_DATE,  22, 2 )
        db.session.add( user_info )
    
        archive= UserYearlyArchive(user, 2014, override_inherited= leftover )
        db.session.add(archive)
    
        mail_user_info(user) 
    db.session.commit()

def add_newly_joined_user(username, join_date_string, password=None):
    from datetime import datetime
    assert join_date_string.startswith(str(datetime.now().year))
    password= password or random_password()
    email= username+"@"+EMAIL_DOMAIN
    user= User(username, password, email= email)
    user_info= UserVacationInfo(user, join_date_string,  22, 2 )
    db.session.add(user)
    db.session.add(user_info)
    db.session.commit()


if __name__=='__main__':
    pass
    #this code was used to create the initial users
    #users= []
    #users= map(get_user, users)
    #map( mail_user_info, users)

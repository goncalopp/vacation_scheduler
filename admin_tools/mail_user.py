from os import devnull
from subprocess import check_call 

def mail_user(user, body, subject="Vacations Application"):
    sender= "ferias@ferias"
    address= user.email
    command= '''echo "{body}" | mail -E -s "{subject}" "{address}" -- -f "{sender}"'''.format(**locals())
    check_call(command, shell=True)

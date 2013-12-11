from flask_wtf import Form
from wtforms import validators
from wtforms.validators import ValidationError, Length, required
from wtforms.fields import TextField, PasswordField, BooleanField, IntegerField
from misc import string_to_date
from models import Vacation

class NewVacationForm(Form):
    def validate_date(form, date_field):
        try:
            string_to_date(date_field.data)
        except ValueError:
            raise ValidationError('Bad date format')
    def validate_type(form, type):
        try:
            Vacation.readable_types[type.data]
        except KeyError:
            raise ValidationError('Bad type')
    date = TextField('date', [required(message="date missing"), validate_date])
    delete= BooleanField('delete')
    type= IntegerField('type', [validate_type], default=0)

class LoginForm(Form):
    username = TextField('Username', [required(message="No username provided"), Length(max=30)])
    password = PasswordField('Password', [required(message="No password provided"), Length(max=30)])
    

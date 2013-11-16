from flask_wtf import Form
from wtforms import validators
from wtforms.validators import ValidationError, Length, required
from wtforms.fields import TextField, PasswordField, BooleanField
from misc import string_to_date

class NewVacationForm(Form):
    def validate_date(form, date_field):
        try:
            string_to_date(date_field.data)
        except ValueError:
            raise ValidationError('Bad date format')
    date = TextField('date', [required(message="date missing"), validate_date])
    delete= BooleanField('delete')

class LoginForm(Form):
    username = TextField('Username', [required(message="No username provided"), Length(max=30)])
    password = PasswordField('Password', [required(message="No password provided"), Length(max=30)])
    

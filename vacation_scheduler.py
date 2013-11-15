from flask import Flask, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import flask_wtf
from flask_wtf import Form
import wtforms
from wtforms.validators import ValidationError, required
from wtforms.fields import TextField
import datetime
import json

DATE_FORMAT="%Y-%m-%dT%H:%M:%SZ"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'LTjzysF0RfSPmmBd'

db = SQLAlchemy(app)

csrf=flask_wtf.csrf.CsrfProtect(app)
@csrf.error_handler
def csrf_error(reason):
    return "Bad CSRF token: "+reason, 400

class NewVacationForm(Form):
    def validate_date(form, date_field):
        try:
            datetime.datetime.strptime(date_field.data, DATE_FORMAT)
        except ValueError:
            raise ValidationError('Bad date format')
    date = TextField('date', [required(message="date missing"), validate_date])

class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date= db.Column(db.Date)

    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return str(self.date)
        
def vacations_to_json(vacations):
    def craft_dict(vacation, title="my_user"):
        return {"start":vacation.date.strftime(DATE_FORMAT), "title": "my event"}
    return json.dumps(map(craft_dict, vacations))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events', methods=['GET','POST'])
def events():
    if request.method=='GET':
        vs= Vacation.query.all()
        return vacations_to_json( vs )
    else:
        form= NewVacationForm()
        if form.validate():
            date= datetime.datetime.strptime(form.date.data, DATE_FORMAT)
            v= Vacation(date)
            db.session.add(v)
            db.session.commit()
            return ""
        return form_errors_as_text(form),400

def form_errors_as_text( form ):
    return ",".join([",".join(x) for x in form.errors.values()])



if __name__ == '__main__':
    app.run(host='0.0.0.0', use_reloader=True)

from flask import Flask, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['DEBUG'] = True

db = SQLAlchemy(app)


class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date= db.Column(db.Date)

    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return str(self.date)
        
def vacations_to_json(vacations):
    def craft_dict(vacation, title="my_user"):
        return {"start":vacation.date.strftime("%Y-%m-%dT%H:%M:%SZ"), "title": "my event"}
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
        date= request.form['date']
        date= datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        v= Vacation(date)
        db.session.add(v)
        db.session.commit()
        return ""



if __name__ == '__main__':
    app.run(host='0.0.0.0', use_reloader=True)

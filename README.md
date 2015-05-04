#Project overview

This is a web app that allows corporate employeees to schedule vacations with a single click.


# Technology used

 - [Flask](http://flask.pocoo.org/), a python web microframework
 - The [SQLAlchemy](http://www.sqlalchemy.org/) [ORM](https://en.wikipedia.org/wiki/Object-relational_mapping), with [it's flask extension](https://pythonhosted.org/Flask-SQLAlchemy/), for the database backend
 - [WTForms](https://wtforms.readthedocs.org/en/latest/), with [it's flask extension](https://flask-wtf.readthedocs.org/en/latest/),  for HTML form handling


# Project technical overview

`models.py` holds all model (data) related code.

`views.py` contains the URL handlers (entry points)




# Configuration

`configuration.py` contains the application configuration.

`SQLALCHEMY_DATABASE_URI` is the URI for the database. This is handled by SQLAlchemy, and can use many different DB engines (SQLite, MySQL, PostgreSQL, etc)

`DEBUG` controls whether the application is in debug mode, which will catch exceptions and allow interactive debugging in the browser, amongst other things.

`SECRET_KEY` is a random string that should be changed for each installation.


`FORBID_MODIFY_PAST` prevents users from modifying past vacations. A "feature" for distrustful management

`FORBID_MODIFY_PAST_YEAR` prevents users from modifying vacations from any other year than the current one. **This MUST be enabled on the current codebase, otherwise the database will become consistent and must be fixed manually**

# More documentation

Documentation on deployment and administration (and possibly others) is available in the `doc` directory

#!/bin/bash
authbind --deep gunicorn -w 4 -b "0.0.0.0:80" --access-logfile data/access.log --error-logfile data/app.log vacation_scheduler:app

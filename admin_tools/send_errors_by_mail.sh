#!/bin/bash
ADDRESS=goncalo.pinheira@novabase.pt
cat /var/log/gunicorn/vacation_scheduler.log | grep -v INFO |  mail -E -s "Errors on ferias database"  $ADDRESS -- -f ferias@ferias

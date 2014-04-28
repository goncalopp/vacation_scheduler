#!/bin/bash
ADDRESS=myaddress@domain.tld
cat /var/log/gunicorn/vacation_scheduler.log | grep Vacation | cut -b 49- |  mail -E -s "Changes to ferias database"  $ADDRESS -- -f ferias@ferias

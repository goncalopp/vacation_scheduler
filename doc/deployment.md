# Deployment

Here we describe an example deployment using:

 - A Debian-like server
 - The [gunicorn](http://gunicorn.org/) web server
 - [virtualenv](https://virtualenv.pypa.io/en/latest/) to isolate the deployment from the system's python installation.

###Pre-requirements:

    apt-get install python-pip      #the python package manager
    pip install virtualenv          
    
###installing project and dependencies

    git clone PROJECT_LOCATION      #get the project
    virtualenv env                  #create virtualenv
    source env/bin/activate         #and activate it
    cd vacation_scheduler       
    pip install -r requirements.txt #install all project dependencies into the virtualenv
    deactivate                      #deactivate virtualenv

###Configuring Gunicorn, making it run on system boot

    adduser gunicorn    #add a separate user for gunicorn to run on. DON'T run as root...

For System-V-style init, there's a gunicorn init script with virtualenv support at
`https://github.com/MYUSER/gunicorn-init`

You'll need to setup [runlevels](https://en.wikipedia.org/wiki/Runlevel).

Configuration is stored at `/etc/default/gunicorn` and `/etc/gunicorn`

Here's example files:

    $ cat /etc/gunicorn/vacation_scheduler.conf 
    WORKING_DIR=/home/ferias/vacation_scheduler
    APP_MODULE="vacation_scheduler:app"
    CONFIG_FILE=/etc/gunicorn/py/vacation_scheduler.py
    LOG_LEVEL="info"
    VIRTUALENV=/home/ferias/vacation_scheduler/env
    
    $ cat /etc/gunicorn/py/vacation_scheduler.py
    import os
    def numCPUs():
        return os.sysconf("SC_NPROCESSORS_ONLN")
    bind = "0.0.0.0:80"
    workers = numCPUs() * 2 + 1
    
    $ cat /etc/default/gunicorn 
    RUN=yes
    CONF_DIR=/etc/gunicorn
    CONFIGS="vacation_scheduler"
    RUN_USER=gunicorn
    USE_VIRTUALENVS=yes


###Backups 

If you use SQLite, you can just copy the database file to `/var/backups/YOUR_COMPANY`. Sending them to a remote machine is also not a bad idea at all, if your environment allows it

###Log handling

You can use standard tools like `logrotate`. Emailing an administrator on errors might not be a bad idea (don't forget to configure your mail server).

###Configuration
see `configuration.py`

###Database creation and populating with initial data
see `init_db.py`




    

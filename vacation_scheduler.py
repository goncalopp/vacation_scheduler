from app import *
from configuration import *
from db import *
from forms import *
from models import *
from views import *
from misc import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', use_reloader=True)

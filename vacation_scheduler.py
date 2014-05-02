from app import app
import configuration 
import db 
import forms 
import models 
import views 
import misc 

if __name__ == '__main__':
    app.run(host='0.0.0.0', use_reloader=True)

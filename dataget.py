import RPi.GPIO as GPIO
import sqlite3
import time
import json
from flask import Flask
from flask import request




#program with logic for forecasts
import weatherforesend as wf

#database setup
con = sqlite3.connect('valvestate.db')
cur = con.cursor()
#cur.execute('''CREATE TABLE valveoctable
           #(Time, State)'')

#valve setup
ssig = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(ssig, GPIO.OUT)


app = Flask(__name__)

@app.route("/")
def show():
    return("<h1> hello </h1>")

@app.route("/postdata", methods = ['POST', 'GET'])
def put():
    ocvalve = request.json
    cur.execute('''INSERT INTO valveoctable VALUES(?,?)''', (time.ctime(), ocvalve['state']))
    valvestate = ocvalve['state']
    if (valvestate == 'open'):
        GPIO.output(ssig, 1)
    elif valvestate == 'close':
        GPIO.output(ssig, 0)
    print(ocvalve['state'])
    return {"status":"success"},201



#
#
#


            
                
            

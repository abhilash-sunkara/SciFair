import RPi.GPIO as GPIO
import sqlite3
import time
import json
from flask import Flask,g
from flask import request
import os
import logging


DATABASE='/home/pi/scifair/valvestate.db'
app = Flask(__name__)

#program with logic for forecasts
#import weatherforesend as wf

#DATABASE SETUP
if not os.path.exists(DATABASE):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

#cur.execute('''CREATE TABLE valveoctable#(Time, State)''')

def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

#valve setup
msig = 12
ssig = 3
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(ssig, GPIO.OUT)
GPIO.setup(msig, GPIO.OUT)
GPIO.output(msig, 0)
GPIO.output(ssig, 0)


@app.route("/")
def show():
    tablestring = "<table border = 1px black> <tr> <th> TIME OF OPENING OR CLOSING </th> <th> VALVESTATE </th> </tr>"
    app.logger.info("received request to show currentvalve state")
    apdb = get_db()
    cur = apdb.cursor()
    for row in cur.execute('''SELECT * FROM valveoctable'''):
        t = row[0]
        s = row[1]
        tablestring = tablestring + "<tr> <td> %s </td> <td> %s </td> </tr>"%(t, s)
    tablestring = tablestring + "</table>"
    return tablestring

@app.route("/postdata", methods = ['POST'])
def put():
    ocvalve = request.json
    apdb = get_db()
    cur = apdb.cursor()
    app.logger.info("received  valve state  '%s', inserting into db"%(ocvalve.get('state')))
    cur.execute('''INSERT INTO valveoctable VALUES(?,?)''', (time.ctime(), ocvalve['state']))
    apdb.commit()
    valvestate = ocvalve['state']
    if (valvestate == 'open'):
        GPIO.output(ssig, 1)
        time.sleep(1)
        GPIO.output(msig, 1)
    elif valvestate == 'close':
        GPIO.output(msig, 0)
        time.sleep(1)
        GPIO.output(ssig, 0)
    print(ocvalve['state'])
    return {"status":"success"},201

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g,'_database',None)
    if db is not None:
        db.close()

if __name__ == "__main__":
        app.run(host='0.0.0.0',debug=True)



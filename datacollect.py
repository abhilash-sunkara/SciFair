#module import
import RPi.GPIO as GPIO
import sqlite3
import time
import json
from flask import Flask
import requests
import weatherforesend as wf


#GPIO setup
rsig = 22
rp = 24
ssig = 12
moistp = 16
moistsig = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(ssig, GPIO.OUT)
GPIO.setup(moistp, GPIO.OUT)
GPIO.setup(moistsig, GPIO.IN)
GPIO.setup(rsig, GPIO.IN)
GPIO.setup(rp, GPIO.OUT)
GPIO.output(moistp, 1)
GPIO.output(rp, 1)

#hourly forecast time management
hour = 0
tm = 0

#database setup
con = sqlite3.connect('sensorsig.db')
cur = con.cursor()
#cur.execute('''CREATE TABLE datasense
            #(Time, Rain, Moisture)'')


#sensor data collection and transfer to valve
x=1
while True:
    if tm >= 60:
        if hour >= 23:
            hour = 0
        else:
            hour = hour+1
        tm = tm-60
    r = GPIO.input(rsig)
    m = GPIO.input(moistsig)
    wcode = wf.forelogic(hour)
    if x == 1:
        print('inserted initial value')
        cur.execute('''INSERT INTO datasense VALUES(?, ?, ?)''', (time.ctime(), r, m))
        if (r == 1 and m == 1):
            requests.post("http://127.0.0.1:5000/postdata",json = {"time" : time.ctime(), "state" : "open"})
        else:   
            requests.post("http://127.0.0.1:5000/postdata",json = {"time" : time.ctime(), "state" : "close"})
        x = x+1
    for row in cur.execute('''SELECT * FROM datasense ORDER BY time DESC LIMIT 1'''):
        print (row)
        ar = row[1]
        am = row[2]
        print('ar am',ar,am)
        print('r m' ,r,m)
        if not (ar == r and am == m):
            cur.execute('''INSERT INTO datasense VALUES(?, ?, ?)''', (time.ctime(), r, m))
            print('inserted')
            con.commit()
            if (r == 1 and m == 1):
                if wcode == 'dopen':
                    requests.post("http://127.0.0.1:5000/postdata",json = {"time" : time.ctime(), "state" : "open"})
                elif wcode == 'dclose':
                    requests.post("http://127.0.0.1:5000/postdata",json = {"time" : time.ctime(), "state" : "close"})
                elif wcode == 'popen':
                    tm = tm + 5
                    requests.post("http://127.0.0.1:5000/postdata",json = {"time" : time.ctime(), "state" : "open"})
                elif wcode == 'pclose':
                    tm = tm + 5
                    requests.post("http://127.0.0.1:5000/postdata",json = {"time" : time.ctime(), "state" : "close"})
                else:
                    tm = tm + 10
                    if (r==1 and m == 1):
                        requests.post("http://127.0.0.1:5000/postdata",json = {"time" : time.ctime(), "state" : "open"})
                    else:
                        requests.post("http://127.0.0.1:5000/postdata",json = {"time" : time.ctime(), "state" : "close"})
            else:
                requests.post("http://127.0.0.1:5000/postdata",json = {"time" : time.ctime(), "state" : "close"})
        break
    
    time.sleep(30)
    tm = tm+0.5
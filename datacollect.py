#module import
import RPi.GPIO as GPIO
import sqlite3
import time
import json
from flask import Flask
import requests
import weatherforesend as wf
import logging
from logging.handlers import TimedRotatingFileHandler

app_logger = logging.getLogger('data_collect.log')
app_logger.setLevel(logging.DEBUG)
handler = TimedRotatingFileHandler('/home/pi/scifair/data_collect.log',when='d',interval=30,backupCount=5)
handler.setLevel(logging.INFO)
f_format = logging.Formatter('%(asctime)s - %(name)s %(levelname)s - %(message)s')
handler.setFormatter(f_format)
app_logger.addHandler(handler)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(f_format)
app_logger.addHandler(ch)

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

def log_call(lm):
	app_logger.info(lm)

#functions to send data
def senddata(jd):
    url = "http://127.0.0.1:5000/postdata"
    requests.post(url,json = jd)
    log_call('posted data %r at %r '%(repr(jd),repr(time.ctime())))



#hourly forecast time management
wck = 0
hour = 15
tm = 0

#database setup
con = sqlite3.connect('sensorsig.db')
cur = con.cursor()
#cur.execute('''CREATE TABLE datasense(Time, Rain, Moisture)''')

print('starting datacollect at %r '%(repr(time.ctime())))
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
    if x == 1 or wck >= 3600:
        wcode = wf.forelogic(hour)
        wck = 0
    ctm = time.ctime()
    if x == 1:
        log_call('inserted initial value at %r'%(repr(time.ctime())))
        cur.execute('''INSERT INTO datasense VALUES(?, ?, ?)''', (str(int(time.time())), r, m))
        log_call('got moisture sensor value %d , 0 mean water presense 1 means no water'%(m))
        if (r == 1 and m == 1):
            senddata({"time" : ctm, "state" : "open"})
        else:
            senddata({"time" : ctm, "state" : "close"})
        x = x+1
    for row in cur.execute('''SELECT * FROM datasense ORDER BY Time DESC LIMIT 1'''):
        log_call(str(row))
        ar = row[1]
        am = row[2]
        log_call('ar am %d %d'%(ar,am))
        print('r m' ,r,m)
        if not (ar == r and am == m):
            cur.execute('''INSERT INTO datasense VALUES(?, ?, ?)''', (str(int(time.time())), r, m))
            log_call('inserted')
            con.commit()
            if (r == 1 and m == 1):
                if wcode == 'dopen':
                    senddata({"time" : ctm, "state" : "open"})
                elif wcode == 'dclose':
                    log_call(' sending  close when dclose')
                    senddata({"time" : ctm, "state" : "close"})
                elif wcode == 'popen':
                    tm = tm + 5
                    wck = wck + 300
                    senddata({"time" : ctm, "state" : "open"})
                elif wcode == 'pclose':
                    tm = tm + 5
                    wck = wck + 300
                    log_call('sending close when pclose')
                    senddata({"time" : ctm, "state" : "close"})
                else:
                    tm = tm + 10
                    wck = wck + 600
                    if (r==1 and m == 1):
                        senddata({"time" : ctm, "state" : "open"})
                    else:
                        log_call('sending close when  not r=1 and  m=1')
                        senddata({"time" : ctm, "state" : "close"})
            else:
                log_call('outer else  r=1 and m=1  sending close')
                senddata({"time" : ctm, "state" : "close"})
        else:
            log_call('x')

    time.sleep(30)
    tm = tm+0.5
    wck = wck +30

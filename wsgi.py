import sys
sys.path.insert(0,'/home/pi/scifair')
from dataget import app as application
import logging
from logging.handlers import TimedRotatingFileHandler
if __name__ != "__main__":
	app_logger = logging.getLogger('dataget_app.log')
	app_logger.setLevel(logging.DEBUG)
	handler = TimedRotatingFileHandler('/home/pi/scifair/dataget_app.log',when='d',interval=30,backupCount=5)
	handler.setLevel(logging.INFO)
	f_format = logging.Formatter('%(asctime)s - %(name)s %(levelname)s - %(message)s')
	handler.setFormatter(f_format)
	app_logger.addHandler(handler)
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	ch.setFormatter(f_format)
	app_logger.addHandler(ch)
	application.logger.handlers = app_logger.handlers
	application.logger.setLevel(app_logger.level)

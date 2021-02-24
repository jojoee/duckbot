import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
from pytz import timezone
import sys
from helper.config import TIMEZONE
from helper.notification import line

"""
https://stackoverflow.com/questions/44718204/python-how-to-create-log-file-everyday-using-logging-module
https://stackoverflow.com/questions/8467978/python-want-logging-with-log-rotation-and-compression
https://tutorialedge.net/python/python-logging-best-practices/
https://stackoverflow.com/questions/32402502/how-to-change-the-time-zone-in-python-logging
https://stackoverflow.com/questions/6321160/how-to-set-timestamps-on-gmt-utc-on-python-logging
"""

# logger format
# logging.Formatter.converter = time.gmtime  # uncomment if you want UTC+0
logging.Formatter.converter = lambda *args: datetime.datetime.now(tz=timezone(TIMEZONE)).timetuple()
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')


class BotLogger:
    name: str = ''
    path: str = ''  # log path
    file_logger = None
    console_logger = None

    def get_file_logger(self, name, path):
        file_handler = TimedRotatingFileHandler(
            path,
            when="midnight",
            interval=1,
            encoding='utf8',
            backupCount=3
        )
        file_handler.suffix = "%Y%m%d"
        file_handler.setFormatter(formatter)

        # logger
        logger = logging.getLogger(name)
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)

        return logger

    def get_console_logger(self, name):
        # console handler
        # https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # logger
        # https://docs.python.org/3/library/logging.html
        # Multiple calls to getLogger() with the same name will always return a reference to the same Logger object.
        logger = logging.getLogger("console-%s" % name)
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)

        return logger

    def __init__(self, name):
        self.name = name
        self.path = 'log/%s.log' % self.name
        self.file_logger = self.get_file_logger(self.name, self.path)
        self.console_logger = self.get_console_logger(self.name)

    def debug(self, msg: str):
        self.console_logger.debug(msg)

    def info(self, msg: str):
        self.console_logger.info(msg)
        self.file_logger.info(msg)
        line(msg)

    def error(self, msg: str):
        self.console_logger.error(msg)
        self.file_logger.error(msg)
        line(msg)

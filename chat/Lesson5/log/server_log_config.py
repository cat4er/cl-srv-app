import logging
from logging.handlers import TimedRotatingFileHandler
import os

logger = logging.getLogger('chat.server')
logger.setLevel(logging.INFO)


def get_filename(filename):
    log_directory = os.path.split(filename)[0]
    date = os.path.splitext(filename)[1][1:]
    filename = os.path.join(log_directory, date)

    if not os.path.exists(f'{filename}.log'):
        return f'{filename}.log'


logger_handler = TimedRotatingFileHandler('realtime.log', when='d', interval=1, backupCount=10)
logger_handler.suffix = 'server_%Y-%m-%d'
logger_handler.namer = get_filename
# logger_handler = logging.FileHandler('server.log')
logger_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s -  %(message)s'))
logger.addHandler(logger_handler)
logger.info('Логирование включено!')

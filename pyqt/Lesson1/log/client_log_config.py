import logging

logger = logging.getLogger('chat.client')
logger.setLevel(logging.INFO)

logger_handler = logging.FileHandler('client.log')
logger_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s -  %(message)s'))
logger.addHandler(logger_handler)
logger.info('Логирование включено!')
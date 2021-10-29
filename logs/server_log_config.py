import sys
import os
import logging
import logging.handlers

from common.variables import LOGGING_STRING_FORMAT, LOGGING_DATE_FORMAT

log = logging.getLogger('server_log')
log.setLevel(logging.INFO)

PATH_TO_FILE = os.path.dirname(os.path.abspath(__file__))
PATH_TO_FILE = os.path.join(PATH_TO_FILE, 'server_logs', 'server.log')

SERVER_FORMATTER = logging.Formatter(fmt=LOGGING_STRING_FORMAT, datefmt=LOGGING_DATE_FORMAT)

stream_log_handler = logging.StreamHandler(sys.stdout)
stream_log_handler.setFormatter(SERVER_FORMATTER)
stream_log_handler.setLevel(logging.ERROR)
file_log_handler = logging.handlers.TimedRotatingFileHandler(PATH_TO_FILE, when='midnight', encoding='utf-8')
file_log_handler.setFormatter(SERVER_FORMATTER)

log.addHandler(stream_log_handler)
log.addHandler(file_log_handler)

if __name__ == '__main__':
    log.critical('crit')
    log.error('err')
    log.warning('warn')
    log.info('inf')

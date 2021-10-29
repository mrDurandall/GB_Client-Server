import sys
import os
import logging
import logging.handlers

from common.variables import LOGGING_STRING_FORMAT, LOGGING_DATE_FORMAT

log = logging.getLogger('client_log')
log.setLevel(logging.INFO)

PATH_TO_FILE = os.path.dirname(os.path.abspath(__file__))
PATH_TO_FILE = os.path.join(PATH_TO_FILE, 'client_logs', 'client.log')

CLIENT_FORMATTER = logging.Formatter(fmt=LOGGING_STRING_FORMAT, datefmt=LOGGING_DATE_FORMAT)

stream_log_handler = logging.StreamHandler(sys.stdout)
stream_log_handler.setFormatter(CLIENT_FORMATTER)
stream_log_handler.setLevel(logging.ERROR)
file_log_handler = logging.FileHandler(PATH_TO_FILE, encoding='utf-8')
file_log_handler.setFormatter(CLIENT_FORMATTER)

log.addHandler(stream_log_handler)
log.addHandler(file_log_handler)

if __name__ == '__main__':
    log.critical('crit')
    log.error('err')
    log.warning('warn')
    log.info('inf')

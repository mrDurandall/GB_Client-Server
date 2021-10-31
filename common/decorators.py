import sys
import logging
import logs.client_log_config
import logs.server_log_config
import traceback
import inspect

if sys.argv[0].find('client') == -1:
    log = logging.getLogger('server_log')
else:
    log = logging.getLogger('client_log')


def log_it(func):
    def wrapper(*args, **kwargs):
        decorated_func = func(*args, **kwargs)
        file_name = inspect.stack()[1][1].split("\\")[-1]
        log.debug(f'Вызвана функция {func.__name__} из модуля {func.__module__} с параметрами {args}, {kwargs}. '
                  f'Вызов произведен из функции {traceback.format_stack()[0].strip().split()[-1]} '
                  f'файла {file_name}.')
        return decorated_func

    return wrapper


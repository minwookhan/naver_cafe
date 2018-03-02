import logging
import logging.config
import json

def configure_logger(name, _cnf_file):
    '''
    name: cls_logger, info_only, default
    _cnf_file: the name of config file
    '''
    with open(_cnf_file, 'rt') as f:
        cnf = json.load(f)


    logging.config.dictConfig(cnf)

    return logging.getLogger(name)


class Log_filter(object):
    def __init__(self, level):
        self.__level = level
    def filter(self, logRecord):
        return logRecord.levelno == self.__level
#You can apply the filter to each of the two handlers like this:

# handler1.addFilter(Log_filter(logging.INFO))
# handler2.addFilter(Log_filter(logging.ERROR))




# alog = configure_logger('info_only','logging_config.json')
# alog.debug('debug message!')
# alog.info('info message!')
# alog.warning('warning message')
# alog.error('error message')
# alog.warning('warning message')
# alog.critical('critical message')


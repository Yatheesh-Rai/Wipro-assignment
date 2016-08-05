import logging
import logging.config
import os


def set_pylogger_config(name, loglevel):
    '''
    Control the logger configuration via codes
    '''
    if not loglevel:
        logging_level = logging.INFO
    else:
        logging_level = logging.DEBUG
    logging.basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=logging_level,
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)

    fh = logging.FileHandler('pydeploy.log')
    fh.setLevel(logging_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    logging.getLogger('').addHandler(fh)
    return logger


def set_pylogger_prop():
    '''
    Control the logger configuration via properties file
    '''
    logging.config.fileConfig(os.getcwd() + '/logger.properties')


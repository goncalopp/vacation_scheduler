from sys import stdout, stderr
from logging import getLogger, Formatter, StreamHandler, DEBUG, INFO, WARN, ERROR, CRITICAL

def get_logger(name, level=INFO ):
    logger= getLogger(name)
    fmt= Formatter('%(asctime)s %(levelname)8s %(name)8s %(lineno)3s - %(message)s')
    hdlr= StreamHandler(stderr)
    hdlr.setFormatter(fmt)
    logger.addHandler(hdlr)
    
    logger.setLevel(level)
    
    return logger


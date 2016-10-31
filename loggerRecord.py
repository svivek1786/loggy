#! /usr/bin/python
import logging
import sys
#===============================================================================
# Create a logging objects
#===============================================================================
#let force the name whichever invokes it doesnt matter
__name__ = 'OCPM Loggy Tool'

def loggerInit(logFileName):
    '''Handler for a streaming logging request. This basically logs the record
    using whatever logging policy is configured locally'''

    # create logger with 'OCPM Loggy Tool'
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('OCPM Loggy Tool')
    #logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(logFileName)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    #ch = logging.StreamHandler()
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.ERROR)
    #ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(funcName)s %(module)s:%(lineno)d - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    #print logger
    return logger

def get_logger():
    return logging.getLogger('OCPM Loggy Tool')

################################################################################

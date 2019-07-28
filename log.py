#!/usr/bin/env python
#-*-Python-*-

# pylint: disable-msg=C0103
# pylint: disable-msg=C0111
# pylint: disable-msg=C0301
# pylint: disable-msg=C0325
# pylint: disable-msg=C0330
# pylint: disable-msg=R0903

"""log.py

very simple logger based on logging.py

usage:

# create a logging object
import log
lg = log.create_logger(
    level=logging.INFO,
    name="test-logger",
    filename="/tmp/test-logger.log"
    console=True
)
lg.info("testing out logging")

# if you don't add a file handler right away,
# you can do it later with this function
log.add_file_handler(
    lg,
    filename="/tmp/another-log-file.log"
)

# you can alter the logging threshold level
# after the fact
#
# this change applies to all handlers associated with
# your logging object
log.change_log_level(
        lg,
        level=logging.WARNING
)

"""

import logging

# ------------------------------------------------------------
log_level_map = {
    "CRITICAL": logging.CRITICAL,
    "ERROR":    logging.ERROR,
    "WARNING":  logging.WARNING,
    "INFO":     logging.INFO,
    "DEBUG":    logging.DEBUG,
    "NOTSET":   logging.NOTSET
}

# ------------------------------------------------------------
def create_logger(
        level=logging.DEBUG,
        name="default.log.py",
        filename=None,
        console=True
):
    """ very simple logging to file and/or console """
    # log to console and file
    log = logging.getLogger(name)
    log.setLevel(level)
    # create formatter to add to handlers
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter(
         '%(created)s [%(name)s] %(asctime)s [%(levelname)s] [line %(lineno)s in %(module)s] : %(message)s'
    )
    if filename:
        # use file handler
        fh = logging.FileHandler(filename or ("/tmp/" + name + '.log'))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        log.addHandler(fh)
    if console:
        # use console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        log.addHandler(ch)
    return log

# ------------------------------------------------------------
def change_log_level(
        lg=None,
        level=logging.DEBUG
):
    """reset the logging level of logger object and its handlers"""
    if lg and level:
        lg.setLevel(level)
        [h.setLevel(level) for h in lg.handlers]

# ------------------------------------------------------------
def add_file_handler(
        lg=None,
        filename=None
):
    """add a file handler to an existing logger"""
    if lg and filename:
        handlers = [h for h in lg.handlers]
        # assumption: formatters and levels are all the same
        f = handlers[0].formatter
        l = handlers[0].level
        fh = logging.FileHandler(filename)
        fh.setLevel(l)
        fh.setFormatter(f)
        lg.addHandler(fh)

import os
import sys
import socket
import logging
from logging.handlers import SysLogHandler


# Logging initialization
# This filter adds the hostname and name to the log message
class ContextFilter(logging.Filter):
    hostname: str = socket.gethostname()
    def filter(self, record):
        record.hostname = ContextFilter.hostname
        return True


class LevelFilter(logging.Filter):
    def __init__(self, level: int):
        self.level = level

    def filter(self, record):
        return record.levelno <= self.level

    
def init_logging():
    """Initializes the logging system. This should be called at the beginning of the program."""

    CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(hostname)s %(levelname)s tootbot: %(message)s",
                "datefmt": "%b %d %H:%M:%S",
            },
        },
        "filters": {
            "level_filter": {
                "()": LevelFilter,
                "level": logging.WARNING,
            },
            "context_filter": {
                "()": ContextFilter,
            },
        },
        "handlers": {
            "syslog": {
                "class": "logging.handlers.SysLogHandler",
                "address": (os.getenv("LOG_DESTINATION", "localhost"), int(os.getenv("LOG_PORT", 514))),
                "facility": "LOG_USER",
                "formatter": "default",
                "filters": ["context_filter"],
                "level": logging.INFO,
            },
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default",
                "filters": ["context_filter", "level_filter"],
            },
        },
        "loggers": {
            "": {
                "handlers": ["syslog", "stdout"],
                "level": logging.INFO,
            },
        },
    }


    # This is the format for the log messages
    format_str = '%(asctime)s %(hostname)s %(levelname)s %(name)s: %(message)s'
    formatter = logging.Formatter(format_str, datefmt='%b %d %H:%M:%S')

    # These are the syslog parameters
    syslog_url = os.getenv('LOG_DESTINATION', 'localhost') # Backwards compatible with the original papertrail setup
    syslog_port = int(os.getenv('LOG_PORT', 514)) # Backwards compatible with the original papertrail setup
    syslog_address = (syslog_url, syslog_port)

    # This is the syslog handlers to send logs to the log sink
    syslog = SysLogHandler(address=syslog_address, facility=SysLogHandler.LOG_USER)
    syslog.addFilter(ContextFilter())
    syslog.setFormatter(formatter)
    syslog.setLevel(logging.INFO)

    # This is the stream handler to send logs to stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.addFilter(ContextFilter())
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    # This is the logger object
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(syslog)
    logger.addHandler(stream_handler)
    # End logging initialization

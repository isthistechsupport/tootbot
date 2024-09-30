import os
import sys
import socket
import logging
import logging.config
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
                "level": logging.INFO
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "stream": sys.stderr,
                "formatter": "default",
                "filters": ["context_filter"],
                "level": logging.ERROR,
            },
        },
        "loggers": {
            "": {
                "handlers": ["syslog", "stdout"],
                "level": logging.INFO,
            },
        },
    }
    logging.config.dictConfig(CONFIG)
    # End logging initialization

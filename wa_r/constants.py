import logging
import colorama
import time

CONSOLE_LOG_FORMAT = "{}%(name)s - {}[%(levelname)s] {}%(message)s"
CONSOLE_LOG_COLOURS = colorama.Fore
CONSOLE_LOG_LEVEL_COLOURS = {logging.DEBUG: CONSOLE_LOG_COLOURS.MAGENTA,
                             logging.INFO: CONSOLE_LOG_COLOURS.CYAN,
                             logging.WARNING: CONSOLE_LOG_COLOURS.YELLOW,
                             logging.ERROR: CONSOLE_LOG_COLOURS.RED,
                             logging.CRITICAL: CONSOLE_LOG_COLOURS.BLACK}

FILE_LOG_FORMAT = "%(name)s - [%(asctime)s] - %(levelname)s: %(message)s"
LOG_DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

UTC_TIME_OFFSET = int((time.timezone if (time.localtime().tm_isdst == 0) else time.altzone) / -3600)

import logging
import colorama

CONSOLE_LOG_FORMAT = "{}%(name)s - {}[%(levelname)s] {}%(message)s"
CONSOLE_LOG_COLOURS = colorama.Fore
CONSOLE_LOG_LEVEL_COLOURS = {logging.DEBUG: CONSOLE_LOG_COLOURS.MAGENTA,
                             logging.INFO: CONSOLE_LOG_COLOURS.CYAN,
                             logging.WARNING: CONSOLE_LOG_COLOURS.YELLOW,
                             logging.ERROR: CONSOLE_LOG_COLOURS.RED,
                             logging.CRITICAL: CONSOLE_LOG_COLOURS.BLACK}

FILE_LOG_FORMAT = "%(name)s - [%(asctime)s] - %(levelname)s: %(message)s"
LOG_DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
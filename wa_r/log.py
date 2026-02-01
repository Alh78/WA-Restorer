import config
import logging
import colorama

colorama.init(True)


class BasicConsoleFormatter(logging.Formatter):
    console_log_format = config.CONSOLE_LOG_FORMAT
    console_log_level_colours = config.CONSOLE_LOG_LEVEL_COLOURS

    def __init__(self):
        super().__init__(BasicConsoleFormatter.console_log_format)
    
    def format(self, record):
        return logging.Formatter(self._fmt.format(config.CONSOLE_LOG_COLOURS.LIGHTBLACK_EX, self.console_log_level_colours[record.levelno], config.CONSOLE_LOG_LEVEL_MESSAGES_COLOURS[record.levelno])).format(record)

class BasicFileFormatter(logging.Formatter):
    file_log_format = config.FILE_LOG_FORMAT

    def __init__(self):
        super().__init__(BasicFileFormatter.file_log_format, config.LOG_DATE_FORMAT)

basic_console_handler = logging.StreamHandler()
basic_console_handler.setFormatter(BasicConsoleFormatter())

sameline_console_handler = logging.StreamHandler()
sameline_console_handler.terminator = "\r"
sameline_console_handler.setFormatter(BasicConsoleFormatter())

def initialize_ingestor_file_handler():
    global ingestor_file_handler
    ingestor_file_handler = logging.FileHandler(config.INGESTOR_LOG_FILE_NAME, "a")
    ingestor_file_handler.setFormatter(BasicFileFormatter())

def initialize_restorer_file_handler():
    global restorer_file_handler
    restorer_file_handler = logging.FileHandler(config.RESTORER_LOG_FILE_NAME, "a")
    restorer_file_handler.setFormatter(BasicFileFormatter())


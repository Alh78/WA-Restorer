import wa_r.constants
import logging
import colorama

colorama.init(True)

CONSOLE_LOG_FORMAT = "{}%(name)-18s: {}%(message)s"
CONSOLE_LOG_COLOURS = colorama.Fore
CONSOLE_LOG_LEVEL_COLOURS = {
    logging.DEBUG: CONSOLE_LOG_COLOURS.RESET,
    logging.INFO: CONSOLE_LOG_COLOURS.RESET,
    logging.WARNING: CONSOLE_LOG_COLOURS.YELLOW,
    logging.ERROR: CONSOLE_LOG_COLOURS.LIGHTRED_EX,
    logging.CRITICAL: CONSOLE_LOG_COLOURS.RED,
}

CONSOLE_LOG_LEVEL_MESSAGES_COLOURS = {
    logging.DEBUG: CONSOLE_LOG_COLOURS.RESET,
    logging.INFO: CONSOLE_LOG_COLOURS.RESET,
    logging.WARNING: CONSOLE_LOG_COLOURS.RESET,
    logging.ERROR: CONSOLE_LOG_COLOURS.LIGHTRED_EX,
    logging.CRITICAL: CONSOLE_LOG_COLOURS.LIGHTRED_EX,
}

FILE_LOG_FORMAT = "%(name)s - [%(asctime)s] - %(levelname)s: %(message)s"
LOG_DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

INGESTOR_LOG_FILE_NAME = f"ingestor_{wa_r.constants.CURRENT_INIT_TIME:%H-%M-%S_%m-%d-%Y}.log"
RESTORER_LOG_FILE_NAME = f"restorer_{wa_r.constants.CURRENT_INIT_TIME:%H-%M-%S_%m-%d-%Y}.log"
FILTERER_LOG_FILE_NAME = f"filterer_{wa_r.constants.CURRENT_INIT_TIME:%H-%M-%S_%m-%d-%Y}.log"


class BasicConsoleFormatter(logging.Formatter):
    console_log_format = CONSOLE_LOG_FORMAT
    console_log_level_colours = CONSOLE_LOG_LEVEL_COLOURS

    def __init__(self):
        super().__init__(BasicConsoleFormatter.console_log_format)

    def format(self, record):
        return logging.Formatter(
            self._fmt.format(
                CONSOLE_LOG_COLOURS.LIGHTBLACK_EX,
                self.console_log_level_colours[record.levelno],
                CONSOLE_LOG_LEVEL_MESSAGES_COLOURS[record.levelno],
            )
        ).format(record)


class BasicFileFormatter(logging.Formatter):
    file_log_format = FILE_LOG_FORMAT

    def __init__(self):
        super().__init__(
            BasicFileFormatter.file_log_format, LOG_DATE_FORMAT
        )


basic_console_handler = logging.StreamHandler()
basic_console_handler.setFormatter(BasicConsoleFormatter())

sameline_console_handler = logging.StreamHandler()
sameline_console_handler.terminator = "\r"
sameline_console_handler.setFormatter(BasicConsoleFormatter())


def prepare_filterer_loggers(save_logs: bool = False):
    main_logger = logging.getLogger("filterer")
    main_logger.setLevel(logging.INFO)
    main_logger.addHandler(basic_console_handler)

    filterer_logger = logging.getLogger("wa_r.core.filter")
    database_logger = logging.getLogger("wa_r.database")

    filterer_logger.setLevel(logging.INFO)
    filterer_logger.addHandler(basic_console_handler)

    database_logger.setLevel(logging.INFO)
    database_logger.addHandler(basic_console_handler)

    if save_logs:
        file_handler = logging.FileHandler(FILTERER_LOG_FILE_NAME, "a")
        file_handler.setFormatter(BasicFileFormatter())

        main_logger.addHandler(file_handler)
        filterer_logger.addHandler(file_handler)
        database_logger.addHandler(file_handler)

def prepare_ingestor_loggers(save_logs: bool = False):
    main_logger = logging.getLogger("ingestor")
    main_logger.setLevel(logging.INFO)
    main_logger.addHandler(basic_console_handler)

    ingestor_parser_logger = logging.getLogger("wa_r.core.ingest")
    database_logger = logging.getLogger("wa_r.database")

    ingestor_parser_logger.setLevel(logging.INFO)
    ingestor_parser_logger.addHandler(basic_console_handler)

    database_logger.setLevel(logging.INFO)
    database_logger.addHandler(basic_console_handler)

    if save_logs:
        file_handler = logging.FileHandler(INGESTOR_LOG_FILE_NAME, "a")
        file_handler.setFormatter(BasicFileFormatter())

        main_logger.addHandler(file_handler)
        ingestor_parser_logger.addHandler(file_handler)
        database_logger.addHandler(file_handler)

def prepare_restorer_loggers(save_logs: bool = False):
    main_logger = logging.getLogger("restorer")
    main_logger.setLevel(logging.INFO)
    main_logger.addHandler(basic_console_handler)

    restorer_writer_logger = logging.getLogger("wa_r.core.restore")
    database_logger = logging.getLogger("wa_r.database")

    restorer_writer_logger.setLevel(logging.INFO)
    restorer_writer_logger.addHandler(basic_console_handler)

    database_logger.setLevel(logging.INFO)
    database_logger.addHandler(basic_console_handler)

    if save_logs:
        file_handler = logging.FileHandler(RESTORER_LOG_FILE_NAME, "a")
        file_handler.setFormatter(BasicFileFormatter())

        main_logger.addHandler(file_handler)
        restorer_writer_logger.addHandler(file_handler)
        database_logger.addHandler(file_handler)

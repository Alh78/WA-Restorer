import wa_r.constants
import logging
import colorama

colorama.init(True)


class BasicConsoleFormatter(logging.Formatter):
    console_log_format = wa_r.constants.CONSOLE_LOG_FORMAT
    console_log_level_colours = wa_r.constants.CONSOLE_LOG_LEVEL_COLOURS

    def __init__(self):
        super().__init__(BasicConsoleFormatter.console_log_format)

    def format(self, record):
        return logging.Formatter(
            self._fmt.format(
                wa_r.constants.CONSOLE_LOG_COLOURS.LIGHTBLACK_EX,
                self.console_log_level_colours[record.levelno],
                wa_r.constants.CONSOLE_LOG_LEVEL_MESSAGES_COLOURS[record.levelno],
            )
        ).format(record)


class BasicFileFormatter(logging.Formatter):
    file_log_format = wa_r.constants.FILE_LOG_FORMAT

    def __init__(self):
        super().__init__(
            BasicFileFormatter.file_log_format, wa_r.constants.LOG_DATE_FORMAT
        )


basic_console_handler = logging.StreamHandler()
basic_console_handler.setFormatter(BasicConsoleFormatter())

sameline_console_handler = logging.StreamHandler()
sameline_console_handler.terminator = "\r"
sameline_console_handler.setFormatter(BasicConsoleFormatter())


def prepare_ingestor_loggers(save_logs: bool = False):
    main_logger = logging.getLogger("ingestor")
    main_logger.setLevel(logging.INFO)
    main_logger.addHandler(basic_console_handler)

    ingestor_parser_logger = logging.getLogger("wa_r.core.ingestor")
    database_logger = logging.getLogger("wa_r.database")

    ingestor_parser_logger.setLevel(logging.WARNING)
    ingestor_parser_logger.addHandler(basic_console_handler)

    database_logger.setLevel(logging.INFO)
    database_logger.addHandler(basic_console_handler)

    if save_logs:
        file_handler = logging.FileHandler(wa_r.constants.INGESTOR_LOG_FILE_NAME, "a")
        file_handler.setFormatter(BasicFileFormatter())

        main_logger.addHandler(file_handler)
        ingestor_parser_logger.addHandler(file_handler)
        database_logger.addHandler(file_handler)

def prepare_restorer_loggers(save_logs: bool = False):
    main_logger = logging.getLogger("restorer")
    main_logger.setLevel(logging.INFO)
    main_logger.addHandler(basic_console_handler)

    restorer_writer_logger = logging.getLogger("wa_r.core.restorer")
    database_logger = logging.getLogger("wa_r.database")

    restorer_writer_logger.setLevel(logging.INFO)
    restorer_writer_logger.addHandler(basic_console_handler)

    database_logger.setLevel(logging.INFO)
    database_logger.addHandler(basic_console_handler)

    if save_logs:
        file_handler = logging.FileHandler(wa_r.constants.RESTORER_LOG_FILE_NAME, "a")
        file_handler.setFormatter(BasicFileFormatter())

        main_logger.addHandler(file_handler)
        restorer_writer_logger.addHandler(file_handler)
        database_logger.addHandler(file_handler)

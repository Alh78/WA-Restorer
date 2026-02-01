import wa_r.types
import logging
import colorama
import datetime
import logging
import time
import os


CURRENT_INIT_TIME = datetime.datetime.now()

DEFAULT_MEDIA_CHUNK_SIZE = 1024 * 16
PROC_POOL_SIZE = os.cpu_count() - 1 # os.process_cpu_count() for Python 3.13+

DATABASE_COMMIT_BUFFER_SIZE = 100

GENERIC_ATTACHED_MESSAGE_PATTERN = r"^(\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2})\s-\s([^:]+):\s(.*?)\s\(dosya ekli\)"
NATIVE_ATTACHED_FILE_NAME_PATTERN = r"^(\w{3})-(\d{8})-WA\d{4}.*?"

DEFAULT_IMAGE_HASH_SIZE = 8

DEFAULT_IMAGE_HASHING_ALGORITHM = wa_r.types.ImageHashingAlgorithm.PHASH
DEFAULT_VIDEO_HASHING_ALGORITHM = wa_r.types.VideoHashingAlgorithm.WHASH 

DEFAULT_METADATA_DATE_PRIORITY = wa_r.types.MetadataDatePriority.EARLIEST

CONSOLE_LOG_FORMAT = "{}%(name)s - {}[%(levelname)s] {}%(message)s"
CONSOLE_LOG_COLOURS = colorama.Fore
CONSOLE_LOG_LEVEL_COLOURS = {logging.DEBUG: CONSOLE_LOG_COLOURS.RESET,
                             logging.INFO: CONSOLE_LOG_COLOURS.RESET,
                             logging.WARNING: CONSOLE_LOG_COLOURS.YELLOW,
                             logging.ERROR: CONSOLE_LOG_COLOURS.LIGHTRED_EX,
                             logging.CRITICAL: CONSOLE_LOG_COLOURS.RED}

CONSOLE_LOG_LEVEL_MESSAGES_COLOURS = {logging.DEBUG: CONSOLE_LOG_COLOURS.RESET,
                                      logging.INFO: CONSOLE_LOG_COLOURS.RESET,
                                      logging.WARNING: CONSOLE_LOG_COLOURS.RESET,
                                      logging.ERROR: CONSOLE_LOG_COLOURS.LIGHTRED_EX,
                                      logging.CRITICAL: CONSOLE_LOG_COLOURS.LIGHTRED_EX}

FILE_LOG_FORMAT = "%(name)s - [%(asctime)s] - %(levelname)s: %(message)s"
LOG_DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

INGESTOR_LOG_FILE_NAME = f"ingestor_{CURRENT_INIT_TIME:%H-%M-%S_%m-%d-%Y}.log"
RESTORER_LOG_FILE_NAME = f"restorer_{CURRENT_INIT_TIME:%H-%M-%S_%m-%d-%Y}.log"

UTC_TIME_OFFSET = int((time.timezone if (time.localtime().tm_isdst == 0) else time.altzone) / -3600)

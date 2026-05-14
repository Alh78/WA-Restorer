import wa_r.types
import datetime
import time
import os

CURRENT_INIT_TIME = datetime.datetime.now()

DEFAULT_FILE_READING_CHUNK_SIZE = 1024 * 16

DEFAULT_PROC_POOL_SIZE = os.cpu_count() - 1  # os.process_cpu_count() for Python 3.13+

DEFAULT_DATABASE_COMMIT_BUFFER_SIZE = 100

DEFAULT_FILE_HASHING_ALGORITHM = wa_r.types.FileHashingAlgorithm.SHA256

DEFAULT_IMAGE_HASHING_ALGORITHM = wa_r.types.ImageHashingAlgorithm.PHASH
DEFAULT_IMAGE_HASH_SIZE = 8

DEFAULT_VIDEO_HASHING_ALGORITHM = wa_r.types.VideoHashingAlgorithm.WHASH

DEFAULT_METADATA_DATE_PRIORITY = wa_r.types.MetadataDatePriority.EARLIEST

DEFAULT_INGESTOR_LANGUAGE_PREFERENCE = wa_r.types.BackupMessagesLangDetectionPreferences.AUTO_FAST


UTC_TIME_OFFSET = int(
    (time.timezone if (time.localtime().tm_isdst == 0) else time.altzone) / -3600
)

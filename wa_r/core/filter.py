import wa_r.parsing.engine
import wa_r.factory
import wa_r.exceptions
import wa_r.types
import wa_r.database
import wa_r.constants
import wa_r.hashing
import wa_r.file
import contextlib
import typing
import logging
import os

main_logger = logging.getLogger(__name__)

# wa_r filter --media --origin --exclude-dir ... --include-only-dir ... --include ... --exclude ... --hash


def initiate_filtering_process(messages_database: wa_r.database.AttachedMessagesDatabaseProcessor, filter_media: bool, filter_origin: bool, exclude_dir: str = None, include_only_dir: str = None, exclude_file: str = None):
    if filter_media:
        main_logger.debug("Filtering media messages...")
        messages_database.filter_media_messages()

    if filter_origin:
        main_logger.debug("Filtering origin messages...")
        messages_database.filter_origin_messages()

    if isinstance(exclude_dir, str):
        excluded_files = os.listdir(exclude_dir)
        main_logger.debug(f"Excluding files in: {exclude_dir}")
        messages_database.remove_messages_by_file_name(excluded_files)

    if isinstance(include_only_dir, str):
        whitelist_files = os.listdir(include_only_dir)
        main_logger.debug(f"Whitelisting files in: {include_only_dir}")
        messages_database.whitelist_messages_by_file_name(whitelist_files)

    if isinstance(exclude_file, str):
        main_logger.debug(f"Excluding file: {exclude_file}")
        messages_database.remove_messages_by_file_name([exclude_file,])





    # --include-file won't be added as an optional argument because the file intended to be included in the database cannot be validated
    # and this may cause serious problems in database and filtering operations.
    
    # Hashing later...



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

parser_logger = logging.getLogger(__name__)

# We won't be using process pool.


def process_message_line(message_line: str, line_index: int, language: wa_r.types.BackupMessagesLanguages, directory: str = "") -> typing.Union[wa_r.types.AttachedMessageData, None]:
    parser_logger.debug(f"Processing message line {line_index}...")

    try:
        raw_message_data = wa_r.parsing.engine.parse_raw_message_data(
            message_line, line_index, language)

    except wa_r.exceptions.MismatchMessagePatternException:
        parser_logger.debug(
            f"Message line {line_index} doesn't contain any attachment or is a continuation of a message earlier.")
        return  # ! Will return here
        # This exception means this line is probably a continuation of a message, so there won't be any attachment information
        # to be gathered in this line, thus we have to cut the flow and return.

    parser_logger.debug(
        "Parsing file meta data by name and generating hash...")
    file_meta_data = wa_r.parsing.engine.parse_file_meta_data(
        raw_message_data.content)

    try:
        file_hash = wa_r.hashing.generate_file_content_hash(
            os.path.abspath(os.path.join(directory, file_meta_data.file_name)))

    except FileNotFoundError:
        parser_logger.error(
            f"Failed to find the file of Message(line_index={line_index}) and failed to generate file hash.")
        parser_logger.warning(
            f"Message(line_index={line_index}) and its attachments won't be added to database.")
        return

    parser_logger.debug("Packaging file data...")
    file_data = wa_r.factory.package_file_data(file_meta_data, file_hash)

    parser_logger.debug("Packaging message data...")
    message_data = wa_r.factory.package_message_data(
        raw_message_data, file_data)

    return message_data


def detect_backup_language(language_detection_preference: wa_r.types.BackupMessagesLangDetectionPreferences, backup_message_file_path: str) -> wa_r.types.BackupMessagesLanguages:
    if language_detection_preference == wa_r.types.BackupMessagesLangDetectionPreferences.AUTO_FAST:
        deep_search = False

    elif language_detection_preference == wa_r.types.BackupMessagesLangDetectionPreferences.AUTO_ALL:
        deep_search = True

    else:
        raise ValueError(
            "Invalid auto searching preference: {language_detection_preference}")

    with contextlib.closing(wa_r.file.read_file_message_lines(backup_message_file_path)) as backup_messages_lines:
        return wa_r.parsing.engine.determine_backup_language(backup_messages_lines, deep_search)


def initiate_importing_process(backup_dir: str, backup_message_file_path: str, messages_database: wa_r.database.AttachedMessagesDatabaseImporter, commit_buffer_size: int = wa_r.constants.DEFAULT_DATABASE_COMMIT_BUFFER_SIZE, language_detection_preference: wa_r.types.BackupMessagesLangDetectionPreferences = None, language: wa_r.types.BackupMessagesLanguages = None):
    if language_detection_preference and language:
        raise ValueError("language_detection_preference and language cannot be used together.")


    if language_detection_preference in wa_r.types.BackupMessagesLangDetectionPreferences:
        backup_language = detect_backup_language(
            language_detection_preference, backup_message_file_path)

        parser_logger.info(f"Detected language: {backup_language}")

    elif language in wa_r.types.BackupMessagesLanguages:
        backup_language = language

    else:
        raise ValueError("Invalid or missing configuration. "
                         f"(language_detection_preference={language_detection_preference!r}, "
                         f"language={language!r})")

    committing_counter = 0
    for line_index, message_line in enumerate(wa_r.file.read_file_message_lines(backup_message_file_path), 1):
        message = process_message_line(
            message_line, line_index, backup_language, backup_dir)
        if message is None:
            parser_logger.debug(f"Passing message line {line_index}.")
            continue

        try:
            messages_database.add_attached_message(message)

        except (wa_r.exceptions.SenderAdditionError, wa_r.exceptions.MessageInsertionError):
            # Think about reverting.
            parser_logger.debug(f"Passing message line {line_index}.")
            continue

        committing_counter += 1

        if committing_counter >= commit_buffer_size:
            messages_database.commit_changes()
            committing_counter = 0

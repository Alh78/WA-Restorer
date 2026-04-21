import wa_r.parsing
import wa_r.factory
import wa_r.exceptions
import wa_r.types
import wa_r.database
import wa_r.constants
import wa_r.hashing
import wa_r.file
import typing
import logging
import os

parser_logger = logging.getLogger(__name__)

#We won't be using process pool.

def process_message_line(message_line: str, line_index: int, directory: str = "") -> typing.Union[wa_r.types.AttachedMessageData, None]:
    parser_logger.info(f"Processing message line {line_index}...")

    parser_logger.debug("Filtering message line with RegEx expression...")
    try:
        raw_message_data = wa_r.parsing.parse_raw_message_data(message_line, line_index)

    except wa_r.exceptions.MismatchMessagePatternException:
        parser_logger.debug(f"Message line {line_index} doesn't contain any attachment or is a continuation of a message earlier.")
        return #! Will return here
               # This exception means this line is probably a continuation of a message, so there won't be any attachment information
               # to be gathered in this line, thus we have to cut the flow and return.

    parser_logger.debug("Parsing file meta data by name and generating hash...")
    file_meta_data = wa_r.parsing.parse_file_meta_data(raw_message_data.content)

    try:
        file_hash = wa_r.hashing.generate_file_content_hash(os.path.abspath(os.path.join(directory, file_meta_data.file_name)))

    except FileNotFoundError:
        parser_logger.error(f"Failed to find the file of Message(line_index={line_index}) and failed to generate file hash.")
        parser_logger.warning(f"Message(line_index={line_index}) and its attachments won't be added to database.")
        return

    parser_logger.debug("Packaging file data...")
    file_data = wa_r.factory.package_file_data(file_meta_data, file_hash)

    parser_logger.debug("Packaging message data...")
    message_data = wa_r.factory.package_message_data(raw_message_data, file_data)

    return message_data


def initiate_importing_process(backup_dir: str, backup_message_file_path: str, messages_database: wa_r.database.AttachedMessagesDatabaseImporter):
        committing_counter = 0
        for line_index, message_line in enumerate(wa_r.file.read_file_message_lines(backup_message_file_path), 1):
            message = process_message_line(message_line, line_index, backup_dir)
            if message is None:
                parser_logger.debug(f"Passing message line {line_index}.")
                continue
            
            try:
                messages_database.add_attached_message(message)

            except (wa_r.exceptions.SenderAdditionError, wa_r.exceptions.MessageInsertionError):
                parser_logger.debug(f"Passing message line {line_index}.") # Think about reverting.
                continue

            committing_counter += 1 

            if committing_counter >= wa_r.constants.DATABASE_COMMIT_BUFFER_SIZE:
                messages_database.commit_changes()
                committing_counter = 0

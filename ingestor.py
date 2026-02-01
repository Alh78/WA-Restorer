import wa_r.exceptions
import wa_r.database
import wa_r.parsing
import wa_r.types
import wa_r.file
import wa_r.log
import argparse
import logging
import typing
import config
import sys
import os

#We won't be using process pool.

def process_message_line(message_line: str, line_index: int, directory: str = "") -> typing.Union[wa_r.types.AttachedMessageData, None]:
	parser_log.info(f"Processing message line {line_index}...")

	parser_log.debug("Filtering message line with RegEx expression...")
	try:
		raw_message_data = wa_r.parsing.parse_raw_message_data(message_line, line_index)

	except wa_r.exceptions.MismatchMessagePatternException:
		parser_log.debug(f"Message line {line_index} doesn't contain any attachment or is a continuation of a message earlier.")
		return #! Will return here
			   # This exception means this line is probably a continuation of a message, so there won't be any attachment information
			   # to be gathered in this line, thus we have to cut the flow and return.

	parser_log.debug("Parsing file meta data by name and generating hash...")
	file_meta_data = wa_r.parsing.parse_file_meta_data(raw_message_data.content)

	try:
		file_hash = wa_r.file.generate_file_content_hash(os.path.abspath(os.path.join(directory, file_meta_data.file_name)))

	except FileNotFoundError:
		parser_log.error(f"Failed to find the file of Message(line_index={line_index}) and failed to generate file hash.")
		parser_log.warning(f"Message(line_index={line_index}) and its attachments won't be added to database.")
		return

	parser_log.debug("Packaging file data...")
	file_data = wa_r.parsing.package_file_data(file_meta_data, file_hash)

	parser_log.debug("Packaging message data...")
	message_data = wa_r.parsing.package_message_data(raw_message_data, file_data)

	return message_data


if __name__ == "__main__": 
	main_parser = argparse.ArgumentParser(prog = "ingestor.py",
					                	  description = "Parses, packages and converts WhatsApp messages with attachments to SQL database.",
					                	  add_help = False)
	main_parser.add_argument("backup_directory")
	main_parser.add_argument("backup_message_file")

	app_args = main_parser.parse_args()
	app_args.backup_directory = os.path.abspath(app_args.backup_directory)
	app_args.backup_message_file = os.path.abspath(app_args.backup_message_file)


	main_log = logging.getLogger("main")
	main_log.setLevel(logging.INFO)

	wa_r.log.initialize_ingestor_file_handler()

	main_log.addHandler(wa_r.log.basic_console_handler)
	main_log.addHandler(wa_r.log.ingestor_file_handler)

	main_log.info(f"Backup directory: {app_args.backup_directory}")
	main_log.info(f"Backup messages file: {app_args.backup_message_file}")

	if not os.path.exists(app_args.backup_directory):
		main_log.critical("Specified backup directory doesn't exist.")
		raise SystemExit()

	elif not os.path.isdir(app_args.backup_directory):
		main_log.critical("Specified backup directory path doesn't refer to a proper directory.")
		raise SystemExit()

	if not os.path.exists(app_args.backup_message_file):
		main_log.critical("Specified backup messages file doesn't exist.")
		main_log.warning("Backup files containing messages and exported from WhatsApp has a hidden character in their name. If the file name you prompted is same with the message file name, please try to rename the specified file.")
		raise SystemExit()

	elif not os.path.isfile(app_args.backup_message_file):
		main_log.critical("Specified backup messages file path doesn't refer to a proper file.")
		raise SystemExit()

	main_log.info("Initializing loggers...")

	parser_log = logging.getLogger("MessageParser")
	parser_log.setLevel(logging.WARNING)
	parser_log.addHandler(wa_r.log.basic_console_handler)
	parser_log.addHandler(wa_r.log.ingestor_file_handler)


	main_log.info("Initializing database class...")

	messages_db = wa_r.database.AttachedMessagesDatabaseIngestor(f"{os.path.basename(app_args.backup_directory)}_media.db")
	messages_db.database_log.setLevel(logging.INFO)
	messages_db.database_log.addHandler(wa_r.log.basic_console_handler)
	messages_db.database_log.addHandler(wa_r.log.ingestor_file_handler)

	main_log.info("Starting to read line by line and parsing...")

	try:
		committing_counter = 0
		for line_index, message_line in enumerate(wa_r.file.read_file_message_lines(os.path.abspath(app_args.backup_message_file)), 1):
			message = process_message_line(message_line, line_index, app_args.backup_directory)
			if message is None:
				parser_log.debug(f"Passing message line {line_index}.")
				continue

			messages_db.add_attached_message(message)
			committing_counter += 1 

			if committing_counter >= config.DATABASE_COMMIT_BUFFER_SIZE:
				messages_db.commit_changes()
				committing_counter = 0

	except:
		main_log.error("An exception occured during the process!", exc_info = True)

	else:
		main_log.info("Ingestion successful!")

	finally:
		main_log.info("Applying last commit...")
		messages_db.commit_changes()
    	
    	messages_db.close()
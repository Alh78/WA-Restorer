import helper.exceptions
import helper.database
import helper.parsing
import helper.types
import helper.file
import helper.log
import argparse
import logging
import typing
import config
import os

def write_restored_metadata_to_file(file_name: str, device_brand: str = None, device_model: str = None):
	writer_log.info(f"Writing restored metadata to File(file_name=\"{file_name}\")...")

	writer_log.debug(f"Getting origin message of File(file_name=\"{file_name}\") from reference database...")
	message_data = reference_db.get_sender_message_by_attached_file_name(file_name)

	if isinstance(message_data, list) and message_data:
		writer_log.critical(f"File(file_name=\"{file_name}\") contains multiple origins in the database!")
		raise helper.exceptions.MultipleOriginFilesException(f"File \"{file_name}\" have multiple origins in the database!")

	if not message_data: # This means message data returned as a blank list from database,  which means this file doesn't have any record on DB.
		writer_log.error(f"File(file_name=\"{file_name}\") doesn't have any record in the database.")
		writer_log.warning(f"File(\"{file_name}\") will be skipped during the process.")
		return

	writer_log.debug("Generating WPMediaExifData instance using fetched origin message data...")
	exif_data = helper.parsing.generate_media_exif_data(message_data, device_brand, device_model)

	writer_log.debug(f"Writing new File(file_path=\"{os.path.abspath(os.path.join(app_args.destination_directory, file_name))}\")...")

	try:
		helper.file.write_new_exif_data(os.path.abspath(os.path.join(app_args.media_directory, file_name)),
										os.path.abspath(os.path.join(app_args.destination_directory, file_name)),
										exif_data,
										add_owner = True,
										edit_file_dates = True)

	except helper.exceptions.FileAlreadyContainsMetaDataException:
		pass
		"""writer_log.error(f"File(file_name=\"{file_name}\") already contains EXIF data.")
								writer_log.warning("File(\"{file_name}\") will be skipped during the process.")
								return"""


if __name__ == "__main__": 
	main_parser = argparse.ArgumentParser(prog = "restorer.py",
					                	  description = "Restores EXIF data of media files exported from Whatsapp Backup using SQL databases.",
					                	  add_help = False)
	main_parser.add_argument("reference_database_file")
	main_parser.add_argument("media_directory")
	main_parser.add_argument("destination_directory")

	app_args = main_parser.parse_args()
	app_args.reference_database_file = os.path.abspath(app_args.reference_database_file)
	app_args.media_directory = os.path.abspath(app_args.media_directory)
	app_args.destination_directory = os.path.abspath(app_args.destination_directory)


	main_log = logging.getLogger("main")
	main_log.setLevel(logging.INFO)

	helper.log.initialize_restorer_file_handler()

	main_log.addHandler(helper.log.basic_console_handler)
	main_log.addHandler(helper.log.restorer_file_handler)

	main_log.info(f"Reference database file: {app_args.reference_database_file}")
	main_log.info(f"Media directory: {app_args.destination_directory}")
	main_log.info(f"Destination directory: {app_args.destination_directory}")

	if not os.path.exists(app_args.reference_database_file):
		main_log.critical("Specified database file doesn't exist.")
		raise SystemExit()

	elif not os.path.isfile(app_args.reference_database_file):
		main_log.critical("Specified database file path doesn't refer to a proper file.")
		raise SystemExit()


	if not os.path.exists(app_args.media_directory):
		main_log.critical("Specified media directory doesn't exist.")
		raise SystemExit()

	elif not os.path.isdir(app_args.media_directory):
		main_log.critical("Specified media directory path doesn't refer to a proper directory.")
		raise SystemExit()

	if not os.path.exists(app_args.destination_directory):
		main_log.info("Creating destination directory...")
		os.makedirs(app_args.destination_directory)

	elif not os.path.isdir(app_args.destination_directory):
		main_log.critical("Specified destination directory path doesn't refer to a proper directory.")
		raise SystemExit()


	main_log.info("Initializing loggers...")

	writer_log = logging.getLogger("FileMetadataWriter")
	writer_log.setLevel(logging.INFO)
	writer_log.addHandler(helper.log.basic_console_handler)
	writer_log.addHandler(helper.log.restorer_file_handler)

	main_log.info("Initializing database class...")

	reference_db = helper.database.AttachedMessagesDatabaseAnalyzer(app_args.reference_database_file)
	reference_db.database_log.setLevel(logging.INFO)
	reference_db.database_log.addHandler(helper.log.basic_console_handler)
	reference_db.database_log.addHandler(helper.log.restorer_file_handler)

	main_log.info("Starting to restoration...")

	try:
		for media_file_name in os.listdir(app_args.media_directory):
			write_restored_metadata_to_file(media_file_name, "samsung", "SM721-B")

	except helper.exceptions.MultipleOriginFilesException:
		main_log.warning("Please filter the database file specified before using restorer.")

	except:
		main_log.error("An exception occured during the process!", exc_info = True)

	else:
		main_log.info("Restoration completed without any issues.")

	finally:
		main_log.info("Closing database...")
		reference_db.close()
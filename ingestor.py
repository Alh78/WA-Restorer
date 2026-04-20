import wa_r.core.ingest
import wa_r.database
import wa_r.log
import argparse
import logging
import typing
import sys
import os


if __name__ == "__main__": 
    main_parser = argparse.ArgumentParser(prog = "ingestor.py",
                                          description = "Parses, packages and converts WhatsApp messages with attachments to SQL database.",
                                          add_help = False)
    main_parser.add_argument("backup_directory")
    main_parser.add_argument("backup_message_file")

    app_args = main_parser.parse_args()
    app_args.backup_directory = os.path.abspath(app_args.backup_directory)
    app_args.backup_message_file = os.path.abspath(app_args.backup_message_file)

    main_logger = logging.getLogger("ingestor")

    main_logger.info("Initializing loggers...")
    wa_r.log.prepare_ingestor_loggers()

    main_logger.info(f"Backup directory: {app_args.backup_directory}")
    main_logger.info(f"Backup messages file: {app_args.backup_message_file}")

    if not os.path.exists(app_args.backup_directory):
        main_logger.critical("Specified backup directory doesn't exist.")
        raise SystemExit()

    elif not os.path.isdir(app_args.backup_directory):
        main_logger.critical("Specified backup directory path doesn't refer to a proper directory.")
        raise SystemExit()

    if not os.path.exists(app_args.backup_message_file):
        main_logger.critical("Specified backup messages file doesn't exist.")
        main_logger.warning("Backup files containing messages and exported from WhatsApp has a hidden character in their name. If the file name you prompted is same with the message file name, please try to rename the specified file.")
        raise SystemExit()

    elif not os.path.isfile(app_args.backup_message_file):
        main_logger.critical("Specified backup messages file path doesn't refer to a proper file.")
        raise SystemExit()

    main_logger.info("Initializing database class...")

    messages_db = wa_r.database.AttachedMessagesDatabaseImporter(f"{os.path.basename(app_args.backup_directory)}_media.db")

    main_logger.info("Starting to read line by line and parsing...")

    try:
        wa_r.core.ingest.initiate_importing_process(app_args.backup_directory, app_args.backup_message_file, messages_db)

    except:
        main_logger.error("An exception occured during the process!", exc_info = True)

    else:
        main_logger.info("Ingestion successful!")

    finally:
        main_logger.info("Applying last commit...")
        messages_db.commit_changes()
        
        messages_db.close()

import wa_r.core.ingest
import wa_r.database
import wa_r.constants
import wa_r.types
import wa_r.log
import argparse
import logging
import typing
import sys
import os

def language_preference_type(arg_value) -> typing.Union[wa_r.types.BackupMessagesLangDetectionPreferences, wa_r.types.BackupMessagesLanguages]:
    try:
        return wa_r.types.BackupMessagesLangDetectionPreferences(arg_value)

    except ValueError:
        return wa_r.types.BackupMessagesLanguages(arg_value)


if __name__ == "__main__": 
    main_parser = argparse.ArgumentParser(prog = "ingestor.py",
                                          description = "Parses, packages and converts WhatsApp messages with attachments to SQL database.",
                                          add_help = False)
    main_parser.add_argument("backup_directory")
    main_parser.add_argument("backup_message_file")
    main_parser.add_argument("--commit-buffer-size", type = int, default = wa_r.constants.DEFAULT_DATABASE_COMMIT_BUFFER_SIZE)
    main_parser.add_argument("--language", type = language_preference_type, default = wa_r.constants.DEFAULT_INGESTOR_LANGUAGE_PREFERENCE)

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

    ingestor_kwargs = {"commit_buffer_size": app_args.commit_buffer_size}

    if app_args.language in wa_r.types.BackupMessagesLangDetectionPreferences:
        ingestor_kwargs["language_detection_preference"] = app_args.language
        main_logger.info(f"Language detection preference: {app_args.language}")

    elif app_args.language in wa_r.types.BackupMessagesLanguages:
        ingestor_kwargs["language"] = app_args.language
        main_logger.info(f"Backup language: {app_args.language}")

    main_logger.info("Initializing database class...")

    messages_db = wa_r.database.AttachedMessagesDatabaseImporter(f"{os.path.basename(app_args.backup_directory)}_attachments.db")

    ingestor_args = (app_args.backup_directory,
                     app_args.backup_message_file,
                     messages_db)

    main_logger.info("Starting to ingest the backup...")

    try:
        wa_r.core.ingest.initiate_importing_process(*ingestor_args, **ingestor_kwargs)

    except wa_r.exceptions.NoLanguageFoundException:
        main_logger.error("No supported languages found in backup messages file.")
        main_logger.warning("If your language is not supported yet, please consider to contribute on GitHub.")

    except wa_r.exceptions.MultipleLanguagesFoundException as multiple_lang_exception:
        main_logger.error("Multiple languages found in backup messages file: {', '.join(multiple_lang_exception.found_languages)}")
        main_logger.warning("Please specify one of these languages manually with --language parameter.")

    except Exception:
        main_logger.error("An exception occured during the process!", exc_info = True)

    else:
        main_logger.info("Ingestion successful!")

    finally:
        main_logger.info("Applying last commit...")
        messages_db.commit_changes()
        
        messages_db.close()

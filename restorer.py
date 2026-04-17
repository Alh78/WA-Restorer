import wa_r.core.restorer
import wa_r.exceptions
import wa_r.database
import wa_r.log
import argparse
import logging
import config
import os


if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(
        prog="restorer.py",
        description="Restores EXIF data of media files exported from Whatsapp Backup using SQL databases.",
        add_help=False,
    )
    main_parser.add_argument("reference_database_file")
    main_parser.add_argument("media_directory")
    main_parser.add_argument("destination_directory")

    app_args = main_parser.parse_args()
    app_args.reference_database_file = os.path.abspath(app_args.reference_database_file)
    app_args.media_directory = os.path.abspath(app_args.media_directory)
    app_args.destination_directory = os.path.abspath(app_args.destination_directory)

    main_log = logging.getLogger("restorer")
 
    main_log.info("Initializing loggers...")
    wa_r.log.prepare_restorer_loggers()

    main_log.info(f"Reference database file: {app_args.reference_database_file}")
    main_log.info(f"Media directory: {app_args.destination_directory}")
    main_log.info(f"Destination directory: {app_args.destination_directory}")

    if not os.path.exists(app_args.reference_database_file):
        main_log.critical("Specified database file doesn't exist.")
        raise SystemExit()

    elif not os.path.isfile(app_args.reference_database_file):
        main_log.critical(
            "Specified database file path doesn't refer to a proper file."
        )
        raise SystemExit()

    if not os.path.exists(app_args.media_directory):
        main_log.critical("Specified media directory doesn't exist.")
        raise SystemExit()

    elif not os.path.isdir(app_args.media_directory):
        main_log.critical(
            "Specified media directory path doesn't refer to a proper directory."
        )
        raise SystemExit()

    if not os.path.exists(app_args.destination_directory):
        main_log.info("Creating destination directory...")
        os.makedirs(app_args.destination_directory)

    elif not os.path.isdir(app_args.destination_directory):
        main_log.critical(
            "Specified destination directory path doesn't refer to a proper directory."
        )
        raise SystemExit()


    main_log.info("Initializing database class...")

    reference_db = wa_r.database.AttachedMessagesDatabaseProcessor(
        app_args.reference_database_file
    )

    main_log.info("Starting to restoration...")

    try:
        wa_r.core.restorer.initiate_restoring_process(reference_db, app_args.media_directory, app_args.destination_directory)

    except wa_r.exceptions.MultipleOriginFilesException:
        main_log.warning(
            "Please filter the database file specified before using restorer."
        )

    except Exception:
        main_log.error("An exception occured during the process!", exc_info=True)

    else:
        main_log.info("Restoration completed without any issues.")

    finally:
        main_log.info("Closing database...")
        reference_db.close()

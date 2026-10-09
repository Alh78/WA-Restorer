import wa_r.core.filter
import wa_r.constants
import wa_r.types
import wa_r.log
import argparse   
import shutil
import logging
import os


if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(
        prog="filterer.py",
        description="Filters WhatsApp messages from the specified database file and rearranges",
        add_help=False,                                                                                                                                            )
    main_parser.add_argument("source_database", type=str)
    main_parser.add_argument("--media", "-m", action="store_true")
    main_parser.add_argument("--origin", "-org", action="store_true")
    main_parser.add_argument("--exclude-dir", "-exd", type=str, default=None)
    main_parser.add_argument("--include-dir-only", "-incd", type=str, default=None)
    main_parser.add_argument("--exclude", "-e", type=str, default=None)
    main_parser.add_argument("--unsafe", "-s", action="store_true", default=False)

    """ These arguments haven't been added yet because the required modules are still in development.
    main_parser.add_argument("-ih", "--image-hash", type=wa_r.types.ImageHashingAlgorithm, default=wa_r.constants.DEFAULT_IMAGE_HASHING_ALGORITHM)
    main_parser.add_argument("-vh", "--video-hash", type=wa_r.types.VideoHashingAlgoritm, default=wa_r.constants.DEFAULT_VIDEO_HASHING_ALGORITHM)
    """

    app_args = main_parser.parse_args()
    app_args.source_database = os.path.abspath(app_args.source_database)

    if isinstance(app_args.exclude_dir, str):
        app_args.exclude_dir = os.path.abspath(app_args.exclude_dir)

    if isinstance(app_args.include_dir_only, str):
        app_args.include_dir_only = os.path.abspath(app_args.include_dir_only)

    if isinstance(app_args.exclude, str):
        app_args.exclude = os.path.abspath(app_args.exclude)


    main_logger = logging.getLogger("filterer")
    
    main_logger.info("Initializing loggers...")
    wa_r.log.prepare_filterer_loggers()

    if not os.path.exists(app_args.source_database):
        main_logger.critical("The source database file doesn't exist.")                                                                                     
        raise SystemExit()

    elif not os.path.isfile(app_args.source_database):
        main_logger.critical(
            "The specified database file path doesn't refer to a proper file."
        )

        raise SystemExit()

    if not any(list(vars(app_args).values())[1:-1]):
        main_logger.critical("No argument specified!")
        raise SystemExit()
    
    symbolize_bool = lambda bool_: "+" if bool_ is True else "-"
    main_logger.info(f"Filter media messages: {symbolize_bool(app_args.media)}")
    main_logger.info(f"Filter origin messages: {symbolize_bool(app_args.origin)}")

    main_logger.info(f"Excluding files in the directory: {app_args.exclude_dir}")
    main_logger.info(f"Whitelisted files in the directory: {app_args.include_dir_only}")
    main_logger.info(f"Excluding the file: {app_args.exclude}")

    
    if not app_args.unsafe:
        main_logger.info("Creating the backup of the source database...")

        dest_db_path = f"{os.path.basename(app_args.source_database)}_filtered.db"
        shutil.copy2(app_args.source_database, dest_db_path)
    
    else:
        dest_db_path = app_args.source_database

        main_logger.warning("Backup copy has been disabled.")
        main_logger.warning("Please consider that this operation may result in data loss.")

    main_logger.info("Initializing database class...")

    source_db = wa_r.database.AttachedMessagesDatabaseProcessor(dest_db_path)


    main_logger.info("Initiating filtering process...")

    try:
        wa_r.core.filter.initiate_filtering_process(source_db, app_args.media, app_args.origin, app_args.exclude_dir, app_args.include_dir_only, app_args.exclude)

    except Exception:
        main_logger.error("An exception occured during the process!", exc_info = True)

    else:
        main_logger.info("Filtering process successful!")
        source_db.commit_changes()

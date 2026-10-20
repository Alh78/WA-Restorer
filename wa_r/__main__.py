import wa_r.constants
import wa_r.types
import argparse
import typing


def start_ingestion(app_args) -> None:
    import wa_r.console.ingest

    return wa_r.console.ingest.start_ingestion_session(app_args)

def start_filtration(app_args) -> None:
    import wa_r.console.filter

    return wa_r.console.filter.start_filtration_session(app_args)

def start_restoration(app_args) -> None:
    import wa_r.console.restore

    return wa_r.console.restore.start_restoration_session(app_args)


def ingestion_language_preference_type(arg_value) -> typing.Union[wa_r.types.BackupMessagesLangDetectionPreferences, wa_r.types.BackupMessagesLanguages]:
    try:
        return wa_r.types.BackupMessagesLangDetectionPreferences(arg_value)

    except ValueError:
        return wa_r.types.BackupMessagesLanguages(arg_value)

if __name__ == "__main__":
    main_parser = argparse.ArgumentParser()
    main_parser.add_argument("-l,", "--save-logs", action="store_true", default=False)
    subparsers = main_parser.add_subparsers(required=True)

    
    ingestor_parser = subparsers.add_parser("ingest") 
    ingestor_parser.add_argument("backup_directory")
    ingestor_parser.add_argument("backup_message_file")
    ingestor_parser.add_argument("--commit-buffer-size", type = int, default = wa_r.constants.DEFAULT_DATABASE_COMMIT_BUFFER_SIZE)
    ingestor_parser.add_argument("--language", type = ingestion_language_preference_type, default = wa_r.constants.DEFAULT_INGESTOR_LANGUAGE_PREFERENCE)

    filterer_parser = subparsers.add_parser("filter")
    filterer_parser.add_argument("source_database", type=str)
    filterer_parser.add_argument("--media", "-m", action="store_true")
    filterer_parser.add_argument("--origin", "-org", action="store_true")
    filterer_parser.add_argument("--exclude-dir", "-exd", type=str, default=None)
    filterer_parser.add_argument("--include-dir-only", "-incd", type=str, default=None)
    filterer_parser.add_argument("--exclude", "-e", type=str, default=None)
    filterer_parser.add_argument("--unsafe", "-s", action="store_true", default=False)

    """ These arguments haven't been added yet because the required modules are still in development.
    filterer_parser.add_argument("-ih", "--image-hash", type=wa_r.types.ImageHashingAlgorithm, default=wa_r.constants.DEFAULT_IMAGE_HASHING_ALGORITHM)
    filterer_parser.add_argument("-vh", "--video-hash", type=wa_r.types.VideoHashingAlgoritm, default=wa_r.constants.DEFAULT_VIDEO_HASHING_ALGORITHM)
    """

    restorer_parser = subparsers.add_parser("restore") 
    restorer_parser.add_argument("reference_database_file")
    restorer_parser.add_argument("media_directory")
    restorer_parser.add_argument("destination_directory")

    ingestor_parser.set_defaults(func=start_ingestion)
    filterer_parser.set_defaults(func=start_filtration)
    restorer_parser.set_defaults(func=start_restoration)

    main_args = main_parser.parse_args()
    main_args.func(main_args)


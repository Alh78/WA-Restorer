import wa_r.database
import wa_r.parsing
import wa_r.file
import wa_r.exceptions
import logging
import os


writer_logger = logging.getLogger(__name__)

def write_restored_metadata_to_file(
        file_name: str, media_dir: str, dest_dir: str, reference_database: wa_r.database.AttachedMessagesDatabaseProcessor, device_brand: str = None, device_model: str = None
):
    writer_logger.info(f'Writing restored metadata to File(file_name="{file_name}")...')

    writer_logger.debug(
        f'Getting origin message of File(file_name="{file_name}") from reference database...'
    )
    message_data = reference_database.get_sender_message_by_attached_file_name(file_name)

    if isinstance(message_data, list) and message_data:
        writer_logger.critical(
            f'File(file_name="{file_name}") contains multiple origins in the database!'
        )
        raise wa_r.exceptions.MultipleOriginFilesException(
            f'File "{file_name}" have multiple origins in the database!'
        )

    if (
        not message_data
    ):  # This means message data returned as a blank list from database,  which means this file doesn't have any record on DB.
        writer_logger.error(
            f'File(file_name="{file_name}") doesn\'t have any record in the database.'
        )
        writer_logger.warning(f'File("{file_name}") will be skipped during the process.')
        return

    writer_logger.debug(
        "Generating WPMediaMetaData instance using fetched origin message data..."
    )
    exif_data = wa_r.parsing.generate_media_meta_data(
        message_data, device_brand, device_model
    )

    writer_logger.debug(
        f'Writing new File(file_path="{os.path.abspath(os.path.join(dest_dir, file_name))}")...'
    )

    try:
        wa_r.file.write_new_exif_data(
            os.path.abspath(os.path.join(media_dir, file_name)),
            os.path.abspath(os.path.join(dest_dir, file_name)),
            exif_data,
            add_owner=True,
            edit_file_dates=True,
        )

    except wa_r.exceptions.FileAlreadyContainsMetaDataException:
        pass
        """writer_logger.error(f"File(file_name=\"{file_name}\") already contains EXIF data.")
								writer_logger.warning("File(\"{file_name}\") will be skipped during the process.")
								return"""



def initiate_restoring_process(reference_database: wa_r.database.AttachedMessagesDatabaseProcessor, media_dir: str, destination_dir: str):
    for media_file_name in os.listdir(media_dir):
        write_restored_metadata_to_file(media_file_name, media_dir, destination_dir, reference_database)

import wa_r.constants
import wa_r.types
import datetime


def package_file_data(file_meta_data: wa_r.types.WPFileMetaData, file_hash: bytes) -> wa_r.types.WPFileData:
    return wa_r.types.WPFileData(file_meta_data, file_hash)

def package_message_data(message_data: wa_r.types.RawMessageData, file_data: wa_r.types.WPFileData) -> wa_r.types.AttachedMessageData:
    return wa_r.types.AttachedMessageData(sender = message_data.sender,
                                            line_index = message_data.line_index,
                                            message_date = message_data.date,
                                            file = file_data)

def package_message_data_raw(sender: str, # This function should be called only in database operations. Manual use is not recommended.
                             line_index: int,
                             message_date_timestamp: int,
                             file_name: str,
                             file_type: str,
                             file_name_timestamp: int,
                             file_hash: bytes) -> wa_r.types.AttachedMessageData:
    return wa_r.types.AttachedMessageData(sender = sender,
                                             line_index = line_index,
                                             message_date = datetime.datetime.fromtimestamp(message_date_timestamp),
                                             file = wa_r.types.WPFileData(file_meta_data = wa_r.types.WPFileMetaData(file_name = file_name,
                                                                                                                           file_type = wa_r.types.WPFileTypes(file_type),
                                                                                                                           file_name_timestamp = None if not isinstance(file_name_timestamp, int) else datetime.datetime.fromtimestamp(file_name_timestamp)
                                                                                                                          ),
                                                                             file_hash = file_hash)
                                             )

def generate_media_meta_data(attached_message_data: wa_r.types.AttachedMessageData,
                             device_brand: str = None,
                             device_model: str = None,
                             date_priority: wa_r.types.MetadataDatePriority = wa_r.constants.DEFAULT_METADATA_DATE_PRIORITY) -> wa_r.types.WPMediaMetaData:
    if date_priority == wa_r.types.MetadataDatePriority.EARLIEST:
        if (attached_message_data.file.file_meta_data.file_name_timestamp + datetime.timedelta(days = 1)) < attached_message_data.message_date:
            timestamp_to_add = attached_message_data.file.file_meta_data.file_name_timestamp

        else:
            timestamp_to_add = attached_message_data.message_date

    elif date_priority == wa_r.types.MetadataDatePriority.MESSAGE:
        timestamp_to_add = attached_message_data.message_date

    elif date_priority == wa_r.types.MetadataDatePriority.FILE_NAME:
        timestamp_to_add = attached_message_data.file.file_meta_data.file_name_timestamp
        

    return wa_r.types.WPMediaMetaData(owner = owner,
                                      device_brand = device_brand,
                                      device_model = device_model,
                                      timestamp = timestamp_to_add)


def generate_media_meta_data_raw(owner: str = None,
                                 device_brand: str = None,
                                 device_model: str = None,
                                 timestamp: int = None) -> wa_r.types.WPMediaMetaData:
    return wa_r.types.WPMediaMetaData(owner = owner,
                                        device_brand = device_brand,
                                        device_model = device_model,
                                        timestamp = datetime.datetime.fromtimestamp(timestamp_to_add))

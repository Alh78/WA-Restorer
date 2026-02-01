import wa_r.exceptions
import wa_r.constants
import wa_r.types
import datetime
import config
import os
import re

generic_attached_message_pattern = re.compile(wa_r.constants.GENERIC_ATTACHED_MESSAGE_PATTERN)
native_attached_file_name_pattern = re.compile(wa_r.constants.NATIVE_ATTACHED_FILE_NAME_PATTERN)

def _parse_raw_message_data(line: str, line_index: int, message_pattern: re.Pattern) -> wa_r.types.RawMessageData:
    pattern_match = message_pattern.match(line)

    if not pattern_match:
        raise wa_r.exceptions.MismatchMessagePatternException("Message line doesn't match generic message pattern.")
    
    date = datetime.datetime.strptime(pattern_match.group(1), "%d.%m.%Y %H:%M")
    sender = pattern_match.group(2)
    file_name = pattern_match.group(3)[1:]

    return wa_r.types.RawMessageData(date, sender, file_name, line_index)

def _parse_file_meta_data(file_name: str, name_pattern: re.Pattern) -> wa_r.types.WPFileMetaData:
    file_name = os.path.basename(file_name)
    pattern_match = name_pattern.match(file_name)

    if not pattern_match:
        return wa_r.types.WPFileMetaData(file_name, wa_r.types.WPFileTypes.NON_NATIVE_FILE_TYPE, None)

    file_type = pattern_match.group(1)
    name_based_file_timestamp = datetime.datetime.strptime(pattern_match.group(2), "%Y%m%d")

    return wa_r.types.WPFileMetaData(file_name, wa_r.types.WPFileTypes(file_type), name_based_file_timestamp)

def parse_raw_message_data(line: str, line_index: int) -> wa_r.types.RawMessageData:
    return _parse_raw_message_data(line, line_index, generic_attached_message_pattern)

def parse_file_meta_data(file_name: str) -> wa_r.types.WPFileMetaData:
    return _parse_file_meta_data(file_name, native_attached_file_name_pattern)

def package_file_data(file_meta_data: wa_r.types.WPFileMetaData, file_hash: bytes):
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
        

    if "(eski)" in attached_message_data.sender:
        owner = " ".join(attached_message_data.sender.split()[:-1])

    else:
        owner = attached_message_data.sender

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

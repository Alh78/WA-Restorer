import dataclasses
import datetime
import types
import enum


class WPFileTypes(enum.Enum):
    IMAGE_FILE_TYPE = "IMG"
    VIDEO_FILE_TYPE = "VID"
    DOCUMENT_FILE_TYPE = "DOC"
    STICKER_FILE_TYPE = "STK" 
    VOICE_MESSAGE_FILE_TYPE = "PTT"
    AUDIO_FILE_TYPE = "AUD"
    NON_NATIVE_FILE_TYPE = "UNK"

class EXIFTimePriority(enum.Enum):
    MESSAGE_PRIORITIZED = 1
    FILE_NAME_PRIORITIZED = 2
    GET_EARLIEST = 3

@dataclasses.dataclass(slots = True)
class RawMessageData:
    date: datetime.datetime
    sender: str
    content: str
    line_index: int

    def __post_init__(self):
        if not isinstance(self.date, datetime.datetime):
            raise TypeError(f"Expected datetime.datetime, {type(self.date).__name__} found")
        
        if not isinstance(self.sender, str):
            raise TypeError(f"Expected str, {type(self.sender).__name__} found")

        if not isinstance(self.content, str):
            raise TypeError(f"Expected str, {type(self.content).__name__} found")
        
        if not isinstance(self.line_index, int):
            raise TypeError(f"Expected int, {type(self.line_index).__name__} found")
         

@dataclasses.dataclass(slots = True)
class WPFileMetaData:
    file_name: str 
    file_type: WPFileTypes
    file_name_timestamp: datetime.datetime | types.NoneType

    def __post_init__(self):
        if not isinstance(self.file_name, str):
            raise TypeError(f"Expected str, {type(self.file_name).__name__} found")
        
        if not isinstance(self.file_name_timestamp, (datetime.datetime, types.NoneType)):
            raise TypeError(f"Expected datetime.datetime, {type(self.file_name_timestamp).__name__} found")

        if isinstance(self.file_type, str):
            try:
                self.file_type = WPFileTypes(self.file_type)

            except ValueError:
                raise ValueError("Unknown file type: {self.file_type}")

        elif not isinstance(self.file_type, WPFileTypes):
            raise TypeError(f"Expected WPFileTypes, {type(self.file_type).__name__} found")

@dataclasses.dataclass(slots = True)
class WPFileData:
    file_meta_data: WPFileMetaData
    file_hash: bytes

    def __post_init__(self):
        if not isinstance(self.file_meta_data, WPFileMetaData):
            raise TypeError(f"Expected WPFileMetaData, {type(self.file_meta_data).__name__} found")
        
        if not isinstance(self.file_hash, bytes):
            raise TypeError(f"Expected bytes, {type(self.file_hash).__name__} found")


@dataclasses.dataclass(slots = True)
class AttachedMessageData:
    sender: str
    line_index: int
    message_date: datetime.datetime
    file: WPFileData

@dataclasses.dataclass(slots = True)
class WPMediaExifData:
    owner: str | types.NoneType
    device_brand: str | types.NoneType
    device_model: str | types.NoneType
    timestamp: datetime.datetime

    def __post_init__(self):
        if not isinstance(self.timestamp, datetime.datetime):
            raise TypeError(f"Expected datetime.datetime, {type(self.file_name_timestamp).__name__} found")

        if not isinstance(self.owner, (str, types.NoneType)):
            raise TypeError(f"Expected str, {type(self.owner).__name__} found")
        
        if not isinstance(self.device_brand, (str, types.NoneType)):
            raise TypeError(f"Expected str, {type(self.device_brand).__name__} found")

        if not isinstance(self.device_model, (str, types.NoneType)):
            raise TypeError(f"Expected str, {type(self.device_model).__name__} found")
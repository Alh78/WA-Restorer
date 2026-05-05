import wa_r.types
import typing

class ParsingError(Exception):
    pass

class MismatchMessagePatternException(ParsingError):
    pass

class MultipleLanguagesFoundException(ParsingError):
    def __init__(self, languages_found: typing.Iterable[wa_r.types.BackupMessagesLanguages]):
        self.languages_found = languages_found

        super().__init__("Multiple languages detected: {}".format(", ".join([language.value for language in languages_found])))

class NoLanguageFoundException(ParsingError):
    def __init__(self):
        super().__init__("No supported language found. Supported languages: {}".format(", ".join([language.value for language in wa_r.types.BackupMessagesLanguages])))

class DatabaseError(Exception):
    pass

class DatabaseCacheConflictException(DatabaseError):
    pass

class SenderAdditionError(DatabaseError):
    pass

class MessageInsertionError(DatabaseError):
    pass

class MultipleOriginFilesException(DatabaseError):
    pass

class FileProcessingError(Exception):
    pass

class FileAlreadyContainsMetaDataException(FileProcessingError):
    pass

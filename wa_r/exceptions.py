class ParsingError(Exception):
    pass

class MismatchMessagePatternException(ParsingError):
    pass

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

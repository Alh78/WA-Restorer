class ParsingError(Exception):
    pass

class MismatchMessagePatternException(ParsingError):
    pass

class DatabaseError(Exception):
    pass

class DatabaseCacheConflictException(DatabaseError):
    pass

class SenderAdditionException(DatabaseError):
    pass

class MultipleOriginFilesException(DatabaseError):
    pass

class FileProcessingError(Exception):
    pass

class FileAlreadyContainsMetaDataException(FileProcessingError):
    pass

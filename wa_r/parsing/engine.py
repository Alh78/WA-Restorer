from .languages import BACKUP_MESSAGES_LANGUAGES_FORMATS, COMPILED_MESSAGE_LINE_PATTERNS, COMPILED_DATE_PATTERNS
import wa_r.exceptions
import wa_r.types
import datetime
import typing
import os
import re


NATIVE_ATTACHED_FILE_NAME_REGEX_PATTERN = r"^(\w{3})-(\d{8})-WA\d{4}.*?"
COMPILED_NATIVE_ATTACHED_FILE_NAME_REGEX_PATTERN = re.compile(NATIVE_ATTACHED_FILE_NAME_REGEX_PATTERN)

NATIVE_FILE_NAME_TIMESTAMP_DT_PATTERN = "%Y%m%d"


def determine_backup_language(messages_lines: typing.Iterable[str], deep_search: bool = False) -> wa_r.types.BackupMessagesLanguages:
    if deep_search:
        return deep_scan_backup_messages_language(messages_lines)

    else:
        return fast_scan_backup_messages_language(messages_lines)

def fast_scan_backup_messages_language(messages_lines: typing.Iterable[str]) -> wa_r.types.BackupMessagesLanguages:
    for line in messages_lines:
        if "(" in line and ")" in line:
            for language in BACKUP_MESSAGES_LANGUAGES_FORMATS:
                if COMPILED_MESSAGE_LINE_PATTERNS[language].match(line):
                    return language

    else:
        raise wa_r.exceptions.NoLanguageFoundException()


def deep_scan_backup_messages_language(messages_lines: typing.Iterable[str]) -> wa_r.types.BackupMessagesLanguages:
    languages_with_correct_date_fmt = set()
    found_languages = set()

    for line in messages_lines:
        if not ("(" in line and ")" in line):
            continue

        for language, language_format in BACKUP_MESSAGES_LANGUAGES_FORMATS.items():
            if COMPILED_DATE_PATTERNS[language].match(line):
                languages_with_correct_date_fmt.add(language)
                break

        for language in languages_with_correct_date_fmt:
            if COMPILED_MESSAGE_LINE_PATTERNS[language].match(line):
                found_languages.add(language)
                break

    if not len(found_languages):
        raise wa_r.exceptions.NoLanguageFoundException()

    elif len(found_languages) > 1:
        raise MultipleLanguagesFoundException(found_languages)

    return found_languages.pop()


def _parse_raw_message_data(line: str, line_index: int, message_pattern: re.Pattern, date_dt_format: str) -> wa_r.types.RawMessageData:
    pattern_match = message_pattern.match(line)

    if not pattern_match:
        raise wa_r.exceptions.MismatchMessagePatternException("Message line doesn't match generic message pattern.")

    date = datetime.datetime.strptime(pattern_match.group(1), date_dt_format)
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

def parse_raw_message_data(line: str, line_index: int, language: wa_r.types.BackupMessagesLanguages) -> wa_r.types.RawMessageData:
    return _parse_raw_message_data(line, line_index, COMPILED_MESSAGE_LINE_PATTERNS[language], BACKUP_MESSAGES_LANGUAGES_FORMATS.get(language).date_dt_format)

def parse_file_meta_data(file_name: str) -> wa_r.types.WPFileMetaData:
    return _parse_file_meta_data(file_name, COMPILED_NATIVE_ATTACHED_FILE_NAME_REGEX_PATTERN)

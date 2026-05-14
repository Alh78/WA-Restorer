import wa_r.types
import typing
import re


class CompiledPatternsMap(dict[wa_r.types.BackupMessagesLanguages, re.Pattern]):
    def __init__(self, format_getter: typing.Callable[[wa_r.types.BackupMessagesLanguages], str]):
        super().__init__()

        self._pattern_format_getter = format_getter

    def __missing__(self, key: wa_r.types.BackupMessagesLanguages) -> re.Pattern:
        compiled_pattern = re.compile(self._pattern_format_getter(key))
        self[key] = compiled_pattern

        return compiled_pattern


BACKUP_MESSAGES_LANGUAGES_FORMATS: typing.Dict[wa_r.types.BackupMessagesLanguages, wa_r.types.BackupMessagesLanguageFormat] = {wa_r.types.BackupMessagesLanguages.TR_TR: wa_r.types.BackupMessagesLanguageFormat(
    r"^(\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2})\s-\s([^:]+):\s(.*?)\s\(dosya ekli\)",
    r"^(\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2})",
    "%d.%m.%Y %H:%M"),
                                     }

COMPILED_MESSAGE_LINE_PATTERNS: CompiledPatternsMap = CompiledPatternsMap(lambda lang: BACKUP_MESSAGES_LANGUAGES_FORMATS.get(lang).message_line_regex_format)
COMPILED_DATE_PATTERNS: CompiledPatternsMap = CompiledPatternsMap(lambda lang: BACKUP_MESSAGES_LANGUAGES_FORMATS.get(lang).date_regex_format)

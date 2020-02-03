from dataclasses import dataclass
from enum import Enum


@dataclass
class File:
    archive_name: str = None
    file_name: str = None
    mime_type: str = None
    size_deflated: int = None
    size_compressed: int = None

    def dumps(self, add_newline: bool = True):
        """
        @serializer
        """
        line = '{} – {} – {} - {}'.format(
            self.archive_name, self.file_name,
            self.mime_type, self.size_deflated
        )
        if add_newline:
            line += '\n'

        return line


class AppState(Enum):
    INITIALIZED = 10
    FETCHED = 20
    DOWNLOADED = 30


class PageState(Enum):
    INITIALIZED = 10
    FETCHED = 20

from dataclasses import dataclass
from enum import Enum


@dataclass
class File:
    archive_name: str = None
    file_name: str = None
    mime_type: str = None
    size_deflated: int = None
    size_compressed: int = None


class AppState(Enum):
    INITIALIZED = 10
    FETCHED = 20
    DOWNLOADED = 20
    EXTRACTED = 30

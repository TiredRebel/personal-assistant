"""
Storage package - Data persistence layer
"""

from __future__ import annotations

from .file_storage import (
    BackupNotFoundError,
    CorruptedDataError,
    FileStorage,
    StorageError,
)

__all__: list[str] = ["FileStorage", "StorageError", "CorruptedDataError", "BackupNotFoundError"]

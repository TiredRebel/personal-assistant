"""Storage module for data persistence."""

from __future__ import annotations

from .file_storage import DateTimeEncoder, FileStorage

__all__: list[str] = ["FileStorage", "DateTimeEncoder"]

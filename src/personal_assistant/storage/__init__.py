"""Storage module for data persistence."""

from __future__ import annotations

from .file_storage import FileStorage, DateTimeEncoder

__all__: list[str] = ["FileStorage", "DateTimeEncoder"]

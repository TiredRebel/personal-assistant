"""
Services package - Business logic layer
"""

from __future__ import annotations

from .contact_service import ContactService
from .note_service import NoteService

__all__: list[str] = ["ContactService", "NoteService"]

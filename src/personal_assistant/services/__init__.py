"""
Services package - Business logic layer
"""

from __future__ import annotations

from src.personal_assistant.services.contact_service import ContactService
from src.personal_assistant.services.note_service import NoteService

__all__: list[str] = ["ContactService", "NoteService"]

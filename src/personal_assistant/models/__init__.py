"""
Models package - Data structures for contacts and notes
"""

from __future__ import annotations

from .contact import Contact
from .note import Note

__all__: list[str] = ["Contact", "Note"]

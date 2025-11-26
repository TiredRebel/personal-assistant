"""
Personal Assistant - A CLI tool for managing contacts and notes

This package provides:
- Contact management with validation
- Note management with tags
- Intelligent command parsing
- Data persistence with backups
"""

from __future__ import annotations

from typing import Final

from .cli import CLI, ColoredCLI, CommandParser, IntentRecognizer, SmartCommandParser
from .models import Contact, Note
from .services import ContactService, NoteService
from .storage import DateTimeEncoder, FileStorage
from .validators import (
    BirthdayValidator,
    EmailValidationError,
    EmailValidator,
    InputValidator,
    PhoneValidationError,
    PhoneValidator,
    ValidationError,
)

__version__: Final[str] = "1.0.0"
__author__: Final[str] = "Your Team Name"

# Package metadata
__all__: list[str] = [
    # CLI
    "CLI",
    "ColoredCLI",
    "CommandParser",
    "IntentRecognizer",
    "SmartCommandParser",
    # Models
    "Contact",
    "Note",
    # Services
    "ContactService",
    "NoteService",
    # Storage
    "FileStorage",
    "DateTimeEncoder",
    # Validators
    "PhoneValidator",
    "EmailValidator",
    "InputValidator",
    "ValidationError",
    "PhoneValidationError",
    "EmailValidationError",
    "BirthdayValidator",
]

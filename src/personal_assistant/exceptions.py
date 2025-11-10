"""
Custom exceptions for the Personal Assistant application.

This module defines custom exception classes for better error handling
and more informative error messages throughout the application.
"""


class NoteError(Exception):
    """Base exception for note-related errors."""

    pass


class NoteNotFoundError(NoteError):
    """Raised when note is not found."""

    pass


class InvalidNoteContentError(NoteError):
    """Raised when note content is invalid."""

    pass

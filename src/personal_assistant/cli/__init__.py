"""
CLI package - Command-line interface
"""

from __future__ import annotations

from .command_parser import CommandParser
from .intent_recognizer import IntentRecognizer
from .interface import CLI, ColoredCLI
from .smart_command_parser import SmartCommandParser

__all__: list[str] = [
    "CLI",
    "ColoredCLI",
    "CommandParser",
    "IntentRecognizer",
    "SmartCommandParser",
]

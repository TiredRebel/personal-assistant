"""
CLI package - Command-line interface
"""

from __future__ import annotations

from .interface import CLI, ColoredCLI
from .command_parser import CommandParser
from .smart_command_parser import SmartCommandParser
from .intent_recognizer import IntentRecognizer

__all__: list[str] = [
    "CLI",
    "ColoredCLI",
    "CommandParser",
    "IntentRecognizer",
    "SmartCommandParser",
]

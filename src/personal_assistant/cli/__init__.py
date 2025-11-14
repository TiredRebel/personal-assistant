"""
CLI package - Command-line interface
"""

from __future__ import annotations

from personal_assistant.cli.command_parser import CommandParser
from personal_assistant.cli.intent_recognizer import IntentRecognizer
from personal_assistant.cli.smart_command_parser import SmartCommandParser

# from .interface import CLI

__all__: list[str] = ["CommandParser", "IntentRecognizer", "SmartCommandParser"]

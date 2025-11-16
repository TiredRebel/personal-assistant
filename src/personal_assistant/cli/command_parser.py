"""
Command Parser Module

Provides intelligent command parsing and interpretation for the Personal Assistant CLI.
"""

import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Set, Tuple, Union

# Type alias for command arguments (can contain strings, lists, other dicts)
ArgValue = Union[str, List[str], Dict[str, str]]
ParsedCommand = Dict[str, Union[str, Dict[str, ArgValue], float]]


class CommandParser:
    """
    Intelligent command parser that interprets user input.

    Features:
    - Fuzzy command matching
    - Natural language understanding
    - Command suggestions
    - Argument extraction
    """

    # Command patterns and aliases
    COMMAND_PATTERNS = {
        "add-contact": [
            "add contact",
            "new contact",
            "create contact",
            "add person",
            "new person",
            "save contact",
        ],
        "search-contact": [
            "find contact",
            "search contact",
            "look for contact",
            "find person",
            "search person",
            "where is",
        ],
        "list-contacts": [
            "list contacts",
            "show contacts",
            "all contacts",
            "show all contacts",
            "display contacts",
        ],
        "edit-contact": [
            "edit contact",
            "update contact",
            "change contact",
            "modify contact",
        ],
        "delete-contact": [
            "delete contact",
            "remove contact",
            "erase contact",
            "drop contact",
        ],
        "birthdays": [
            "birthdays",
            "upcoming birthdays",
            "show birthdays",
            "birthday reminder",
            "who has birthday",
        ],
        "add-note": [
            "add note",
            "new note",
            "create note",
            "write note",
            "save note",
        ],
        "search-note": [
            "find note",
            "search note",
            "look for note",
            "search notes",
        ],
        "list-notes": [
            "list notes",
            "show notes",
            "all notes",
            "show all notes",
            "display notes",
        ],
        "edit-note": [
            "edit note",
            "update note",
            "change note",
            "modify note",
        ],
        "delete-note": [
            "delete note",
            "remove note",
            "erase note",
            "drop note",
        ],
        "search-by-tag": [
            "search by tag",
            "find by tag",
            "search tag",
            "notes with tag",
            "filter by tag",
        ],
        "list-tags": [
            "list tags",
            "show tags",
            "all tags",
            "available tags",
        ],
        "help": [
            "help",
            "h",
            "?",
            "commands",
            "what can you do",
        ],
        "stats": [
            "stats",
            "statistics",
            "show stats",
            "show statistics",
            "info",
        ],
        "clear": [
            "clear",
            "cls",
            "clear screen",
            "clean",
        ],
        "exit": [
            "exit",
            "quit",
            "bye",
            "goodbye",
            "q",
        ],
    }

    def __init__(self) -> None:
        """Initialize command parser."""
        self.command_map = self._build_command_map()

    def _build_command_map(self) -> Dict[str, str]:
        """
        Build a mapping from patterns to canonical commands.

        Returns:
            Dictionary mapping pattern to command name
        """
        command_map = {}
        for command, patterns in self.COMMAND_PATTERNS.items():
            for pattern in patterns:
                command_map[pattern.lower()] = command
        return command_map

    def parse(self, input_str: str) -> Optional[ParsedCommand]:
        """
        Parse user input into command and arguments.

        Args:
            input_str: Raw user input

        Returns:
            Dictionary with 'command' and 'args', or None if not recognized
        """
        input_str = input_str.strip().lower()

        # Try exact match first
        if input_str in self.command_map:
            return {"command": self.command_map[input_str], "args": {}}

        # Try fuzzy matching
        command, confidence = self._fuzzy_match_command(input_str)
        if command and confidence > 0.7:
            return {
                "command": command,
                "args": self._extract_arguments(input_str),
                "confidence": confidence,
            }

        # Try natural language parsing
        parsed = self._parse_natural_language(input_str)
        if parsed:
            return parsed

        return None

    def _fuzzy_match_command(self, input_str: str) -> Tuple[Optional[str], float]:
        """
        Find the best matching command using fuzzy matching.

        Args:
            input_str: User input

        Returns:
            Tuple of (command_name, confidence_score)
        """
        best_match = None
        best_score = 0.0

        for pattern, command in self.command_map.items():
            # Calculate similarity
            score = SequenceMatcher(None, input_str, pattern).ratio()

            # Check if input starts with pattern
            if input_str.startswith(pattern):
                score += 0.2  # Bonus for prefix match

            # Check word overlap
            input_words = set(input_str.split())
            pattern_words = set(pattern.split())
            if pattern_words:
                word_overlap = len(input_words & pattern_words) / len(pattern_words)
                score += word_overlap * 0.3

            if score > best_score:
                best_score = score
                best_match = command

        return best_match, best_score

    def _parse_natural_language(self, input_str: str) -> Optional[ParsedCommand]:
        """
        Parse natural language commands.

        Examples:
        - "show me all contacts" -> list-contacts
        - "find john's phone" -> search-contact with query "john"
        - "add a note about meeting" -> add-note

        Args:
            input_str: Natural language input

        Returns:
            Parsed command dictionary or None
        """
        # Intent patterns
        intent_patterns = {
            "add-contact": [
                r"(add|create|new|save)\s+(a\s+)?(contact|person)",
            ],
            "search-contact": [
                r"(find|search|look\s+for|where\s+is)\s+(.*?)\s*(phone|email|contact)?",
            ],
            "list-contacts": [
                r"(show|list|display)\s+(all\s+)?(contacts|people)",
            ],
            "add-note": [
                r"(add|create|new|write)\s+(a\s+)?(note)\s+(about\s+)?",
            ],
            "search-note": [
                r"(find|search|look\s+for)\s+(notes?)\s+(about\s+)?",
            ],
            "list-notes": [
                r"(show|list|display)\s+(all\s+)?(notes)",
            ],
            "birthdays": [
                r"(show|list|who\s+has)\s+.*birthday",
            ],
        }

        for command, patterns in intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, input_str, re.IGNORECASE)
                if match:
                    # Extract query/arguments from the match
                    args: Dict[str, ArgValue] = {}
                    if len(match.groups()) > 2 and match.group(2):
                        args["query"] = match.group(2).strip()

                    return {"command": command, "args": args, "confidence": 0.85}

        return None

    def _extract_arguments(self, input_str: str) -> Dict[str, ArgValue]:
        """
        Extract arguments from command string.

        Args:
            input_str: Command string

        Returns:
            Dictionary of extracted arguments
        """
        args: Dict[str, ArgValue] = {}

        # Extract quoted strings
        quoted = re.findall(r'"([^"]*)"', input_str)
        if quoted:
            args["values"] = quoted

        # Extract options (--key value)
        # Fixed regex: escape the hyphen or put it at the end of character class
        options = re.findall(r"--(\w+)\s+([^\s\-]+)", input_str)
        for key, value in options:
            args[key] = value

        return args

    def suggest_commands(self, input_str: str, max_suggestions: int = 3) -> List[str]:
        """
        Suggest commands based on partial or misspelled input.

        Args:
            input_str: User input
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggested commands
        """
        input_str = input_str.strip().lower()
        suggestions: List[str] = []

        # Calculate similarity scores for all commands
        scores: List[Tuple[str, str, float]] = []
        for pattern, command in self.command_map.items():
            score: float = SequenceMatcher(None, input_str, pattern).ratio()

            # Bonus for matching first letters
            if len(input_str) >= 2 and pattern.startswith(input_str[:2]):
                score += 0.2

            scores.append((command, pattern, score))

        # Sort by score and remove duplicates
        scores.sort(key=lambda x: x[2], reverse=True)
        seen_commands: Set[str] = set()

        for command, pattern, score in scores:
            if command not in seen_commands and score > 0.4:
                suggestions.append(f"{command} ({pattern})")
                seen_commands.add(command)
                if len(suggestions) >= max_suggestions:
                    break

        return suggestions

    def get_command_help(self, command: str) -> str:
        """
        Get help text for a specific command.

        Args:
            command: Command name

        Returns:
            Help text string
        """
        help_texts = {
            "add-contact": """
Add a new contact to your address book.
Usage: add-contact
       You will be prompted for contact details.
            """,
            "search-contact": """
Search for contacts by name, phone, or email.
Usage: search-contact
       You will be prompted for a search query.
            """,
            "add-note": """
Create a new note with optional tags.
Usage: add-note
       You will be prompted for note content and tags.
            """,
            "search-by-tag": """
Search notes by tags (can specify multiple tags).
Usage: search-by-tag
       You will be prompted for tags.
            """,
        }

        return help_texts.get(command, "No help available for this command.")

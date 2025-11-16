"""
Smart Command Parser Module

Provides an enhanced command parser with learning capabilities.
Extends CommandParser to track user behavior and improve suggestions over time.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from personal_assistant.cli.command_parser import CommandParser, ParsedCommand


class SmartCommandParser(CommandParser):
    """
    Enhanced command parser with learning capabilities.

    This class extends CommandParser to add:
    - Command usage history tracking
    - User pattern learning
    - Frequency-based command suggestions

    The parser learns from user input patterns and can suggest
    the most frequently used commands.
    """

    def __init__(self) -> None:
        """
        Initialize SmartCommandParser.

        Initializes the parent CommandParser and adds:
        - command_history: List of all command executions with timestamps
        - user_patterns: Dictionary mapping commands to user input patterns
        """
        super().__init__()
        self.command_history: List[Dict[str, str]] = []
        self.user_patterns: Dict[str, List[str]] = {}

    def learn_from_usage(self, input_str: str, selected_command: str) -> None:
        """
        Learn from user's command usage to improve suggestions.

        Records the pattern of how the user invoked a command and
        adds an entry to the command history for frequency tracking.

        Args:
            input_str: Original user input (will be normalized)
            selected_command: The command that was executed

        Example:
            >>> parser = SmartCommandParser()
            >>> parser.learn_from_usage("add person", "add-contact")
            >>> "add person" in parser.user_patterns["add-contact"]
            True
        """
        # Normalize the input pattern
        input_pattern = input_str.strip().lower()

        # Initialize pattern list for this command if needed
        if selected_command not in self.user_patterns:
            self.user_patterns[selected_command] = []

        # Add pattern if it's new (avoid duplicates)
        if input_pattern not in self.user_patterns[selected_command]:
            self.user_patterns[selected_command].append(input_pattern)

        # Record in command history
        self.command_history.append(
            {
                "input": input_str,
                "command": selected_command,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def suggest_based_on_history(self) -> List[str]:
        """
        Suggest commands based on user's history.

        Analyzes command_history to determine which commands are
        used most frequently and returns up to 5 suggestions.

        Returns:
            List of command names sorted by frequency (most used first),
            limited to 5 commands

        Example:
            >>> parser = SmartCommandParser()
            >>> parser.learn_from_usage("a", "add-contact")
            >>> parser.learn_from_usage("b", "add-contact")
            >>> parser.learn_from_usage("c", "search-contact")
            >>> suggestions = parser.suggest_based_on_history()
            >>> suggestions[0]
            'add-contact'
        """
        if not self.command_history:
            return []

        # Count command frequency
        command_counts: Dict[str, int] = {}
        for entry in self.command_history:
            cmd = entry["command"]
            command_counts[cmd] = command_counts.get(cmd, 0) + 1

        # Sort by frequency (descending) and return top 5
        sorted_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)

        return [cmd for cmd, count in sorted_commands[:5]]

    def parse(self, input_str: str) -> Optional[ParsedCommand]:
        """
        Parse user input and learn from successful recognition.

        Extends the parent parse() method to automatically learn
        from successfully recognized commands.
        """
        # Use parent parser to recognize command
        result = super().parse(input_str)

        # Learn from successful recognition
        if result is not None:
            command: Any = result.get("command")
            if isinstance(command, str):
                self.learn_from_usage(input_str, command)

        return result

    def get_usage_stats(self) -> Dict[str, int]:
        """
        Get usage statistics for all commands.

        Returns:
            Dictionary mapping command names to usage counts

        Example:
            >>> parser = SmartCommandParser()
            >>> parser.learn_from_usage("a", "add-contact")
            >>> parser.learn_from_usage("b", "add-contact")
            >>> stats = parser.get_usage_stats()
            >>> stats["add-contact"]
            2
        """
        stats: Dict[str, int] = {}
        for entry in self.command_history:
            cmd = entry["command"]
            stats[cmd] = stats.get(cmd, 0) + 1
        return stats

    def get_user_patterns_for_command(self, command: str) -> List[str]:
        """
        Get all user input patterns for a specific command.

        Args:
            command: Command name

        Returns:
            List of input patterns used for this command

        Example:
            >>> parser = SmartCommandParser()
            >>> parser.learn_from_usage("add person", "add-contact")
            >>> parser.learn_from_usage("new contact", "add-contact")
            >>> patterns = parser.get_user_patterns_for_command("add-contact")
            >>> len(patterns)
            2
        """
        return self.user_patterns.get(command, [])

    def clear_history(self) -> None:
        """
        Clear all learning data.

        Removes all command history and user patterns.
        Useful for testing or resetting the parser state.
        """
        self.command_history.clear()
        self.user_patterns.clear()

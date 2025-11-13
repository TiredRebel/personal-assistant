"""
Unit tests for CommandParser

These tests verify the CommandParser functionality.
Run with: pytest tests/test_command_parser.py
"""

import pytest

from personal_assistant.cli.command_parser import CommandParser


class TestCommandParser:
    """Test suite for CommandParser."""

    @pytest.fixture
    def parser(self):
        """Create a CommandParser instance."""
        return CommandParser()

    def test_exact_command_match(self, parser: CommandParser):
        """Test parsing exact command match."""
        result = parser.parse("add contact")
        assert result is not None
        assert result["command"] == "add-contact"
        assert result["args"] == {}

    def test_command_alias(self, parser: CommandParser):
        """Test parsing command aliases."""
        result = parser.parse("new contact")
        assert result is not None
        assert result["command"] == "add-contact"

        result = parser.parse("create contact")
        assert result is not None
        assert result["command"] == "add-contact"

    def test_case_insensitive(self, parser: CommandParser):
        """Test that parsing is case-insensitive."""
        result = parser.parse("ADD CONTACT")
        assert result is not None
        assert result["command"] == "add-contact"

        result = parser.parse("Add Contact")
        assert result is not None
        assert result["command"] == "add-contact"

    def test_help_commands(self, parser: CommandParser):
        """Test help command and aliases."""
        result = parser.parse("help")
        assert result is not None
        assert result["command"] == "help"

        result = parser.parse("?")
        assert result is not None
        assert result["command"] == "help"

        result = parser.parse("h")
        assert result is not None
        assert result["command"] == "help"

    def test_exit_commands(self, parser: CommandParser):
        """Test exit command and aliases."""
        result = parser.parse("exit")
        assert result is not None
        assert result["command"] == "exit"

        result = parser.parse("quit")
        assert result is not None
        assert result["command"] == "exit"

        result = parser.parse("bye")
        assert result is not None
        assert result["command"] == "exit"

    def test_fuzzy_matching(self, parser: CommandParser):
        """Test fuzzy command matching."""
        # Slight typo should still match
        result = parser.parse("list contacs")  # typo: contacs
        assert result is not None
        assert result["command"] == "list-contacts"
        assert type(result["confidence"]) is float
        assert result["confidence"] > 0.7

    def test_natural_language_list_contacts(self, parser: CommandParser):
        """Test natural language parsing for listing contacts."""
        result = parser.parse("show all contacts")
        assert result is not None
        assert result["command"] == "list-contacts"

        result = parser.parse("display contacts")
        assert result is not None
        assert result["command"] == "list-contacts"

    def test_natural_language_add_note(self, parser: CommandParser):
        """Test natural language parsing for adding notes."""
        result = parser.parse("create a note")
        assert result is not None
        assert result["command"] == "add-note"

        result = parser.parse("write note")
        assert result is not None
        assert result["command"] == "add-note"

    def test_extract_quoted_arguments(self, parser: CommandParser):
        """Test extracting quoted string arguments."""
        result = parser.parse('add contact "John Doe"')
        assert result is not None
        assert type(result["args"]) is dict
        assert "values" in result["args"]
        # Note: input is lowercased, so quoted text is also lowercased
        assert "john doe" in result["args"]["values"]

    def test_extract_options(self, parser: CommandParser):
        """Test extracting command options."""
        result = parser.parse("edit contact --phone +380501234567")
        assert result is not None
        assert type(result["args"]) is dict
        assert "phone" in result["args"]
        assert result["args"]["phone"] == "+380501234567"

    def test_suggest_commands_typo(self, parser: CommandParser):
        """Test command suggestions for typos."""
        suggestions = parser.suggest_commands("ad contct")
        assert len(suggestions) > 0
        # Should suggest add-contact
        assert any("add-contact" in s for s in suggestions)

    def test_suggest_commands_partial(self, parser: CommandParser):
        """Test command suggestions for partial input."""
        suggestions = parser.suggest_commands("add")
        assert len(suggestions) > 0
        # Should suggest add-contact and add-note
        assert any("add" in s for s in suggestions)

    def test_suggest_commands_max_limit(self, parser: CommandParser):
        """Test that suggestions respect max_suggestions parameter."""
        suggestions = parser.suggest_commands("show", max_suggestions=2)
        assert len(suggestions) <= 2

    def test_unrecognized_command(self, parser: CommandParser):
        """Test that unrecognized commands return None."""
        result = parser.parse("completely unknown command xyz123")
        assert result is None

    def test_get_command_help(self, parser: CommandParser):
        """Test getting help text for commands."""
        help_text = parser.get_command_help("add-contact")
        assert help_text is not None
        assert "contact" in help_text.lower()

        help_text = parser.get_command_help("add-note")
        assert help_text is not None
        assert "note" in help_text.lower()

    def test_get_command_help_unknown(self, parser: CommandParser):
        """Test getting help for unknown command."""
        help_text = parser.get_command_help("unknown-command")
        assert "No help available" in help_text

    def test_all_command_patterns_registered(self, parser: CommandParser):
        """Test that all commands are properly registered."""
        expected_commands = [
            "add-contact",
            "search-contact",
            "list-contacts",
            "edit-contact",
            "delete-contact",
            "birthdays",
            "add-note",
            "search-note",
            "list-notes",
            "edit-note",
            "delete-note",
            "search-by-tag",
            "list-tags",
            "help",
            "exit",
        ]

        for command in expected_commands:
            # Each command should have at least one pattern
            assert command in CommandParser.COMMAND_PATTERNS
            assert len(CommandParser.COMMAND_PATTERNS[command]) > 0

    def test_birthdays_command(self, parser: CommandParser):
        """Test birthdays command recognition."""
        result = parser.parse("birthdays")
        assert result is not None
        assert result["command"] == "birthdays"

        result = parser.parse("upcoming birthdays")
        assert result is not None
        assert result["command"] == "birthdays"

        result = parser.parse("show birthdays")
        assert result is not None
        assert result["command"] == "birthdays"

    def test_note_commands(self, parser: CommandParser):
        """Test all note-related commands."""
        note_commands = [
            ("add note", "add-note"),
            ("search note", "search-note"),
            ("list notes", "list-notes"),
            ("edit note", "edit-note"),
            ("delete note", "delete-note"),
            ("search by tag", "search-by-tag"),
            ("list tags", "list-tags"),
        ]

        for input_cmd, expected_cmd in note_commands:
            result = parser.parse(input_cmd)
            assert result is not None
            assert result["command"] == expected_cmd

    def test_contact_commands(self, parser: CommandParser):
        """Test all contact-related commands."""
        contact_commands = [
            ("add contact", "add-contact"),
            ("search contact", "search-contact"),
            ("list contacts", "list-contacts"),
            ("edit contact", "edit-contact"),
            ("delete contact", "delete-contact"),
        ]

        for input_cmd, expected_cmd in contact_commands:
            result = parser.parse(input_cmd)
            assert result is not None
            assert result["command"] == expected_cmd


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

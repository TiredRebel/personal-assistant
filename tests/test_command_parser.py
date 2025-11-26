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
        assert isinstance(result["confidence"], float)
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
        assert isinstance(result["args"], dict)
        assert "values" in result["args"]
        # Note: original case is preserved for arguments
        values = result["args"]["values"]
        assert isinstance(values, list)
        assert values[0] == "John Doe"

    def test_extract_options(self, parser: CommandParser):
        """Test extracting command options."""
        result = parser.parse("edit contact --phone +380501234567")
        assert result is not None
        assert isinstance(result["args"], dict)
        assert "phone" in result["args"]
        assert result["args"]["phone"] == "+380501234567"

    def test_extract_quoted_option_values(self, parser: CommandParser):
        """Test extracting options with quoted values."""
        result = parser.parse('add contact --email "john@example.com"')
        assert result is not None
        assert isinstance(result["args"], dict)
        assert "email" in result["args"]
        assert result["args"]["email"] == "john@example.com"

    def test_extract_multiple_options(self, parser: CommandParser):
        """Test extracting multiple options."""
        result = parser.parse('add contact --phone +380501234567 --email "test@example.com"')
        assert result is not None
        assert isinstance(result["args"], dict)
        assert "phone" in result["args"]
        assert "email" in result["args"]
        assert result["args"]["phone"] == "+380501234567"
        assert result["args"]["email"] == "test@example.com"

    def test_command_word_filtering(self, parser: CommandParser):
        """Test that command keywords are filtered from values."""
        result = parser.parse("add contact John")
        assert result is not None
        assert isinstance(result["args"], dict)
        assert "values" in result["args"]
        values = result["args"]["values"]
        # Should only contain "John", not "add" or "contact"
        assert values == ["John"]
        assert "add" not in values
        assert "contact" not in values

    def test_mixed_arguments_and_options(self, parser: CommandParser):
        """Test combination of quoted args, unquoted args, and options."""
        result = parser.parse(
            'add contact "John Doe" --phone +380501234567 --email "john@example.com"'
        )
        assert result is not None
        assert isinstance(result["args"], dict)
        assert "values" in result["args"]
        assert isinstance(result["args"]["values"], list)
        assert result["args"]["values"][0] == "John Doe"
        assert result["args"]["phone"] == "+380501234567"
        assert result["args"]["email"] == "john@example.com"

    def test_unquoted_and_quoted_mixed_values(self, parser: CommandParser):
        """Test mix of quoted and unquoted values without options."""
        result = parser.parse('add contact John "Doe Smith" test')
        assert result is not None
        assert isinstance(result["args"], dict)
        assert "values" in result["args"]
        values = result["args"]["values"]
        # Command words filtered, values preserved
        assert "John" in values
        assert "Doe Smith" in values
        assert "test" in values

    def test_options_before_arguments(self, parser: CommandParser):
        """Test that options can come before regular arguments."""
        result = parser.parse(
            'add contact --phone +380501234567 --email "john@example.com" "John Doe"'
        )
        assert result is not None
        assert isinstance(result["args"], dict)
        # Check that options are parsed correctly
        assert "phone" in result["args"]
        assert "email" in result["args"]
        assert result["args"]["phone"] == "+380501234567"
        assert result["args"]["email"] == "john@example.com"
        # Check that regular arguments still work
        assert "values" in result["args"]
        assert isinstance(result["args"]["values"], list)
        assert result["args"]["values"][0] == "John Doe"

    def test_hyphenated_command_with_arguments(self, parser: CommandParser):
        """Test that hyphenated commands work with arguments."""
        result = parser.parse('add-contact "John Smith" +380501234567 john@smith.com')
        assert result is not None
        assert isinstance(result["args"], dict)
        assert result["command"] == "add-contact"
        assert "values" in result["args"]
        values = result["args"]["values"]
        assert isinstance(values, list)
        assert values[0] == "John Smith"
        assert values[1] == "+380501234567"
        assert values[2] == "john@smith.com"

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

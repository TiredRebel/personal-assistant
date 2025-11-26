"""
Unit tests for SmartCommandParser

These tests verify the SmartCommandParser functionality for learning user behavior.
Run with: pytest tests/test_smart_command_parser.py
"""

import pytest
from personal_assistant.cli.smart_command_parser import SmartCommandParser


class TestSmartCommandParser:
    """Test suite for SmartCommandParser."""

    @pytest.fixture
    def parser(self):
        """Create a SmartCommandParser instance."""
        return SmartCommandParser()

    # ===== Basic Learning Tests =====

    def test_learning_patterns(self, parser: SmartCommandParser):
        """Test that parser learns user input patterns."""
        parser.learn_from_usage("add person", "add-contact")

        assert "add person" in parser.user_patterns["add-contact"]

    def test_learning_multiple_patterns_same_command(self, parser: SmartCommandParser):
        """Test learning multiple patterns for the same command."""
        parser.learn_from_usage("add person", "add-contact")
        parser.learn_from_usage("new contact", "add-contact")
        parser.learn_from_usage("create contact", "add-contact")

        assert len(parser.user_patterns["add-contact"]) == 3
        assert "add person" in parser.user_patterns["add-contact"]
        assert "new contact" in parser.user_patterns["add-contact"]
        assert "create contact" in parser.user_patterns["add-contact"]

    def test_learning_patterns_different_commands(self, parser: SmartCommandParser):
        """Test learning patterns for different commands."""
        parser.learn_from_usage("add person", "add-contact")
        parser.learn_from_usage("add memo", "add-note")

        assert "add person" in parser.user_patterns["add-contact"]
        assert "add memo" in parser.user_patterns["add-note"]
        assert len(parser.user_patterns) == 2

    def test_learning_normalizes_input(self, parser: SmartCommandParser):
        """Test that input is normalized (lowercase, trimmed)."""
        parser.learn_from_usage("  Add Person  ", "add-contact")

        # Should be normalized to lowercase and trimmed
        assert "add person" in parser.user_patterns["add-contact"]
        assert "  Add Person  " not in parser.user_patterns["add-contact"]

    def test_learning_avoids_duplicates(self, parser: SmartCommandParser):
        """Test that duplicate patterns are not added multiple times."""
        parser.learn_from_usage("add person", "add-contact")
        parser.learn_from_usage("add person", "add-contact")
        parser.learn_from_usage("add person", "add-contact")

        # Should only store once
        assert len(parser.user_patterns["add-contact"]) == 1

    # ===== History Recording Tests =====

    def test_history_recording(self, parser: SmartCommandParser):
        """Test that command history is recorded."""
        parser.learn_from_usage("find John", "search-contact")

        assert len(parser.command_history) == 1
        assert parser.command_history[0]["command"] == "search-contact"
        assert parser.command_history[0]["input"] == "find John"

    def test_history_includes_timestamp(self, parser: SmartCommandParser):
        """Test that history entries include timestamps."""
        parser.learn_from_usage("add contact", "add-contact")

        assert "timestamp" in parser.command_history[0]
        assert isinstance(parser.command_history[0]["timestamp"], str)

    def test_history_records_multiple_entries(self, parser: SmartCommandParser):
        """Test that multiple history entries are recorded."""
        parser.learn_from_usage("add person", "add-contact")
        parser.learn_from_usage("find john", "search-contact")
        parser.learn_from_usage("list all", "list-contacts")

        assert len(parser.command_history) == 3

    def test_history_allows_duplicates(self, parser: SmartCommandParser):
        """Test that history records duplicate commands (unlike patterns)."""
        parser.learn_from_usage("add person", "add-contact")
        parser.learn_from_usage("add person", "add-contact")
        parser.learn_from_usage("add person", "add-contact")

        # History should have all 3 entries
        assert len(parser.command_history) == 3
        # But patterns should only have 1
        assert len(parser.user_patterns["add-contact"]) == 1

    # ===== Suggestions from History Tests =====

    def test_suggestions_from_history(self, parser: SmartCommandParser):
        """Test basic frequency-based suggestions."""
        parser.learn_from_usage("a", "add-contact")
        parser.learn_from_usage("b", "add-contact")
        parser.learn_from_usage("c", "search-contact")

        suggestions = parser.suggest_based_on_history()

        assert suggestions[0] == "add-contact"  # Most frequent
        assert "search-contact" in suggestions

    def test_suggestions_sorted_by_frequency(self, parser: SmartCommandParser):
        """Test that suggestions are sorted by frequency."""
        # add-note: 5 times
        for _ in range(5):
            parser.learn_from_usage("n", "add-note")

        # add-contact: 3 times
        for _ in range(3):
            parser.learn_from_usage("c", "add-contact")

        # search-contact: 1 time
        parser.learn_from_usage("s", "search-contact")

        suggestions = parser.suggest_based_on_history()

        assert suggestions[0] == "add-note"  # 5 times
        assert suggestions[1] == "add-contact"  # 3 times
        assert suggestions[2] == "search-contact"  # 1 time

    def test_suggestions_max_five_items(self, parser: SmartCommandParser):
        """Test that suggestions are limited to 5 items."""
        # Create more than 5 different commands
        commands = [
            "add-contact",
            "add-note",
            "search-contact",
            "search-note",
            "list-contacts",
            "list-notes",
            "delete-contact",
            "delete-note",
        ]

        for cmd in commands:
            parser.learn_from_usage("test", cmd)

        suggestions = parser.suggest_based_on_history()

        assert len(suggestions) <= 5

    def test_suggestions_empty_when_no_history(self, parser: SmartCommandParser):
        """Test that empty list is returned when there's no history."""
        suggestions = parser.suggest_based_on_history()

        assert suggestions == []

    def test_suggestions_with_equal_frequencies(self, parser: SmartCommandParser):
        """Test suggestions when multiple commands have same frequency."""
        parser.learn_from_usage("a", "add-contact")
        parser.learn_from_usage("b", "add-note")
        parser.learn_from_usage("c", "search-contact")

        suggestions = parser.suggest_based_on_history()

        # All have frequency 1, order may vary but should include all
        assert len(suggestions) == 3
        assert "add-contact" in suggestions
        assert "add-note" in suggestions
        assert "search-contact" in suggestions

    # ===== Integration with parse() Tests =====

    def test_parse_learns_automatically(self, parser: SmartCommandParser):
        """Test that parse() automatically learns from recognized commands."""
        result = parser.parse("add contact")

        # Should be recognized
        assert result is not None
        assert result["command"] == "add-contact"

        # Should be automatically learned
        assert len(parser.command_history) == 1
        assert parser.command_history[0]["command"] == "add-contact"

    def test_parse_does_not_learn_from_unrecognized(self, parser: SmartCommandParser):
        """Test that parse() doesn't learn from unrecognized commands."""
        result = parser.parse("completely unknown xyz123")

        # Should not be recognized
        assert result is None

        # Should not add to history
        assert len(parser.command_history) == 0

    def test_parse_learns_with_fuzzy_match(self, parser: SmartCommandParser):
        """Test that parse() learns from fuzzy-matched commands."""
        result = parser.parse("add contac")  # typo

        # Should be fuzzy-matched
        assert result is not None
        assert result["command"] == "add-contact"

        # Should be learned with the typo
        assert len(parser.command_history) == 1
        assert parser.command_history[0]["input"] == "add contac"

    def test_parse_multiple_calls_build_history(self, parser: SmartCommandParser):
        """Test that multiple parse() calls build up history."""
        parser.parse("add contact")
        parser.parse("search contact")
        parser.parse("list contacts")

        assert len(parser.command_history) == 3

        suggestions = parser.suggest_based_on_history()
        assert len(suggestions) == 3

    # ===== Additional Helper Methods Tests =====

    def test_get_usage_stats(self, parser: SmartCommandParser):
        """Test getting usage statistics."""
        parser.learn_from_usage("a", "add-contact")
        parser.learn_from_usage("b", "add-contact")
        parser.learn_from_usage("c", "search-contact")

        stats = parser.get_usage_stats()

        assert stats["add-contact"] == 2
        assert stats["search-contact"] == 1

    def test_get_user_patterns_for_command(self, parser: SmartCommandParser):
        """Test getting patterns for a specific command."""
        parser.learn_from_usage("add person", "add-contact")
        parser.learn_from_usage("new contact", "add-contact")

        patterns = parser.get_user_patterns_for_command("add-contact")

        assert len(patterns) == 2
        assert "add person" in patterns
        assert "new contact" in patterns

    def test_get_user_patterns_for_nonexistent_command(self, parser: SmartCommandParser):
        """Test getting patterns for a command that hasn't been used."""
        patterns = parser.get_user_patterns_for_command("nonexistent-command")

        assert patterns == []

    def test_clear_history(self, parser: SmartCommandParser):
        """Test clearing all history and patterns."""
        parser.learn_from_usage("a", "add-contact")
        parser.learn_from_usage("b", "search-contact")

        assert len(parser.command_history) > 0
        assert len(parser.user_patterns) > 0

        parser.clear_history()

        assert len(parser.command_history) == 0
        assert len(parser.user_patterns) == 0

    # ===== Inheritance Tests =====

    def test_inherits_from_command_parser(self, parser: SmartCommandParser):
        """Test that SmartCommandParser inherits CommandParser functionality."""
        # Should still be able to parse exact commands
        result = parser.parse("add contact")
        assert result is not None
        assert result["command"] == "add-contact"

        # Should still be able to suggest commands
        suggestions = parser.suggest_commands("add con")
        assert len(suggestions) > 0

    def test_command_patterns_inherited(self, parser: SmartCommandParser):
        """Test that COMMAND_PATTERNS are inherited."""
        assert hasattr(parser, "COMMAND_PATTERNS")
        assert "add-contact" in parser.COMMAND_PATTERNS
        assert len(parser.COMMAND_PATTERNS) > 0

    # ===== Real-World Scenario Tests =====

    def test_realistic_usage_scenario(self, parser: SmartCommandParser):
        """Test a realistic usage scenario."""
        # User adds several contacts
        parser.parse("add contact")
        parser.parse("add contact")
        parser.parse("add contact")

        # User searches once
        parser.parse("search contact")

        # User lists contacts once
        parser.parse("list contacts")

        # Get suggestions - should prioritize add-contact
        suggestions = parser.suggest_based_on_history()

        assert suggestions[0] == "add-contact"
        assert len(parser.command_history) == 5
        stats = parser.get_usage_stats()
        assert stats["add-contact"] == 3

    def test_user_learns_shorthand(self, parser: SmartCommandParser):
        """Test that user can develop their own shorthand patterns."""
        # User uses various shorthands for add-contact
        parser.learn_from_usage("ac", "add-contact")
        parser.learn_from_usage("a c", "add-contact")
        parser.learn_from_usage("new c", "add-contact")

        patterns = parser.get_user_patterns_for_command("add-contact")

        assert "ac" in patterns
        assert "a c" in patterns
        assert "new c" in patterns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

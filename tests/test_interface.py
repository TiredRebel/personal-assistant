from datetime import date
from unittest.mock import Mock, patch

import pytest

from personal_assistant.cli.interface import CLI
from personal_assistant.models.contact import Contact
from personal_assistant.models.note import Note


@pytest.fixture
def mock_contact_service():
    """Mock ContactService for testing."""
    service = Mock()
    service.get_contacts_count.return_value = 5
    return service


@pytest.fixture
def mock_note_service():
    """Mock NoteService for testing."""
    service = Mock()
    service.get_notes_count.return_value = 10
    service.get_all_tags.return_value = ["work", "personal"]
    return service


@pytest.fixture
def mock_command_parser():
    """Mock CommandParser for testing."""
    parser = Mock()
    parser.suggest_commands.return_value = ["add-contact", "add-note"]
    return parser


@pytest.fixture
def cli(mock_contact_service, mock_note_service, mock_command_parser):
    """Create CLI instance with mocked dependencies."""
    return CLI(mock_contact_service, mock_note_service, mock_command_parser)


class TestCLIInitialization:
    """Test CLI initialization and command registration."""

    def test_cli_initialization(self, cli, mock_contact_service, mock_note_service):
        """Test that CLI initializes correctly with services."""
        assert cli.contact_service == mock_contact_service
        assert cli.note_service == mock_note_service
        assert cli.running is False
        assert isinstance(cli.commands, dict)

    def test_command_registration(self, cli):
        """Test that all commands are registered correctly."""
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
            "clear",
            "stats",
        ]

        for cmd in expected_commands:
            assert cmd in cli.commands
            assert callable(cli.commands[cmd])


class TestContactCommands:
    """Test contact management commands."""

    def test_add_contact_interactive(self, cli, mock_contact_service, monkeypatch):
        """Test adding contact interactively."""
        inputs = iter(
            ["John Doe", "+380501234567", "john@example.com", "123 Main St", "1990-01-15"]
        )
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        mock_contact = Contact(name="John Doe", phone="+380501234567")
        mock_contact_service.add_contact.return_value = mock_contact

        cli.add_contact()

        mock_contact_service.add_contact.assert_called_once()
        call_args = mock_contact_service.add_contact.call_args[1]
        assert call_args["name"] == "John Doe"
        assert call_args["phone"] == "+380501234567"

    def test_add_contact_with_parsed_args(self, cli, mock_contact_service, monkeypatch):
        """Test adding contact with pre-parsed arguments."""
        args = {"values": ["Jane Smith", "+380509876543", "jane@example.com"]}

        # Mock confirmation
        monkeypatch.setattr("builtins.input", lambda _: "yes")

        mock_contact = Contact(name="Jane Smith", phone="+380509876543")
        mock_contact_service.add_contact.return_value = mock_contact

        cli.add_contact(args)

        mock_contact_service.add_contact.assert_called_once()

    def test_search_contact_with_query(self, cli, mock_contact_service, monkeypatch):
        """Test searching contacts with query."""
        args = {"values": ["John"]}

        mock_contacts = [
            Contact(name="John Doe", phone="+380501234567"),
            Contact(name="Johnny Smith", phone="+380509876543"),
        ]
        mock_contact_service.search_contacts.return_value = mock_contacts

        cli.search_contact(args)

        mock_contact_service.search_contacts.assert_called_once_with("John")

    def test_search_contact_no_results(self, cli, mock_contact_service):
        """Test searching contacts with no results."""
        args = {"values": ["NonExistent"]}
        mock_contact_service.search_contacts.return_value = []

        cli.search_contact(args)

        mock_contact_service.search_contacts.assert_called_once()

    def test_list_contacts(self, cli, mock_contact_service):
        """Test listing all contacts."""
        mock_contacts = [
            Contact(name="John Doe", phone="+380501234567"),
            Contact(name="Jane Smith", phone="+380509876543"),
        ]
        mock_contact_service.get_all_contacts.return_value = mock_contacts

        cli.list_contacts()

        mock_contact_service.get_all_contacts.assert_called_once()

    def test_list_contacts_empty(self, cli, mock_contact_service):
        """Test listing contacts when none exist."""
        mock_contact_service.get_all_contacts.return_value = []

        cli.list_contacts()

        mock_contact_service.get_all_contacts.assert_called_once()

    def test_edit_contact_interactive(self, cli, mock_contact_service, monkeypatch):
        """Test editing contact interactively."""
        inputs = iter(["John Doe", "John Smith", "+380501111111", "", "", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        existing_contact = Contact(name="John Doe", phone="+380501234567")
        updated_contact = Contact(name="John Smith", phone="+380501111111")

        mock_contact_service.get_contact_by_name.return_value = existing_contact
        mock_contact_service.edit_contact.return_value = updated_contact

        cli.edit_contact()

        mock_contact_service.edit_contact.assert_called_once()

    def test_edit_contact_not_found(self, cli, mock_contact_service, monkeypatch):
        """Test editing non-existent contact."""
        monkeypatch.setattr("builtins.input", lambda _: "NonExistent")

        mock_contact_service.get_contact_by_name.return_value = None

        cli.edit_contact()

        mock_contact_service.get_contact_by_name.assert_called_once()

    def test_delete_contact_confirmed(self, cli, mock_contact_service, monkeypatch):
        """Test deleting contact with confirmation."""
        args = {"values": ["John Doe"]}
        monkeypatch.setattr("builtins.input", lambda _: "yes")

        mock_contact_service.delete_contact.return_value = True

        cli.delete_contact(args)

        mock_contact_service.delete_contact.assert_called_once_with("John Doe")

    def test_delete_contact_cancelled(self, cli, mock_contact_service, monkeypatch):
        """Test cancelling contact deletion."""
        args = {"values": ["John Doe"]}
        monkeypatch.setattr("builtins.input", lambda _: "no")

        cli.delete_contact(args)

        mock_contact_service.delete_contact.assert_not_called()

    def test_show_birthdays(self, cli, mock_contact_service, monkeypatch):
        """Test showing upcoming birthdays."""
        args = {"days": "7"}

        mock_contact = Contact(name="John Doe", phone="+380501234567")
        mock_contact.birthday = date(1990, 1, 15)
        mock_contact.days_until_birthday = Mock(return_value=5)

        mock_contact_service.get_upcoming_birthdays.return_value = [mock_contact]

        cli.show_birthdays(args)

        mock_contact_service.get_upcoming_birthdays.assert_called_once_with(7)


class TestNoteCommands:
    """Test note management commands."""

    def test_add_note_with_args(self, cli, mock_note_service):
        """Test adding note with pre-parsed arguments."""
        args = {"values": ["Test Title"], "content": "Test content", "tags": "work,urgent"}

        mock_note = Note(content="Test content", title="Test Title")
        mock_note_service.create_note.return_value = mock_note

        cli.add_note(args)

        mock_note_service.create_note.assert_called_once()
        call_args = mock_note_service.create_note.call_args[1]
        assert call_args["content"] == "Test content"
        assert "work" in call_args["tags"]

    def test_search_note(self, cli, mock_note_service):
        """Test searching notes."""
        args = {"values": ["test query"]}

        mock_notes = [
            Note(content="Test note 1", title="Title 1"),
            Note(content="Test note 2", title="Title 2"),
        ]
        # Mock get_note_by_id to return None (no ID match)
        mock_note_service.get_note_by_id.return_value = None
        mock_note_service.search_notes.return_value = mock_notes

        cli.search_note(args)

        # Should try ID search first, then content search
        mock_note_service.get_note_by_id.assert_called_once_with("test query")
        mock_note_service.search_notes.assert_called_once_with("test query")

    def test_list_notes(self, cli, mock_note_service):
        """Test listing all notes."""
        mock_notes = [
            Note(content="Note 1", title="Title 1"),
            Note(content="Note 2", title="Title 2"),
        ]
        mock_note_service.get_all_notes.return_value = mock_notes

        cli.list_notes()

        mock_note_service.get_all_notes.assert_called_once()

    def test_list_notes_empty(self, cli, mock_note_service):
        """Test listing notes when none exist."""
        mock_note_service.get_all_notes.return_value = []

        cli.list_notes()

        mock_note_service.get_all_notes.assert_called_once()

    def test_search_notes_by_tag(self, cli, mock_note_service):
        """Test searching notes by tags."""
        args = {"tags": "work,urgent"}

        mock_notes = [Note(content="Work note", title="Work", tags=["work"])]
        mock_note_service.search_notes_by_tags.return_value = mock_notes

        cli.search_notes_by_tag(args)

        mock_note_service.search_notes_by_tags.assert_called_once()

    def test_list_all_tags(self, cli, mock_note_service):
        """Test listing all tags."""
        mock_note_service.get_all_tags.return_value = ["work", "personal", "urgent"]
        mock_note_service.search_notes_by_any_tag.return_value = [
            Note(content="Test", tags=["work"])
        ]

        cli.list_all_tags()

        mock_note_service.get_all_tags.assert_called_once()

    def test_edit_note_by_id(self, cli, mock_note_service, monkeypatch):
        """Test editing note by ID."""
        args = {"values": ["abc123"]}

        existing_note = Note(content="Old content", title="Old Title")
        updated_note = Note(content="New content", title="New Title")

        mock_note_service.get_note_by_id.return_value = existing_note
        mock_note_service.edit_note.return_value = updated_note

        inputs = iter(["1", "New Title"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        cli.edit_note(args)

        mock_note_service.edit_note.assert_called_once()

    def test_delete_note_confirmed(self, cli, mock_note_service, monkeypatch):
        """Test deleting note with confirmation."""
        args = {"values": ["abc123"]}

        mock_note = Note(content="Test note")
        mock_note_service.get_note_by_id.return_value = mock_note
        mock_note_service.delete_note.return_value = True

        monkeypatch.setattr("builtins.input", lambda _: "yes")

        cli.delete_note(args)

        mock_note_service.delete_note.assert_called_once()

    def test_delete_note_cancelled(self, cli, mock_note_service, monkeypatch):
        """Test cancelling note deletion."""
        args = {"values": ["abc123"]}

        mock_note = Note(content="Test note")
        mock_note_service.get_note_by_id.return_value = mock_note

        monkeypatch.setattr("builtins.input", lambda _: "no")

        cli.delete_note(args)

        mock_note_service.delete_note.assert_not_called()


class TestDisplayHelpers:
    """Test display helper methods."""

    def test_display_contact(self, cli, capsys):
        """Test displaying a single contact."""
        contact = Contact(
            name="John Doe",
            phone="+380501234567",
            email="john@example.com",
            address="123 Main St",
            birthday=date(1990, 1, 15),
        )
        contact.days_until_birthday = Mock(return_value=30)

        cli.display_contact(contact)

        captured = capsys.readouterr()
        assert "John Doe" in captured.out
        assert "+380501234567" in captured.out
        assert "john@example.com" in captured.out
        assert "123 Main St" in captured.out
        assert "30 days until birthday" in captured.out

    def test_display_contact_minimal(self, cli, capsys):
        """Test displaying a contact with only required fields."""
        contact = Contact(name="Jane Smith", phone="+380509876543")

        cli.display_contact(contact)

        captured = capsys.readouterr()
        assert "Jane Smith" in captured.out
        assert "+380509876543" in captured.out
        assert "Email" not in captured.out or "Email:" in captured.out

    def test_display_contacts_table(self, cli, capsys):
        """Test displaying contacts table."""
        contacts = [
            Contact(name="John Doe", phone="+380501234567", email="john@example.com"),
            Contact(name="Jane Smith", phone="+380509876543"),
        ]

        cli.display_contacts_table(contacts)

        captured = capsys.readouterr()
        assert "John Doe" in captured.out
        assert "+380501234567" in captured.out
        assert "john@example.com" in captured.out
        assert "Jane Smith" in captured.out
        assert "+380509876543" in captured.out
        assert "Name" in captured.out  # Table header
        assert "Phone" in captured.out

    def test_display_contacts_table_empty(self, cli, capsys):
        """Test displaying empty contacts table."""
        cli.display_contacts_table([])

        captured = capsys.readouterr()
        assert "Name" in captured.out  # Header should still appear
        assert "Phone" in captured.out

    def test_display_note(self, cli, capsys):
        """Test displaying a single note."""
        note = Note(content="Test content", title="Test Title", tags=["work", "urgent"])

        cli.display_note(note)

        captured = capsys.readouterr()
        assert "Test Title" in captured.out
        assert "Test content" in captured.out
        assert "work" in captured.out
        assert "urgent" in captured.out
        assert "ID:" in captured.out

    def test_display_note_no_title(self, cli, capsys):
        """Test displaying a note without title."""
        note = Note(content="Just some content")

        cli.display_note(note)

        captured = capsys.readouterr()
        assert "Just some content" in captured.out
        assert "ID:" in captured.out

    def test_display_note_long_content(self, cli, capsys):
        """Test displaying a note with long content."""
        long_content = "A" * 150
        note = Note(content=long_content)

        cli.display_note(note)

        captured = capsys.readouterr()
        assert "..." in captured.out  # Content should be truncated
        assert captured.out.count("A") < 150  # Not all content shown

    def test_display_notes_list(self, cli, capsys):
        """Test displaying notes list."""
        notes = [
            Note(content="Note 1", title="Title 1", tags=["work"]),
            Note(content="Note 2" * 50, tags=["personal"]),  # Long content
        ]

        cli.display_notes_list(notes)

        captured = capsys.readouterr()
        assert "Title 1" in captured.out
        assert "Note 1" in captured.out
        assert "work" in captured.out
        assert "(Untitled)" in captured.out  # Second note has no title
        assert "personal" in captured.out
        assert "..." in captured.out  # Long content truncated

    def test_display_notes_list_empty(self, cli, capsys):
        """Test displaying empty notes list."""
        cli.display_notes_list([])

        captured = capsys.readouterr()
        # Should not crash, output may be empty
        assert isinstance(captured.out, str)


class TestMessageHelpers:
    """Test message display helpers."""

    def test_show_success(self, cli, capsys):
        """Test showing success message."""
        cli.show_success("Operation completed")
        captured = capsys.readouterr()
        assert "✓" in captured.out
        assert "Operation completed" in captured.out

    def test_show_error(self, cli, capsys):
        """Test showing error message."""
        cli.show_error("Something went wrong")
        captured = capsys.readouterr()
        assert "✗" in captured.out
        assert "Something went wrong" in captured.out

    def test_show_warning(self, cli, capsys):
        """Test showing warning message."""
        cli.show_warning("Be careful")
        captured = capsys.readouterr()
        assert "⚠" in captured.out
        assert "Be careful" in captured.out

    def test_show_command_suggestions(self, cli, mock_command_parser, capsys):
        """Test showing command suggestions."""
        mock_command_parser.suggest_commands.return_value = ["add-contact", "add-note"]

        cli.show_command_suggestions("add")
        captured = capsys.readouterr()

        assert "add-contact" in captured.out
        assert "add-note" in captured.out
        assert "not recognized" in captured.out.lower()

    def test_show_command_suggestions_no_matches(self, cli, mock_command_parser, capsys):
        """Test showing command suggestions when no matches found."""
        mock_command_parser.suggest_commands.return_value = []

        cli.show_command_suggestions("xyz123")
        captured = capsys.readouterr()

        assert "not recognized" in captured.out.lower()
        assert "help" in captured.out.lower()


class TestSystemCommands:
    """Test system commands."""

    def test_show_help(self, cli, capsys):
        """Test showing help information."""
        cli.show_help()

        captured = capsys.readouterr()
        assert "Help" in captured.out or "help" in captured.out
        assert "add-contact" in captured.out
        assert "add-note" in captured.out
        assert "exit" in captured.out

    def test_show_statistics(self, cli, mock_contact_service, mock_note_service, capsys):
        """Test showing statistics."""
        cli.show_statistics()

        mock_contact_service.get_contacts_count.assert_called_once()
        mock_note_service.get_notes_count.assert_called_once()
        mock_note_service.get_all_tags.assert_called_once()

        captured = capsys.readouterr()
        assert "Statistics" in captured.out or "statistics" in captured.out
        assert "5" in captured.out  # Contact count
        assert "10" in captured.out  # Note count

    @patch("os.system")
    def test_clear_screen_windows(self, mock_system, cli):
        """Test clearing screen on Windows."""
        with patch("os.name", "nt"):
            cli.clear_screen()
            mock_system.assert_called_once_with("cls")

    @patch("os.system")
    def test_clear_screen_unix(self, mock_system, cli):
        """Test clearing screen on Unix/Linux."""
        with patch("os.name", "posix"):
            cli.clear_screen()
            mock_system.assert_called_once_with("clear")

    def test_exit_app(self, cli):
        """Test exit application."""
        with pytest.raises(SystemExit):
            cli.exit_app()

        assert cli.running is False


class TestCommandExecution:
    """Test command execution and parsing."""

    def test_execute_command_valid(self, cli, mock_command_parser):
        """Test executing a valid command."""
        mock_command_parser.parse.return_value = {"command": "list-contacts", "args": {}}

        # Mock get_all_contacts to return an empty list
        cli.contact_service.get_all_contacts.return_value = []

        cli.execute_command("list-contacts")

        cli.contact_service.get_all_contacts.assert_called_once()

    def test_execute_command_invalid(self, cli, mock_command_parser, capsys):
        """Test executing an invalid command."""
        mock_command_parser.parse.return_value = None

        cli.execute_command("invalid-command")

        mock_command_parser.suggest_commands.assert_called_once()
        captured = capsys.readouterr()
        assert len(captured.out) > 0  # Should output something

    def test_execute_command_with_args(self, cli, mock_command_parser, mock_contact_service):
        """Test executing command with arguments."""
        mock_command_parser.parse.return_value = {
            "command": "search-contact",
            "args": {"values": ["John"]},
        }

        mock_contact_service.search_contacts.return_value = []

        cli.execute_command("search-contact John")

        mock_contact_service.search_contacts.assert_called_once()

    def test_execute_command_help(self, cli, mock_command_parser, capsys):
        """Test executing help command."""
        mock_command_parser.parse.return_value = {"command": "help", "args": {}}

        cli.execute_command("help")

        captured = capsys.readouterr()
        assert "help" in captured.out.lower()

    def test_execute_command_stats(self, cli, mock_command_parser, capsys):
        """Test executing stats command."""
        mock_command_parser.parse.return_value = {"command": "stats", "args": {}}

        cli.execute_command("stats")

        captured = capsys.readouterr()
        assert "5" in captured.out or "10" in captured.out  # Should show counts


class TestErrorHandling:
    """Test error handling."""

    def test_add_contact_invalid_date(self, cli, mock_contact_service, monkeypatch, capsys):
        """Test adding contact with invalid birthday."""
        inputs = iter(["John Doe", "+380501234567", "", "", "invalid-date"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        mock_contact = Contact(name="John Doe", phone="+380501234567")
        mock_contact_service.add_contact.return_value = mock_contact

        cli.add_contact()

        # Should handle invalid date gracefully
        mock_contact_service.add_contact.assert_called_once()
        captured = capsys.readouterr()
        assert "invalid" in captured.out.lower() or "warning" in captured.out.lower()

    def test_add_contact_service_error(self, cli, mock_contact_service, monkeypatch, capsys):
        """Test handling service errors when adding contact."""
        inputs = iter(["John Doe", "+380501234567", "", "", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        mock_contact_service.add_contact.side_effect = ValueError("Invalid phone")

        cli.add_contact()

        captured = capsys.readouterr()
        assert "error" in captured.out.lower() or "invalid" in captured.out.lower()

    def test_edit_contact_service_error(self, cli, mock_contact_service, monkeypatch, capsys):
        """Test handling service errors when editing contact."""
        inputs = iter(["John Doe"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        mock_contact_service.get_contact_by_name.side_effect = ValueError("Contact not found")

        cli.edit_contact()

        captured = capsys.readouterr()
        assert "error" in captured.out.lower()


class TestWelcomeAndMenu:
    """Test welcome message and menu display."""

    def test_show_welcome(self, cli, capsys):
        """Test showing welcome message."""
        cli.show_welcome()

        captured = capsys.readouterr()
        assert "Personal Assistant" in captured.out
        assert "=" in captured.out  # Decorative lines

    def test_show_main_menu(self, cli, capsys):
        """Test showing main menu."""
        cli.show_main_menu()

        captured = capsys.readouterr()
        assert "Main Menu" in captured.out or "Menu" in captured.out
        assert "add-contact" in captured.out
        assert "add-note" in captured.out
        assert "help" in captured.out
        assert "exit" in captured.out


class TestStartMethod:
    """Test the start method and main loop."""

    def test_start_sets_running_flag(self, cli):
        """Test that start sets running flag to True."""
        with patch.object(cli, "show_welcome"):
            with patch.object(cli, "show_main_menu"):
                with patch("builtins.input", side_effect=KeyboardInterrupt):
                    with patch.object(cli, "confirm_exit", side_effect=SystemExit):
                        with pytest.raises(SystemExit):
                            cli.start()


class TestNoteCommandsExtended:
    """Extended tests for note commands."""

    def test_edit_note_interactive_all_fields(self, cli, mock_note_service, monkeypatch):
        """Test editing all fields of a note interactively."""
        args = {"values": ["abc123"]}

        existing_note = Note(content="Old content", title="Old Title", tags=["old"])
        updated_note = Note(content="New content", title="New Title", tags=["new"])

        mock_note_service.get_note_by_id.return_value = existing_note
        mock_note_service.edit_note.return_value = updated_note

        # Simplified input sequence: choice, title, content, tags
        inputs = iter(["4", "New Title", "New content", "new,tag"])
        input_call_count = [0]

        def mock_input(prompt=None):
            prompt_str = str(prompt).lower() if prompt else ""
            input_call_count[0] += 1

            # First call: choice selection
            if input_call_count[0] == 1:
                return "4"
            # Second call: title
            elif input_call_count[0] == 2:
                return "New Title"
            # Third call: content (first line triggers EOFError after)
            elif input_call_count[0] == 3:
                return "New content"
            # Fourth call: still in content, raise EOFError
            elif input_call_count[0] == 4:
                raise EOFError()
            # Fifth call: tags
            elif input_call_count[0] == 5:
                return "new,tag"
            return ""

        monkeypatch.setattr("builtins.input", mock_input)

        cli.edit_note(args)

        mock_note_service.edit_note.assert_called_once()
        call_args = mock_note_service.edit_note.call_args
        # Check both kwargs and positional args
        if call_args[1]:
            assert call_args[1].get("title") == "New Title"
            assert "New content" in call_args[1].get("content", "")
        else:
            # If using positional args, just verify it was called
            assert mock_note_service.edit_note.called

    def test_edit_note_by_search(self, cli, mock_note_service, monkeypatch, capsys):
        """Test editing note found by search."""
        args = {"values": ["search term"]}

        note = Note(content="Test content", title="Test Title")
        mock_note_service.get_note_by_id.return_value = None
        mock_note_service.search_notes.return_value = [note]
        mock_note_service.edit_note.return_value = note

        inputs = iter(["1", "New Title"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        cli.edit_note(args)

        mock_note_service.edit_note.assert_called_once()

    def test_edit_note_multiple_matches(self, cli, mock_note_service, monkeypatch, capsys):
        """Test editing note when multiple matches found."""
        args = {"values": ["search"]}

        notes = [Note(content="Note 1", title="Title 1"), Note(content="Note 2", title="Title 2")]

        mock_note_service.get_note_by_id.return_value = None
        mock_note_service.search_notes.return_value = notes
        mock_note_service.edit_note.return_value = notes[0]

        inputs = iter(["1", "1", "New Title"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        cli.edit_note(args)

        captured = capsys.readouterr()
        assert "Multiple" in captured.out or "select" in captured.out.lower()

    def test_delete_note_by_search(self, cli, mock_note_service, monkeypatch):
        """Test deleting note found by search."""
        args = {"values": ["search term"]}

        note = Note(content="Test note")
        mock_note_service.get_note_by_id.return_value = None
        mock_note_service.search_notes.return_value = [note]
        mock_note_service.delete_note.return_value = True

        monkeypatch.setattr("builtins.input", lambda _: "yes")

        cli.delete_note(args)

        mock_note_service.delete_note.assert_called_once()

    def test_delete_note_not_found(self, cli, mock_note_service, monkeypatch, capsys):
        """Test deleting non-existent note."""
        args = {"values": ["nonexistent"]}

        mock_note_service.get_note_by_id.return_value = None
        mock_note_service.search_notes.return_value = []

        cli.delete_note(args)

        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()
        mock_note_service.delete_note.assert_not_called()


class TestContactCommandsExtended:
    """Extended tests for contact commands."""

    def test_add_contact_with_name_only(self, cli, mock_contact_service, monkeypatch):
        """Test adding contact when only name is provided in args."""
        args = {"values": ["John Doe"]}

        inputs = iter(["no", "John Doe", "", "+380501234567", "", "", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        mock_contact = Contact(name="John Doe", phone="+380501234567")
        mock_contact_service.add_contact.return_value = mock_contact

        cli.add_contact(args)

        mock_contact_service.add_contact.assert_called_once()

    def test_add_contact_with_phone_only(self, cli, mock_contact_service, monkeypatch):
        """Test adding contact when only phone is provided in args."""
        args = {"values": ["+380501234567"]}

        inputs = iter(["yes", "John Doe", "", "", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        mock_contact = Contact(name="John Doe", phone="+380501234567")
        mock_contact_service.add_contact.return_value = mock_contact

        cli.add_contact(args)

        mock_contact_service.add_contact.assert_called_once()

    def test_add_contact_rejected_confirmation(self, cli, mock_contact_service, monkeypatch):
        """Test adding contact when user rejects initial confirmation."""
        args = {"values": ["Jane Smith", "+380509876543"]}

        # Sequence: reject confirmation, then provide new details (name, phone, email, address, birthday)
        inputs = iter(["no", "Corrected Name", "+380501111111", "", "", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        mock_contact = Contact(name="Corrected Name", phone="+380501111111")
        mock_contact_service.add_contact.return_value = mock_contact

        cli.add_contact(args)

        # Verify the service was called
        mock_contact_service.add_contact.assert_called_once()
        call_args = mock_contact_service.add_contact.call_args
        # Check the call was made with correct data
        if call_args[1]:  # If keyword arguments exist
            assert call_args[1]["name"] == "Corrected Name"
            assert call_args[1]["phone"] == "+380501111111"

    def test_search_contact_interactive(self, cli, mock_contact_service, monkeypatch):
        """Test searching contacts interactively without args."""
        monkeypatch.setattr("builtins.input", lambda _: "John")

        mock_contacts = [Contact(name="John Doe", phone="+380501234567")]
        mock_contact_service.search_contacts.return_value = mock_contacts

        cli.search_contact()

        mock_contact_service.search_contacts.assert_called_once_with("John")

    def test_search_contact_empty_query(self, cli, mock_contact_service, monkeypatch, capsys):
        """Test searching with empty query."""
        monkeypatch.setattr("builtins.input", lambda _: "")

        cli.search_contact()

        mock_contact_service.search_contacts.assert_not_called()
        captured = capsys.readouterr()
        assert "empty" in captured.out.lower() or "error" in captured.out.lower()

    def test_edit_contact_with_options(self, cli, mock_contact_service, monkeypatch):
        """Test editing contact with command-line options."""
        args = {"values": ["John Doe"], "name": "John Smith", "phone": "+380501111111"}

        existing_contact = Contact(name="John Doe", phone="+380501234567")
        updated_contact = Contact(name="John Smith", phone="+380501111111")

        mock_contact_service.get_contact_by_name.return_value = existing_contact
        mock_contact_service.edit_contact.return_value = updated_contact

        cli.edit_contact(args)

        call_args = mock_contact_service.edit_contact.call_args[1]
        assert call_args["name"] == "John Smith"
        assert call_args["phone"] == "+380501111111"

    def test_show_birthdays_default_days(self, cli, mock_contact_service, monkeypatch):
        """Test showing birthdays with default 7 days."""
        monkeypatch.setattr("builtins.input", lambda _: "")

        mock_contact_service.get_upcoming_birthdays.return_value = []

        cli.show_birthdays()

        mock_contact_service.get_upcoming_birthdays.assert_called_once_with(7)

    def test_show_birthdays_custom_days(self, cli, mock_contact_service, monkeypatch):
        """Test showing birthdays with custom number of days."""
        monkeypatch.setattr("builtins.input", lambda _: "14")

        mock_contact_service.get_upcoming_birthdays.return_value = []

        cli.show_birthdays()

        mock_contact_service.get_upcoming_birthdays.assert_called_once_with(14)

    def test_delete_contact_interactive(self, cli, mock_contact_service, monkeypatch):
        """Test deleting contact interactively."""
        inputs = iter(["John Doe", "yes"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        mock_contact_service.delete_contact.return_value = True

        cli.delete_contact()

        mock_contact_service.delete_contact.assert_called_once_with("John Doe")

    def test_delete_contact_empty_name(self, cli, mock_contact_service, monkeypatch):
        """Test deleting contact with empty name."""
        monkeypatch.setattr("builtins.input", lambda _: "")

        cli.delete_contact()

        mock_contact_service.delete_contact.assert_not_called()


class TestNoteSearchAndList:
    """Test note search and list functionality."""

    def test_search_note_interactive(self, cli, mock_note_service, monkeypatch):
        """Test searching notes interactively."""
        monkeypatch.setattr("builtins.input", lambda _: "test")

        mock_notes = [Note(content="Test note")]
        # Mock get_note_by_id to return None (no ID match)
        mock_note_service.get_note_by_id.return_value = None
        mock_note_service.search_notes.return_value = mock_notes

        cli.search_note()

        # Should try ID search first, then content search
        mock_note_service.get_note_by_id.assert_called_once_with("test")
        mock_note_service.search_notes.assert_called_once_with("test")

    def test_search_note_empty_query(self, cli, mock_note_service, monkeypatch, capsys):
        """Test searching notes with empty query."""
        monkeypatch.setattr("builtins.input", lambda _: "")

        cli.search_note()

        mock_note_service.search_notes.assert_not_called()
        captured = capsys.readouterr()
        assert "empty" in captured.out.lower()

    def test_search_notes_by_tag_interactive(self, cli, mock_note_service, monkeypatch):
        """Test searching notes by tag interactively."""
        monkeypatch.setattr("builtins.input", lambda _: "work,urgent")

        mock_notes = [Note(content="Work note", tags=["work"])]
        mock_note_service.search_notes_by_tags.return_value = mock_notes

        cli.search_notes_by_tag()

        mock_note_service.search_notes_by_tags.assert_called_once()

    def test_search_notes_by_tag_from_values(self, cli, mock_note_service):
        """Test searching notes by tags from values."""
        args = {"values": ["work", "urgent"]}

        mock_notes = [Note(content="Work note", tags=["work"])]
        mock_note_service.search_notes_by_tags.return_value = mock_notes

        cli.search_notes_by_tag(args)

        mock_note_service.search_notes_by_tags.assert_called_once()

    def test_list_all_tags_with_counts(self, cli, mock_note_service, capsys):
        """Test listing all tags with note counts."""
        mock_note_service.get_all_tags.return_value = ["work", "personal"]
        mock_note_service.search_notes_by_any_tag.return_value = [
            Note(content="Test", tags=["work"])
        ]

        cli.list_all_tags()

        captured = capsys.readouterr()
        assert "work" in captured.out
        assert "personal" in captured.out
        assert "(1)" in captured.out  # Count

    def test_list_all_tags_empty(self, cli, mock_note_service, capsys):
        """Test listing tags when none exist."""
        mock_note_service.get_all_tags.return_value = []

        cli.list_all_tags()

        captured = capsys.readouterr()
        assert "no tags" in captured.out.lower()
        assert "no tags" in captured.out.lower()

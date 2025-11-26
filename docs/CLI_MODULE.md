# CLI Module Specification

## Overview
The Command-Line Interface (CLI) module provides the main user interface for interacting with the Personal Assistant application.

## Design Principles
- **Intuitive**: Commands should be easy to remember and use
- **Consistent**: Similar operations use similar command patterns
- **Helpful**: Provide clear feedback and suggestions
- **Forgiving**: Handle typos and suggest corrections

## Command Structure

### Command Format
```
command [subcommand] [arguments] [--options]
```

### Examples
```bash
add contact "John Doe" +380501234567
search contact john
edit contact "John Doe" --phone +380509999999
delete contact "John Doe"

add note "Meeting notes" --tags work,important
search note meeting
edit note <id> --content "Updated content"
delete note <id>
```

## Main Menu Interface

### Class: `CLI`

```python
from typing import Optional, Callable, Dict, List
import sys
from datetime import datetime

class CLI:
    """
    Command-line interface for Personal Assistant.

    Features:
    - Interactive menu
    - Command parsing
    - Input validation
    - Colored output (optional)
    - Help system
    """

    def __init__(self, contact_service, note_service, command_parser):
        """
        Initialize CLI.

        Args:
            contact_service: ContactService instance
            note_service: NoteService instance
            command_parser: CommandParser for intelligent parsing
        """
        self.contact_service = contact_service
        self.note_service = note_service
        self.command_parser = command_parser
        self.running = False

        # Command registry
        self.commands: Dict[str, Callable] = self._register_commands()

    def _register_commands(self) -> Dict[str, Callable]:
        """
        Register all available commands.

        Returns:
            Dictionary mapping command names to handler functions
        """
        return {
            # Contact commands
            'add-contact': self.add_contact,
            'search-contact': self.search_contact,
            'list-contacts': self.list_contacts,
            'edit-contact': self.edit_contact,
            'delete-contact': self.delete_contact,
            'birthdays': self.show_birthdays,

            # Note commands
            'add-note': self.add_note,
            'search-note': self.search_note,
            'list-notes': self.list_notes,
            'edit-note': self.edit_note,
            'delete-note': self.delete_note,
            'search-by-tag': self.search_notes_by_tag,
            'list-tags': self.list_all_tags,

            # System commands
            'help': self.show_help,
            'exit': self.exit_app,
            'clear': self.clear_screen,
            'stats': self.show_statistics
        }

    def start(self):
        """
        Start the CLI application.

        Main loop:
        1. Display welcome message
        2. Show main menu
        3. Process user input
        4. Repeat until exit
        """
        self.running = True
        self.show_welcome()

        while self.running:
            try:
                self.show_main_menu()
                command = input("\nEnter command: ").strip()

                if not command:
                    continue

                # Parse and execute command
                self.execute_command(command)

            except KeyboardInterrupt:
                self.confirm_exit()
            except Exception as e:
                self.show_error(f"Error: {str(e)}")

    def show_welcome(self):
        """Display welcome message."""
        print("="* 60)
        print("  Personal Assistant")
        print("  Manage your contacts and notes efficiently")
        print("="* 60)
        print()

    def show_main_menu(self):
        """Display main menu options."""
        print("\n--- Main Menu ---")
        print("Contact Management:")
        print("  add-contact      - Add a new contact")
        print("  search-contact   - Search for contacts")
        print("  list-contacts    - List all contacts")
        print("  edit-contact     - Edit a contact")
        print("  delete-contact   - Delete a contact")
        print("  birthdays        - Show upcoming birthdays")
        print()
        print("Note Management:")
        print("  add-note         - Create a new note")
        print("  search-note      - Search notes")
        print("  list-notes       - List all notes")
        print("  edit-note        - Edit a note")
        print("  delete-note      - Delete a note")
        print("  search-by-tag    - Search notes by tag")
        print("  list-tags        - Show all tags")
        print()
        print("System:")
        print("  help             - Show detailed help")
        print("  stats            - Show statistics")
        print("  clear            - Clear screen")
        print("  exit             - Exit application")

    def execute_command(self, command_str: str):
        """
        Parse and execute a command.

        Args:
            command_str: Raw command string from user
        """
        # Try intelligent command parsing first
        parsed = self.command_parser.parse(command_str)

        if parsed and parsed.get('command') in self.commands:
            command_func = self.commands[parsed['command']]
            command_func(parsed.get('args', {}))
        else:
            # Command not recognized, show suggestions
            self.show_command_suggestions(command_str)

    # Contact Commands

    def add_contact(self, args: Dict = None):
        """
        Add a new contact interactively.

        Args:
            args: Pre-parsed arguments (optional)
        """
        print("\n--- Add New Contact ---")

        try:
            # Get contact information
            name = input("Name: ").strip()
            phone = input("Phone: ").strip()
            email = input("Email (optional): ").strip() or None
            address = input("Address (optional): ").strip() or None

            # Get birthday
            birthday_str = input("Birthday (YYYY-MM-DD, optional): ").strip()
            birthday = None
            if birthday_str:
                from datetime import date
                birthday = date.fromisoformat(birthday_str)

            # Add contact
            contact = self.contact_service.add_contact(
                name=name,
                phone=phone,
                email=email,
                address=address,
                birthday=birthday
            )

            self.show_success(f"Contact '{contact.name}' added successfully!")
            self.display_contact(contact)

        except ValueError as e:
            self.show_error(f"Invalid input: {str(e)}")
        except Exception as e:
            self.show_error(f"Error adding contact: {str(e)}")

    def search_contact(self, args: Dict = None):
        """
        Search for contacts.

        Args:
            args: Pre-parsed arguments (optional)
        """
        print("\n--- Search Contacts ---")

        query = input("Search query: ").strip()
        if not query:
            self.show_error("Search query cannot be empty")
            return

        results = self.contact_service.search_contacts(query)

        if results:
            self.show_success(f"Found {len(results)} contact(s):")
            self.display_contacts_table(results)
        else:
            self.show_warning(f"No contacts found matching '{query}'")

    def list_contacts(self, args: Dict = None):
        """List all contacts."""
        print("\n--- All Contacts ---")

        contacts = self.contact_service.get_all_contacts()

        if contacts:
            self.display_contacts_table(contacts)
            print(f"\nTotal: {len(contacts)} contact(s)")
        else:
            self.show_warning("No contacts in address book")

    def edit_contact(self, args: Dict = None):
        """Edit an existing contact."""
        print("\n--- Edit Contact ---")

        # Implementation: Interactive editing
        pass

    def delete_contact(self, args: Dict = None):
        """Delete a contact."""
        print("\n--- Delete Contact ---")

        name = input("Contact name to delete: ").strip()
        if not name:
            return

        # Confirm deletion
        confirm = input(f"Are you sure you want to delete '{name}'? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Deletion cancelled")
            return

        if self.contact_service.delete_contact(name):
            self.show_success(f"Contact '{name}' deleted successfully")
        else:
            self.show_error(f"Contact '{name}' not found")

    def show_birthdays(self, args: Dict = None):
        """Show upcoming birthdays."""
        print("\n--- Upcoming Birthdays ---")

        days = input("Days ahead (default: 7): ").strip()
        days = int(days) if days.isdigit() else 7

        contacts = self.contact_service.get_upcoming_birthdays(days)

        if contacts:
            print(f"\nBirthdays in the next {days} days:")
            for contact in contacts:
                days_until = contact.days_until_birthday()
                print(f"  • {contact.name}: {days_until} day(s)")
        else:
            self.show_warning(f"No birthdays in the next {days} days")

    # Note Commands

    def add_note(self, args: Dict = None):
        """Add a new note."""
        print("\n--- Add New Note ---")

        try:
            title = input("Title (optional): ").strip() or None
            print("Content (press Ctrl+D or Ctrl+Z when done):")

            # Multi-line input
            content_lines = []
            try:
                while True:
                    line = input()
                    content_lines.append(line)
            except EOFError:
                pass

            content = '\n'.join(content_lines).strip()

            if not content:
                self.show_error("Content cannot be empty")
                return

            # Get tags
            tags_str = input("Tags (comma-separated, optional): ").strip()
            tags = [t.strip() for t in tags_str.split(',')] if tags_str else []

            # Create note
            note = self.note_service.create_note(
                content=content,
                title=title,
                tags=tags
            )

            self.show_success(f"Note created successfully! (ID: {note.id[:8]})")
            self.display_note(note)

        except Exception as e:
            self.show_error(f"Error creating note: {str(e)}")

    def search_note(self, args: Dict = None):
        """Search notes by content."""
        print("\n--- Search Notes ---")

        query = input("Search query: ").strip()
        if not query:
            self.show_error("Search query cannot be empty")
            return

        results = self.note_service.search_notes(query)

        if results:
            self.show_success(f"Found {len(results)} note(s):")
            self.display_notes_list(results)
        else:
            self.show_warning(f"No notes found matching '{query}'")

    def list_notes(self, args: Dict = None):
        """List all notes."""
        print("\n--- All Notes ---")

        notes = self.note_service.get_all_notes()

        if notes:
            self.display_notes_list(notes)
            print(f"\nTotal: {len(notes)} note(s)")
        else:
            self.show_warning("No notes available")

    def search_notes_by_tag(self, args: Dict = None):
        """Search notes by tags."""
        print("\n--- Search by Tags ---")

        tags_str = input("Tags (comma-separated): ").strip()
        if not tags_str:
            return

        tags = [t.strip() for t in tags_str.split(',')]
        results = self.note_service.search_notes_by_tags(tags)

        if results:
            self.show_success(f"Found {len(results)} note(s) with tags: {', '.join(tags)}")
            self.display_notes_list(results)
        else:
            self.show_warning(f"No notes found with tags: {', '.join(tags)}")

    def list_all_tags(self, args: Dict = None):
        """List all available tags."""
        print("\n--- All Tags ---")

        tags = self.note_service.get_all_tags()

        if tags:
            sorted_tags = sorted(tags)
            for tag in sorted_tags:
                # Count notes with this tag
                notes = self.note_service.search_notes_by_any_tag([tag])
                print(f"  • {tag} ({len(notes)})")
            print(f"\nTotal: {len(tags)} tag(s)")
        else:
            self.show_warning("No tags available")

    # Display Helpers

    def display_contact(self, contact):
        """Display a single contact details."""
        print(f"\nName:     {contact.name}")
        print(f"Phone:    {contact.phone}")
        if contact.email:
            print(f"Email:    {contact.email}")
        if contact.address:
            print(f"Address:  {contact.address}")
        if contact.birthday:
            print(f"Birthday: {contact.birthday}")
            days = contact.days_until_birthday()
            if days is not None:
                print(f"          ({days} days until birthday)")

    def display_contacts_table(self, contacts: List):
        """Display contacts in a table format."""
        # Print table header
        print(f"\n{'Name':<25} {'Phone':<20} {'Email':<30}")
        print("-" * 75)

        # Print contacts
        for contact in contacts:
            email = contact.email or ""
            print(f"{contact.name:<25} {contact.phone:<20} {email:<30}")

    def display_note(self, note):
        """Display a single note details."""
        print(f"\nID:       {note.id[:8]}")
        if note.title:
            print(f"Title:    {note.title}")
        print(f"Content:  {note.content[:100]}{'...' if len(note.content) > 100 else ''}")
        if note.tags:
            print(f"Tags:     {', '.join(note.tags)}")
        print(f"Created:  {note.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"Updated:  {note.updated_at.strftime('%Y-%m-%d %H:%M')}")

    def display_notes_list(self, notes: List):
        """Display notes in a list format."""
        for i, note in enumerate(notes, 1):
            print(f"\n{i}. [{note.id[:8]}] ", end="")
            if note.title:
                print(f"{note.title}")
            else:
                print("(Untitled)")

            # Show preview of content
            preview = note.content[:80].replace('\n', ' ')
            print(f"   {preview}{'...' if len(note.content) > 80 else ''}")

            # Show tags
            if note.tags:
                print(f"   Tags: {', '.join(note.tags)}")

    # System Commands

    def show_help(self, args: Dict = None):
        """Show detailed help information."""
        print("\n--- Personal Assistant Help ---")
        print("\nAvailable Commands:")

        for cmd_name, cmd_func in self.commands.items():
            doc = cmd_func.__doc__ or "No description"
            print(f"  {cmd_name:<20} - {doc.strip()}")

    def show_statistics(self, args: Dict = None):
        """Show application statistics."""
        print("\n--- Statistics ---")

        contact_count = self.contact_service.get_contacts_count()
        note_count = self.note_service.get_notes_count()
        tag_count = len(self.note_service.get_all_tags())

        print(f"Contacts:  {contact_count}")
        print(f"Notes:     {note_count}")
        print(f"Tags:      {tag_count}")

    def clear_screen(self, args: Dict = None):
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def confirm_exit(self):
        """Confirm exit with user."""
        confirm = input("\n\nAre you sure you want to exit? (yes/no): ")
        if confirm.lower() in ['yes', 'y']:
            self.exit_app()
        else:
            print("Continuing...")

    def exit_app(self, args: Dict = None):
        """Exit the application."""
        print("\nThank you for using Personal Assistant!")
        print("Goodbye!")
        self.running = False
        sys.exit(0)

    # Message Display Helpers

    def show_success(self, message: str):
        """Display success message."""
        print(f"✓ {message}")

    def show_error(self, message: str):
        """Display error message."""
        print(f"✗ {message}")

    def show_warning(self, message: str):
        """Display warning message."""
        print(f"⚠ {message}")

    def show_command_suggestions(self, command_str: str):
        """Show command suggestions for unrecognized command."""
        suggestions = self.command_parser.suggest_commands(command_str)

        if suggestions:
            print(f"\n✗ Command not recognized: '{command_str}'")
            print("\nDid you mean:")
            for cmd in suggestions[:3]:
                print(f"  • {cmd}")
        else:
            print(f"\n✗ Command not recognized: '{command_str}'")
            print("Type 'help' for available commands")
```

## Enhanced CLI with Colors (Optional)

```python
class ColoredCLI(CLI):
    """
    CLI with colored output using colorama.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            from colorama import init, Fore, Style
            init(autoreset=True)
            self.Fore = Fore
            self.Style = Style
            self.colors_enabled = True
        except ImportError:
            self.colors_enabled = False

    def show_success(self, message: str):
        """Display success message in green."""
        if self.colors_enabled:
            print(f"{self.Fore.GREEN}✓ {message}{self.Style.RESET_ALL}")
        else:
            super().show_success(message)

    def show_error(self, message: str):
        """Display error message in red."""
        if self.colors_enabled:
            print(f"{self.Fore.RED}✗ {message}{self.Style.RESET_ALL}")
        else:
            super().show_error(message)

    def show_warning(self, message: str):
        """Display warning message in yellow."""
        if self.colors_enabled:
            print(f"{self.Fore.YELLOW}⚠ {message}{self.Style.RESET_ALL}")
        else:
            super().show_warning(message)
```

## Testing Requirements

```python
def test_cli_initialization():
    """Test CLI initialization."""
    pass

def test_command_parsing():
    """Test command parsing."""
    pass

def test_add_contact_command():
    """Test add contact command."""
    pass

def test_search_contact_command():
    """Test search contact command."""
    pass

def test_command_suggestions():
    """Test command suggestions for typos."""
    pass
```

## Best Practices

1. **Clear feedback**: Always show what happened after a command
2. **Confirmation**: Ask for confirmation on destructive operations
3. **Validation**: Validate all input before processing
4. **Help text**: Provide helpful error messages and suggestions
5. **Consistency**: Use consistent command patterns

## Future Enhancements

- Command history (arrow keys to navigate)
- Tab completion for commands
- Batch operations
- Command scripting
- Configuration via command line
- Internationalization (i18n)

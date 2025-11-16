import os
import sys
from datetime import date
from typing import Any, Callable, Dict, List, Optional

# Try to import colorama, but don't fail if not available
try:
    from colorama import Fore, Style, init  # type: ignore[import-untyped]

    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

# Try to import readline for command completion (Windows: pyreadline3, Unix: readline)
try:
    import readline

    READLINE_AVAILABLE = True
    READLINE_MODULE: Any = readline
except ImportError:
    try:
        import pyreadline3  # type: ignore[import-untyped]

        # pyreadline3 uses a different API - get the readline instance
        READLINE_AVAILABLE = True
        READLINE_MODULE: Any = pyreadline3.Readline()  # type: ignore[attr-defined]
    except (ImportError, AttributeError):
        READLINE_AVAILABLE = False
        READLINE_MODULE: Any = None


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

        # Setup command completion
        self._setup_command_completion()

    def _setup_command_completion(self) -> None:
        """Setup readline command completion if available."""
        if READLINE_AVAILABLE and READLINE_MODULE:
            # Get all command names for completion
            command_names = sorted(list(self.commands.keys()))

            def completer(text: str, state: int) -> Optional[str]:
                """Autocomplete function for readline."""
                # If text is empty, show all commands
                if not text:
                    options = command_names
                else:
                    # Find commands that start with the text (case-insensitive)
                    text_lower = text.lower()
                    options = [cmd for cmd in command_names if cmd.lower().startswith(text_lower)]

                # Return the option at the given state index
                if state < len(options):
                    return options[state]
                return None

            try:
                READLINE_MODULE.set_completer(completer)  # type: ignore[attr-defined]

                # Configure readline behavior
                # Use tab for completion, show all options on double-tab
                if sys.platform == "win32":
                    READLINE_MODULE.parse_and_bind("tab: complete")  # type: ignore[attr-defined]
                else:
                    READLINE_MODULE.parse_and_bind("tab: complete")  # type: ignore[attr-defined]
                    # On Unix, also enable menu-complete for cycling through options
                    READLINE_MODULE.parse_and_bind("set show-all-if-ambiguous on")  # type: ignore[attr-defined]

                # Set word delimiters (don't break on hyphens)
                READLINE_MODULE.set_completer_delims(" \t\n")  # type: ignore[attr-defined]
            except AttributeError:
                # If methods don't exist, silently disable completion
                pass

    def _register_commands(self) -> Dict[str, Callable]:
        """
        Register all available commands.

        Returns:
            Dictionary mapping command names to handler functions
        """
        return {
            # Contact commands
            "add-contact": self.add_contact,
            "search-contact": self.search_contact,
            "list-contacts": self.list_contacts,
            "edit-contact": self.edit_contact,
            "delete-contact": self.delete_contact,
            "birthdays": self.show_birthdays,
            # Note commands
            "add-note": self.add_note,
            "search-note": self.search_note,
            "list-notes": self.list_notes,
            "edit-note": self.edit_note,
            "delete-note": self.delete_note,
            "search-by-tag": self.search_notes_by_tag,
            "list-tags": self.list_all_tags,
            # System commands
            "help": self.show_help,
            "exit": self.exit_app,
            "clear": self.clear_screen,
            "stats": self.show_statistics,
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
        self.show_main_menu()

        while self.running:
            try:
                command = input(self.get_prompt()).strip()

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
        print("=" * 60)
        print("  Personal Assistant")
        print("  Manage your contacts and notes efficiently")
        print("=" * 60)
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

    def execute_command(self, command_str: str) -> None:
        """
        Parse and execute a command.

        Args:
            command_str: Raw command string from user
        """
        # Try intelligent command parsing first
        parsed = self.command_parser.parse(command_str)

        if parsed and parsed.get("command") in self.commands:
            command_func = self.commands[parsed["command"]]
            command_func(parsed.get("args", {}))
        else:
            # Command not recognized, show suggestions
            self.show_command_suggestions(command_str)

    # Contact Commands

    def add_contact(self, args: Optional[Dict] = None) -> None:
        """
        Add a new contact interactively.

        Accepts pre-parsed arguments: add-contact "John Doe" +380501234567 john@example.com
        If arguments provided, asks for confirmation before requesting additional fields.

        Args:
            args: Pre-parsed arguments (optional, may contain 'values' list with name, phone, email, address)
        """
        print("\n--- Add New Contact ---")

        try:
            name = None
            phone = None
            email = None
            address = None

            # Check for --option style arguments first
            if args:
                email = args.get("email")
                address = args.get("address")

            # Try to extract name, phone, email, address from pre-parsed arguments
            # args format: {'values': ['John Doe', '+380501234567', 'john@example.com'], 'email': '...', ...}
            if args and args.get("values"):
                values = args["values"]

                # Try to identify which value is what based on pattern
                for value in values:
                    value_str = str(value).strip()

                    # Check if it looks like a phone number (starts with + or digit)
                    if not phone and (
                        value_str.startswith("+") or (value_str and value_str[0].isdigit())
                    ):
                        phone = value_str
                    # Check if it looks like an email (contains @)
                    elif not email and "@" in value_str:
                        email = value_str
                    # Otherwise, assume it's a name (if we don't have one) or address
                    elif not name:
                        name = value_str
                    elif not address:
                        # Remaining values could be address
                        address = value_str

            # If we extracted both name and phone, show for confirmation
            if name and phone:
                print("\nDetected information:")
                print(f"  Name:  {name}")
                print(f"  Phone: {phone}")
                if email:
                    print(f"  Email: {email}")
                if address:
                    print(f"  Address: {address}")

                if not self._is_confirmed("Is this information correct?"):
                    # User rejected, ask for correct values
                    print("\nPlease provide correct information:")
                    name = input("Name: ").strip()
                    phone = input("Phone: ").strip()

            # If only name was detected, ask for phone
            elif name and not phone:
                print(f"\nDetected name: {name}")
                if email:
                    print(f"  Email: {email}")

                if not self._is_confirmed("Is this correct?"):
                    name = input("Name: ").strip()
                    email = input("Email (optional): ").strip() or email

                phone = input("Phone: ").strip()

            # If only phone was detected, ask for name
            elif phone and not name:
                print(f"\nDetected phone: {phone}")
                if email:
                    print(f"  Email: {email}")

                if not self._is_confirmed("Is this correct?"):
                    phone = input("Phone: ").strip()
                    email = input("Email (optional): ").strip() or email

                name = input("Name: ").strip()

            # If nothing was detected, ask for all
            else:
                name = input("Name: ").strip()
                phone = input("Phone: ").strip()

            # Ask for missing optional fields
            if not email:
                email = input("Email (optional): ").strip() or None

            if not address:
                address = input("Address (optional): ").strip() or None

            # Get birthday
            birthday_str = input("Birthday (YYYY-MM-DD, optional): ").strip()
            birthday = None
            if birthday_str:
                try:
                    birthday = date.fromisoformat(birthday_str)
                except ValueError:
                    self.show_warning("Invalid date format. Skipping birthday.")
                    birthday = None

            # Add contact
            contact = self.contact_service.add_contact(
                name=name, phone=phone, email=email, address=address, birthday=birthday
            )

            self.show_success(f"Contact '{contact.name}' added successfully!")
            self.display_contact(contact)

        except ValueError as e:
            self.show_error(f"Invalid input: {str(e)}")
        except Exception as e:
            self.show_error(f"Error adding contact: {str(e)}")

    def search_contact(self, args: Optional[Dict] = None) -> None:
        """
        Search for contacts.

        Args:
            args: Pre-parsed arguments (optional, may contain 'values' with search query)
        """
        print("\n--- Search Contacts ---")

        # Try to get query from args first
        query = None
        if args and args.get("values"):
            # Join all values as search query
            query = " ".join(str(v) for v in args["values"])

        # If no query from args, ask user
        if not query:
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

    def list_contacts(self, args: Optional[Dict] = None) -> None:
        """List all contacts."""
        print("\n--- All Contacts ---")

        contacts = self.contact_service.get_all_contacts()

        if contacts:
            self.display_contacts_table(contacts)
            print(f"\nTotal: {len(contacts)} contact(s)")
        else:
            self.show_warning("No contacts in address book")

    def edit_contact(self, args: Optional[Dict] = None) -> None:
        """
        Edit an existing contact.

        Args:
            args: Pre-parsed arguments (optional, may contain name and --name/--phone/--email/--address options)
        """
        print("\n--- Edit Contact ---")

        try:
            # Try to get name from args
            name = None
            if args and args.get("values"):
                name = args["values"][0]  # First value is the name

            if not name:
                name = input("Contact name to edit: ").strip()

            if not name:
                return

            # Check if specific fields provided via options
            new_name = args.get("name") if args else None
            new_phone = args.get("phone") if args else None
            new_email = args.get("email") if args else None
            new_address = args.get("address") if args else None
            birthday_str = args.get("birthday") if args else None

            # If options provided, use them; otherwise ask interactively
            if not any([new_name, new_phone, new_email, new_address, birthday_str]):
                # Service will handle finding contact and raise exception if not found
                contact = self.contact_service.get_contact_by_name(name)

                if not contact:
                    self.show_error(f"Contact '{name}' not found")
                    return

                # Display current contact info
                print("\nCurrent contact information:")
                self.display_contact(contact)

                print("\nEnter new values (press Enter to keep current value):")
                new_name = input(f"Name [{contact.name}]: ").strip()
                new_phone = input(f"Phone [{contact.phone}]: ").strip()
                new_email = input(f"Email [{contact.email or ''}]: ").strip()
                new_address = input(f"Address [{contact.address or ''}]: ").strip()
                current_birthday = contact.birthday.isoformat() if contact.birthday else ""
                birthday_str = input(f"Birthday (YYYY-MM-DD) [{current_birthday}]: ").strip()

            # Parse birthday if provided
            birthday = None
            if birthday_str:
                try:
                    birthday = date.fromisoformat(birthday_str)
                except ValueError:
                    self.show_warning("Invalid date format. Skipping birthday.")
                    birthday = None

            # Service handles validation and raises exceptions
            updated_contact = self.contact_service.edit_contact(
                old_name=name,
                name=new_name if new_name else None,
                phone=new_phone if new_phone else None,
                email=new_email if new_email else None,
                address=new_address if new_address else None,
                birthday=birthday,
            )

            self.show_success(f"Contact '{updated_contact.name}' updated successfully!")
            self.display_contact(updated_contact)

        except ValueError as e:
            # Contact not found or validation errors
            self.show_error(f"Error: {str(e)}")
        except Exception as e:
            # Other errors
            self.show_error(f"Error updating contact: {str(e)}")

    def delete_contact(self, args: Optional[Dict] = None) -> None:
        """
        Delete a contact.

        Args:
            args: Pre-parsed arguments (optional, may contain name to delete)
        """
        print("\n--- Delete Contact ---")

        # Try to get name from args
        name = None
        if args and args.get("values"):
            name = args["values"][0]  # First value is the name

        if not name:
            name = input("Contact name to delete: ").strip()

        if not name:
            return

        # Confirm deletion
        if not self._is_confirmed(f"Are you sure you want to delete '{name}'?"):
            self.show_warning("Deletion cancelled")
            return

        if self.contact_service.delete_contact(name):
            self.show_success(f"Contact '{name}' deleted successfully")
        else:
            self.show_error(f"Contact '{name}' not found")

    def show_birthdays(self, args: Optional[Dict] = None) -> None:
        """
        Show upcoming birthdays.

        Args:
            args: Pre-parsed arguments (optional, may contain --days option)
        """
        print("\n--- Upcoming Birthdays ---")

        # Try to get days from args (--days option)
        days = None
        if args and args.get("days"):
            days_str = args["days"]
            if days_str.isdigit():
                days = int(days_str)

        # If not provided, ask user
        if days is None:
            days_input = input("Days ahead (default: 7): ").strip()
            days = int(days_input) if days_input.isdigit() else 7

        contacts = self.contact_service.get_upcoming_birthdays(days)

        if contacts:
            print(f"\nBirthdays in the next {days} days:")
            for contact in contacts:
                days_until = contact.days_until_birthday()
                print(f"  • {contact.name}: {days_until} day(s)")
        else:
            self.show_warning(f"No birthdays in the next {days} days")

    # Note Commands

    def add_note(self, args: Optional[Dict] = None) -> None:
        """
        Add a new note.

        Args:
            args: Pre-parsed arguments (optional, may contain title, content via --content, and --tags)
        """
        print("\n--- Add New Note ---")

        try:
            # Try to get title from values
            title = None
            if args and args.get("values"):
                title = args["values"][0] if args["values"] else None

            # Check for --content option
            content = args.get("content") if args else None

            # Check for --tags option
            tags_str = args.get("tags") if args else None

            # If content not provided via option, get it interactively
            if not content:
                if not title:
                    title = input("Title (optional): ").strip() or None

                print("Content (press Ctrl+D or Ctrl+Z when done):")
                content_lines = []
                try:
                    while True:
                        line = input()
                        content_lines.append(line)
                except EOFError:
                    pass

                content = "\n".join(content_lines).strip()

            if not content:
                self.show_error("Content cannot be empty")
                return

            # Get tags if not provided
            if not tags_str:
                tags_str = input("Tags (comma-separated, optional): ").strip()

            tags = [t.strip() for t in tags_str.split(",")] if tags_str else []

            # Create note
            note = self.note_service.create_note(content=content, title=title, tags=tags)

            self.show_success(f"Note created successfully! (ID: {note.id[:8]})")
            self.display_note(note)

        except Exception as e:
            self.show_error(f"Error creating note: {str(e)}")

    def search_note(self, args: Optional[Dict] = None) -> None:
        """
        Search notes by content or ID.

        Args:
            args: Pre-parsed arguments (optional, may contain search query in values)
        """
        print("\n--- Search Notes ---")

        # Try to get query from args
        query = None
        if args and args.get("values"):
            query = " ".join(str(v) for v in args["values"])

        if not query:
            query = input("Search query or ID: ").strip()

        if not query:
            self.show_error("Search query cannot be empty")
            return

        # First try to find by exact ID match
        note_by_id = self.note_service.get_note_by_id(query)
        if note_by_id:
            self.show_success("Found note by ID:")
            self.display_notes_list([note_by_id])
            return

        # If not found by ID, search by content
        results = self.note_service.search_notes(query)

        if results:
            self.show_success(f"Found {len(results)} note(s):")
            self.display_notes_list(results)
        else:
            self.show_warning(f"No notes found matching '{query}'")

    def list_notes(self, args: Optional[Dict] = None) -> None:
        """List all notes."""
        print("\n--- All Notes ---")

        notes = self.note_service.get_all_notes()

        if notes:
            self.display_notes_list(notes)
            print(f"\nTotal: {len(notes)} note(s)")
        else:
            self.show_warning("No notes available")

    def search_notes_by_tag(self, args: Optional[Dict] = None) -> None:
        """
        Search notes by tags.

        Args:
            args: Pre-parsed arguments (optional, may contain tags in values or --tags option)
        """
        print("\n--- Search by Tags ---")

        # Try to get tags from --tags option first
        tags_str = args.get("tags") if args else None

        # If not in option, try values
        if not tags_str and args and args.get("values"):
            tags_str = ",".join(str(v) for v in args["values"])

        # If still not provided, ask user
        if not tags_str:
            tags_str = input("Tags (comma-separated): ").strip()

        if not tags_str:
            return

        tags = [t.strip() for t in tags_str.split(",")]
        results = self.note_service.search_notes_by_tags(tags)

        if results:
            self.show_success(f"Found {len(results)} note(s) with tags: {', '.join(tags)}")
            self.display_notes_list(results)
        else:
            self.show_warning(f"No notes found with tags: {', '.join(tags)}")

    def list_all_tags(self, args: Optional[Dict] = None) -> None:
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

    def display_contact(self, contact) -> None:
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

    def display_contacts_table(self, contacts: List) -> None:
        """Display contacts in a table format."""
        # Print table header
        print(f"\n{'Name':<25} {'Phone':<20} {'Email':<30}")
        print("-" * 75)

        # Print contacts
        for contact in contacts:
            email = contact.email or ""
            print(f"{contact.name:<25} {contact.phone:<20} {email:<30}")

    def display_note(self, note) -> None:
        """Display a single note details."""
        print(f"\nID:       {note.id[:8]}")
        if note.title:
            print(f"Title:    {note.title}")
        print(f"Content:  {note.content[:100]}{'...' if len(note.content) > 100 else ''}")
        if note.tags:
            print(f"Tags:     {', '.join(note.tags)}")
        print(f"Created:  {note.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"Updated:  {note.updated_at.strftime('%Y-%m-%d %H:%M')}")

    def display_notes_list(self, notes: List) -> None:
        """Display notes in a list format."""
        for i, note in enumerate(notes, 1):
            print(f"\n{i}. [{note.id[:8]}] ", end="")
            if note.title:
                print(f"{note.title}")
            else:
                print("(Untitled)")

            # Show preview of content
            preview = note.content[:80].replace("\n", " ")
            print(f"   {preview}{'...' if len(note.content) > 80 else ''}")

            # Show tags
            if note.tags:
                print(f"   Tags: {', '.join(note.tags)}")

    # System Commands

    def show_help(self, args: Optional[Dict] = None) -> None:
        """Show detailed help information."""
        print("\n--- Personal Assistant Help ---")
        print("\nAvailable Commands:")

        for cmd_name, cmd_func in self.commands.items():
            doc = cmd_func.__doc__ or "No description"
            print(f"  {cmd_name:<20} - {doc.strip()}")

    def show_statistics(self, args: Optional[Dict] = None) -> None:
        """Show application statistics."""
        print("\n--- Statistics ---")

        contact_count = self.contact_service.get_contacts_count()
        note_count = self.note_service.get_notes_count()
        tag_count = len(self.note_service.get_all_tags())

        print(f"Contacts:  {contact_count}")
        print(f"Notes:     {note_count}")
        print(f"Tags:      {tag_count}")

    def clear_screen(self, args: Optional[Dict] = None) -> None:
        """Clear the terminal screen."""

        os.system("cls" if os.name == "nt" else "clear")

    def confirm_exit(self) -> None:
        """Confirm exit with user."""
        if self._is_confirmed("\n\nAre you sure you want to exit?"):
            self.exit_app()
        else:
            self.show_warning("Continuing...")

    def exit_app(self, args: Optional[Dict] = None) -> None:
        """Exit the application."""
        print("\nThank you for using Personal Assistant!")
        print("Goodbye!")
        self.running = False
        sys.exit(0)  # consider to move sys.exit to main loop

    # Message Display Helpers

    def show_success(self, message: str) -> None:
        """Display success message."""
        print(f"✓ {message}")

    def show_error(self, message: str) -> None:
        """Display error message."""
        print(f"✗ {message}")

    def show_warning(self, message: str) -> None:
        """Display warning message."""
        print(f"⚠ {message}")

    def show_command_suggestions(self, command_str: str) -> None:
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

    def edit_note(self, args: Optional[Dict] = None) -> None:
        """
        Edit an existing note.

        Args:
            args: Pre-parsed arguments (optional, may contain note_id and --title/--content/--tags options)
        """
        print("\n--- Edit Note ---")

        try:
            # Try to get note ID from args
            note_id = None
            if args and args.get("values"):
                note_id = args["values"][0]  # First value is note ID

            # If not provided, ask user
            if not note_id:
                note_id = input("Note ID (or search term): ").strip()

            if not note_id:
                return

            # Try to find note by ID first (handles full UUID or partial match)
            note = self.note_service.get_note_by_id(note_id)

            # If not found by ID, search by content/title
            if not note:
                results = self.note_service.search_notes(note_id)
                if not results:
                    self.show_error("Note not found")
                    return
                if len(results) > 1:
                    self.show_warning("Multiple notes found. Please select one:")
                    self.display_notes_list(results)
                    index = input("\nEnter note number: ").strip()
                    if index.isdigit() and 0 < int(index) <= len(results):
                        note = results[int(index) - 1]
                    else:
                        self.show_error("Invalid selection")
                        return
                else:
                    note = results[0]

            # Display current note
            print("\nCurrent note:")
            self.display_note(note)

            # Check for options in args
            new_title = args.get("title") if args else None
            new_content = args.get("content") if args else None
            tags_str = args.get("tags") if args else None
            new_tags = None

            # If options provided, use them; otherwise interactive edit
            if not any([new_title, new_content, tags_str]):
                # Interactive mode - ask what to edit
                print("\nWhat would you like to edit?")
                print("1. Title")
                print("2. Content")
                print("3. Tags")
                print("4. All")
                choice = input("\nChoice (1-4): ").strip()

                if choice in ["1", "4"]:
                    new_title = input(f"Title [{note.title or ''}]: ").strip()
                    new_title = new_title if new_title else None

                if choice in ["2", "4"]:
                    print("Content (press Ctrl+D or Ctrl+Z when done, or Enter to keep current):")
                    content_lines = []
                    try:
                        first_line = input()
                        if first_line:
                            content_lines.append(first_line)
                            while True:
                                line = input()
                                content_lines.append(line)
                    except EOFError:
                        pass

                    if content_lines:
                        new_content = "\n".join(content_lines).strip()

                if choice in ["3", "4"]:
                    current_tags = ", ".join(note.tags) if note.tags else ""
                    tags_str = input(f"Tags (comma-separated) [{current_tags}]: ").strip()

            # Parse tags if provided
            if tags_str:
                new_tags = [t.strip() for t in tags_str.split(",")]

            # Service uses edit_note
            updated_note = self.note_service.edit_note(
                note_id=note.id, title=new_title, content=new_content, tags=new_tags
            )

            self.show_success(f"Note updated successfully! (ID: {updated_note.id[:8]})")
            self.display_note(updated_note)

        except ValueError as e:
            # Validation errors (note not found, empty content, etc.)
            self.show_error(f"Error: {str(e)}")
        except Exception as e:
            # Other errors
            self.show_error(f"Error updating note: {str(e)}")

    def delete_note(self, args: Optional[Dict] = None) -> None:
        """
        Delete a note.

        Args:
            args: Pre-parsed arguments (optional, may contain note_id to delete)
        """
        print("\n--- Delete Note ---")

        try:
            # Try to get note ID from args
            note_id = None
            if args and args.get("values"):
                note_id = args["values"][0]  # First value is note ID

            # If not provided, ask user
            if not note_id:
                note_id = input("Note ID (or search term): ").strip()

            if not note_id:
                return

            # Try to find note by ID first
            note = self.note_service.get_note_by_id(note_id)

            # If not found by ID, search by content/title
            if not note:
                results = self.note_service.search_notes(note_id)
                if not results:
                    self.show_error("Note not found")
                    return
                if len(results) > 1:
                    self.show_warning("Multiple notes found. Please select one:")
                    self.display_notes_list(results)
                    index = input("\nEnter note number: ").strip()
                    if index.isdigit() and 0 < int(index) <= len(results):
                        note = results[int(index) - 1]
                    else:
                        self.show_error("Invalid selection")
                        return
                else:
                    note = results[0]

            # Display note to be deleted
            print("\nNote to delete:")
            self.display_note(note)

            # Confirm deletion
            if not self._is_confirmed("Are you sure you want to delete this note?"):
                self.show_warning("Deletion cancelled")
                return

            # Service handles deletion
            if self.note_service.delete_note(note.id):
                self.show_success("Note deleted successfully")
            else:
                self.show_error("Failed to delete note")

        except ValueError as e:
            # Note not found
            self.show_error(f"Error: {str(e)}")
        except Exception as e:
            # Other errors
            self.show_error(f"Error deleting note: {str(e)}")

    def _is_confirmed(self, prompt: str = "Are you sure?") -> bool:
        """
        Ask user for confirmation.

        Args:
            prompt: Question to ask user

        Returns:
            True if user confirmed (yes/y), False otherwise
        """
        return input(f"\n{prompt} (yes/no): ").strip().lower() in {"yes", "y"}

    def get_prompt(self) -> str:
        """
        Get the command prompt string.

        Returns:
            The prompt string to display
        """
        return "\nEnter command: "


class ColoredCLI(CLI):
    """
    CLI with colored output using colorama.
    Provides color-coded success, error, and warning messages.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if COLORAMA_AVAILABLE:
            init(autoreset=True)
            self.Fore = Fore
            self.Style = Style
            self.colors_enabled = True
        else:
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

    def get_prompt(self) -> str:
        """
        Get the command prompt string with color.

        Returns:
            The colored prompt string to display
        """
        if self.colors_enabled:
            # Wrap ANSI codes in \001 and \002 for readline compatibility
            # This tells readline these are non-printing characters
            cyan = f"\001{self.Fore.CYAN}\002"
            reset = f"\001{self.Style.RESET_ALL}\002"
            return f"\n{cyan}Enter command:{reset} "
        else:
            return super().get_prompt()

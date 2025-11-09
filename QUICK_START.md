# Quick Start Guide

Get up and running with Personal Assistant in minutes!

## Prerequisites

- Python 3.8 or higher
- uv (Fast Python package installer) - [Install here](https://github.com/astral-sh/uv)
- Git (for cloning the repository)

## Installation

### 1. Install uv (if not already installed)

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd personal-assistant
```

### 3. Setup Virtual Environment and Install Dependencies

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On macOS/Linux
source .venv/bin/activate

# On Windows
.venv\Scripts\activate

# Install project with dependencies
uv pip install -e .

# For development (includes testing tools)
uv pip install -e ".[dev]"

# For colored output
uv pip install -e ".[colors]"
```

## Running the Application

### Basic Usage

```bash
# Using uv run (automatically uses virtual environment)
uv run personal-assistant

# Or activate venv and run directly
source .venv/bin/activate
personal-assistant

# Short alias
pa

# Or run as module
uv run python -m personal_assistant.main
```

## First Steps

### 1. Add Your First Contact

```
Enter command: add-contact

--- Add New Contact ---
Name: John Doe
Phone: +380501234567
Email: john@example.com
Address: 123 Main Street, Kyiv
Birthday (YYYY-MM-DD): 1990-05-15

✓ Contact 'John Doe' added successfully!
```

### 2. Search for Contacts

```
Enter command: search-contact

--- Search Contacts ---
Search query: john

✓ Found 1 contact(s):

Name                      Phone                Email
---------------------------------------------------------------------------
John Doe                  +380501234567        john@example.com
```

### 3. Create a Note

```
Enter command: add-note

--- Add New Note ---
Title: Meeting Notes
Content (press Ctrl+D when done):
Discussed Q4 strategy
Action items: Update roadmap, schedule follow-up
^D
Tags (comma-separated): work, meeting, important

✓ Note created successfully! (ID: abc12345)
```

### 4. Check Upcoming Birthdays

```
Enter command: birthdays

--- Upcoming Birthdays ---
Days ahead (default: 7): 7

Birthdays in the next 7 days:
  • John Doe: 5 day(s)
```

## Common Commands

### Contact Management
- `add-contact` - Add a new contact
- `search-contact` - Search contacts
- `list-contacts` - Show all contacts
- `edit-contact` - Edit existing contact
- `delete-contact` - Delete a contact
- `birthdays` - Show upcoming birthdays

### Note Management
- `add-note` - Create a new note
- `search-note` - Search notes by content
- `list-notes` - Show all notes
- `edit-note` - Edit a note
- `delete-note` - Delete a note
- `search-by-tag` - Search notes by tags
- `list-tags` - Show all available tags

### System Commands
- `help` - Show detailed help
- `stats` - Show statistics
- `clear` - Clear screen
- `exit` - Exit application

## Tips & Tricks

### 1. Natural Language Commands

You can use natural language instead of exact commands:

```
"show me all contacts"     → list-contacts
"find john's phone"        → search-contact john
"create a note about X"    → add-note
```

### 2. Quick Phone Formats

All these phone formats are valid:
- `+380501234567`
- `0501234567`
- `+380 50 123 45 67`
- `050-123-45-67`

### 3. Organize with Tags

Use tags to organize notes:
```
Tags: work, project-x, urgent
```

Then search by tag:
```
Enter command: search-by-tag
Tags: work, urgent
```

### 4. Keyboard Shortcuts

- `Ctrl+C` - Cancel current operation
- `Ctrl+D` or `Ctrl+Z` - Finish multi-line input (notes)

## Data Location

Your data is stored in:
- **Location**: `~/.personal_assistant/`
- **Contacts**: `~/.personal_assistant/contacts.json`
- **Notes**: `~/.personal_assistant/notes.json`
- **Backups**: `~/.personal_assistant/backups/`

## Troubleshooting

### Problem: "Module not found" error

**Solution**: Make sure you're in the project directory and dependencies are installed

```bash
# Check if you're in the right directory
pwd  # Should end with /personal-assistant

# Create and activate venv
uv venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e ".[dev]"
```

### Problem: uv command not found

**Solution**: Install uv or add to PATH

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or check if it's in PATH
which uv  # macOS/Linux
where uv  # Windows

# Restart terminal after installation
```

### Problem: Data not saving

**Solution**: Check file permissions

```bash
# Check if directory is writable
ls -la ~/.personal_assistant

# If needed, fix permissions
chmod 755 ~/.personal_assistant
```

### Problem: Invalid phone number

**Solution**: Use Ukrainian phone format
- Start with `+380` or `0`
- Valid operator codes: 039, 050, 063, 066, 067, 068, 091-099

### Problem: Cannot find contacts/notes

**Solution**: Check data files exist

```bash
# List files
ls -la ~/.personal_assistant

# If empty, data hasn't been saved yet
```

## Getting Help

### In-App Help
```
Enter command: help
```

### View Command Details
Each command shows instructions when you run it.

### Documentation
Full documentation is in the `docs/` folder:
- `IMPLEMENTATION_GUIDE.md` - Development guide
- `CONTACTS_MODULE.md` - Contact management details
- `NOTES_MODULE.md` - Note management details
- `VALIDATION_MODULE.md` - Input validation
- `STORAGE_MODULE.md` - Data persistence
- `CLI_MODULE.md` - User interface
- `INTELLIGENCE_MODULE.md` - Command parsing
- `ARCHITECTURE.md` - System architecture

## Next Steps

1. **Explore features**: Try all commands to see what's available
2. **Import data**: Add your existing contacts
3. **Organize notes**: Create notes with tags for better organization
4. **Set up backups**: Data is automatically backed up, but you can export manually
5. **Customize**: Check `~/.personal_assistant/config.json` for settings

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/personal_assistant

# Run specific test file
uv run pytest tests/test_contacts.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run pylint src/

# Type checking
uv run mypy src/

# Run all quality checks
uv run black src/ tests/ && uv run pylint src/ && uv run mypy src/
```

## Support

For issues or questions:
1. Check documentation in `docs/` folder
2. Review error logs in `~/.personal_assistant/storage.log`
3. Open an issue on GitHub
4. Contact the development team

## License

[Add your license information here]

---

**Ready to get started?** Run `personal-assistant` and type `help` for guidance!

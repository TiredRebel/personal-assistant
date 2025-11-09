# Personal Assistant Project

A Python-based personal assistant application for managing contacts and notes with intelligent command recognition.

## Project Overview

This Personal Assistant helps users:
- 📇 Manage contacts with full information (name, address, phone, email, birthday)
- 📝 Create and organize notes with tags
- 🔍 Search and filter contacts and notes
- 🎂 Track upcoming birthdays
- 🤖 Intelligent command recognition

## Features

### Core Features (Required)
- ✅ Contact Management (add, edit, delete, search)
- ✅ Birthday tracking and reminders
- ✅ Phone number and email validation
- ✅ Note management (add, edit, delete, search)
- ✅ Data persistence (save to disk)

### Additional Features
- ✅ Tag system for notes
- ✅ Tag-based search and sorting
- ✅ Intelligent command parsing
- ✅ Natural language command suggestions

## Project Structure

```
personal-assistant/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── setup.py                          # Package setup
├── docs/
│   ├── IMPLEMENTATION_GUIDE.md       # Step-by-step implementation guide
│   ├── ARCHITECTURE.md               # System architecture
│   ├── CONTACTS_MODULE.md           # Contact management specs
│   ├── NOTES_MODULE.md              # Notes management specs
│   ├── VALIDATION_MODULE.md         # Validation logic specs
│   ├── STORAGE_MODULE.md            # Data persistence specs
│   ├── CLI_MODULE.md                # Command-line interface specs
│   └── INTELLIGENCE_MODULE.md       # Command intelligence specs
├── src/
│   └── personal_assistant/
│       ├── __init__.py
│       ├── main.py                  # Entry point
│       ├── models/
│       │   ├── __init__.py
│       │   ├── contact.py           # Contact model
│       │   └── note.py              # Note model
│       ├── services/
│       │   ├── __init__.py
│       │   ├── contact_service.py   # Contact operations
│       │   ├── note_service.py      # Note operations
│       │   └── command_parser.py    # Command intelligence
│       ├── storage/
│       │   ├── __init__.py
│       │   └── file_storage.py      # Data persistence
│       ├── validators/
│       │   ├── __init__.py
│       │   └── validators.py        # Input validation
│       └── cli/
│           ├── __init__.py
│           └── interface.py         # CLI interface
├── tests/
│   ├── __init__.py
│   ├── test_contacts.py
│   ├── test_notes.py
│   ├── test_validation.py
│   └── test_storage.py
└── data/                            # User data directory (auto-created)
    ├── contacts.json
    └── notes.json
```

## Quick Start

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd personal-assistant

# Setup and install
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Run the assistant
uv run personal-assistant
```

## Development Guidelines

1. **Code Style**: Follow PEP 8
2. **Documentation**: Use docstrings for all classes and methods
3. **Testing**: Write unit tests for all modules
4. **Git Workflow**: Feature branches, PR reviews
5. **GitHub Copilot**: Use the detailed MD specs in `docs/` folder

## Team Members

- [Add team member names and roles]

## License

[Add license information]

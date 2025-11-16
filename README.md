# Personal Assistant Project

A Python-based personal assistant application for managing contacts and notes with intelligent command recognition.

[![Tests](https://img.shields.io/badge/tests-316%20passed-success)](TEST_REPORT.md)
[![Coverage](https://img.shields.io/badge/coverage-81%25-green)](TEST_REPORT.md)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](pyproject.toml)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-black)](pyproject.toml)
[![Type Checked](https://img.shields.io/badge/type%20checked-mypy-blue)](pyproject.toml)

## 🎯 Project Overview

This Personal Assistant helps users:
- 📇 Manage contacts with full information (name, address, phone, email, birthday)
- 📝 Create and organize notes with tags
- 🔍 Search and filter contacts and notes
- 🎂 Track upcoming birthdays
- 💾 Automatic backups and data recovery
- 🤖 Intelligent command recognition

## ✨ Features

### Core Features (Required)
- ✅ Contact Management (add, edit, delete, search)
- ✅ Birthday tracking and reminders
- ✅ Phone number and email validation (Ukrainian format)
- ✅ Note management (add, edit, delete, search)
- ✅ Data persistence with atomic writes
- ✅ Automatic backup system

### Additional Features
- ✅ Tag system for notes
- ✅ Tag-based search and sorting
- ✅ Export/Import functionality
- ✅ Corruption recovery
- ✅ Comprehensive logging
- ✅ CLI interface with arguments

## 🧪 Testing & Quality

### Test Results
```
✅ 316/316 tests passed (100%)
✅ 81% code coverage
✅ 0 type errors (mypy)
✅ 0 style errors (ruff)
✅ All CLI commands working
```

**Детальний звіт:** [TEST_REPORT.md](TEST_REPORT.md)

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
uv pip install -e .

# For colored output (optional)
uv pip install -e ".[colors]"

# For development (includes testing tools)
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

- **Dmytro** (TiredRebel)
- **Oleksandr** (Ponomaleks)
- **Vitalii** (ynot99)
- **Denys** (Bliznyuk)
- **Daniel** (kassimuss)

## License

[Add license information]

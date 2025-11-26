# CLAUDE.MD - AI Assistant Guide

This file provides context for AI assistants (Claude, GitHub Copilot, etc.) working on the Personal Assistant project.

## Project Overview

This is a Python CLI application for managing contacts and notes with intelligent command recognition. The project emphasizes clean architecture, comprehensive testing, and user-friendly command parsing.

## Key Technical Details

- **Language**: Python 3.9+
- **Package Manager**: uv (modern, fast Python package installer)
- **Code Quality Tools**: ruff, mypy, pytest
- **Test Coverage**: 81% (316 tests passing)
- **Line Endings**: LF (enforced via .gitattributes)
- **Code Style**: PEP 8, 100 character line length

## Project Architecture

### Directory Structure
```
src/personal_assistant/
├── models/          # Data models (Contact, Note)
├── services/        # Business logic (ContactService, NoteService)
├── storage/         # Data persistence (FileStorage with atomic writes)
├── validators/      # Input validation (phone, email, birthday)
├── cli/            # Command-line interface and parsing
└── utils/          # Utility functions
```

### Core Components

1. **Models** (`models/`)
   - `Contact`: name, phones, emails, address, birthday
   - `Note`: content, tags, timestamps
   - Both use dataclass pattern

2. **Services** (`services/`)
   - `ContactService`: CRUD operations for contacts
   - `NoteService`: CRUD operations for notes
   - Separation of concerns between business logic and storage

3. **Storage** (`storage/file_storage.py`)
   - Atomic writes to prevent corruption
   - Automatic backups
   - Recovery from corruption
   - JSON-based persistence

4. **CLI** (`cli/`)
   - `interface.py`: Main command loop
   - `command_parser.py`: Command parsing logic
   - `intent_recognizer.py`: Intelligent command recognition
   - `smart_command_parser.py`: Advanced parsing features

5. **Validators** (`validators/validators.py`)
   - Ukrainian phone format: +380XXXXXXXXX or 380XXXXXXXXX
   - Email validation
   - Birthday validation (not in future)

## Development Guidelines

### Code Style
- Follow PEP 8 strictly
- Line length: 100 characters
- Use type hints for all functions
- Docstrings for all public classes and methods
- No unused imports or variables

### Testing
- All new features must have tests
- Maintain >80% code coverage
- Run tests with: `pytest`
- Run with coverage: `pytest --cov`

### Quality Checks
Before committing, ensure:
```bash
ruff check .           # Style checks
mypy src/              # Type checking
pytest                 # All tests pass
```

### Git Workflow
- Feature branches from `main`
- Pull requests required
- CI/CD checks must pass
- LF line endings enforced

## Common Tasks

### Adding a New Feature
1. Read relevant documentation in `docs/` folder
2. Update models if needed
3. Implement service layer logic
4. Add CLI commands in interface
5. Write comprehensive tests
6. Update documentation

### Fixing Bugs
1. Write a failing test that reproduces the bug
2. Fix the issue
3. Ensure test passes
4. Run full test suite
5. Check code quality tools

### Modifying Storage
- Always maintain backward compatibility with existing data files
- Use atomic writes (temp file + rename)
- Test corruption recovery
- Update backup logic if needed

## Important Constraints

### Phone Numbers
- Must match Ukrainian format
- Validation in `validators/validators.py`
- Pattern: `+380XXXXXXXXX` (13 chars including +)

### Birthdays
- Cannot be in the future
- Must be valid date
- Used for "upcoming birthdays" feature

### Data Persistence
- Files: `data/contacts.json`, `data/notes.json`
- Atomic writes only (never partial writes)
- Backups created automatically
- Recovery mechanism for corrupted files

### Command Intelligence
- Fuzzy matching for commands
- Intent recognition for natural language
- Autocomplete support
- See `docs/INTELLIGENCE_MODULE.md` for details

## File Locations Reference

- **Main entry point**: `src/personal_assistant/main.py`
- **Contact operations**: `src/personal_assistant/services/contact_service.py`
- **Note operations**: `src/personal_assistant/services/note_service.py`
- **Storage logic**: `src/personal_assistant/storage/file_storage.py`
- **CLI interface**: `src/personal_assistant/cli/interface.py`
- **Validators**: `src/personal_assistant/validators/validators.py`
- **Tests**: `tests/` directory

## Documentation

Comprehensive documentation is in the `docs/` folder:
- `ARCHITECTURE.md` - System architecture
- `IMPLEMENTATION_GUIDE.md` - Step-by-step guide
- `CONTACTS_MODULE.md` - Contact management specs
- `NOTES_MODULE.md` - Notes management specs
- `VALIDATION_MODULE.md` - Validation logic
- `STORAGE_MODULE.md` - Data persistence specs
- `CLI_MODULE.md` - Command-line interface
- `INTELLIGENCE_MODULE.md` - Command intelligence
- `COPILOT_GUIDE.md` - GitHub Copilot integration
- `UV_GUIDE.md` - uv package manager guide

## Team Context

This is a team project with 5 members:
- Dmytro (TiredRebel)
- Oleksandr (Ponomaleks)
- Vitalii (ynot99)
- Denys (Bliznyuk)
- Daniel (kassimuss)

Collaboration is done via GitHub with feature branches and pull requests.

## Quick Commands

```bash
# Setup
uv venv
uv pip install -e ".[dev]"

# Run application
uv run personal-assistant
# or
uv run pa

# Testing
pytest
pytest --cov
pytest -v

# Quality checks
ruff check .
ruff format .
mypy src/

# Build
python -m build
```

## When Working on This Project

1. Always read the relevant `docs/*.md` file before making changes
2. Maintain the existing architecture patterns
3. Keep test coverage high
4. Follow the established code style
5. Don't break backward compatibility with existing data files
6. Update documentation when adding features
7. Test with actual user workflows

## Notes for AI Assistants

- The project uses modern Python features (dataclasses, type hints)
- Storage layer uses atomic writes - never bypass this
- Command parsing is sophisticated - check existing patterns before adding new commands
- Ukrainian phone format is strict - don't suggest other formats
- Tests are comprehensive - use them as examples for new tests
- The CLI is the primary interface - keep it user-friendly

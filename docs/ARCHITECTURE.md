# System Architecture

## Overview
This document describes the architecture of the Personal Assistant application, including its components, data flow, and design decisions.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                         │
│  (Command-line interface for user interaction)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Command Parser                            │
│  (Intelligent command interpretation & NLP)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│ Contact Service  │          │  Note Service    │
│                  │          │                  │
│ • Add/Edit       │          │ • Add/Edit       │
│ • Search         │          │ • Search         │
│ • Delete         │          │ • Tag Mgmt       │
│ • Birthdays      │          │ • Delete         │
└────────┬─────────┘          └────────┬─────────┘
         │                             │
         ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│ Contact Model    │          │   Note Model     │
│                  │          │                  │
│ • Data structure │          │ • Data structure │
│ • Validation     │          │ • Tag support    │
└────────┬─────────┘          └────────┬─────────┘
         │                             │
         └──────────────┬──────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   Validators     │
              │                  │
              │ • Phone validator│
              │ • Email validator│
              │ • Input sanitize │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  File Storage    │
              │                  │
              │ • JSON files     │
              │ • Atomic writes  │
              │ • Backups        │
              │ • Recovery       │
              └──────────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │   File System    │
              │                  │
              │ ~/.personal_     │
              │   assistant/     │
              └──────────────────┘
```

## Architectural Layers

### 1. Presentation Layer (CLI)
**Responsibility**: User interface and interaction

**Components**:
- `CLI` class: Main command-line interface
- Input handling and display formatting
- Command routing
- User feedback and messages

**Design Decisions**:
- Text-based interface for simplicity and portability
- Optional colored output for better UX
- Interactive prompts for complex operations

### 2. Application Layer (Services)
**Responsibility**: Business logic and orchestration

**Components**:
- `ContactService`: Contact management operations
- `NoteService`: Note management operations
- `CommandParser`: Intelligent command interpretation

**Design Decisions**:
- Service layer separates business logic from UI
- Each service manages its own domain
- Services interact with storage layer only

### 3. Domain Layer (Models)
**Responsibility**: Data structures and domain logic

**Components**:
- `Contact` model: Contact data structure
- `Note` model: Note data structure
- Data validation and business rules

**Design Decisions**:
- Dataclasses for clean, type-safe models
- Models handle their own serialization
- Immutable where appropriate

### 4. Infrastructure Layer (Storage & Validation)
**Responsibility**: Technical concerns and external interactions

**Components**:
- `FileStorage`: Data persistence
- `PhoneValidator`: Phone number validation
- `EmailValidator`: Email validation
- `InputValidator`: General input validation

**Design Decisions**:
- JSON for human-readable storage
- Atomic writes prevent data corruption
- Validators are stateless and reusable

## Data Flow

### Adding a Contact

```
User Input → CLI.add_contact()
    ↓
Validate input (name, phone, email)
    ↓
ContactService.add_contact()
    ↓
Create Contact model
    ↓
Validate business rules
    ↓
Add to contacts list
    ↓
FileStorage.save()
    ↓
Serialize to JSON
    ↓
Write to disk (atomic)
    ↓
Return success to user
```

### Searching Notes by Tag

```
User Input → CLI.search_notes_by_tag()
    ↓
Parse tag input
    ↓
NoteService.search_notes_by_tags()
    ↓
Filter notes by tags
    ↓
Sort by relevance
    ↓
Return results
    ↓
Display in CLI (formatted)
```

## Design Patterns

### 1. Service Layer Pattern
**Purpose**: Separate business logic from presentation

```python
class ContactService:
    def __init__(self, storage):
        self.storage = storage
        self.contacts = []
    
    def add_contact(self, ...):
        # Business logic here
        pass
```

**Benefits**:
- Testable business logic
- Reusable across different UIs
- Clear separation of concerns

### 2. Repository Pattern
**Purpose**: Abstract data access

```python
class FileStorage:
    def save(self, filename, data):
        # Persistence logic
        pass
    
    def load(self, filename):
        # Loading logic
        pass
```

**Benefits**:
- Easy to swap storage implementations
- Centralized data access
- Consistent API

### 3. Strategy Pattern (Validators)
**Purpose**: Encapsulate validation algorithms

```python
class PhoneValidator:
    @staticmethod
    def validate(phone):
        # Validation logic
        pass

class EmailValidator:
    @staticmethod
    def validate(email):
        # Validation logic
        pass
```

**Benefits**:
- Reusable validators
- Easy to add new validation rules
- Testable in isolation

### 4. Command Pattern (CLI)
**Purpose**: Encapsulate operations as commands

```python
commands = {
    'add-contact': self.add_contact,
    'search-contact': self.search_contact,
    # ...
}
```

**Benefits**:
- Extensible command set
- Easy to add new commands
- Supports undo/redo (future)

## Technology Stack

### Core Technologies
- **Python 3.8+**: Main programming language
- **JSON**: Data storage format
- **Standard Library**: Minimal dependencies

### Optional Dependencies
- **colorama**: Colored terminal output
- **python-dateutil**: Advanced date parsing

### Development Tools
- **pytest**: Unit testing
- **black**: Code formatting
- **pylint**: Code linting
- **mypy**: Static type checking

## File Structure

```
personal-assistant/
├── src/personal_assistant/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Application entry point
│   ├── models/                  # Domain models
│   │   ├── contact.py
│   │   └── note.py
│   ├── services/                # Business logic
│   │   ├── contact_service.py
│   │   ├── note_service.py
│   │   └── command_parser.py
│   ├── storage/                 # Data persistence
│   │   └── file_storage.py
│   ├── validators/              # Input validation
│   │   └── validators.py
│   └── cli/                     # User interface
│       └── interface.py
├── tests/                       # Test suite
├── docs/                        # Documentation
└── data/                        # User data (auto-created)
```

## Data Storage

### Storage Location
- **Primary**: `~/.personal_assistant/`
- **Backups**: `~/.personal_assistant/backups/`

### File Format
```json
{
  "contacts": [
    {
      "name": "John Doe",
      "phone": "+380501234567",
      "email": "john@example.com",
      "address": "123 Main St",
      "birthday": "1990-05-15"
    }
  ]
}
```

### Backup Strategy
- Automatic backup before each save
- Keep last 10 backups
- Timestamped backup files
- Restore from backup on corruption

## Security Considerations

### Data Protection
- Files stored in user's home directory
- File permissions: 0600 (user read/write only)
- No sensitive data in logs

### Input Validation
- All user input sanitized
- Phone and email format validation
- SQL injection prevention (N/A for JSON)
- Path traversal prevention

### Error Handling
- Graceful degradation on errors
- No sensitive data in error messages
- Logging for debugging

## Performance Considerations

### Current Scale
- Designed for: 1,000 contacts, 10,000 notes
- Expected response time: <100ms for most operations
- Memory usage: <50MB

### Optimization Strategies
1. **Lazy Loading**: Load data on demand
2. **Indexing**: In-memory indices for fast lookup
3. **Caching**: Cache frequently accessed data
4. **Batch Operations**: Group multiple saves

### Future Scalability
For larger datasets (>10,000 records):
- Consider SQLite instead of JSON
- Implement pagination
- Add full-text search index
- Use database indexing

## Error Recovery

### Corruption Recovery
1. Detect corrupted file
2. Attempt JSON repair
3. Restore from latest backup
4. Try older backups
5. Fail gracefully with empty dataset

### Data Loss Prevention
- Atomic writes (write to temp, then rename)
- Automatic backups
- Validation before save
- Write confirmation

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock dependencies
- Cover edge cases
- Aim for >80% code coverage

### Integration Tests
- Test component interactions
- Use real file system (temp directory)
- Test full workflows

### Manual Testing
- User acceptance testing
- Performance testing
- Usability testing

## Deployment

### Installation
```bash
pip install -r requirements.txt
python -m src.personal_assistant.main
```

### Configuration
- Config file: `~/.personal_assistant/config.json`
- Environment variables: None required
- First-run setup: Auto-creates directories

## Future Architecture Considerations

### Potential Enhancements
1. **Web Interface**: Add Flask/FastAPI web interface
2. **API**: REST API for third-party integrations
3. **Database**: Migrate to SQLite/PostgreSQL
4. **Cloud Sync**: Add cloud backup/sync
5. **Plugins**: Plugin architecture for extensions
6. **Multi-user**: Support multiple user profiles

### Scalability Path
```
Phase 1: JSON files (current)
    ↓
Phase 2: SQLite database (>10K records)
    ↓
Phase 3: PostgreSQL + API (multi-user)
    ↓
Phase 4: Microservices (enterprise)
```

## Monitoring and Logging

### Logging
- Log level: INFO
- Log file: `~/.personal_assistant/storage.log`
- Log rotation: Keep last 7 days
- No sensitive data in logs

### Metrics to Track
- Number of contacts/notes
- Operation success/failure rates
- Average response time
- Storage usage

## Maintenance

### Regular Maintenance
- Clean old backups (auto)
- Compact storage (manual)
- Update dependencies (quarterly)
- Security patches (as needed)

### Troubleshooting
- Check logs for errors
- Verify file permissions
- Test with empty dataset
- Restore from backup if needed

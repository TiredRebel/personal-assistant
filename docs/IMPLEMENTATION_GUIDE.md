# Implementation Guide

This guide provides a step-by-step approach to implementing the Personal Assistant project.

## Phase 1: Foundation (Week 1)

### 1.1 Project Setup
- [ ] Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Create virtual environment: `uv venv`
- [ ] Install dependencies: `uv pip install -e ".[dev]"`
- [ ] Set up project structure
- [ ] Initialize Git repository
- [ ] Configure .gitignore

### 1.2 Data Models
- [ ] Implement `Contact` class (see CONTACTS_MODULE.md)
- [ ] Implement `Note` class (see NOTES_MODULE.md)
- [ ] Create base model utilities
- [ ] Write unit tests for models

## Phase 2: Core Functionality (Week 2)

### 2.1 Validation Module
- [ ] Implement phone number validator (see VALIDATION_MODULE.md)
- [ ] Implement email validator
- [ ] Add validation error handling
- [ ] Write validation tests

### 2.2 Storage Module
- [ ] Implement file-based storage (see STORAGE_MODULE.md)
- [ ] Create data serialization/deserialization
- [ ] Implement auto-save functionality
- [ ] Add error recovery mechanisms
- [ ] Write storage tests

### 2.3 Contact Service
- [ ] Implement add contact functionality
- [ ] Implement search contacts
- [ ] Implement edit contact
- [ ] Implement delete contact
- [ ] Implement birthday reminders
- [ ] Write service tests

### 2.4 Note Service
- [ ] Implement add note functionality
- [ ] Implement search notes
- [ ] Implement edit note
- [ ] Implement delete note
- [ ] Write service tests

## Phase 3: User Interface (Week 3)

### 3.1 CLI Interface
- [ ] Implement command-line interface (see CLI_MODULE.md)
- [ ] Create main menu
- [ ] Implement command routing
- [ ] Add input validation
- [ ] Create help system

### 3.2 User Experience
- [ ] Add colored output (optional)
- [ ] Implement tabular data display
- [ ] Add confirmation prompts
- [ ] Create error messages

## Phase 4: Advanced Features (Week 4)

### 4.1 Tag System
- [ ] Add tag support to Note model
- [ ] Implement tag-based search
- [ ] Implement tag-based sorting
- [ ] Create tag management commands

### 4.2 Command Intelligence
- [ ] Implement fuzzy command matching (see INTELLIGENCE_MODULE.md)
- [ ] Add command suggestions
- [ ] Create natural language parser
- [ ] Implement command autocomplete

## Phase 5: Testing & Polish (Week 5)

### 5.1 Testing
- [ ] Complete unit test coverage (>80%)
- [ ] Write integration tests
- [ ] Perform manual testing
- [ ] Fix bugs

### 5.2 Documentation
- [ ] Complete code documentation
- [ ] Create user manual
- [ ] Add code examples
- [ ] Update README

### 5.3 Deployment
- [ ] Create installation script
- [ ] Package application
- [ ] Test on clean environment
- [ ] Create release

## Development Best Practices

### Code Quality
```python
# Use type hints
def add_contact(name: str, phone: str, email: str) -> Contact:
    """Add a new contact to the address book.

    Args:
        name: Contact's full name
        phone: Phone number (will be validated)
        email: Email address (will be validated)

    Returns:
        Contact: The created contact object

    Raises:
        ValidationError: If phone or email is invalid
    """
    pass
```

### Error Handling
```python
# Always handle expected errors
try:
    contact = add_contact(name, phone, email)
except ValidationError as e:
    print(f"Error: {e}")
    return None
```

### Testing
```python
# Write comprehensive tests
def test_add_contact_valid_data():
    """Test adding a contact with valid data."""
    service = ContactService()
    contact = service.add_contact(
        name="John Doe",
        phone="+380501234567",
        email="john@example.com"
    )
    assert contact.name == "John Doe"
    assert contact.phone == "+380501234567"
```

## GitHub Copilot Tips

### For Better Code Generation

1. **Use descriptive function names**
   ```python
   # Good
   def find_contacts_by_birthday_in_days(days: int) -> List[Contact]:

   # Bad
   def find(d):
   ```

2. **Write detailed docstrings first**
   ```python
   def validate_phone_number(phone: str) -> bool:
       """
       Validate Ukrainian phone number format.

       Accepts formats:
       - +380501234567
       - 0501234567
       - +38 050 123 45 67

       Args:
           phone: Phone number string to validate

       Returns:
           True if valid, False otherwise
       """
       # Copilot will generate appropriate code
   ```

3. **Use type hints everywhere**
   ```python
   from typing import List, Optional, Dict

   def search_contacts(query: str) -> List[Contact]:
       pass
   ```

4. **Write test names that describe behavior**
   ```python
   def test_phone_validation_accepts_ukrainian_format():
       pass

   def test_phone_validation_rejects_invalid_format():
       pass
   ```

## Troubleshooting

### Common Issues

**Issue**: Data not persisting
- Check file permissions in user directory
- Verify JSON serialization works
- Ensure auto-save is called

**Issue**: Validation not working
- Test regex patterns separately
- Check input sanitization
- Verify error messages

**Issue**: Command not recognized
- Check command parser logic
- Verify fuzzy matching threshold
- Test with various inputs

## Resources

- Python Documentation: https://docs.python.org/3/
- JSON Handling: https://docs.python.org/3/library/json.html
- Regular Expressions: https://docs.python.org/3/library/re.html
- Unit Testing: https://docs.python.org/3/library/unittest.html

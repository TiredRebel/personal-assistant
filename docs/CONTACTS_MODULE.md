# Contacts Module Specification

## Overview
The contacts module manages all contact-related operations including storage, retrieval, editing, and deletion of contact information.

## Contact Model

### Class: `Contact`

```python
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Contact:
    """
    Represents a contact in the address book.
    
    Attributes:
        name: Full name of the contact (required)
        phone: Phone number (validated, required)
        email: Email address (validated, optional)
        address: Physical address (optional)
        birthday: Date of birth (optional)
    """
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    birthday: Optional[date] = None
    
    def __post_init__(self):
        """Validate contact data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Contact name cannot be empty")
        if not self.phone:
            raise ValueError("Contact phone cannot be empty")
    
    def to_dict(self) -> dict:
        """
        Convert contact to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the contact
        """
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "birthday": self.birthday.isoformat() if self.birthday else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        """
        Create contact from dictionary (JSON deserialization).
        
        Args:
            data: Dictionary containing contact data
        
        Returns:
            Contact instance
        """
        birthday = None
        if data.get("birthday"):
            birthday = date.fromisoformat(data["birthday"])
        
        return cls(
            name=data["name"],
            phone=data["phone"],
            email=data.get("email"),
            address=data.get("address"),
            birthday=birthday
        )
    
    def days_until_birthday(self) -> Optional[int]:
        """
        Calculate days until next birthday.
        
        Returns:
            Number of days until birthday, or None if birthday not set
        """
        if not self.birthday:
            return None
        
        today = date.today()
        next_birthday = date(today.year, self.birthday.month, self.birthday.day)
        
        # If birthday already passed this year, use next year
        if next_birthday < today:
            next_birthday = date(today.year + 1, self.birthday.month, self.birthday.day)
        
        return (next_birthday - today).days
```

## Contact Service

### Class: `ContactService`

```python
from typing import List, Optional
from datetime import date

class ContactService:
    """
    Service class for managing contacts.
    
    Handles all business logic for contact operations:
    - Adding new contacts
    - Searching contacts
    - Editing contacts
    - Deleting contacts
    - Birthday reminders
    """
    
    def __init__(self, storage):
        """
        Initialize contact service.
        
        Args:
            storage: Storage instance for data persistence
        """
        self.storage = storage
        self.contacts: List[Contact] = []
        self.load_contacts()
    
    def load_contacts(self):
        """Load contacts from storage."""
        # Implementation: Load from storage.load("contacts")
        pass
    
    def save_contacts(self):
        """Save contacts to storage."""
        # Implementation: Save to storage.save("contacts", contacts)
        pass
    
    def add_contact(self, name: str, phone: str, email: Optional[str] = None,
                   address: Optional[str] = None, birthday: Optional[date] = None) -> Contact:
        """
        Add a new contact to the address book.
        
        Args:
            name: Contact's full name
            phone: Phone number (will be validated)
            email: Email address (will be validated, optional)
            address: Physical address (optional)
            birthday: Date of birth (optional)
        
        Returns:
            The created Contact object
        
        Raises:
            ValidationError: If phone or email format is invalid
            ValueError: If contact with same name already exists
        """
        # Implementation steps:
        # 1. Validate phone number using validator
        # 2. Validate email if provided
        # 3. Check if contact with same name exists
        # 4. Create new Contact instance
        # 5. Add to self.contacts list
        # 6. Save to storage
        # 7. Return created contact
        pass
    
    def search_contacts(self, query: str) -> List[Contact]:
        """
        Search contacts by name, phone, or email.
        
        Performs case-insensitive partial matching across:
        - Contact name
        - Phone number
        - Email address
        
        Args:
            query: Search query string
        
        Returns:
            List of matching contacts
        """
        # Implementation:
        # 1. Convert query to lowercase
        # 2. Filter contacts where query matches name, phone, or email
        # 3. Return matching contacts
        pass
    
    def get_contact_by_name(self, name: str) -> Optional[Contact]:
        """
        Find a contact by exact name match.
        
        Args:
            name: Contact name to search for
        
        Returns:
            Contact if found, None otherwise
        """
        # Implementation: Search for exact name match (case-insensitive)
        pass
    
    def edit_contact(self, old_name: str, name: Optional[str] = None,
                    phone: Optional[str] = None, email: Optional[str] = None,
                    address: Optional[str] = None, birthday: Optional[date] = None) -> Contact:
        """
        Edit an existing contact.
        
        Args:
            old_name: Current name of the contact to edit
            name: New name (optional, keeps old if None)
            phone: New phone (optional, keeps old if None)
            email: New email (optional, keeps old if None)
            address: New address (optional, keeps old if None)
            birthday: New birthday (optional, keeps old if None)
        
        Returns:
            The updated Contact object
        
        Raises:
            ValueError: If contact not found
            ValidationError: If new phone or email is invalid
        """
        # Implementation:
        # 1. Find contact by old_name
        # 2. Validate new phone/email if provided
        # 3. Update contact fields
        # 4. Save to storage
        # 5. Return updated contact
        pass
    
    def delete_contact(self, name: str) -> bool:
        """
        Delete a contact by name.
        
        Args:
            name: Name of contact to delete
        
        Returns:
            True if contact was deleted, False if not found
        """
        # Implementation:
        # 1. Find contact by name
        # 2. Remove from self.contacts list
        # 3. Save to storage
        # 4. Return True/False
        pass
    
    def get_upcoming_birthdays(self, days: int) -> List[Contact]:
        """
        Get contacts with birthdays in the next N days.
        
        Args:
            days: Number of days to look ahead
        
        Returns:
            List of contacts with upcoming birthdays, sorted by days until birthday
        """
        # Implementation:
        # 1. Filter contacts that have birthday set
        # 2. Calculate days_until_birthday for each
        # 3. Filter where days_until_birthday <= days
        # 4. Sort by days_until_birthday
        # 5. Return sorted list
        pass
    
    def get_all_contacts(self) -> List[Contact]:
        """
        Get all contacts.
        
        Returns:
            List of all contacts
        """
        return self.contacts.copy()
    
    def get_contacts_count(self) -> int:
        """
        Get total number of contacts.
        
        Returns:
            Number of contacts in address book
        """
        return len(self.contacts)
```

## Usage Examples

### Adding a Contact

```python
from datetime import date

# Initialize service
service = ContactService(storage)

# Add contact with all fields
contact = service.add_contact(
    name="John Doe",
    phone="+380501234567",
    email="john.doe@example.com",
    address="123 Main St, Kyiv",
    birthday=date(1990, 5, 15)
)

# Add contact with minimal fields
contact = service.add_contact(
    name="Jane Smith",
    phone="0671234567"
)
```

### Searching Contacts

```python
# Search by name
results = service.search_contacts("John")

# Search by phone
results = service.search_contacts("050")

# Search by email
results = service.search_contacts("@example.com")
```

### Editing a Contact

```python
# Edit phone number only
contact = service.edit_contact(
    old_name="John Doe",
    phone="+380509999999"
)

# Edit multiple fields
contact = service.edit_contact(
    old_name="John Doe",
    name="John Smith",
    email="john.smith@example.com",
    address="456 Oak Ave, Kyiv"
)
```

### Birthday Reminders

```python
# Get contacts with birthdays in next 7 days
upcoming = service.get_upcoming_birthdays(7)

for contact in upcoming:
    days = contact.days_until_birthday()
    print(f"{contact.name}'s birthday is in {days} days!")
```

### Deleting a Contact

```python
# Delete contact
success = service.delete_contact("John Doe")
if success:
    print("Contact deleted successfully")
else:
    print("Contact not found")
```

## Testing Requirements

### Unit Tests to Implement

1. **Model Tests** (`test_contact_model.py`)
   ```python
   def test_contact_creation_with_all_fields():
       """Test creating contact with all fields populated."""
       pass
   
   def test_contact_creation_minimal_fields():
       """Test creating contact with only required fields."""
       pass
   
   def test_contact_to_dict():
       """Test contact serialization to dictionary."""
       pass
   
   def test_contact_from_dict():
       """Test contact deserialization from dictionary."""
       pass
   
   def test_days_until_birthday_calculation():
       """Test birthday countdown calculation."""
       pass
   
   def test_contact_validation_empty_name():
       """Test that empty name raises ValueError."""
       pass
   ```

2. **Service Tests** (`test_contact_service.py`)
   ```python
   def test_add_contact_valid_data():
       """Test adding contact with valid data."""
       pass
   
   def test_add_contact_invalid_phone():
       """Test that invalid phone raises ValidationError."""
       pass
   
   def test_add_contact_duplicate_name():
       """Test that duplicate name raises ValueError."""
       pass
   
   def test_search_contacts_by_name():
       """Test searching contacts by name."""
       pass
   
   def test_search_contacts_case_insensitive():
       """Test that search is case-insensitive."""
       pass
   
   def test_edit_contact_success():
       """Test editing existing contact."""
       pass
   
   def test_edit_contact_not_found():
       """Test editing non-existent contact raises error."""
       pass
   
   def test_delete_contact_success():
       """Test deleting existing contact."""
       pass
   
   def test_get_upcoming_birthdays():
       """Test getting contacts with upcoming birthdays."""
       pass
   ```

## Error Handling

### Custom Exceptions

```python
class ContactError(Exception):
    """Base exception for contact-related errors."""
    pass

class ContactNotFoundError(ContactError):
    """Raised when contact is not found."""
    pass

class DuplicateContactError(ContactError):
    """Raised when attempting to add duplicate contact."""
    pass
```

### Error Handling Examples

```python
try:
    contact = service.add_contact("John Doe", "invalid-phone")
except ValidationError as e:
    print(f"Validation error: {e}")

try:
    contact = service.get_contact_by_name("Unknown")
    if not contact:
        raise ContactNotFoundError("Contact not found")
except ContactNotFoundError as e:
    print(f"Error: {e}")
```

## Performance Considerations

- Use list comprehension for searching (efficient for small datasets)
- Consider indexing by name for larger datasets
- Implement caching for frequently accessed contacts
- Batch save operations to reduce I/O

## Future Enhancements

- Support for multiple phone numbers per contact
- Contact groups/categories
- Import/export contacts (vCard format)
- Contact photos
- Custom fields
- Contact history/audit log

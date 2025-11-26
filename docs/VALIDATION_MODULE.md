# Validation Module Specification

## Overview
The validation module provides input validation for phone numbers, email addresses, and other user inputs to ensure data quality and consistency.

## Phone Number Validation

### Requirements
- Support Ukrainian phone number formats
- Accept international format with country code (+380)
- Accept national format (0XX...)
- Allow spaces and hyphens for readability
- Validate correct length and format

### Supported Formats

```python
"""
Supported phone number formats:

1. International format:
   +380501234567
   +380 50 123 45 67
   +380-50-123-45-67

2. National format:
   0501234567
   050 123 45 67
   050-123-45-67

3. Ukrainian mobile operators:
   039, 050, 063, 066, 067, 068, 091, 092, 093, 094, 095, 096, 097, 098, 099

Note: Only mobile numbers are supported (no landlines)
"""
```

### Implementation: `PhoneValidator`

```python
import re
from typing import Tuple

class PhoneValidator:
    """
    Validates and normalizes Ukrainian phone numbers.
    """

    # Ukrainian mobile operator codes
    MOBILE_CODES = [
        '039', '050', '063', '066', '067', '068',
        '091', '092', '093', '094', '095', '096', '097', '098', '099'
    ]

    @staticmethod
    def validate(phone: str) -> Tuple[bool, str]:
        """
        Validate a phone number.

        Args:
            phone: Phone number to validate

        Returns:
            Tuple of (is_valid, error_message)
            If valid: (True, "")
            If invalid: (False, "error description")
        """
        # Implementation:
        # 1. Remove all spaces and hyphens
        # 2. Check if starts with +380 or 0
        # 3. Validate length (10 digits for national, 12 for international)
        # 4. Check if operator code is valid
        # 5. Return validation result
        pass

    @staticmethod
    def normalize(phone: str) -> str:
        """
        Normalize phone number to international format.

        Converts all valid formats to +380XXXXXXXXX

        Args:
            phone: Phone number to normalize

        Returns:
            Normalized phone number

        Raises:
            ValidationError: If phone number is invalid
        """
        # Implementation:
        # 1. Validate phone number first
        # 2. Remove all non-digit characters except leading +
        # 3. Convert to international format
        # 4. Return normalized phone
        pass

    @staticmethod
    def format_display(phone: str) -> str:
        """
        Format phone number for display.

        Converts +380501234567 to +380 50 123 45 67

        Args:
            phone: Normalized phone number

        Returns:
            Formatted phone number for display
        """
        # Implementation:
        # Format as: +380 XX XXX XX XX
        pass

    @classmethod
    def is_valid_operator_code(cls, code: str) -> bool:
        """
        Check if operator code is valid.

        Args:
            code: Three-digit operator code

        Returns:
            True if valid Ukrainian mobile operator
        """
        return code in cls.MOBILE_CODES


# Example implementation details
def validate_phone_implementation(phone: str) -> Tuple[bool, str]:
    """
    Detailed validation logic for phone numbers.

    Steps:
    1. Clean input (remove spaces, hyphens)
    2. Handle international format (+380)
    3. Handle national format (0XX)
    4. Validate length
    5. Validate operator code
    6. Return result
    """
    # Remove spaces and hyphens
    cleaned = re.sub(r'[\s\-]', '', phone)

    # Check if empty
    if not cleaned:
        return False, "Phone number cannot be empty"

    # Handle international format
    if cleaned.startswith('+380'):
        if len(cleaned) != 13:  # +380 + 9 digits
            return False, "International format should be +380XXXXXXXXX (12 digits after +380)"
        operator_code = cleaned[4:7]
        if not PhoneValidator.is_valid_operator_code(operator_code):
            return False, f"Invalid operator code: {operator_code}"
        return True, ""

    # Handle national format
    elif cleaned.startswith('0'):
        if len(cleaned) != 10:  # 0 + 9 digits
            return False, "National format should be 0XXXXXXXXX (10 digits total)"
        operator_code = cleaned[1:4]
        if not PhoneValidator.is_valid_operator_code(operator_code):
            return False, f"Invalid operator code: {operator_code}"
        return True, ""

    else:
        return False, "Phone number must start with +380 or 0"
```

## Email Validation

### Requirements
- Validate standard email format (user@domain.ext)
- Check for common typos
- Support international domain names
- Validate TLD (top-level domain)

### Implementation: `EmailValidator`

```python
import re
from typing import Tuple

class EmailValidator:
    """
    Validates email addresses.
    """

    # Regular expression for email validation
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    @staticmethod
    def validate(email: str) -> Tuple[bool, str]:
        """
        Validate an email address.

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Implementation:
        # 1. Check if empty
        # 2. Basic format validation (user@domain.ext)
        # 3. Check for common typos (@gmali.com, @yaho.com)
        # 4. Validate TLD length
        # 5. Return validation result
        pass

    @staticmethod
    def normalize(email: str) -> str:
        """
        Normalize email address (lowercase, trim).

        Args:
            email: Email address to normalize

        Returns:
            Normalized email address
        """
        return email.strip().lower()

    @staticmethod
    def check_common_typos(email: str) -> list:
        """
        Check for common email typos.

        Args:
            email: Email address to check

        Returns:
            List of suggested corrections
        """
        # Common typos mapping
        typos = {
            'gmali.com': 'gmail.com',
            'gmai.com': 'gmail.com',
            'yaho.com': 'yahoo.com',
            'yahooo.com': 'yahoo.com',
            'hotmali.com': 'hotmail.com',
            'outlok.com': 'outlook.com'
        }

        # Check domain against typos
        suggestions = []
        domain = email.split('@')[1] if '@' in email else ''

        for typo, correction in typos.items():
            if domain == typo:
                suggestions.append(email.replace(typo, correction))

        return suggestions


# Example implementation details
def validate_email_implementation(email: str) -> Tuple[bool, str]:
    """
    Detailed validation logic for email addresses.

    Steps:
    1. Check if empty
    2. Normalize (trim, lowercase)
    3. Basic format validation
    4. Check for @ symbol
    5. Validate domain and TLD
    6. Check for common typos
    """
    # Check if empty
    if not email or not email.strip():
        return False, "Email address cannot be empty"

    # Normalize
    email = email.strip().lower()

    # Check for @ symbol
    if '@' not in email:
        return False, "Email must contain @ symbol"

    # Split into local and domain parts
    parts = email.split('@')
    if len(parts) != 2:
        return False, "Email must have exactly one @ symbol"

    local, domain = parts

    # Validate local part
    if not local:
        return False, "Email local part cannot be empty"

    if len(local) > 64:
        return False, "Email local part too long (max 64 characters)"

    # Validate domain
    if not domain:
        return False, "Email domain cannot be empty"

    if '.' not in domain:
        return False, "Email domain must contain at least one dot"

    # Check TLD
    tld = domain.split('.')[-1]
    if len(tld) < 2:
        return False, "Top-level domain must be at least 2 characters"

    # Use regex for final validation
    if not EmailValidator.EMAIL_REGEX.match(email):
        return False, "Invalid email format"

    # Check for common typos
    suggestions = EmailValidator.check_common_typos(email)
    if suggestions:
        return False, f"Possible typo. Did you mean: {suggestions[0]}?"

    return True, ""
```

## General Input Validation

### Implementation: `InputValidator`

```python
class InputValidator:
    """
    General input validation utilities.
    """

    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """
        Validate contact/person name.

        Requirements:
        - Not empty
        - 2-100 characters
        - Only letters, spaces, hyphens, apostrophes

        Args:
            name: Name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Implementation:
        # 1. Check if empty
        # 2. Check length (2-100 chars)
        # 3. Check allowed characters
        pass

    @staticmethod
    def validate_text_content(text: str, min_length: int = 1,
                            max_length: int = 10000) -> Tuple[bool, str]:
        """
        Validate text content (notes, addresses, etc.).

        Args:
            text: Text to validate
            min_length: Minimum length
            max_length: Maximum length

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Implementation:
        # 1. Check if empty (if min_length > 0)
        # 2. Check length constraints
        pass

    @staticmethod
    def validate_tag(tag: str) -> Tuple[bool, str]:
        """
        Validate a tag/keyword.

        Requirements:
        - Not empty
        - 2-30 characters
        - Only alphanumeric and hyphens
        - No spaces

        Args:
            tag: Tag to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Implementation:
        # 1. Check if empty
        # 2. Check length
        # 3. Check allowed characters (alphanumeric + hyphen)
        pass

    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize user input (trim, remove dangerous characters).

        Args:
            text: Input text to sanitize

        Returns:
            Sanitized text
        """
        # Remove leading/trailing whitespace
        text = text.strip()

        # Remove null bytes
        text = text.replace('\0', '')

        # Normalize whitespace
        text = ' '.join(text.split())

        return text
```

## Validation Exceptions

```python
class ValidationError(Exception):
    """
    Base exception for validation errors.

    Attributes:
        message: Error message
        field: Name of field that failed validation
        value: Invalid value that was provided
    """

    def __init__(self, message: str, field: str = None, value: str = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)

    def __str__(self):
        if self.field:
            return f"Validation error for '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class PhoneValidationError(ValidationError):
    """Raised when phone number validation fails."""
    pass


class EmailValidationError(ValidationError):
    """Raised when email validation fails."""
    pass
```

## Usage Examples

### Phone Number Validation

```python
# Validate phone number
is_valid, error = PhoneValidator.validate("+380501234567")
if is_valid:
    normalized = PhoneValidator.normalize("+380501234567")
    print(f"Valid phone: {normalized}")
    display = PhoneValidator.format_display(normalized)
    print(f"Display format: {display}")
else:
    print(f"Invalid phone: {error}")

# Handle different formats
phones = [
    "+380501234567",      # Valid
    "0501234567",         # Valid
    "+380 50 123 45 67",  # Valid
    "050-123-45-67",      # Valid
    "+380123456789",      # Invalid (wrong operator)
    "12345",              # Invalid (too short)
]

for phone in phones:
    is_valid, error = PhoneValidator.validate(phone)
    print(f"{phone}: {'✓' if is_valid else '✗ ' + error}")
```

### Email Validation

```python
# Validate email
is_valid, error = EmailValidator.validate("user@example.com")
if is_valid:
    normalized = EmailValidator.normalize("User@Example.COM")
    print(f"Valid email: {normalized}")
else:
    print(f"Invalid email: {error}")

# Check for typos
email = "user@gmali.com"
is_valid, error = EmailValidator.validate(email)
if not is_valid:
    suggestions = EmailValidator.check_common_typos(email)
    if suggestions:
        print(f"Did you mean: {suggestions[0]}?")
```

### Using with Contact Creation

```python
def create_contact_with_validation(name: str, phone: str, email: str = None):
    """Create contact with input validation."""

    # Validate name
    is_valid, error = InputValidator.validate_name(name)
    if not is_valid:
        raise ValidationError(error, field="name", value=name)

    # Validate and normalize phone
    is_valid, error = PhoneValidator.validate(phone)
    if not is_valid:
        raise PhoneValidationError(error, field="phone", value=phone)
    phone = PhoneValidator.normalize(phone)

    # Validate and normalize email (if provided)
    if email:
        is_valid, error = EmailValidator.validate(email)
        if not is_valid:
            raise EmailValidationError(error, field="email", value=email)
        email = EmailValidator.normalize(email)

    # Create contact
    contact = Contact(name=name, phone=phone, email=email)
    return contact
```

## Testing Requirements

### Unit Tests

```python
def test_phone_validation_international_format():
    """Test phone validation with international format."""
    assert PhoneValidator.validate("+380501234567")[0] is True

def test_phone_validation_national_format():
    """Test phone validation with national format."""
    assert PhoneValidator.validate("0501234567")[0] is True

def test_phone_validation_with_spaces():
    """Test phone validation with spaces."""
    assert PhoneValidator.validate("+380 50 123 45 67")[0] is True

def test_phone_validation_invalid_operator():
    """Test phone validation rejects invalid operator code."""
    is_valid, error = PhoneValidator.validate("+380111234567")
    assert is_valid is False
    assert "operator" in error.lower()

def test_phone_normalization():
    """Test phone number normalization."""
    assert PhoneValidator.normalize("0501234567") == "+380501234567"
    assert PhoneValidator.normalize("+380 50 123 45 67") == "+380501234567"

def test_email_validation_valid():
    """Test email validation with valid email."""
    assert EmailValidator.validate("user@example.com")[0] is True

def test_email_validation_no_at():
    """Test email validation rejects email without @."""
    is_valid, error = EmailValidator.validate("userexample.com")
    assert is_valid is False

def test_email_validation_typo_detection():
    """Test email typo detection."""
    is_valid, error = EmailValidator.validate("user@gmali.com")
    assert is_valid is False
    assert "gmail.com" in error

def test_email_normalization():
    """Test email normalization."""
    assert EmailValidator.normalize("User@Example.COM") == "user@example.com"

def test_name_validation():
    """Test name validation."""
    assert InputValidator.validate_name("John Doe")[0] is True
    assert InputValidator.validate_name("Mary-Ann O'Connor")[0] is True
    assert InputValidator.validate_name("")[0] is False

def test_tag_validation():
    """Test tag validation."""
    assert InputValidator.validate_tag("python")[0] is True
    assert InputValidator.validate_tag("web-dev")[0] is True
    assert InputValidator.validate_tag("has spaces")[0] is False
```

## Best Practices

1. **Always validate before storing**: Validate all input before creating or updating records
2. **Normalize consistently**: Use normalization functions to ensure data consistency
3. **Provide helpful error messages**: Tell users exactly what's wrong and how to fix it
4. **Use exceptions for validation failures**: Make validation errors easy to catch and handle
5. **Test edge cases**: Test empty strings, special characters, very long inputs, etc.

## Future Enhancements

- Support for more international phone formats
- Email deliverability checking (DNS lookup)
- Address validation using geocoding APIs
- Custom validation rules per field
- Batch validation for imports
- Validation rule configuration file

import re
from typing import Tuple, Optional


class PhoneValidator:
    """
    Validates and normalizes Ukrainian phone numbers.
    """

    # Ukrainian mobile operator codes
    MOBILE_CODES = {
        "039",
        "050",
        "063",
        "066",
        "067",
        "068",
        "091",
        "092",
        "093",
        "094",
        "095",
        "096",
        "097",
        "098",
        "099",
    }

    # Pattern to extract digits (removes all non-digit characters)
    # Used to clean phone input before validation
    _DIGIT_PATTERN = re.compile(r"\D")

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
        if phone is None:
            return False, "Phone number cannot be empty"

        raw = str(phone).strip()
        if not raw:
            return False, "Phone number cannot be empty"

        # preserve leading +, remove other non-digit characters
        if raw.startswith("+"):
            cleaned = "+" + PhoneValidator._DIGIT_PATTERN.sub("", raw[1:])
        else:
            cleaned = PhoneValidator._DIGIT_PATTERN.sub("", raw)

        # International format: +380 followed by 9 digits -> total length 13
        if cleaned.startswith("+380"):
            if len(cleaned) != 13:
                return False, "International format should be +380XXXXXXXXX (9 digits after +380)"
            # operator in national form is '0' + first two digits after +380
            op_code = "0" + cleaned[4:6]
            if not PhoneValidator.is_valid_operator_code(op_code):
                return False, f"Invalid operator code: {op_code}"
            return True, ""

        # National format: starts with 0 and total length 10 (0 + 9 digits)
        if cleaned.startswith("0"):
            if len(cleaned) != 10:
                return False, "National format should be 0XXXXXXXXX (10 digits total)"
            op_code = cleaned[:3]  # e.g. "050"
            if not PhoneValidator.is_valid_operator_code(op_code):
                return False, f"Invalid operator code: {op_code}"
            return True, ""

        return False, "Phone number must start with +380 or 0"

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
            PhoneValidationError: If phone number is invalid
        """
        ok, err = PhoneValidator.validate(phone)
        if not ok:
            raise PhoneValidationError(err, value=phone)

        raw = str(phone).strip()
        # preserve leading +, remove other non-digit characters
        if raw.startswith("+"):
            cleaned = "+" + PhoneValidator._DIGIT_PATTERN.sub("", raw[1:])
        else:
            cleaned = PhoneValidator._DIGIT_PATTERN.sub("", raw)

        # If national format (starts with 0 and len 10) -> +380 + cleaned[1:]
        if cleaned.startswith("0") and len(cleaned) == 10:
            return "+380" + cleaned[1:]

        # If already international and valid
        if cleaned.startswith("+380") and len(cleaned) == 13:
            return cleaned

        # Fallback (shouldn't happen due to validation)
        raise PhoneValidationError("Unable to normalize phone number", value=phone)

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
        d = phone[4:]  # '501234567'
        # groups: 2,3,2,2 -> '50' '123' '45' '67'
        return f"+380 {d[0:2]} {d[2:5]} {d[5:7]} {d[7:9]}"

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


"""
## Email Validation

### Requirements
- Validate standard email format (user@domain.ext)
- Check for common typos
- Support international domain names
- Validate TLD (top-level domain)
"""


class EmailValidator:
    """
    Validates email addresses.
    """

    # Regular expression for email validation: user@domain.ext format
    _EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    @staticmethod
    def validate(email: str) -> Tuple[bool, str]:
        """
        Validate an email address.

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if empty
        if email is None:
            return False, "Email cannot be empty"

        normalized = EmailValidator.normalize(email)
        if not normalized:
            return False, "Email cannot be empty"

        # Split into local and domain parts
        parts = normalized.split("@")
        if len(parts) != 2:
            return False, "Email must have exactly one @ symbol"

        local, domain = parts

        # Validate user part
        if not local or len(local) > 64:
            return False, "Email local part cannot be empty or exceed 64 characters"

        # Validate domain and TLD
        if not domain:
            return False, "Email domain cannot be empty"

        if "." not in domain:
            return False, "Email domain must contain a dot (.)"

        parts = domain.split(".")
        tld = parts[-1]

        # Validate TLD length (2-6 characters is standard)
        if len(tld) < 2:
            return False, "Top-level domain must be at least 2 characters"

        # Use regex for final validation
        if not EmailValidator._EMAIL_PATTERN.match(normalized):
            return False, "Invalid email format. Expected format: user@domain.ext"

        # Check for common typos
        typo_suggestions = EmailValidator.check_common_typos(normalized)
        if typo_suggestions:
            return False, f"Email domain may contain typo. Did you mean: {typo_suggestions[0]}?"

        # All checks passed
        return True, ""

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
            "gmali.com": "gmail.com",
            "gmai.com": "gmail.com",
            "yaho.com": "yahoo.com",
            "yahooo.com": "yahoo.com",
            "hotmali.com": "hotmail.com",
            "outlok.com": "outlook.com",
        }

        # Check domain against typos
        suggestions = []
        domain = email.split("@")[1] if "@" in email else ""

        for typo, correction in typos.items():
            if domain == typo:
                suggestions.append(email.replace(typo, correction))

        return suggestions


class InputValidator:
    """
    General input validation utilities.
    """

    # Name pattern: letters (Latin + Cyrillic), spaces, hyphens, apostrophes
    # Examples: "John Doe", "Mary-Ann O'Connor", "Іван Петренко"
    _NAME_PATTERN = re.compile(r"^[a-zA-Zа-яА-ЯіїєґІЇЄҐ\s\-']+$")

    # Tag pattern: alphanumeric and hyphens only, no spaces
    # Examples: "python", "web-dev", "machine-learning"
    _TAG_PATTERN = re.compile(r"^[a-zA-Z0-9\-]+$")

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
        # Check if empty
        if name is None:
            return False, "Name cannot be empty"

        name_str = str(name).strip()
        if not name_str:
            return False, "Name cannot be empty"

        # Check length (2-100 chars)
        if len(name_str) < 2:
            return False, "Name must be at least 2 characters"
        if len(name_str) > 100:
            return False, "Name must not exceed 100 characters"

        # Check allowed characters (letters, spaces, hyphens, apostrophes)
        if not re.match(InputValidator._NAME_PATTERN, name_str):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"

        return True, ""

    @staticmethod
    def validate_text_content(
        text: str, min_length: int = 1, max_length: int = 10000
    ) -> Tuple[bool, str]:
        """
        Validate text content (notes, addresses, etc.).

        Args:
            text: Text to validate
            min_length: Minimum length
            max_length: Maximum length

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if empty (if min_length > 0)
        if text is None:
            return False, "Text cannot be empty"

        text_str = str(text).strip()
        if min_length > 0 and not text_str:
            return False, f"Text cannot be empty (minimum {min_length} characters)"

        # Check length constraints
        if len(text_str) < min_length:
            return (
                False,
                f"Text must be at least {min_length} characters (current: {len(text_str)})",
            )
        if len(text_str) > max_length:
            return False, f"Text must not exceed {max_length} characters (current: {len(text_str)})"

        return True, ""

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
        # Check if empty
        if tag is None:
            return False, "Tag cannot be empty"

        tag_str = str(tag).strip()
        if not tag_str:
            return False, "Tag cannot be empty"

        # Check length (2-30 chars)
        if len(tag_str) < 2:
            return False, "Tag must be at least 2 characters"
        if len(tag_str) > 30:
            return False, "Tag must not exceed 30 characters"

        # Check for spaces
        if " " in tag_str:
            return False, "Tag cannot contain spaces"

        if not re.match(InputValidator._TAG_PATTERN, tag_str):
            return False, "Tag can only contain letters, numbers, and hyphens"

        return True, ""

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
        text = text.replace("\0", "")

        # Normalize whitespace
        text = " ".join(text.split())

        return text


class ValidationError(Exception):
    """
    Base exception for validation errors.

    Attributes:
        message: Error message
        field: Name of field that failed validation
        value: Invalid value that was provided (not exposed in logs)
    """

    def __init__(self, message: str, field: Optional[str] = None, value: Optional[str] = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.field:
            return f"Validation error for '{self.field}': {self.message}"
        return f"Validation error: {self.message}"

    def to_dict(self) -> dict:
        """
        Return a dictionary suitable for logging / API responses.
        Note: 'value' is intentionally excluded to avoid exposing private data.

        Returns:
            Dictionary with keys: {"error": message, "field": field}
        """
        return {"error": self.message, "field": self.field}


class PhoneValidationError(ValidationError):
    """Raised when phone number validation fails."""

    def __init__(self, message: str, value: Optional[str] = None):
        # field is predefined for this subclass
        super().__init__(message, field="phone", value=value)


class EmailValidationError(ValidationError):
    """Raised when email validation fails."""

    def __init__(self, message: str, value: Optional[str] = None):
        # field is predefined for this subclass
        super().__init__(message, field="email", value=value)

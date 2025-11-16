"""
Unit tests for Validation models

These tests verify the validation functionality.
Run with: pytest tests/test_validation.py
"""

import pytest

from personal_assistant.validators import (
    PhoneValidationError,
    PhoneValidator,
    EmailValidator,
    InputValidator,
)


class TestPhoneValidator:
    """Test suite for PhoneValidator."""

    @pytest.mark.parametrize(
        "phone, expected_validity",
        [
            ("+380501234567", True),
            ("0501234567", True),
            ("+1-800-555-1234", False),
            ("12345", False),
            ("+38050ABCDEF", False),
            ("", False),
        ],
    )
    def test_phone_validation(self, phone: str, expected_validity: bool) -> None:
        """Test phone number validation."""
        is_valid, _ = PhoneValidator.validate(phone)
        assert is_valid == expected_validity

    def test_phone_validation_international_format(self):
        """Test phone validation with international format."""
        assert PhoneValidator.validate("+380501234567")[0] is True

    def test_phone_validation_national_format(self):
        """Test phone validation with national format."""
        assert PhoneValidator.validate("0501234567")[0] is True

    def test_phone_validation_with_spaces(self):
        """Test phone validation with spaces."""
        assert PhoneValidator.validate("+380 50 123 45 67")[0] is True

    def test_phone_validation_invalid_operator(self):
        """Test phone validation rejects invalid operator code."""
        is_valid, error = PhoneValidator.validate("+380111234567")
        assert is_valid is False
        assert "operator" in error.lower()

    def test_phone_normalization(self):
        """Test phone number normalization."""
        assert PhoneValidator.normalize("0501234567") == "+380501234567"
        assert PhoneValidator.normalize("+380 50 123 45 67") == "+380501234567"

    def test_normalize_invalid_phone_raises(self):
        with pytest.raises(PhoneValidationError) as excinfo:
            PhoneValidator.normalize("+380111234567")
        assert "operator" in str(excinfo.value).lower()

    def test_normalize_invalid_phone_catch(self):
        try:
            PhoneValidator.normalize("+380111234567")
            pytest.fail("Expected PhoneValidationError")
        except PhoneValidationError as e:
            assert "operator" in str(e).lower()

    def test_phone_none_validation(self):
        """Test that None phone is invalid."""
        is_valid, error = PhoneValidator.validate(None)  # pyright: ignore[reportArgumentType]
        assert is_valid is False


class TestEmailValidator:
    """Test suite for EmailValidator."""

    def test_email_validation_valid(self):
        assert EmailValidator.validate("user@example.com")[0] is True

    def test_email_validation_no_at(self):
        """Test email validation rejects email without @."""
        is_valid, error = EmailValidator.validate("userexample.com")
        assert is_valid is False

    def test_email_validation_typo_detection(self):
        """Test email typo detection."""
        is_valid, error = EmailValidator.validate("user@gmali.com")
        assert is_valid is False
        assert "gmail.com" in error

    def test_email_normalization(self):
        """Test email normalization."""
        assert EmailValidator.normalize("User@Example.COM") == "user@example.com"

    def test_email_validation_empty(self):
        """Test email validation rejects empty email."""
        is_valid, error = EmailValidator.validate("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_email_validation_invalid_format(self):
        """Test email validation rejects invalid format."""
        is_valid, error = EmailValidator.validate("user@.com")
        assert is_valid is False
        assert "invalid" in error.lower()

    def test_email_validation_multiple_at(self):
        """Test email validation rejects email with multiple @."""
        is_valid, error = EmailValidator.validate("user@@example.com")
        assert is_valid is False
        assert "@" in error.lower()


class TestInputValidator:
    """Test suite for InputValidator."""

    def test_input_validate_name_non_empty_string(self):
        """Test that non-empty string is valid."""
        is_valid, error = InputValidator.validate_name("Valid Input")
        assert is_valid is True

    def test_input_validate_name_empty_string(self):
        """Test that empty string is invalid."""
        is_valid, error = InputValidator.validate_name("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_input_validate_name_none(self):
        """Test that None input is invalid."""
        is_valid, error = InputValidator.validate_name(None)  # pyright: ignore[reportArgumentType]
        assert is_valid is False
        assert "empty" in error.lower()

    def test_input_validate_name_whitespace(self):
        """Test that whitespace-only string is invalid."""
        is_valid, error = InputValidator.validate_name("   ")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_input_validate_name_numeric(self):
        """Test that numeric input is invalid."""
        is_valid, error = InputValidator.validate_name("12345")
        assert is_valid is False
        assert "contain" in error.lower()

    def test_input_validate_name_special_characters(self):
        """Test that input with special characters is invalid."""
        is_valid, error = InputValidator.validate_name("Name@123")
        assert is_valid is False
        assert "contain" in error.lower()

    def test_input_validate_name_valid_complex(self):
        """Test that valid complex name is accepted."""
        is_valid, error = InputValidator.validate_name("John Doe-Smith")
        assert is_valid is True

    def test_input_validate_name_leading_trailing_spaces(self):
        """Test that leading/trailing spaces are trimmed and validated."""
        is_valid, error = InputValidator.validate_name("  Jane Doe  ")
        assert is_valid is True

    def test_validation_name_with_unicode(self):
        """Test that names with unicode characters are accepted."""
        is_valid, error = InputValidator.validate_name("Андрій Шевченко")
        assert is_valid is True

    def test_validation_name_length_limit(self):
        """Test that overly long names are rejected."""
        long_name = "A" * 101  # assuming 100 is the limit
        is_valid, error = InputValidator.validate_name(long_name)
        assert is_valid is False
        assert "100" in error.lower()

    def test_validation_name_length_within_limit(self):
        """Test that names within length limit are accepted."""
        valid_name = "A" * 50  # assuming 100 is the limit
        is_valid, error = InputValidator.validate_name(valid_name)
        assert is_valid is True

    def test_validation_name_length_exact_limit(self):
        """Test that names exactly at length limit are accepted."""
        exact_name = "A" * 100  # assuming 100 is the limit
        is_valid, error = InputValidator.validate_name(exact_name)
        assert is_valid is True

    def test_validation_name_length_min_limit(self):
        """Test that names below minimum length are rejected."""
        short_name = "A" * 1  # assuming 2 is the minimum
        is_valid, error = InputValidator.validate_name(short_name)
        assert is_valid is False
        assert "2" in error.lower()

    def test_validation_name_length_min_within_limit(self):
        """Test that names at minimum length are accepted."""
        min_name = "AB"  # assuming 2 is the minimum
        is_valid, error = InputValidator.validate_name(min_name)
        assert is_valid is True

    def test_validation_text_content_empty(self):
        """Test that empty text is invalid."""
        is_valid, error = InputValidator.validate_text_content("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validation_text_content_valid(self):
        """Test that valid text content is accepted."""
        is_valid, error = InputValidator.validate_text_content("This is a valid note.")
        assert is_valid is True

    def test_validation_text_content_whitespace(self):
        """Test that whitespace-only text is invalid."""
        is_valid, error = InputValidator.validate_text_content("    ")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validation_text_content_special_characters(self):
        """Test that text with special characters is accepted."""
        is_valid, error = InputValidator.validate_text_content(
            "Note with special chars! @#$$%^&*()"
        )
        assert is_valid is True

    def test_validation_text_content_length_limit(self):
        """Test that overly long text content is rejected."""
        long_text = "A" * 10001  # assuming 10000 is the limit
        is_valid, error = InputValidator.validate_text_content(long_text)
        assert is_valid is False
        assert "1000" in error.lower()

    def test_validation_text_content_length_within_limit(self):
        """Test that text content within length limit is accepted."""
        valid_text = "A" * 5000  # assuming 10000 is the limit
        is_valid, error = InputValidator.validate_text_content(valid_text)
        assert is_valid is True

    def test_validation_text_content_length_exact_limit(self):
        """Test that text content exactly at length limit is accepted."""
        exact_text = "A" * 10000  # assuming 10000 is the limit
        is_valid, error = InputValidator.validate_text_content(exact_text)
        assert is_valid is True

    def test_validation_text_content_length_min_limit(self):
        """Test that text content below minimum length is rejected."""
        short_text = "A" * 0  # assuming 1 is the minimum
        is_valid, error = InputValidator.validate_text_content(short_text)
        assert is_valid is False
        assert "1" in error.lower()

    def test_validation_text_content_length_min_with_defined_min_limit(self, min_length: int = 5):
        """Test that text content at minimum length is accepted."""
        min_text = "A" * min_length  # assuming min_length is the minimum
        is_valid, error = InputValidator.validate_text_content(min_text, min_length=min_length)
        assert is_valid is True

    def test_validation_text_content_length_min_with_defined_min_limit_reject(
        self, min_length: int = 5
    ):
        """Test that text content below minimum length is rejected."""
        short_text = "A" * (min_length - 1)  # assuming min_length is the minimum
        is_valid, error = InputValidator.validate_text_content(short_text, min_length=min_length)
        assert is_valid is False
        assert str(min_length) in error.lower()

    # Validate a tag/keyword.
    # Requirements:
    # - Not empty
    # - 2-30 characters
    # - Only alphanumeric and hyphens
    # - No spaces

    def test_validation_tag_valid(self):
        """Test that valid tag is accepted."""
        is_valid, error = InputValidator.validate_tag("valid-tag123")
        assert is_valid is True

    def test_validation_tag_empty(self):
        """Test that empty tag is rejected."""
        is_valid, error = InputValidator.validate_tag("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validation_tag_too_short(self):
        """Test that too short tag is rejected."""
        is_valid, error = InputValidator.validate_tag("a")
        assert is_valid is False
        assert "2" in error.lower()

    def test_validation_tag_too_long(self):
        """Test that too long tag is rejected."""
        long_tag = "a" * 31
        is_valid, error = InputValidator.validate_tag(long_tag)
        assert is_valid is False
        assert "30" in error.lower()

    def test_validation_tag_with_hyphens(self):
        """Test that tag with hyphens is accepted."""
        is_valid, error = InputValidator.validate_tag("valid-tag-name")
        assert is_valid is True

    def test_validation_tag_with_spaces(self):
        """Test that tag with spaces is rejected."""
        is_valid, error = InputValidator.validate_tag("invalid tag")
        assert is_valid is False
        assert "spaces" in error.lower()

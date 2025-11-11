"""
Unit tests for Contact model

These tests verify the Contact model functionality.
Run with: pytest tests/test_contacts.py
"""

from datetime import date

import pytest

from src.personal_assistant.models.contact import Contact


class TestContactModel:
    """Test suite for Contact model."""

    def test_contact_creation_with_all_fields(self) -> None:
        """Test creating contact with all fields populated."""
        contact = Contact(
            name="John Doe",
            phone="+380501234567",
            email="john@example.com",
            address="123 Main St, Kyiv",
            birthday=date(1990, 5, 15),
        )

        assert contact.name == "John Doe"
        assert contact.phone == "+380501234567"
        assert contact.email == "john@example.com"
        assert contact.address == "123 Main St, Kyiv"
        assert contact.birthday == date(1990, 5, 15)

    def test_contact_creation_minimal_fields(self) -> None:
        """Test creating contact with only required fields."""
        contact = Contact(name="Jane Smith", phone="0501234567")

        assert contact.name == "Jane Smith"
        assert contact.phone == "0501234567"
        assert contact.email is None
        assert contact.address is None
        assert contact.birthday is None

    def test_contact_validation_empty_name(self) -> None:
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            Contact(name="", phone="+380501234567")

    def test_contact_validation_empty_phone(self) -> None:
        """Test that empty phone raises ValueError."""
        with pytest.raises(ValueError, match="phone cannot be empty"):
            Contact(name="John Doe", phone="")

    def test_contact_to_dict(self) -> None:
        """Test contact serialization to dictionary."""
        contact = Contact(
            name="John Doe",
            phone="+380501234567",
            email="john@example.com",
            birthday=date(1990, 5, 15),
        )

        data = contact.to_dict()

        assert data["name"] == "John Doe"
        assert data["phone"] == "+380501234567"
        assert data["email"] == "john@example.com"
        assert data["birthday"] == "1990-05-15"

    def test_contact_to_dict_minimal(self) -> None:
        """Test serialization with minimal fields."""
        contact = Contact(name="Jane", phone="0501234567")
        data = contact.to_dict()

        assert data["name"] == "Jane"
        assert data["phone"] == "0501234567"
        assert data["email"] is None
        assert data["birthday"] is None

    def test_contact_from_dict(self) -> None:
        """Test contact deserialization from dictionary."""
        data = {
            "name": "John Doe",
            "phone": "+380501234567",
            "email": "john@example.com",
            "address": "123 Main St",
            "birthday": "1990-05-15",
        }

        contact = Contact.from_dict(data)

        assert contact.name == "John Doe"
        assert contact.phone == "+380501234567"
        assert contact.email == "john@example.com"
        assert contact.birthday == date(1990, 5, 15)

    def test_contact_from_dict_minimal(self) -> None:
        """Test deserialization with minimal fields."""
        data = {"name": "Jane", "phone": "0501234567"}

        contact = Contact.from_dict(data)

        assert contact.name == "Jane"
        assert contact.phone == "0501234567"
        assert contact.email is None

    def test_days_until_birthday_calculation(self) -> None:
        """Test birthday countdown calculation."""
        # Create contact with birthday
        today = date.today()
        future_date = date(today.year, 12, 31)

        contact = Contact(name="Test User", phone="+380501234567", birthday=future_date)

        days = contact.days_until_birthday()
        assert days is not None
        assert days >= 0

    def test_days_until_birthday_no_birthday(self) -> None:
        """Test that None is returned when no birthday set."""
        contact = Contact(name="Test User", phone="+380501234567")

        assert contact.days_until_birthday() is None


# TODO: Add tests for ContactService when implemented
# - test_add_contact_valid_data()
# - test_add_contact_invalid_phone()
# - test_search_contacts_by_name()
# - test_edit_contact_success()
# - test_delete_contact_success()
# - test_get_upcoming_birthdays()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

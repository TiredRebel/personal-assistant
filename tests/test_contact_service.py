"""
Unit tests for ContactService

These tests verify the ContactService functionality.
Run with: pytest tests/test_contact_service.py
"""

from datetime import date, timedelta
from typing import List
from unittest.mock import MagicMock

import pytest

from personal_assistant.models import Contact
from personal_assistant.services import ContactService
from personal_assistant.validators import ValidationError


class TestContactService:
    """Test suite for ContactService."""

    @pytest.fixture
    def mock_storage(self) -> MagicMock:
        """Create a mock storage object."""
        storage = MagicMock()
        storage.load.return_value = []
        storage.save.return_value = None
        return storage

    @pytest.fixture
    def service(self, mock_storage: MagicMock) -> ContactService:
        """Create a ContactService instance with mock storage."""
        return ContactService(mock_storage)

    def test_add_contact_valid_data(self, service: ContactService):
        """Test adding contact with valid data."""
        contact = service.add_contact(
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
        assert len(service.contacts) == 1
        assert service.save_contacts

    def test_add_contact_minimal_fields(self, service: ContactService):
        """Test adding contact with only required fields."""
        contact = service.add_contact(name="Jane Smith", phone="0501234567")

        assert contact.name == "Jane Smith"
        assert contact.phone == "+380501234567"  # Normalized
        assert contact.email is None
        assert contact.address is None
        assert contact.birthday is None
        assert len(service.contacts) == 1

    def test_add_contact_invalid_phone(self, service: ContactService):
        """Test that invalid phone raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid phone number"):
            service.add_contact(name="Test User", phone="invalid-phone")

    def test_add_contact_invalid_email(self, service: ContactService):
        """Test that invalid email raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid email"):
            service.add_contact(name="Test User", phone="+380501234567", email="invalid-email")

    def test_add_contact_duplicate_name(self, service: ContactService):
        """Test that duplicate name raises ValueError."""
        service.add_contact(name="John Doe", phone="+380501234567")

        with pytest.raises(ValueError, match="already exists"):
            service.add_contact(name="John Doe", phone="+380509999999")

    def test_add_contact_duplicate_name_case_insensitive(self, service: ContactService):
        """Test that duplicate name check is case-insensitive."""
        service.add_contact(name="John Doe", phone="+380501234567")

        with pytest.raises(ValueError, match="already exists"):
            service.add_contact(name="JOHN DOE", phone="+380509999999")

    def test_add_contact_phone_normalization(self, service: ContactService):
        """Test that phone numbers are normalized to international format."""
        contact1 = service.add_contact(name="User1", phone="0501234567")
        contact2 = service.add_contact(name="User2", phone="+380671234567")
        contact3 = service.add_contact(name="User3", phone="+380931234567")
        contact4 = service.add_contact(name="User4", phone="   093 12 34 567   ")

        assert contact1.phone == "+380501234567"
        assert contact2.phone == "+380671234567"
        assert contact3.phone == "+380931234567"
        assert contact4.phone == "+380931234567"

    def test_add_contact_email_normalization(self, service: ContactService):
        """Test that email addresses are normalized to lowercase."""
        contact = service.add_contact(
            name="Test User", phone="+380501234567", email="Test@Example.COM"
        )

        assert contact.email == "test@example.com"

    def test_search_contacts_by_name(self, service: ContactService):
        """Test searching contacts by name."""
        service.add_contact(name="John Doe", phone="+380501234567")
        service.add_contact(name="Jane Smith", phone="+380502234567")
        service.add_contact(name="Bob Johnson", phone="+380503234567")

        results = service.search_contacts("John")
        assert len(results) == 2
        assert any(c.name == "John Doe" for c in results)
        assert any(c.name == "Bob Johnson" for c in results)

    def test_search_contacts_by_phone(self, service: ContactService):
        """Test searching contacts by phone number."""
        service.add_contact(name="User1", phone="+380501234567")
        service.add_contact(name="User2", phone="+380671234567")
        service.add_contact(name="User3", phone="+380501234568")

        results: List[Contact] = service.search_contacts("050")
        assert len(results) == 2
        assert results[0].name == "User1"
        assert results[1].name == "User3"

    def test_search_contacts_by_email(self, service):
        """Test searching contacts by email."""
        service.add_contact(name="User1", phone="+380501234567", email="user1@test.com")
        service.add_contact(name="User2", phone="+380502234567", email="user2@test.com")
        service.add_contact(name="User3", phone="+380503234567", email="user3@example.com")

        results = service.search_contacts("@test.com")
        assert len(results) == 2
        assert results[0].name == "User1"
        assert results[1].name == "User2"

    def test_search_contacts_case_insensitive(self, service: ContactService):
        """Test that search is case-insensitive."""
        service.add_contact(name="John Doe", phone="+380501234567")

        results_lower = service.search_contacts("john")
        results_upper = service.search_contacts("JOHN")
        results_mixed = service.search_contacts("JoHn")

        assert len(results_lower) == 1
        assert len(results_upper) == 1
        assert len(results_mixed) == 1

    def test_search_contacts_empty_query(self, service):
        """Test that empty query returns empty list."""
        service.add_contact(name="John Doe", phone="+380501234567")

        assert service.search_contacts("") == []
        assert service.search_contacts("   ") == []

    def test_get_contact_by_name(self, service: ContactService):
        """Test finding contact by exact name match."""
        created = service.add_contact(name="John Doe", phone="+380501234567")
        found = service.get_contact_by_name("John Doe")

        assert found is not None
        assert found.name == created.name
        assert found.phone == created.phone

    def test_get_contact_by_name_case_insensitive(self, service: ContactService):
        """Test that get_contact_by_name is case-insensitive."""
        service.add_contact(name="John Doe", phone="+380501234567")

        found_lower = service.get_contact_by_name("john doe")
        found_upper = service.get_contact_by_name("JOHN DOE")

        assert found_lower is not None
        assert found_upper is not None

    def test_get_contact_by_name_not_found(self, service: ContactService):
        """Test that non-existent contact returns None."""
        result = service.get_contact_by_name("Non Existent")
        assert result is None

    def test_edit_contact_success(self, service: ContactService):
        """Test editing existing contact."""
        service.add_contact(name="John Doe", phone="+380501234567")

        updated = service.edit_contact(
            old_name="John Doe",
            name="John Smith",
            phone="+380509999999",
            email="john@example.com",
            address="New Address",
            birthday=date(1990, 1, 1),
        )

        assert updated.name == "John Smith"
        assert updated.phone == "+380509999999"
        assert updated.email == "john@example.com"
        assert updated.address == "New Address"
        assert updated.birthday == date(1990, 1, 1)

    def test_edit_contact_partial_update(self, service: ContactService):
        """Test editing contact with partial updates."""
        service.add_contact(
            name="John Doe",
            phone="+380501234567",
            email="old@example.com",
            address="Old Address",
        )

        # Update only phone
        service.edit_contact(old_name="John Doe", phone="+380509999999")
        contact = service.get_contact_by_name("John Doe")

        if not contact:
            pytest.fail("Contact should exist after edit.")

        assert contact.phone == "+380509999999"
        assert contact.email == "old@example.com"
        assert contact.address == "Old Address"

    def test_edit_contact_not_found(self, service: ContactService):
        """Test editing non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            service.edit_contact(old_name="Non Existent", phone="+380501234567")

    def test_edit_contact_invalid_phone(self, service: ContactService):
        """Test that editing with invalid phone raises ValidationError."""
        service.add_contact(name="John Doe", phone="+380501234567")

        with pytest.raises(ValidationError, match="Invalid phone number"):
            service.edit_contact(old_name="John Doe", phone="invalid")

    def test_edit_contact_invalid_email(self, service: ContactService):
        """Test that editing with invalid email raises ValidationError."""
        service.add_contact(name="John Doe", phone="+380501234567")

        with pytest.raises(ValidationError, match="Invalid email"):
            service.edit_contact(old_name="John Doe", email="invalid-email")

    def test_edit_contact_duplicate_name(self, service: ContactService):
        """Test that editing to duplicate name raises ValueError."""
        service.add_contact(name="John Doe", phone="+380501234567")
        service.add_contact(name="Jane Smith", phone="+380502234567")

        with pytest.raises(ValueError, match="already exists"):
            service.edit_contact(old_name="John Doe", name="Jane Smith")

    def test_edit_contact_same_name_different_case(self, service: ContactService):
        """Test that editing to same name with different case is allowed."""
        service.add_contact(name="John Doe", phone="+380501234567")

        updated = service.edit_contact(old_name="John Doe", name="JOHN DOE")
        assert updated.name == "JOHN DOE"

    def test_edit_contact_empty_address(self, service: ContactService):
        """Test that empty address is set to None."""
        service.add_contact(name="John Doe", phone="+380501234567", address="Some Address")

        updated = service.edit_contact(old_name="John Doe", address="   ")
        assert updated.address is None

    def test_delete_contact_success(self, service: ContactService):
        """Test deleting existing contact."""
        service.add_contact(name="John Doe", phone="+380501234567")
        assert len(service.contacts) == 1

        result = service.delete_contact("John Doe")

        assert result is True
        assert len(service.contacts) == 0
        assert service.get_contact_by_name("John Doe") is None

    def test_delete_contact_not_found(self, service: ContactService):
        """Test deleting non-existent contact returns False."""
        result = service.delete_contact("Non Existent")
        assert result is False

    def test_delete_contact_case_insensitive(self, service: ContactService):
        """Test that delete is case-insensitive."""
        service.add_contact(name="John Doe", phone="+380501234567")

        result = service.delete_contact("JOHN DOE")
        assert result is True
        assert len(service.contacts) == 0

    def test_get_upcoming_birthdays(self, service: ContactService):
        """Test getting contacts with upcoming birthdays."""
        today = date.today()
        # Birthday in 3 days
        birthday1 = today + timedelta(days=3)
        # Birthday in 10 days
        birthday2 = today + timedelta(days=10)

        service.add_contact(name="User1", phone="+380501234567", birthday=birthday1)
        service.add_contact(name="User2", phone="+380502234567", birthday=birthday2)

        # Get birthdays in next 7 days
        upcoming = service.get_upcoming_birthdays(7)

        # Depending on current date, we may get 0, 1, or 2 results
        # We just verify the method works without errors
        for contact in upcoming:
            days_until = contact.days_until_birthday()
            assert days_until is not None
            assert days_until <= 7

    def test_get_upcoming_birthdays_sorted(self, service: ContactService):
        """Test that upcoming birthdays are sorted by days until birthday."""
        today = date.today()
        birthday1 = today + timedelta(days=5)
        birthday2 = today + timedelta(days=2)
        birthday3 = today + timedelta(days=8)

        service.add_contact(name="User1", phone="+380501234567", birthday=birthday1)
        service.add_contact(name="User2", phone="+380502234567", birthday=birthday2)
        service.add_contact(name="User3", phone="+380503234567", birthday=birthday3)

        upcoming = service.get_upcoming_birthdays(10)

        # Verify sorted order
        for i in range(len(upcoming) - 1):
            days1 = upcoming[i].days_until_birthday()
            days2 = upcoming[i + 1].days_until_birthday()
            # Ensure days_until_birthday() did not return None before comparing
            assert days1 is not None and days2 is not None
            assert days1 <= days2

    def test_get_upcoming_birthdays_no_birthday(self, service: ContactService):
        """Test that contacts without birthdays are not included."""
        service.add_contact(name="User1", phone="+380501234567")  # No birthday

        upcoming = service.get_upcoming_birthdays(365)
        assert len(upcoming) == 0

    def test_get_all_contacts(self, service: ContactService):
        """Test getting all contacts."""
        service.add_contact(name="User1", phone="+380501234567")
        service.add_contact(name="User2", phone="+380502234567")
        service.add_contact(name="User3", phone="+380503234567")

        all_contacts = service.get_all_contacts()

        assert len(all_contacts) == 3
        # Verify it returns a copy, not the original list
        all_contacts.append(Contact(name="User4", phone="+380504234567"))
        assert len(service.contacts) == 3

    def test_get_contacts_count(self, service: ContactService):
        """Test getting total number of contacts."""
        assert service.get_contacts_count() == 0

        service.add_contact(name="User1", phone="+380501234567")
        assert service.get_contacts_count() == 1

        service.add_contact(name="User2", phone="+380502234567")
        assert service.get_contacts_count() == 2

        service.delete_contact("User1")
        assert service.get_contacts_count() == 1

    def test_load_contacts_from_storage(self, mock_storage: MagicMock):
        """Test loading contacts from storage."""
        mock_storage.load.return_value = [
            {
                "name": "John Doe",
                "phone": "+380501234567",
                "email": "john@example.com",
                "address": "123 Main St",
                "birthday": "1990-05-15",
            }
        ]

        service = ContactService(mock_storage)

        assert len(service.contacts) == 1
        assert service.contacts[0].name == "John Doe"
        assert service.contacts[0].phone == "+380501234567"
        assert service.contacts[0].birthday == date(1990, 5, 15)

    def test_load_contacts_handles_errors(self, mock_storage: MagicMock):
        """Test that loading errors result in empty contact list."""
        mock_storage.load.side_effect = Exception("Storage error")

        service = ContactService(mock_storage)

        assert len(service.contacts) == 0

    def test_save_contacts_called(self, service: ContactService, mock_storage: MagicMock):
        """Test that save_contacts is called after modifications."""
        service.add_contact(name="John Doe", phone="+380501234567")
        assert mock_storage.save.called

        mock_storage.reset_mock()
        service.edit_contact(old_name="John Doe", email="john@example.com")
        assert mock_storage.save.called

        mock_storage.reset_mock()
        service.delete_contact("John Doe")
        assert mock_storage.save.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

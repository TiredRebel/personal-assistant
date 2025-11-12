"""
Contact Service

This module provides business logic for managing contacts.
See docs/CONTACTS_MODULE.md for detailed specifications.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from src.personal_assistant.models.contact import Contact
from src.personal_assistant.storage.file_storage import FileStorage
from src.personal_assistant.validators.validators import (
    EmailValidator,
    PhoneValidator,
    ValidationError,
)


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

    def __init__(self, storage: FileStorage) -> None:
        """
        Initialize contact service.

        Args:
            storage: Storage instance for data persistence
        """
        self.storage: FileStorage = storage
        self.contacts: List[Contact] = []
        self.load_contacts()

    def load_contacts(self) -> None:
        """Load contacts from storage."""
        try:
            contacts_data = self.storage.load("contacts.json")
            self.contacts = [Contact.from_dict(data) for data in contacts_data]
        except Exception:
            # If loading fails, start with empty list
            self.contacts = []

    def save_contacts(self) -> None:
        """Save contacts to storage."""
        contacts_data = [contact.to_dict() for contact in self.contacts]
        self.storage.save("contacts.json", contacts_data)

    def add_contact(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
        address: Optional[str] = None,
        birthday: Optional[date] = None,
    ) -> Contact:
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
        # Validate phone number
        is_valid, error_msg = PhoneValidator.validate(phone)
        if not is_valid:
            raise ValidationError(f"Invalid phone number: {error_msg}")

        # Normalize phone to international format
        normalized_phone = PhoneValidator.normalize(phone)

        # Validate email if provided
        if email:
            is_valid, error_msg = EmailValidator.validate(email)
            if not is_valid:
                raise ValidationError(f"Invalid email: {error_msg}")
            email = EmailValidator.normalize(email)

        # Check if contact with same name exists (case-insensitive)
        if self.get_contact_by_name(name):
            raise ValueError(f"Contact with name '{name}' already exists")

        # Create new contact
        contact = Contact(
            name=name,
            phone=normalized_phone,
            email=email,
            address=address,
            birthday=birthday,
        )

        # Add to contacts list
        self.contacts.append(contact)

        # Save to storage
        self.save_contacts()

        return contact

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
        if not query or not query.strip():
            return []

        query = query.lower().strip()
        matching_contacts: List[Contact] = []

        for contact in self.contacts:
            # Check name
            if query in contact.name.lower():
                matching_contacts.append(contact)
                continue

            # Check phone
            if query in contact.phone.lower():
                matching_contacts.append(contact)
                continue

            # Check email
            if contact.email and query in contact.email.lower():
                matching_contacts.append(contact)
                continue

        return matching_contacts

    def get_contact_by_name(self, name: str) -> Optional[Contact]:
        """
        Find a contact by exact name match.

        Args:
            name: Contact name to search for

        Returns:
            Contact if found, None otherwise
        """
        name_lower = name.lower().strip()
        for contact in self.contacts:
            if contact.name.lower() == name_lower:
                return contact
        return None

    def edit_contact(
        self,
        old_name: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        birthday: Optional[date] = None,
    ) -> Contact:
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
        # Find contact by old name
        contact = self.get_contact_by_name(old_name)
        if not contact:
            raise ValueError(f"Contact with name '{old_name}' not found")

        # Validate and update phone if provided
        if phone is not None:
            is_valid, error_msg = PhoneValidator.validate(phone)
            if not is_valid:
                raise ValidationError(f"Invalid phone number: {error_msg}")
            contact.phone = PhoneValidator.normalize(phone)

        # Validate and update email if provided
        if email is not None:
            is_valid, error_msg = EmailValidator.validate(email)
            if not is_valid:
                raise ValidationError(f"Invalid email: {error_msg}")
            contact.email = EmailValidator.normalize(email)

        # Update other fields if provided
        if name is not None:
            # Check if new name conflicts with existing contact
            if name.lower() != old_name.lower():
                existing = self.get_contact_by_name(name)
                if existing:
                    raise ValueError(f"Contact with name '{name}' already exists")
            contact.name = name

        if address is not None:
            contact.address = address if address.strip() else None

        if birthday is not None:
            contact.birthday = birthday

        # Save to storage
        self.save_contacts()

        return contact

    def delete_contact(self, name: str) -> bool:
        """
        Delete a contact by name.

        Args:
            name: Name of contact to delete

        Returns:
            True if contact was deleted, False if not found
        """
        contact = self.get_contact_by_name(name)
        if not contact:
            return False

        self.contacts.remove(contact)
        self.save_contacts()
        return True

    def get_upcoming_birthdays(self, days: int) -> List[Contact]:
        """
        Get contacts with birthdays in the next N days.

        Args:
            days: Number of days to look ahead

        Returns:
            List of contacts with upcoming birthdays, sorted by days until birthday
        """
        # Build filtered list of (contact, days_until) tuples in single pass
        upcoming = [
            (contact, days_until)
            for contact in self.contacts
            if (days_until := contact.days_until_birthday()) is not None and days_until <= days
        ]

        # Sort by days_until (already calculated)
        upcoming.sort(key=lambda item: item[1])

        # Return just the contacts (not the tuples)
        return [contact for contact, _ in upcoming]

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

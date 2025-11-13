"""
Contact Model

This module defines the Contact data structure for the address book.
See docs/CONTACTS_MODULE.md for detailed specifications.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Optional


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

    Example:
        >>> contact = Contact(
        ...     name="John Doe",
        ...     phone="+380501234567",
        ...     email="john@example.com",
        ...     birthday=date(1990, 5, 15)
        ... )
        >>> print(contact.name)
        John Doe
    """

    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    birthday: Optional[date] = None

    def __post_init__(self) -> None:
        """
        Validate contact data after initialization.

        Raises:
            ValueError: If name or phone is empty
        """
        if not self.name or not self.name.strip():
            raise ValueError("Contact name cannot be empty")
        if not self.phone:
            raise ValueError("Contact phone cannot be empty")

    def to_dict(self) -> dict[str, Optional[str]]:
        """
        Convert contact to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the contact

        Example:
            >>> contact = Contact("John", "+380501234567")
            >>> data = contact.to_dict()
            >>> data['name']
            'John'
        """
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "birthday": self.birthday.isoformat() if self.birthday else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Contact:
        """
        Create contact from dictionary (JSON deserialization).

        Args:
            data: Dictionary containing contact data

        Returns:
            Contact instance

        Example:
            >>> data = {"name": "John", "phone": "+380501234567"}
            >>> contact = Contact.from_dict(data)
            >>> contact.name
            'John'
        """
        birthday = None
        if data.get("birthday"):
            birthday = date.fromisoformat(data["birthday"])

        return cls(
            name=data["name"],
            phone=data["phone"],
            email=data.get("email"),
            address=data.get("address"),
            birthday=birthday,
        )

    def days_until_birthday(self) -> Optional[int]:
        """
        Calculate days until next birthday.

        Returns:
            Number of days until birthday, or None if birthday not set

        Example:
            >>> from datetime import date
            >>> contact = Contact("John", "+380501234567", birthday=date(1990, 12, 31))
            >>> days = contact.days_until_birthday()
            >>> days >= 0
            True
        """
        if not self.birthday:
            return None

        today = date.today()
        next_birthday = date(today.year, self.birthday.month, self.birthday.day)

        # If birthday already passed this year, use next year
        if next_birthday < today:
            next_birthday = date(today.year + 1, self.birthday.month, self.birthday.day)

        return (next_birthday - today).days

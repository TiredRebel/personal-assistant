"""
Note model for the Personal Assistant application.

This module defines the Note class which represents a text note with optional tags,
timestamps, and serialization capabilities.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Note:
    """
    Represents a text note with optional tags.

    Attributes:
        id: Unique identifier for the note
        title: Note title (optional but recommended)
        content: Main text content of the note
        tags: List of tags/keywords for categorization
        created_at: Timestamp when note was created
        updated_at: Timestamp when note was last updated
    """

    content: str
    title: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate note data after initialization."""
        if not self.content or not self.content.strip():
            raise ValueError("Note content cannot be empty")

        # Normalize tags (lowercase, strip whitespace)
        self.tags = [tag.lower().strip() for tag in self.tags if tag.strip()]

        # Remove duplicate tags
        self.tags = list(set(self.tags))

    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the note.

        Args:
            tag: Tag to add (will be normalized)
        """
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()

    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from the note.

        Args:
            tag: Tag to remove
        """
        tag = tag.lower().strip()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()

    def has_tag(self, tag: str) -> bool:
        """
        Check if note has a specific tag.

        Args:
            tag: Tag to check

        Returns:
            True if note has the tag, False otherwise
        """
        return tag.lower().strip() in self.tags

    def update_content(self, content: str, title: Optional[str] = None) -> None:
        """
        Update note content and title.

        Args:
            content: New content
            title: New title (optional)
        """
        if not content or not content.strip():
            raise ValueError("Note content cannot be empty")

        self.content = content
        if title is not None:
            self.title = title
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert note to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the note
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Note":
        """
        Create note from dictionary (JSON deserialization).

        Args:
            data: Dictionary containing note data

        Returns:
            Note instance
        """
        note = cls(
            content=data["content"],
            title=data.get("title"),
            tags=data.get("tags", []),
            id=data.get("id", str(uuid.uuid4())),
        )

        # Restore timestamps
        if "created_at" in data:
            note.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            note.updated_at = datetime.fromisoformat(data["updated_at"])

        return note

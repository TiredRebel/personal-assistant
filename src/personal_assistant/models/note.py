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

    def __post_init__(self):
        """Validate note data after initialization."""
        if not self.content or not self.content.strip():
            raise ValueError("Note content cannot be empty")

        # Normalize tags (lowercase, strip whitespace)
        self.tags = [tag.lower().strip() for tag in self.tags if tag.strip()]

        # Remove duplicate tags and sort them for consistent order
        self.tags = sorted(set(self.tags))

    def add_tag(self, tag: str):
        """
        Add a tag to the note, duplicates or empty tags are skipped.

        Args:
            tag: Tag to add (will be normalized to lowercase and stripped)
        """
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()

    def remove_tag(self, tag: str):
        """
        Remove a tag from the note if exists.

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

    def update_content(self, content: str, title: Optional[str] = None):
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

    def to_dict(self) -> dict:
        """
        Convert note to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the note with keys:
                - id (str): Unique identifier
                - title (str | None): Note title
                - content (str): Note content
                - tags (List[str]): List of tags
                - created_at (str): ISO format timestamp
                - updated_at (str): ISO format timestamp
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
    def from_dict(cls, data: dict) -> "Note":
        """
        Create note from dictionary (JSON deserialization).

        Args:
            data: Dictionary containing note data with keys:
                - content (str, required): Note content
                - id (str, optional): Unique identifier
                - title (str, optional): Note title
                - tags (List[str], optional): List of tags
                - created_at (str, optional): ISO format timestamp
                - updated_at (str, optional): ISO format timestamp

        Returns:
            Note instance

        Raises:
            TypeError: If field types are invalid
        """
        # Validate content type
        content = data["content"]
        if not isinstance(content, str):
            raise TypeError(f"content must be str, not {type(content).__name__}")

        # Validate title type (if present)
        title = data.get("title")
        if title is not None and not isinstance(title, str):
            raise TypeError(f"title must be str or None, not {type(title).__name__}")

        # Validate tags type
        tags = data.get("tags", [])
        if not isinstance(tags, list):
            raise TypeError(f"tags must be list, not {type(tags).__name__}")

        # Validate id type
        note_id = data.get("id")
        if note_id is not None:
            if not isinstance(note_id, str):
                raise TypeError(f"id must be str or None, not {type(note_id).__name__}")
        else:
            note_id = str(uuid.uuid4())

        # Create note instance
        note = cls(
            content=content,
            title=title,
            tags=tags,
            id=note_id,
        )

        # Restore timestamps with validation
        if "created_at" in data:
            created_at = data["created_at"]
            if not isinstance(created_at, str):
                raise TypeError(f"created_at must be str, not {type(created_at).__name__}")
            note.created_at = datetime.fromisoformat(created_at)

        if "updated_at" in data:
            updated_at = data["updated_at"]
            if not isinstance(updated_at, str):
                raise TypeError(f"updated_at must be str, not {type(updated_at).__name__}")
            note.updated_at = datetime.fromisoformat(updated_at)

        return note

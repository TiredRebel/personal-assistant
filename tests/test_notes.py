"""
Unit tests for Note model

These tests verify the Note model functionality.
Run with: pytest tests/test_notes.py
"""

from datetime import datetime

import pytest

from personal_assistant.models import Note


class TestNoteModel:
    """Test suite for Note model."""

    def test_note_creation_with_all_fields(self) -> None:
        """Test creating note with all fields."""
        note = Note(
            title="Team Meeting",
            content="Meeting notes",
            tags=["work", "meeting"],
            created_at=datetime(1990, 5, 15),
            updated_at=datetime(1990, 5, 15),
        )

        assert note.title == "Team Meeting"
        assert note.content == "Meeting notes"
        # Tags are deduplicated and normalized but NOT sorted per spec
        assert set(note.tags) == {"meeting", "work"}
        assert note.created_at == datetime(1990, 5, 15)
        assert note.updated_at == datetime(1990, 5, 15)

    def test_note_creation_minimal_fields(self) -> None:
        """Test creating note with only content."""
        note = Note(
            title="Team Meeting",
            content="Meeting notes",
        )

        assert note.title == "Team Meeting"
        assert note.content == "Meeting notes"
        assert note.tags == []
        assert note.created_at is not None
        assert note.updated_at is not None

    def test_note_tag_normalization(self) -> None:
        """Test that tags are normalized (lowercase, no duplicates)."""
        note = Note(
            title="Team Meeting",
            content="Meeting notes",
            tags=[" Work ", "meeting", "WORK", " "],
        )

        # Tags are deduplicated and normalized but NOT sorted per spec
        assert set(note.tags) == {"meeting", "work"}
        assert len(note.tags) == 2

    def test_note_add_tag(self) -> None:
        """Test adding a tag to a note."""
        note = Note(
            title="Team Meeting",
            content="Meeting notes",
        )

        note.add_tag("Work")
        note.add_tag("work")
        note.add_tag(" ")
        assert note.tags == ["work"]

    def test_note_remove_tag(self) -> None:
        """Test removing a tag from a note."""
        note = Note(
            title="Team Meeting",
            content="Meeting notes",
        )

        note.remove_tag("work")
        note.add_tag("Work")
        note.remove_tag("work")
        assert note.tags == []

    def test_note_has_tag(self) -> None:
        """Test checking if note has a specific tag."""
        note = Note(
            title="Team Meeting",
            content="Meeting notes",
            tags=["work", "meeting"],
        )

        assert note.has_tag("work") is True
        assert note.has_tag("Work") is True
        assert note.has_tag("meeting") is True
        assert note.has_tag("personal") is False

    def test_note_update_content(self) -> None:
        """Test updating note content and timestamp."""
        note = Note(
            title="Team Meeting",
            content="Meeting notes",
        )

        old_updated_at = note.updated_at
        note.update_content("Updated meeting notes", title="Updated Meeting")
        assert note.content == "Updated meeting notes"
        assert note.title == "Updated Meeting"
        assert note.updated_at > old_updated_at

    def test_note_to_dict(self) -> None:
        """Test note serialization to dictionary."""
        note = Note(
            title="Team Meeting",
            content="Meeting notes",
            tags=["work", "meeting"],
            created_at=datetime(1990, 5, 15, 10, 30),
            updated_at=datetime(1990, 5, 15, 12, 0),
        )

        data = note.to_dict()

        assert data["title"] == "Team Meeting"
        assert data["content"] == "Meeting notes"
        assert sorted(data["tags"]) == ["meeting", "work"]
        assert data["created_at"] == "1990-05-15T10:30:00"
        assert data["updated_at"] == "1990-05-15T12:00:00"

    def test_note_from_dict(self) -> None:
        """Test note deserialization from dictionary."""
        data = {
            "id": "1",
            "title": "Team Meeting",
            "content": "Meeting notes",
            "tags": ["work", "meeting"],
            "created_at": "1990-05-15T10:30:00",
            "updated_at": "1990-05-15T12:00:00",
        }

        note = Note.from_dict(data)

        assert note.id == "1"
        assert note.title == "Team Meeting"
        assert note.content == "Meeting notes"
        assert set(note.tags) == {"meeting", "work"}
        assert note.created_at == datetime(1990, 5, 15, 10, 30)
        assert note.updated_at == datetime(1990, 5, 15, 12, 0)

    def test_note_validation_empty_content(self) -> None:
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            Note(title="Empty Note", content=" ")

        with pytest.raises(ValueError, match="content cannot be empty"):
            Note(title="Empty Note", content="\t")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

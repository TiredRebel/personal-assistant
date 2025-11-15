"""
Unit tests for NoteService
These tests verify the NoteService functionality.
Run with: pytest tests/test_note_service.py
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from personal_assistant.models import Note
from personal_assistant.services import NoteService


class TestNoteService:
    """Test suite for NoteService."""

    @pytest.fixture
    def mock_storage(self):
        """Create a mock storage object."""
        storage = MagicMock()
        storage.load.return_value = []
        storage.save.return_value = None
        return storage

    @pytest.fixture
    def service(self, mock_storage):
        """Create a NoteService instance with mock storage."""
        return NoteService(mock_storage)

    def test_create_note_success(self, service, mock_storage):
        """Test creating note with valid data."""
        note = service.create_note(
            content="Test content", title="Test Title", tags=["test", "demo"]
        )

        assert note.content == "Test content"
        assert note.title == "Test Title"
        assert "test" in note.tags
        assert "demo" in note.tags
        assert len(service.notes) == 1
        assert mock_storage.save.called

    def test_create_note_empty_content(self, service):
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            service.create_note(content="  ", title="Empty")

    def test_create_note_minimal(self, service):
        """Test creating note with only content."""
        note = service.create_note(content="Just content")

        assert note.content == "Just content"
        assert note.title is None
        assert note.tags == []
        assert len(service.notes) == 1

    def test_get_note_by_id_found(self, service):
        """Test finding a note by ID."""
        created_note = service.create_note(content="Test")
        found_note = service.get_note_by_id(created_note.id)

        assert found_note is not None
        assert found_note.id == created_note.id
        assert found_note.content == "Test"

    def test_get_note_by_id_not_found(self, service):
        """Test searching for non-existent note ID."""
        result = service.get_note_by_id("non-existent-id")
        assert result is None

    def test_search_notes_by_content(self, service):
        """Test searching notes by content."""
        service.create_note(content="Python programming tips")
        service.create_note(content="Java development guide")
        service.create_note(content="Advanced Python techniques")

        results = service.search_notes("Python")
        assert len(results) == 2
        assert all("python" in note.content.lower() for note in results)

    def test_search_notes_case_insensitive(self, service):
        """Test that search is case-insensitive."""
        service.create_note(content="Python Programming", title="PYTHON Guide")

        results_lower = service.search_notes("python")
        results_upper = service.search_notes("PYTHON")
        results_mixed = service.search_notes("PyThOn")

        assert len(results_lower) == 1
        assert len(results_upper) == 1
        assert len(results_mixed) == 1

    def test_search_notes_by_title(self, service):
        """Test searching notes by title."""
        service.create_note(content="Content here", title="Meeting Notes")
        service.create_note(content="Other content", title="Shopping List")

        results = service.search_notes("Meeting")
        assert len(results) == 1
        assert results[0].title == "Meeting Notes"

    def test_search_notes_by_tags_all(self, service):
        """Test searching notes with all specified tags (AND logic)."""
        service.create_note(content="Note 1", tags=["work", "urgent", "meeting"])
        service.create_note(content="Note 2", tags=["work", "urgent"])
        service.create_note(content="Note 3", tags=["work"])

        results = service.search_notes_by_tags(["work", "urgent"])
        assert len(results) == 2

        results_all_three = service.search_notes_by_tags(["work", "urgent", "meeting"])
        assert len(results_all_three) == 1

    def test_search_notes_by_tags_case_insensitive(self, service):
        """Test that tag search is case-insensitive."""
        service.create_note(content="Test", tags=["Work", "URGENT"])

        results = service.search_notes_by_tags(["work", "urgent"])
        assert len(results) == 1

    def test_search_notes_by_any_tag(self, service):
        """Test searching notes with any specified tag (OR logic)."""
        service.create_note(content="Note 1", tags=["work"])
        service.create_note(content="Note 2", tags=["personal"])
        service.create_note(content="Note 3", tags=["hobby"])

        results = service.search_notes_by_any_tag(["work", "personal"])
        assert len(results) == 2

    def test_search_notes_by_any_tag_sorting(self, service):
        """Test that OR tag search sorts by number of matching tags."""
        service.create_note(content="Note 1", tags=["a"])
        note2 = service.create_note(content="Note 2", tags=["a", "b", "c"])
        note3 = service.create_note(content="Note 3", tags=["a", "b"])

        results = service.search_notes_by_any_tag(["a", "b", "c"])
        # note2 should be first (has all 3 tags)
        assert results[0].id == note2.id
        # note3 should be second (has 2 tags)
        assert results[1].id == note3.id

    def test_edit_note_success(self, service):
        """Test editing existing note."""
        note = service.create_note(content="Original content")
        original_id = note.id

        updated_note = service.edit_note(
            note_id=note.id,
            content="Updated content",
            title="New Title",
            tags=["updated"],
        )

        assert updated_note.id == original_id
        assert updated_note.content == "Updated content"
        assert updated_note.title == "New Title"
        assert updated_note.tags == ["updated"]

    def test_edit_note_partial_update(self, service):
        """Test editing note with partial updates."""
        note = service.create_note(content="Original", title="Original Title", tags=["original"])

        # Update only content
        service.edit_note(note_id=note.id, content="New content")
        assert note.content == "New content"
        assert note.title == "Original Title"
        assert note.tags == ["original"]

    def test_edit_note_not_found(self, service):
        """Test editing non-existent note raises error."""
        with pytest.raises(ValueError, match="not found"):
            service.edit_note(note_id="non-existent", content="New content")

    def test_edit_note_empty_content(self, service):
        """Test that editing with empty content raises error."""
        note = service.create_note(content="Original")

        with pytest.raises(ValueError, match="cannot be empty"):
            service.edit_note(note_id=note.id, content="  ")

    def test_edit_note_normalizes_tags(self, service):
        """Test that editing note properly normalizes tags."""
        note = service.create_note(content="Test content", tags=["original"])

        # Edit with unnormalized tags (uppercase, duplicates, extra spaces)
        updated_note = service.edit_note(
            note_id=note.id,
            tags=["Python", " TESTING ", "python", "Demo", " testing "],
        )

        # Tags should be normalized: lowercase, stripped, deduplicated (not sorted per spec)
        assert set(updated_note.tags) == {"demo", "python", "testing"}
        assert len(updated_note.tags) == 3

    def test_delete_note_success(self, service):
        """Test deleting existing note."""
        note = service.create_note(content="To be deleted")
        note_id = note.id

        assert len(service.notes) == 1

        result = service.delete_note(note_id)

        assert result is True
        assert len(service.notes) == 0
        assert service.get_note_by_id(note_id) is None

    def test_delete_note_not_found(self, service):
        """Test deleting non-existent note returns False."""
        result = service.delete_note("non-existent-id")
        assert result is False

    def test_add_tag_to_note(self, service):
        """Test adding tag to existing note."""
        note = service.create_note(content="Test", tags=["initial"])

        updated_note = service.add_tag_to_note(note.id, "new-tag")

        assert "initial" in updated_note.tags
        assert "new-tag" in updated_note.tags
        assert len(updated_note.tags) == 2

    def test_add_tag_to_note_not_found(self, service):
        """Test adding tag to non-existent note raises error."""
        with pytest.raises(ValueError, match="not found"):
            service.add_tag_to_note("non-existent", "tag")

    def test_remove_tag_from_note(self, service):
        """Test removing tag from existing note."""
        note = service.create_note(content="Test", tags=["tag1", "tag2"])

        updated_note = service.remove_tag_from_note(note.id, "tag1")

        assert "tag1" not in updated_note.tags
        assert "tag2" in updated_note.tags
        assert len(updated_note.tags) == 1

    def test_remove_tag_from_note_not_found(self, service):
        """Test removing tag from non-existent note raises error."""
        with pytest.raises(ValueError, match="not found"):
            service.remove_tag_from_note("non-existent", "tag")

    def test_get_all_tags(self, service):
        """Test getting all unique tags."""
        service.create_note(content="Note 1", tags=["work", "urgent"])
        service.create_note(content="Note 2", tags=["personal", "urgent"])
        service.create_note(content="Note 3", tags=["work", "meeting"])

        all_tags = service.get_all_tags()

        assert len(all_tags) == 4
        assert "work" in all_tags
        assert "urgent" in all_tags
        assert "personal" in all_tags
        assert "meeting" in all_tags

    def test_get_all_tags_empty(self, service):
        """Test getting tags when no notes exist."""
        all_tags = service.get_all_tags()
        assert len(all_tags) == 0

    def test_get_all_notes(self, service):
        """Test getting all notes sorted by updated_at."""
        service.create_note(content="First")
        service.create_note(content="Second")
        note3 = service.create_note(content="Third")

        all_notes = service.get_all_notes()

        assert len(all_notes) == 3
        # Most recent first
        assert all_notes[0].id == note3.id

    def test_get_notes_count(self, service):
        """Test getting total number of notes."""
        assert service.get_notes_count() == 0

        service.create_note(content="Note 1")
        assert service.get_notes_count() == 1

        service.create_note(content="Note 2")
        assert service.get_notes_count() == 2

    def test_sort_notes_by_date_descending(self, service):
        """Test sorting notes by date (newest first)."""
        note1 = Note(content="First", created_at=datetime(2023, 1, 1))
        note2 = Note(content="Second", created_at=datetime(2023, 6, 1))
        note3 = Note(content="Third", created_at=datetime(2023, 12, 1))

        service.notes = [note1, note2, note3]

        sorted_notes = service.sort_notes_by_date(ascending=False)

        assert sorted_notes[0].id == note3.id
        assert sorted_notes[1].id == note2.id
        assert sorted_notes[2].id == note1.id

    def test_sort_notes_by_date_ascending(self, service):
        """Test sorting notes by date (oldest first)."""
        note1 = Note(content="First", created_at=datetime(2023, 1, 1))
        note2 = Note(content="Second", created_at=datetime(2023, 6, 1))
        note3 = Note(content="Third", created_at=datetime(2023, 12, 1))

        service.notes = [note3, note1, note2]

        sorted_notes = service.sort_notes_by_date(ascending=True)

        assert sorted_notes[0].id == note1.id
        assert sorted_notes[1].id == note2.id
        assert sorted_notes[2].id == note3.id

    def test_sort_notes_by_tags_count(self, service):
        """Test sorting notes by number of tags."""
        note1 = service.create_note(content="Note 1", tags=["a"])
        note2 = service.create_note(content="Note 2", tags=["a", "b", "c"])
        note3 = service.create_note(content="Note 3", tags=["a", "b"])

        sorted_notes = service.sort_notes_by_tags_count()

        # note2 should be first (3 tags)
        assert sorted_notes[0].id == note2.id
        # note3 should be second (2 tags)
        assert sorted_notes[1].id == note3.id
        # note1 should be last (1 tag)
        assert sorted_notes[2].id == note1.id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

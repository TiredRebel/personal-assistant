"""
Note service for the Personal Assistant application.

This module provides the NoteService class which handles all business logic
for note operations including creation, editing, deletion, searching, and tag management.
"""

from typing import List, Optional, Set

from src.personal_assistant.models.note import Note
from src.personal_assistant.storage.file_storage import FileStorage


class NoteService:
    """
    Service class for managing notes.

    Handles all business logic for note operations:
    - Creating notes
    - Searching notes by content and tags
    - Editing notes
    - Deleting notes
    - Tag management
    """

    def __init__(self, storage: FileStorage) -> None:
        """
        Initialize note service.

        Args:
            storage: Storage instance for data persistence
        """
        self.storage = storage
        self.notes: List[Note] = []
        self.load_notes()

    def load_notes(self) -> None:
        """Load notes from storage."""
        pass

    def save_notes(self) -> None:
        """Save notes to storage."""
        pass

    def create_note(
        self, content: str, title: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> Note:
        """
        Create a new note.

        Args:
            content: Note content (required)
            title: Note title (optional)
            tags: List of tags (optional)

        Returns:
            The created Note object

        Raises:
            ValueError: If content is empty
        """
        note = Note(content=content, title=title, tags=tags or [])
        self.notes.append(note)
        self.save_notes()
        return note

    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        """
        Find a note by ID.

        Args:
            note_id: Note ID to search for

        Returns:
            Note if found, None otherwise
        """
        for note in self.notes:
            if note.id == note_id:
                return note

        return None

    def search_notes(self, query: str) -> List[Note]:
        """
        Search notes by content and title.

        Performs case-insensitive partial matching in:
        - Note title
        - Note content

        Args:
            query: Search query string

        Returns:
            List of matching notes, sorted by relevance
        """
        if not query or not query.strip():
            return []

        query = query.lower().strip()
        matching_notes: List[Note] = []
        for note in self.notes:
            if (
                note.title is not None and query in note.title.lower()
            ) or query in note.content.lower():
                matching_notes.append(note)

        matching_notes.sort(key=lambda n: n.updated_at, reverse=True)
        return matching_notes

    def search_notes_by_tags(self, tags: List[str]) -> List[Note]:
        """
        Search notes by tags.

        Returns notes that have ALL specified tags (AND logic).

        Args:
            tags: List of tags to search for

        Returns:
            List of notes that have all specified tags
        """
        normalized_tags = [tag.lower().strip() for tag in tags]
        matching_notes: List[Note] = []
        for note in self.notes:
            if all(tag in note.tags for tag in normalized_tags):
                matching_notes.append(note)

        matching_notes.sort(key=lambda n: n.updated_at, reverse=True)
        return matching_notes

    def search_notes_by_any_tag(self, tags: List[str]) -> List[Note]:
        """
        Search notes by tags (OR logic).

        Returns notes that have ANY of the specified tags.

        Args:
            tags: List of tags to search for

        Returns:
            List of notes that have at least one specified tag
        """
        if not tags:
            return []

        normalized_tags = [tag.lower().strip() for tag in tags if tag and tag.strip()]
        if not normalized_tags:
            return []

        matching_notes: List[Note] = []
        for note in self.notes:
            if any(tag in note.tags for tag in normalized_tags):
                matching_notes.append(note)

        matching_notes.sort(
            key=lambda n: (
                sum(tag in n.tags for tag in normalized_tags),
                n.updated_at,
            ),
            reverse=True,
        )
        return matching_notes

    def edit_note(
        self,
        note_id: str,
        content: Optional[str] = None,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Note:
        """
        Edit an existing note.

        Args:
            note_id: ID of note to edit
            content: New content (optional, keeps old if None)
            title: New title (optional, keeps old if None)
            tags: New tags list (optional, keeps old if None)

        Returns:
            The updated Note object

        Raises:
            ValueError: If note not found or content is empty
        """
        note = self.get_note_by_id(note_id)
        if note is None:
            raise ValueError(f"Note with ID {note_id} not found")

        if content is not None:
            if not content.strip():
                raise ValueError("Content cannot be empty")
            note.content = content

        if title is not None:
            note.title = title

        if tags is not None:
            # Normalize tags: lowercase, strip, remove empty, deduplicate
            normalized_tags = [tag.lower().strip() for tag in tags if tag.strip()]
            note.tags = list(set(normalized_tags))

        self.save_notes()
        return note

    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note by ID.

        Args:
            note_id: ID of note to delete

        Returns:
            True if note was deleted, False if not found
        """
        note = self.get_note_by_id(note_id)
        if note is None:
            return False

        self.notes.remove(note)
        self.save_notes()
        return True

    def add_tag_to_note(self, note_id: str, tag: str) -> Note:
        """
        Add a tag to an existing note.

        Args:
            note_id: ID of note
            tag: Tag to add

        Returns:
            The updated Note object

        Raises:
            ValueError: If note not found
        """
        note = self.get_note_by_id(note_id)
        if note is None:
            raise ValueError(f"Note with ID {note_id} not found")

        note.add_tag(tag)
        self.save_notes()
        return note

    def remove_tag_from_note(self, note_id: str, tag: str) -> Note:
        """
        Remove a tag from an existing note.

        Args:
            note_id: ID of note
            tag: Tag to remove

        Returns:
            The updated Note object

        Raises:
            ValueError: If note not found
        """
        note = self.get_note_by_id(note_id)
        if note is None:
            raise ValueError(f"Note with ID {note_id} not found")

        note.remove_tag(tag)
        self.save_notes()
        return note

    def get_all_tags(self) -> Set[str]:
        """
        Get all unique tags used across all notes.

        Returns:
            Set of all tags
        """
        all_tags: Set[str] = set()
        for note in self.notes:
            all_tags.update(note.tags)
        return all_tags

    def get_all_notes(self) -> List[Note]:
        """
        Get all notes.

        Returns:
            List of all notes, sorted by updated_at (most recent first)
        """
        return sorted(self.notes, key=lambda n: n.updated_at, reverse=True)

    def get_notes_count(self) -> int:
        """
        Get total number of notes.

        Returns:
            Number of notes
        """
        return len(self.notes)

    def sort_notes_by_date(self, ascending: bool = False) -> List[Note]:
        """
        Get all notes sorted by date.

        Args:
            ascending: If True, oldest first; if False, newest first

        Returns:
            Sorted list of notes
        """
        return sorted(self.notes, key=lambda n: n.created_at, reverse=not ascending)

    def sort_notes_by_tags_count(self) -> List[Note]:
        """
        Get all notes sorted by number of tags.

        Returns:
            List of notes sorted by tag count (descending)
        """
        return sorted(self.notes, key=lambda n: len(n.tags), reverse=True)

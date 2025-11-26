# Notes Module Specification

## Overview
The notes module manages all note-related operations including creation, editing, deletion, searching, and tag management.

## Note Model

### Class: `Note`

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid

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

        # Remove duplicate tags
        self.tags = list(set(self.tags))

    def add_tag(self, tag: str):
        """
        Add a tag to the note.

        Args:
            tag: Tag to add (will be normalized)
        """
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()

    def remove_tag(self, tag: str):
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
            Dictionary representation of the note
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Note':
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
            id=data.get("id", str(uuid.uuid4()))
        )

        # Restore timestamps
        if "created_at" in data:
            note.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            note.updated_at = datetime.fromisoformat(data["updated_at"])

        return note
```

## Note Service

### Class: `NoteService`

```python
from typing import List, Optional, Set

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

    def __init__(self, storage):
        """
        Initialize note service.

        Args:
            storage: Storage instance for data persistence
        """
        self.storage = storage
        self.notes: List[Note] = []
        self.load_notes()

    def load_notes(self):
        """Load notes from storage."""
        # Implementation: Load from storage.load("notes")
        pass

    def save_notes(self):
        """Save notes to storage."""
        # Implementation: Save to storage.save("notes", notes)
        pass

    def create_note(self, content: str, title: Optional[str] = None,
                   tags: Optional[List[str]] = None) -> Note:
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
        # Implementation:
        # 1. Create new Note instance
        # 2. Add to self.notes list
        # 3. Save to storage
        # 4. Return created note
        pass

    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        """
        Find a note by ID.

        Args:
            note_id: Note ID to search for

        Returns:
            Note if found, None otherwise
        """
        # Implementation: Search for note with matching ID
        pass

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
        # Implementation:
        # 1. Convert query to lowercase
        # 2. Filter notes where query matches title or content
        # 3. Sort by updated_at (most recent first)
        # 4. Return matching notes
        pass

    def search_notes_by_tags(self, tags: List[str]) -> List[Note]:
        """
        Search notes by tags.

        Returns notes that have ALL specified tags (AND logic).

        Args:
            tags: List of tags to search for

        Returns:
            List of notes that have all specified tags
        """
        # Implementation:
        # 1. Normalize tags (lowercase)
        # 2. Filter notes that have all specified tags
        # 3. Sort by updated_at (most recent first)
        # 4. Return matching notes
        pass

    def search_notes_by_any_tag(self, tags: List[str]) -> List[Note]:
        """
        Search notes by tags (OR logic).

        Returns notes that have ANY of the specified tags.

        Args:
            tags: List of tags to search for

        Returns:
            List of notes that have at least one specified tag
        """
        # Implementation:
        # 1. Normalize tags
        # 2. Filter notes that have any specified tag
        # 3. Sort by number of matching tags, then by updated_at
        # 4. Return matching notes
        pass

    def edit_note(self, note_id: str, content: Optional[str] = None,
                 title: Optional[str] = None, tags: Optional[List[str]] = None) -> Note:
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
        # Implementation:
        # 1. Find note by ID
        # 2. Update fields if provided
        # 3. Update timestamp
        # 4. Save to storage
        # 5. Return updated note
        pass

    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note by ID.

        Args:
            note_id: ID of note to delete

        Returns:
            True if note was deleted, False if not found
        """
        # Implementation:
        # 1. Find note by ID
        # 2. Remove from self.notes list
        # 3. Save to storage
        # 4. Return True/False
        pass

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
        # Implementation:
        # 1. Find note by ID
        # 2. Add tag to note
        # 3. Save to storage
        # 4. Return updated note
        pass

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
        # Implementation:
        # 1. Find note by ID
        # 2. Remove tag from note
        # 3. Save to storage
        # 4. Return updated note
        pass

    def get_all_tags(self) -> Set[str]:
        """
        Get all unique tags used across all notes.

        Returns:
            Set of all tags
        """
        # Implementation:
        # 1. Collect all tags from all notes
        # 2. Return unique set
        pass

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
```

## Usage Examples

### Creating Notes

```python
# Create note with title and tags
note = service.create_note(
    content="Remember to buy groceries: milk, bread, eggs",
    title="Shopping List",
    tags=["shopping", "todo"]
)

# Create simple note
note = service.create_note(
    content="Meeting notes from standup..."
)
```

### Searching Notes

```python
# Search by content
results = service.search_notes("groceries")

# Search by tags (AND logic - must have all tags)
results = service.search_notes_by_tags(["shopping", "urgent"])

# Search by tags (OR logic - has any tag)
results = service.search_notes_by_any_tag(["work", "personal"])
```

### Editing Notes

```python
# Edit content only
note = service.edit_note(
    note_id="abc-123",
    content="Updated meeting notes..."
)

# Edit multiple fields
note = service.edit_note(
    note_id="abc-123",
    title="Updated Title",
    content="Updated content...",
    tags=["work", "important", "review"]
)
```

### Tag Management

```python
# Add tag to note
note = service.add_tag_to_note(note_id="abc-123", tag="urgent")

# Remove tag from note
note = service.remove_tag_from_note(note_id="abc-123", tag="completed")

# Get all tags in system
all_tags = service.get_all_tags()
print(f"Available tags: {', '.join(all_tags)}")
```

### Sorting Notes

```python
# Get notes by date (newest first)
recent_notes = service.get_all_notes()

# Get notes by date (oldest first)
old_notes = service.sort_notes_by_date(ascending=True)

# Get notes by number of tags
tagged_notes = service.sort_notes_by_tags_count()
```

### Deleting Notes

```python
# Delete note
success = service.delete_note("abc-123")
if success:
    print("Note deleted successfully")
else:
    print("Note not found")
```

## Testing Requirements

### Unit Tests to Implement

1. **Model Tests** (`test_note_model.py`)
   ```python
   def test_note_creation_with_all_fields():
       """Test creating note with all fields populated."""
       pass

   def test_note_creation_minimal_fields():
       """Test creating note with only content."""
       pass

   def test_note_tag_normalization():
       """Test that tags are normalized (lowercase, no duplicates)."""
       pass

   def test_note_add_tag():
       """Test adding a tag to a note."""
       pass

   def test_note_remove_tag():
       """Test removing a tag from a note."""
       pass

   def test_note_has_tag():
       """Test checking if note has a specific tag."""
       pass

   def test_note_update_content():
       """Test updating note content and timestamp."""
       pass

   def test_note_to_dict():
       """Test note serialization to dictionary."""
       pass

   def test_note_from_dict():
       """Test note deserialization from dictionary."""
       pass

   def test_note_validation_empty_content():
       """Test that empty content raises ValueError."""
       pass
   ```

2. **Service Tests** (`test_note_service.py`)
   ```python
   def test_create_note_success():
       """Test creating note with valid data."""
       pass

   def test_create_note_empty_content():
       """Test that empty content raises ValueError."""
       pass

   def test_search_notes_by_content():
       """Test searching notes by content."""
       pass

   def test_search_notes_case_insensitive():
       """Test that search is case-insensitive."""
       pass

   def test_search_notes_by_tags_all():
       """Test searching notes with all specified tags."""
       pass

   def test_search_notes_by_tags_any():
       """Test searching notes with any specified tag."""
       pass

   def test_edit_note_success():
       """Test editing existing note."""
       pass

   def test_edit_note_not_found():
       """Test editing non-existent note raises error."""
       pass

   def test_delete_note_success():
       """Test deleting existing note."""
       pass

   def test_add_tag_to_note():
       """Test adding tag to existing note."""
       pass

   def test_get_all_tags():
       """Test getting all unique tags."""
       pass

   def test_sort_notes_by_date():
       """Test sorting notes by date."""
       pass
   ```

## Error Handling

### Custom Exceptions

```python
class NoteError(Exception):
    """Base exception for note-related errors."""
    pass

class NoteNotFoundError(NoteError):
    """Raised when note is not found."""
    pass

class InvalidNoteContentError(NoteError):
    """Raised when note content is invalid."""
    pass
```

### Error Handling Examples

```python
try:
    note = service.create_note("")
except ValueError as e:
    print(f"Validation error: {e}")

try:
    note = service.get_note_by_id("unknown-id")
    if not note:
        raise NoteNotFoundError("Note not found")
except NoteNotFoundError as e:
    print(f"Error: {e}")
```

## Advanced Features

### Tag Suggestions

```python
def suggest_tags(note_content: str, existing_tags: Set[str]) -> List[str]:
    """
    Suggest tags based on note content.

    Args:
        note_content: Content to analyze
        existing_tags: Set of existing tags in system

    Returns:
        List of suggested tags
    """
    # Implementation:
    # 1. Extract keywords from content
    # 2. Match with existing tags (fuzzy matching)
    # 3. Return top suggestions
    pass
```

### Note Statistics

```python
def get_note_statistics(service: NoteService) -> dict:
    """
    Get statistics about notes.

    Returns:
        Dictionary with statistics
    """
    return {
        "total_notes": service.get_notes_count(),
        "total_tags": len(service.get_all_tags()),
        "avg_tags_per_note": sum(len(n.tags) for n in service.notes) / len(service.notes),
        "notes_without_tags": len([n for n in service.notes if not n.tags])
    }
```

## Performance Considerations

- Use sets for tag operations (faster membership testing)
- Index notes by ID for O(1) lookup
- Consider full-text search for large note collections
- Implement pagination for large result sets
- Cache frequently accessed notes

## Future Enhancements

- Rich text formatting (Markdown support)
- Note attachments (files, images)
- Note linking (reference other notes)
- Note templates
- Version history
- Shared notes (collaboration)
- Note encryption (for sensitive content)
- Export notes (PDF, Markdown, HTML)

"""
Helper functions for note management.

This module provides advanced features for note operations including:
- Tag suggestions based on content
- Note statistics
"""

import re
from typing import Dict, List, Set

from personal_assistant.services.note_service import NoteService


def suggest_tags(note_content: str, existing_tags: Set[str]) -> List[str]:
    """
    Suggest tags based on note content.

    Analyzes the note content and suggests relevant tags from the existing
    tags in the system. Uses keyword extraction and fuzzy matching.

    Args:
        note_content: Content to analyze
        existing_tags: Set of existing tags in system

    Returns:
        List of suggested tags (up to 5 most relevant)
    """
    if not note_content or not existing_tags:
        return []

    # Extract words from content (lowercase, alphanumeric only)
    words = re.findall(r"\b\w+\b", note_content.lower())

    # Remove common words (basic stopwords)
    stopwords = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "should",
        "could",
        "may",
        "might",
        "must",
        "can",
        "to",
        "from",
        "in",
        "on",
        "at",
        "by",
        "for",
        "with",
        "about",
        "of",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "me",
        "him",
        "her",
        "us",
        "them",
        "my",
        "your",
    }
    keywords = [w for w in words if w not in stopwords and len(w) > 2]

    # Find exact matches
    suggestions = []
    for tag in existing_tags:
        tag_lower = tag.lower()
        # Exact match in keywords
        if tag_lower in keywords:
            suggestions.append(tag)
        # Tag is substring of content
        elif tag_lower in note_content.lower():
            suggestions.append(tag)

    # Remove duplicates and limit to top 5
    unique_suggestions = list(dict.fromkeys(suggestions))
    return unique_suggestions[:5]


def get_note_statistics(service: NoteService) -> dict:
    """
    Get statistics about notes.

    Provides comprehensive statistics about the note collection including
    counts, averages, and other useful metrics.

    Args:
        service: NoteService instance

    Returns:
        Dictionary with statistics:
        - total_notes: Total number of notes
        - total_tags: Number of unique tags
        - avg_tags_per_note: Average number of tags per note
        - notes_without_tags: Count of notes with no tags
        - notes_with_title: Count of notes with titles
        - notes_without_title: Count of notes without titles
        - most_used_tags: List of top 5 most frequently used tags
    """
    total_notes = service.get_notes_count()

    if total_notes == 0:
        return {
            "total_notes": 0,
            "total_tags": 0,
            "avg_tags_per_note": 0.0,
            "notes_without_tags": 0,
            "notes_with_title": 0,
            "notes_without_title": 0,
            "most_used_tags": [],
        }

    all_tags = service.get_all_tags()
    notes = service.notes

    # Count tag occurrences
    tag_counts: Dict[str, int] = {}
    total_tag_count = 0
    for note in notes:
        total_tag_count += len(note.tags)
        for tag in note.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Get most used tags
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    most_used_tags = [{"tag": tag, "count": count} for tag, count in sorted_tags[:5]]

    # Count notes by properties
    notes_without_tags = len([n for n in notes if not n.tags])
    notes_with_title = len([n for n in notes if n.title])
    notes_without_title = total_notes - notes_with_title

    return {
        "total_notes": total_notes,
        "total_tags": len(all_tags),
        "avg_tags_per_note": round(total_tag_count / total_notes, 2),
        "notes_without_tags": notes_without_tags,
        "notes_with_title": notes_with_title,
        "notes_without_title": notes_without_title,
        "most_used_tags": most_used_tags,
    }

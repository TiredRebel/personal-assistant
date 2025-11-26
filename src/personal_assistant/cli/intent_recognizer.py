r"""
Intent Recognizer Module

This module provides natural language intent recognition for the Personal Assistant CLI.
It extracts:

- the user's intended action (add, search, edit, delete, list)
- the target entity (contact, note, birthday, tag)
- any additional parameters (names, phone numbers, emails, tags)

Phone number extraction supports multiple formats, for example:

- International: +380501234567
- With parentheses: (050) 123-4567
- With spaces: 050 123 4567
- With dashes: 050-123-4567

The module uses two regex patterns:
1. Numbers with parentheses, e.g. `$begin:math:text$050$end:math:text$\s*123-4567`
2. General formats without parentheses, e.g. `050 123 4567`

The parser selects the first matched value and returns it as the phone parameter.
"""

import re
from typing import Dict, List, Optional, Union


class IntentRecognizer:
    """
    Recognize user intent from natural language input.

    This class analyzes text to determine:
    - What action the user wants to perform (add, search, edit, delete, list)
    - What entity they want to act on (contact, note, birthday, tag)
    - What parameters are provided (names, phone numbers, emails, tags)
    """

    # Action keywords mapping
    ACTION_KEYWORDS = {
        "add": ["add", "create", "new", "make", "insert", "save"],
        "search": ["find", "search", "look for", "where", "locate"],
        "edit": ["edit", "update", "change", "modify", "alter"],
        "delete": ["delete", "remove", "erase", "drop", "destroy"],
        "list": ["list", "show", "display", "view", "all"],
    }

    # Entity keywords mapping
    # Order matters: more specific entities should come first to avoid false matches
    ENTITY_KEYWORDS = {
        "tag": ["tag", "label", "category"],  # Check 'tag' before 'note'
        "birthday": ["birthday", "birth date", "born"],
        "contact": ["contact", "person", "phone", "number"],
        "note": ["note", "memo", "reminder", "text"],
    }

    @classmethod
    def recognize_intent(cls, text: str) -> Dict[str, Optional[Union[str, float]]]:
        """
        Recognize intent from text.

        Args:
            text: User input text

        Returns:
            Dictionary with 'action', 'entity', and 'confidence' keys

        Examples:
            >>> IntentRecognizer.recognize_intent("add a new contact")
            {'action': 'add', 'entity': 'contact', 'confidence': 0.8}

            >>> IntentRecognizer.recognize_intent("find notes")
            {'action': 'search', 'entity': 'note', 'confidence': 0.8}
        """
        text_lower = text.lower()

        # Detect action
        action: Optional[str] = None
        for act, keywords in cls.ACTION_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                action = act
                break

        # Detect entity
        entity: Optional[str] = None
        for ent, keywords in cls.ENTITY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                entity = ent
                break

        # Calculate confidence based on whether both action and entity were found
        confidence = 0.8 if action and entity else 0.5

        return {"action": action, "entity": entity, "confidence": confidence}

    @classmethod
    def extract_parameters(
        cls, text: str, intent: Dict[str, Union[str, float]]
    ) -> Dict[str, Union[str, List[str]]]:
        """
        Extract parameters based on recognized intent.

        This method extracts various types of parameters from text:
        - Names (capitalized words)
        - Phone numbers (various formats)
        - Email addresses
        - Tags (words starting with #)

        Args:
            text: User input text
            intent: Recognized intent dictionary (not used currently,
                but available for future enhancements)

        Returns:
            Dictionary of extracted parameters

        Examples:
            >>> IntentRecognizer.extract_parameters("Add contact John Doe +380501234567", {})
            {'name': 'John Doe', 'phone': '+380501234567'}

            >>> IntentRecognizer.extract_parameters("Create note #work #important", {})
            {'tags': ['work', 'important']}
        """
        params: Dict[str, Union[str, List[str]]] = {}

        # Extract names (capitalized words, but exclude common command words)
        # Matches sequences of capitalized words: "John", "John Doe", "Mary Jane Smith"
        # Exclude common command verbs that start with capital letter
        command_words = {
            "Add",
            "Create",
            "New",
            "Find",
            "Search",
            "Edit",
            "Update",
            "Delete",
            "Remove",
            "List",
            "Show",
            "Display",
            "Phone",
            "Email",
            "Contact",
            "Note",
            "Tag",
            "Birthday",
        }

        # Find all sequences of capitalized words
        all_matches = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)

        # For each match, split and filter out command words
        for match in all_matches:
            words = match.split()
            filtered_words = [word for word in words if word not in command_words]
            if filtered_words:
                # Reconstruct the name from filtered words
                params["name"] = " ".join(filtered_words)
                break  # Take the first valid name found

        # Extract phone numbers
        # Supports multiple formats:
        # - International: +380501234567
        # - With parentheses: (050) 123-4567
        # - With spaces: 050 123 4567
        # - With dashes: 050-123-4567
        # Pattern 1: with parentheses, Pattern 2: without parentheses
        phones = re.findall(r"\(\d{2,4}\)\s*\d{3}[-\s]?\d{4}", text)

        # If nothing found, fall back to a more general pattern
        if not phones:
            # Supports formats like: +380501234567, 050 123 4567, 050-123-4567
            phones = re.findall(r"\+?[\d\s\-]{7,}", text)

        if phones:
            params["phone"] = phones[0].strip()

        # Extract emails
        emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
        if emails:
            params["email"] = emails[0]

        # Extract tags (words starting with #)
        tags = re.findall(r"#(\w+)", text)
        if tags:
            params["tags"] = tags

        return params

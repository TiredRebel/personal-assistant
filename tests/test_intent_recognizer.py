"""
Unit tests for IntentRecognizer

These tests verify the IntentRecognizer functionality for natural language understanding.
Run with: pytest tests/test_intent_recognizer.py
"""

import pytest
from personal_assistant.cli.intent_recognizer import IntentRecognizer


class TestIntentRecognizer:
    """Test suite for IntentRecognizer."""

    # ===== Intent Recognition Tests =====

    def test_recognize_add_contact_intent(self):
        """Test recognizing 'add contact' intent."""
        intent = IntentRecognizer.recognize_intent("add a new contact")
        assert intent["action"] == "add"
        assert intent["entity"] == "contact"
        assert intent["confidence"] == 0.8

    def test_recognize_search_note_intent(self):
        """Test recognizing 'search note' intent."""
        intent = IntentRecognizer.recognize_intent("find my notes")
        assert intent["action"] == "search"
        assert intent["entity"] == "note"
        assert intent["confidence"] == 0.8

    def test_recognize_delete_contact_intent(self):
        """Test recognizing 'delete contact' intent."""
        intent = IntentRecognizer.recognize_intent("remove this person")
        assert intent["action"] == "delete"
        assert intent["entity"] == "contact"
        assert intent["confidence"] == 0.8

    def test_recognize_list_contacts_intent(self):
        """Test recognizing 'list contacts' intent."""
        intent = IntentRecognizer.recognize_intent("show all contacts")
        assert intent["action"] == "list"
        assert intent["entity"] == "contact"
        assert intent["confidence"] == 0.8

    def test_recognize_edit_note_intent(self):
        """Test recognizing 'edit note' intent."""
        intent = IntentRecognizer.recognize_intent("update my note")
        assert intent["action"] == "edit"
        assert intent["entity"] == "note"
        assert intent["confidence"] == 0.8

    def test_recognize_birthday_intent(self):
        """Test recognizing birthday-related intent."""
        intent = IntentRecognizer.recognize_intent("show birthdays")
        assert intent["action"] == "list"
        assert intent["entity"] == "birthday"
        assert intent["confidence"] == 0.8

    def test_recognize_tag_intent(self):
        """Test recognizing tag-related intent."""
        intent = IntentRecognizer.recognize_intent("find notes by tag")
        assert intent["action"] == "search"
        assert intent["entity"] == "tag"
        assert intent["confidence"] == 0.8

    def test_recognize_action_only(self):
        """Test recognizing intent with action but no entity."""
        intent = IntentRecognizer.recognize_intent("I want to add something")
        assert intent["action"] == "add"
        assert intent["entity"] is None
        assert intent["confidence"] == 0.5  # Lower confidence

    def test_recognize_entity_only(self):
        """Test recognizing intent with entity but no action."""
        intent = IntentRecognizer.recognize_intent("something about contacts")
        assert intent["action"] is None
        assert intent["entity"] == "contact"
        assert intent["confidence"] == 0.5  # Lower confidence

    def test_recognize_no_intent(self):
        """Test text with no recognizable intent."""
        intent = IntentRecognizer.recognize_intent("hello world")
        assert intent["action"] is None
        assert intent["entity"] is None
        assert intent["confidence"] == 0.5

    def test_recognize_multiple_actions_first_wins(self):
        """Test that when multiple actions match, first one is returned."""
        intent = IntentRecognizer.recognize_intent("create and add a new contact")
        # Either 'create' or 'add' should match (both map to 'add' action)
        assert intent["action"] == "add"
        assert intent["entity"] == "contact"

    def test_recognize_case_insensitive(self):
        """Test that intent recognition is case-insensitive."""
        intent1 = IntentRecognizer.recognize_intent("ADD CONTACT")
        intent2 = IntentRecognizer.recognize_intent("add contact")
        intent3 = IntentRecognizer.recognize_intent("Add Contact")

        assert intent1["action"] == intent2["action"] == intent3["action"]
        assert intent1["entity"] == intent2["entity"] == intent3["entity"]

    def test_all_action_keywords(self):
        """Test all action keyword variations."""
        # Test 'add' variations
        for keyword in ["add", "create", "new", "make", "insert", "save"]:
            text = f"{keyword} a contact"
            intent = IntentRecognizer.recognize_intent(text)
            assert intent["action"] == "add", f"Failed for keyword: {keyword}"

        # Test 'search' variations
        for keyword in ["find", "search", "look for", "where", "locate"]:
            text = f"{keyword} a contact"
            intent = IntentRecognizer.recognize_intent(text)
            assert intent["action"] == "search", f"Failed for keyword: {keyword}"

    def test_all_entity_keywords(self):
        """Test all entity keyword variations."""
        # Test 'contact' variations
        for keyword in ["contact", "person", "phone", "number"]:
            text = f"add a {keyword}"
            intent = IntentRecognizer.recognize_intent(text)
            assert intent["entity"] == "contact", f"Failed for keyword: {keyword}"

        # Test 'note' variations
        for keyword in ["note", "memo", "reminder", "text"]:
            text = f"add a {keyword}"
            intent = IntentRecognizer.recognize_intent(text)
            assert intent["entity"] == "note", f"Failed for keyword: {keyword}"

    # ===== Parameter Extraction Tests =====

    def test_extract_name_simple(self):
        """Test extracting a simple name."""
        params = IntentRecognizer.extract_parameters("Add contact John Doe", {})
        assert "name" in params
        assert params["name"] == "John Doe"

    def test_extract_name_single(self):
        """Test extracting a single-word name."""
        params = IntentRecognizer.extract_parameters("Add contact John", {})
        assert "name" in params
        assert params["name"] == "John"

    def test_extract_name_triple(self):
        """Test extracting a three-word name."""
        params = IntentRecognizer.extract_parameters("Add Mary Jane Smith", {})
        assert "name" in params
        assert params["name"] == "Mary Jane Smith"

    def test_extract_phone_international(self):
        """Test extracting international phone number."""
        params = IntentRecognizer.extract_parameters("Call +380501234567 please", {})
        assert "phone" in params
        assert params["phone"] == "+380501234567"

    def test_extract_phone_with_spaces(self):
        """Test extracting phone number with spaces."""
        params = IntentRecognizer.extract_parameters("Phone: 050 123 4567", {})
        assert "phone" in params
        assert "050 123 4567" in params["phone"]

    def test_extract_phone_with_dashes(self):
        """Test extracting phone number with dashes."""
        params = IntentRecognizer.extract_parameters("Call 050-123-4567", {})
        assert "phone" in params
        assert "050-123-4567" in params["phone"]

    def test_extract_phone_with_parentheses(self):
        """Test extracting phone number with parentheses."""
        params = IntentRecognizer.extract_parameters("Phone (050) 123-4567", {})
        assert "phone" in params
        assert "(050) 123-4567" in params["phone"]

    def test_extract_email(self):
        """Test extracting email address."""
        params = IntentRecognizer.extract_parameters("Email john.doe@example.com", {})
        assert "email" in params
        assert params["email"] == "john.doe@example.com"

    def test_extract_email_complex(self):
        """Test extracting complex email address."""
        params = IntentRecognizer.extract_parameters("Contact user+tag@sub.domain.co.uk", {})
        assert "email" in params
        assert params["email"] == "user+tag@sub.domain.co.uk"

    def test_extract_tags_single(self):
        """Test extracting a single tag."""
        params = IntentRecognizer.extract_parameters("Note with #work tag", {})
        assert "tags" in params
        assert params["tags"] == ["work"]

    def test_extract_tags_multiple(self):
        """Test extracting multiple tags."""
        params = IntentRecognizer.extract_parameters("Note #work #important #urgent", {})
        assert "tags" in params
        assert set(params["tags"]) == {"work", "important", "urgent"}
        assert len(params["tags"]) == 3

    def test_extract_all_parameters(self):
        """Test extracting all parameter types at once."""
        text = "Add contact John Doe +380501234567 john@example.com #friend #work"
        params = IntentRecognizer.extract_parameters(text, {})

        assert "name" in params
        assert params["name"] == "John Doe"
        assert "phone" in params
        assert "+380501234567" in params["phone"]
        assert "email" in params
        assert params["email"] == "john@example.com"
        assert "tags" in params
        assert set(params["tags"]) == {"friend", "work"}

    def test_extract_no_parameters(self):
        """Test text with no extractable parameters."""
        params = IntentRecognizer.extract_parameters("just some random text", {})
        assert len(params) == 0

    def test_extract_name_not_lowercase(self):
        """Test that lowercase text doesn't extract as name."""
        params = IntentRecognizer.extract_parameters("add contact john doe", {})
        # lowercase 'john doe' should not match (needs capitalization)
        assert "name" not in params

    def test_extract_phone_multiple_first_wins(self):
        """Test that when multiple phones exist, first one is extracted."""
        params = IntentRecognizer.extract_parameters("Phones: +380501234567 and +380509876543", {})
        assert "phone" in params
        assert params["phone"] == "+380501234567"  # First one

    def test_extract_email_multiple_first_wins(self):
        """Test that when multiple emails exist, first one is extracted."""
        params = IntentRecognizer.extract_parameters(
            "Emails: john@example.com and jane@example.com", {}
        )
        assert "email" in params
        assert params["email"] == "john@example.com"  # First one

    def test_extract_parameters_with_intent(self):
        """Test parameter extraction with provided intent context."""
        # Intent is provided but currently not used in extraction logic
        # This test ensures the method signature works correctly
        intent = {"action": "add", "entity": "contact", "confidence": 0.8}
        params = IntentRecognizer.extract_parameters("Add John Doe", intent)
        assert "name" in params
        assert params["name"] == "John Doe"

    # ===== Integration Tests =====

    def test_full_workflow_add_contact(self):
        """Test complete workflow: recognize intent and extract parameters."""
        text = "I want to add a new contact John Doe +380501234567"

        # Recognize intent
        intent = IntentRecognizer.recognize_intent(text)
        assert intent["action"] == "add"
        assert intent["entity"] == "contact"

        # Extract parameters
        params = IntentRecognizer.extract_parameters(text, intent)
        assert params["name"] == "John Doe"
        assert "+380501234567" in params["phone"]

    def test_full_workflow_create_note_with_tags(self):
        """Test complete workflow for creating a note with tags."""
        text = "create a note about Meeting Notes #work #important"

        # Recognize intent
        intent = IntentRecognizer.recognize_intent(text)
        assert intent["action"] == "add"
        assert intent["entity"] == "note"

        # Extract parameters
        params = IntentRecognizer.extract_parameters(text, intent)
        assert "tags" in params
        assert set(params["tags"]) == {"work", "important"}

    def test_full_workflow_find_person(self):
        """Test complete workflow for finding a person."""
        text = "find person John Smith"

        # Recognize intent
        intent = IntentRecognizer.recognize_intent(text)
        assert intent["action"] == "search"
        assert intent["entity"] == "contact"

        # Extract parameters
        params = IntentRecognizer.extract_parameters(text, intent)
        assert params["name"] == "John Smith"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

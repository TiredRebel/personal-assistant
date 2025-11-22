import logging
import shutil
import traceback
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from personal_assistant.cli.command_parser import CommandParser
from personal_assistant.cli.interface import CLI
from personal_assistant.services.contact_service import ContactService
from personal_assistant.services.note_service import NoteService
from personal_assistant.storage.file_storage import FileStorage


class TestCLIIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = Path("test_cli_storage")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()

        self.storage = FileStorage(self.test_dir)
        self.contact_service = ContactService(self.storage)
        self.note_service = NoteService(self.storage)
        self.command_parser = CommandParser()
        self.cli = CLI(self.contact_service, self.note_service, self.command_parser)

    def tearDown(self) -> None:
        # Close logger handlers to release file lock
        logger = logging.getLogger("FileStorage")
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    @patch("builtins.input")
    def test_add_contact_flow(self, mock_input: MagicMock) -> None:
        # Simulate user inputs:
        # 1. Command: add-contact
        # 2. Name: John Doe
        # 3. Phone: +380501234567
        # 4. Email: john@example.com
        # 5. Address: 123 Main St
        # 6. Birthday: 1990-01-01
        # 7. Command: exit
        mock_input.side_effect = [
            "add-contact",
            "John Doe",
            "+380501234567",
            "john@example.com",
            "123 Main St",
            "1990-01-01",
            "exit",
        ]

        try:
            with self.assertRaises(SystemExit):
                self.cli.start()
        except Exception:
            traceback.print_exc()
            raise

        # Verify contact was actually added
        contacts = self.contact_service.search_contacts("John")
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0].name, "John Doe")
        self.assertEqual(contacts[0].phone, "+380501234567")

    @patch("builtins.input")
    def test_add_note_flow(self, mock_input: MagicMock) -> None:
        # Simulate user inputs:
        # 1. Command: add-note
        # 2. Title: My Note
        # 3. Content line 1: This is a test note
        # 4. Content line 2: (EOF to finish) -> handled by side_effect raising EOFError
        # 5. Tags: test, important
        # 6. Command: exit

        mock_input.side_effect = [
            "add-note",
            "My Note",
            "This is a test note",
            EOFError(),  # End of content
            "test, important",  # Tags
            "exit",
        ]

        try:
            with self.assertRaises(SystemExit):
                self.cli.start()
        except Exception:
            traceback.print_exc()
            raise

        # Verify note was added
        notes = self.note_service.search_notes("test note")
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "My Note")
        self.assertIn("test", notes[0].tags)


if __name__ == "__main__":
    unittest.main()

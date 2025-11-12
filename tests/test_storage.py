"""
Unit tests for FileStorage

These tests verify the file storage functionality.
Run with: pytest tests/test_storage.py
"""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from src.personal_assistant.storage.file_storage import DateTimeEncoder, FileStorage


class TestFileStorage:
    """Test suite for FileStorage class."""

    @pytest.fixture
    def temp_storage(self) -> Any:  # type: ignore[misc]
        """Create temporary storage for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FileStorage(base_dir=Path(tmpdir))
            yield storage
            # Close log handlers to release file handles
            for handler in storage.logger.handlers[:]:
                handler.close()
                storage.logger.removeHandler(handler)

    @pytest.fixture
    def sample_data(self) -> list[dict[str, str]]:
        """Sample data for testing."""
        return [
            {"name": "John Doe", "phone": "+380501234567", "email": "john@example.com"},
            {"name": "Jane Smith", "phone": "+380509876543", "email": "jane@example.com"},
        ]

    def test_storage_initialization(self, temp_storage: FileStorage) -> None:
        """Test storage creates necessary directories."""
        assert temp_storage.base_dir.exists()
        assert temp_storage.backup_dir.exists()
        # Log file may not exist immediately if no operations performed
        # assert (temp_storage.base_dir / 'storage.log').exists()

    def test_save_and_load_data(
        self,
        temp_storage: FileStorage,
        sample_data: list[dict[str, str]]
    ) -> None:
        """Test saving and loading data."""
        # Save data
        result = temp_storage.save('test.json', sample_data)
        assert result is True

        # Load data
        loaded_data = temp_storage.load('test.json')
        assert loaded_data == sample_data

    def test_load_nonexistent_file(self, temp_storage: FileStorage) -> None:
        """Test loading nonexistent file returns empty list."""
        loaded_data = temp_storage.load('nonexistent.json')
        assert loaded_data == []

    def test_atomic_write(
        self,
        temp_storage: FileStorage,
        sample_data: list[dict[str, str]]
    ) -> None:
        """Test atomic write prevents corruption."""
        # Save data
        temp_storage.save('test.json', sample_data)

        # File should exist
        filepath = temp_storage.base_dir / 'test.json'
        assert filepath.exists()

        # File should be readable
        with open(filepath, 'r', encoding='utf-8') as f:
            content = json.load(f)
            assert content == sample_data

    def test_create_backup(
        self,
        temp_storage: FileStorage,
        sample_data: list[dict[str, str]]
    ) -> None:
        """Test backup creation."""
        # Save original data
        temp_storage.save('test.json', sample_data)

        # Create backup
        result = temp_storage.create_backup('test.json')
        assert result is True

        # Check backup exists
        backups = temp_storage.list_backups('test.json')
        assert len(backups) >= 1

    def test_restore_from_backup(
        self,
        temp_storage: FileStorage,
        sample_data: list[dict[str, str]]
    ) -> None:
        """Test restoration from backup."""
        # Save original data
        temp_storage.save('test.json', sample_data)

        # Create backup
        temp_storage.create_backup('test.json')

        # Modify data
        modified_data = [{"name": "Modified", "phone": "123"}]
        temp_storage.save('test.json', modified_data)

        # Restore from backup
        result = temp_storage.restore_from_backup('test.json')
        assert result is True

        # Load restored data
        restored_data = temp_storage.load('test.json')
        assert restored_data == sample_data

    def test_delete_old_backups(
        self,
        temp_storage: FileStorage,
        sample_data: list[dict[str, str]]
    ) -> None:
        """Test cleanup of old backups."""
        # Save and create multiple backups
        temp_storage.save('test.json', sample_data)

        for i in range(15):
            temp_storage.create_backup('test.json')

        # Should keep only 10 backups
        backups = temp_storage.list_backups('test.json')
        assert len(backups) <= 10

    def test_corrupted_file_recovery(
        self,
        temp_storage: FileStorage,
        sample_data: list[dict[str, str]]
    ) -> None:
        """Test recovery from corrupted file."""
        # Save data and create backup
        temp_storage.save('test.json', sample_data)
        temp_storage.create_backup('test.json')

        # Corrupt the file
        filepath = temp_storage.base_dir / 'test.json'
        with open(filepath, 'w') as f:
            f.write("{ corrupted json")

        # Try to load - should recover from backup
        loaded_data = temp_storage.load('test.json')
        assert loaded_data == sample_data

    def test_export_data(
        self,
        temp_storage: FileStorage,
        sample_data: list[dict[str, str]]
    ) -> None:
        """Test data export."""
        # Save some data
        temp_storage.save('test.json', sample_data)

        # Export data
        with tempfile.TemporaryDirectory() as export_dir:
            export_path = Path(export_dir)
            result = temp_storage.export_data(export_path)
            assert result is True

            # Check exported files
            assert (export_path / 'test.json').exists()
            assert (export_path / 'export_manifest.json').exists()

    def test_import_data(
        self,
        temp_storage: FileStorage,
        sample_data: list[dict[str, str]]
    ) -> None:
        """Test data import."""
        # Create export directory with data
        with tempfile.TemporaryDirectory() as import_dir:
            import_path = Path(import_dir)

            # Create test file in import directory
            test_file = import_path / 'imported.json'
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f)

            # Import data
            result = temp_storage.import_data(import_path)
            assert result is True

            # Check imported data
            loaded_data = temp_storage.load('imported.json')
            assert loaded_data == sample_data

    def test_list_backups(
        self,
        temp_storage: FileStorage,
        sample_data: list[dict[str, str]]
    ) -> None:
        """Test listing backups."""
        import time

        # Save and create backups
        temp_storage.save('test.json', sample_data)
        temp_storage.create_backup('test.json')

        # Small delay to ensure different timestamps
        time.sleep(1.1)

        temp_storage.create_backup('test.json')

        # List backups
        backups = temp_storage.list_backups('test.json')

        assert len(backups) >= 2
        # Backups should be sorted newest first
        for i in range(len(backups) - 1):
            assert backups[i]['timestamp'] >= backups[i + 1]['timestamp']

    def test_datetime_encoder(self) -> None:
        """Test DateTimeEncoder for datetime serialization."""
        from datetime import date, datetime

        data = {
            'date': date(2025, 1, 15),
            'datetime': datetime(2025, 1, 15, 12, 30, 0),
            'string': 'test'
        }

        # Serialize with DateTimeEncoder
        json_str = json.dumps(data, cls=DateTimeEncoder)
        parsed = json.loads(json_str)

        assert parsed['date'] == '2025-01-15'
        assert parsed['datetime'] == '2025-01-15T12:30:00'
        assert parsed['string'] == 'test'

    def test_save_with_datetime(self, temp_storage: FileStorage) -> None:
        """Test saving data with datetime objects."""
        from datetime import date

        data = [
            {"name": "John", "birthday": date(1990, 5, 15)}
        ]

        # Should not raise exception
        result = temp_storage.save('test.json', data)
        assert result is True

        # Load and verify
        loaded = temp_storage.load('test.json')
        assert loaded[0]['name'] == 'John'
        assert loaded[0]['birthday'] == '1990-05-15'

    def test_backup_nonexistent_file(self, temp_storage: FileStorage) -> None:
        """Test creating backup of nonexistent file returns False."""
        result = temp_storage.create_backup('nonexistent.json')
        assert result is False

    def test_restore_without_backups(self, temp_storage: FileStorage) -> None:
        """Test restoring without backups returns False."""
        result = temp_storage.restore_from_backup('nonexistent.json')
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

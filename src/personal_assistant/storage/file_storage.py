"""
File Storage Module

Handles file-based storage for application data with atomic writes,
automatic backups, and error recovery.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class StorageError(Exception):
    """Base exception for storage errors."""
    pass


class CorruptedDataError(StorageError):
    """Raised when data file is corrupted."""
    pass


class BackupNotFoundError(StorageError):
    """Raised when backup file is not found."""
    pass


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""

    def default(self, o: Any) -> Any:
        """Convert datetime objects to ISO format strings."""
        from datetime import date, datetime

        if isinstance(o, (date, datetime)):
            return o.isoformat()
        return super().default(o)


class FileStorage:
    """
    Handles file-based storage for application data.

    Features:
    - JSON serialization/deserialization
    - Atomic writes (write to temp file, then rename)
    - Automatic backups
    - Error recovery
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize file storage.

        Args:
            base_dir: Base directory for storage (default: ~/.personal_assistant)
        """
        if base_dir is None:
            # Use user's home directory
            base_dir = Path.home() / '.personal_assistant'

        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / 'backups'
        self.log_file = self.base_dir / 'storage.log'

        # Create directories if they don't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging for storage operations."""
        # Create logger
        self.logger = logging.getLogger('FileStorage')
        self.logger.setLevel(logging.INFO)

        # Avoid duplicate handlers
        if not self.logger.handlers:
            # File handler
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)

            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Add handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def save(self, filename: str, data: list[dict[str, Any]]) -> bool:
        """
        Save data to JSON file with atomic write.

        Uses atomic write pattern:
        1. Write to temporary file
        2. Create backup of existing file
        3. Rename temp file to target file

        Args:
            filename: Name of file (e.g., 'contacts.json')
            data: List of dictionaries to save

        Returns:
            True if successful, False otherwise
        """
        filepath = self.base_dir / filename

        try:
            # Create backup if file exists
            if filepath.exists():
                self.create_backup(filename)

            # Serialize data to JSON
            json_data = json.dumps(
                data,
                cls=DateTimeEncoder,
                indent=2,
                ensure_ascii=False,
                sort_keys=True
            )

            # Atomic write
            self._atomic_write(filepath, json_data)

            self.logger.info(f"Successfully saved {len(data)} items to {filename}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save {filename}: {str(e)}")
            return False

    def load(self, filename: str) -> list[dict[str, Any]]:
        """
        Load data from JSON file.

        Args:
            filename: Name of file to load

        Returns:
            List of dictionaries, or empty list if file doesn't exist
        """
        filepath = self.base_dir / filename

        try:
            # Check if file exists
            if not filepath.exists():
                self.logger.info(f"File {filename} does not exist, returning empty list")
                return []

            # Read and parse JSON
            with open(filepath, 'r', encoding='utf-8') as f:
                data: list[dict[str, Any]] = json.load(f)

            self.logger.info(f"Successfully loaded {len(data)} items from {filename}")
            return data

        except json.JSONDecodeError as e:
            self.logger.error(f"Corrupted data in {filename}: {str(e)}")
            # Attempt recovery from backup
            return self._recover_from_corruption(filename)

        except Exception as e:
            self.logger.error(f"Failed to load {filename}: {str(e)}")
            return []

    def _atomic_write(self, filepath: Path, data: str) -> None:
        """
        Implement atomic write to prevent data corruption.

        Args:
            filepath: Target file path
            data: Data to write

        Raises:
            Exception: If write fails
        """
        temp_dir = filepath.parent

        # Create temp file in same directory (ensures same filesystem)
        temp_fd, temp_path = tempfile.mkstemp(
            dir=temp_dir,
            prefix=f'.{filepath.name}.',
            suffix='.tmp'
        )

        try:
            # Write data to temp file
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            # Atomic rename (replaces target file)
            os.replace(temp_path, filepath)

            # Set file permissions (user read/write only)
            os.chmod(filepath, 0o600)

        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except Exception:
                pass
            raise

    def create_backup(self, filename: str) -> bool:
        """
        Create a timestamped backup of a file.

        Args:
            filename: Name of file to backup

        Returns:
            True if backup created, False otherwise
        """
        source_path = self.base_dir / filename

        try:
            # Check if source file exists
            if not source_path.exists():
                self.logger.warning(f"Cannot backup {filename}: file does not exist")
                return False

            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = filename.rsplit('.', 1)[0]  # Remove extension
            extension = filename.rsplit('.', 1)[1] if '.' in filename else ''

            if extension:
                backup_filename = f"{base_name}_{timestamp}.{extension}"
            else:
                backup_filename = f"{base_name}_{timestamp}"

            backup_path = self.backup_dir / backup_filename

            # Copy file to backup directory
            shutil.copy2(source_path, backup_path)

            self.logger.info(f"Created backup: {backup_filename}")

            # Clean old backups
            self.delete_old_backups(filename, keep_count=10)

            return True

        except Exception as e:
            self.logger.error(f"Failed to create backup for {filename}: {str(e)}")
            return False

    def restore_from_backup(
        self,
        filename: str,
        backup_time: Optional[datetime] = None
    ) -> bool:
        """
        Restore a file from backup.

        Args:
            filename: Name of file to restore
            backup_time: Specific backup time (default: most recent)

        Returns:
            True if restored successfully, False otherwise
        """
        try:
            backups = self.list_backups(filename)

            if not backups:
                self.logger.error(f"No backups found for {filename}")
                return False

            # Find the appropriate backup
            backup_info: dict[str, Any]
            if backup_time is None:
                # Use most recent backup
                backup_info = backups[0]
            else:
                # Find backup matching timestamp
                found_backup: dict[str, Any] | None = None
                for backup in backups:
                    if backup['timestamp'] == backup_time:
                        found_backup = backup
                        break

                if found_backup is None:
                    self.logger.error(f"Backup not found for timestamp {backup_time}")
                    return False

                backup_info = found_backup

            # Copy backup to main location
            backup_path = self.backup_dir / backup_info['filename']
            target_path = self.base_dir / filename

            shutil.copy2(backup_path, target_path)

            self.logger.info(f"Restored {filename} from backup {backup_info['filename']}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to restore {filename} from backup: {str(e)}")
            return False

    def list_backups(self, filename: str) -> list[dict[str, Any]]:
        """
        List all available backups for a file.

        Args:
            filename: Name of file

        Returns:
            List of backup info (filename, timestamp, size), sorted by timestamp (newest first)
        """
        base_name = filename.rsplit('.', 1)[0]

        backups: list[dict[str, Any]] = []

        try:
            # Search backup directory
            for backup_file in self.backup_dir.iterdir():
                if backup_file.is_file() and backup_file.name.startswith(base_name):
                    # Parse timestamp from filename
                    # Format: basename_YYYYMMDD_HHMMSS.ext
                    try:
                        name_parts = backup_file.stem.split('_')
                        if len(name_parts) >= 3:
                            date_str = name_parts[-2]  # YYYYMMDD
                            time_str = name_parts[-1]  # HHMMSS

                            timestamp = datetime.strptime(
                                f"{date_str}_{time_str}",
                                '%Y%m%d_%H%M%S'
                            )

                            # Get file size
                            size = backup_file.stat().st_size

                            backups.append({
                                'filename': backup_file.name,
                                'timestamp': timestamp,
                                'size': size,
                                'size_mb': round(size / (1024 * 1024), 2)
                            })
                    except (ValueError, IndexError):
                        # Skip files that don't match expected format
                        continue

            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x['timestamp'], reverse=True)

        except Exception as e:
            self.logger.error(f"Failed to list backups for {filename}: {str(e)}")

        return backups

    def delete_old_backups(self, filename: str, keep_count: int = 10) -> None:
        """
        Delete old backups, keeping only the most recent N.

        Args:
            filename: Name of file
            keep_count: Number of backups to keep
        """
        try:
            backups = self.list_backups(filename)

            # Delete backups beyond keep_count
            for backup in backups[keep_count:]:
                backup_path = self.backup_dir / backup['filename']
                backup_path.unlink()
                self.logger.info(f"Deleted old backup: {backup['filename']}")

        except Exception as e:
            self.logger.error(f"Failed to delete old backups for {filename}: {str(e)}")

    def _recover_from_corruption(self, filename: str) -> list[dict[str, Any]]:
        """
        Attempt to recover data from corrupted file.

        Args:
            filename: Name of corrupted file

        Returns:
            Recovered data or empty list
        """
        self.logger.warning(f"Attempting to recover corrupted file: {filename}")

        # Try to restore from latest backup
        backups = self.list_backups(filename)

        for backup in backups:
            try:
                self.logger.info(f"Trying backup: {backup['filename']}")

                # Try to load and validate backup
                backup_path = self.backup_dir / backup['filename']
                with open(backup_path, 'r', encoding='utf-8') as f:
                    data: list[dict[str, Any]] = json.load(f)

                # If successful, restore from this backup
                if self.restore_from_backup(filename, backup['timestamp']):
                    self.logger.info(f"Successfully recovered from backup: {backup['filename']}")
                    return data

            except Exception as e:
                self.logger.warning(f"Backup {backup['filename']} also corrupted: {str(e)}")
                continue

        # All recovery attempts failed
        self.logger.error(f"All recovery attempts failed for {filename}")
        return []

    def export_data(self, export_path: Path) -> bool:
        """
        Export all data to specified directory.

        Args:
            export_path: Path to export directory

        Returns:
            True if export successful
        """
        try:
            export_path = Path(export_path)
            export_path.mkdir(parents=True, exist_ok=True)

            # Copy all JSON files
            for file in self.base_dir.glob('*.json'):
                shutil.copy2(file, export_path / file.name)
                self.logger.info(f"Exported {file.name}")

            # Create export manifest
            manifest = {
                'export_date': datetime.now().isoformat(),
                'files': [f.name for f in export_path.glob('*.json')],
                'version': '1.0.0'
            }

            manifest_path = export_path / 'export_manifest.json'
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Export completed successfully to {export_path}")
            return True

        except Exception as e:
            self.logger.error(f"Export failed: {str(e)}")
            return False

    def import_data(self, import_path: Path) -> bool:
        """
        Import data from specified directory.

        Args:
            import_path: Path to import directory

        Returns:
            True if import successful
        """
        try:
            import_path = Path(import_path)

            if not import_path.exists():
                self.logger.error(f"Import path does not exist: {import_path}")
                return False

            # Create backups of current data
            for file in self.base_dir.glob('*.json'):
                self.create_backup(file.name)

            # Copy imported files
            for file in import_path.glob('*.json'):
                if file.name != 'export_manifest.json':
                    target_path = self.base_dir / file.name

                    # Validate JSON before copying
                    with open(file, 'r', encoding='utf-8') as f:
                        json.load(f)  # Validate JSON

                    shutil.copy2(file, target_path)
                    self.logger.info(f"Imported {file.name}")

            self.logger.info(f"Import completed successfully from {import_path}")
            return True

        except Exception as e:
            self.logger.error(f"Import failed: {str(e)}")
            return False

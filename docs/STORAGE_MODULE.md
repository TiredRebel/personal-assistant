# Storage Module Specification

## Overview
The storage module handles data persistence, ensuring all contacts and notes are saved to disk and can be recovered after application restart.

## Requirements
- Store data in user's home directory
- Use JSON format for human-readable storage
- Support atomic writes (prevent data corruption)
- Implement automatic backup
- Handle errors gracefully

## Storage Location

### Directory Structure

```
~/.personal_assistant/          # Main application directory
├── contacts.json               # Contacts database
├── notes.json                  # Notes database
├── config.json                 # Application configuration
└── backups/                    # Automatic backups
    ├── contacts_20240115_120000.json
    ├── contacts_20240114_120000.json
    ├── notes_20240115_120000.json
    └── notes_20240114_120000.json
```

## File Storage Implementation

### Class: `FileStorage`

```python
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
import shutil
import logging

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
        
        # Create directories if they don't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for storage operations."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.base_dir / 'storage.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('FileStorage')
    
    def save(self, filename: str, data: List[Dict]) -> bool:
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
        # Implementation:
        # 1. Create full path
        # 2. Create backup if file exists
        # 3. Write to temporary file
        # 4. Atomic rename temp file to target
        # 5. Log operation
        # 6. Return success status
        pass
    
    def load(self, filename: str) -> List[Dict]:
        """
        Load data from JSON file.
        
        Args:
            filename: Name of file to load
        
        Returns:
            List of dictionaries, or empty list if file doesn't exist
        """
        # Implementation:
        # 1. Create full path
        # 2. Check if file exists
        # 3. Read and parse JSON
        # 4. Handle errors (corruption, parse errors)
        # 5. Attempt recovery from backup if needed
        # 6. Return data or empty list
        pass
    
    def create_backup(self, filename: str) -> bool:
        """
        Create a timestamped backup of a file.
        
        Args:
            filename: Name of file to backup
        
        Returns:
            True if backup created, False otherwise
        """
        # Implementation:
        # 1. Check if source file exists
        # 2. Generate backup filename with timestamp
        # 3. Copy file to backup directory
        # 4. Clean old backups (keep last 10)
        # 5. Log operation
        pass
    
    def restore_from_backup(self, filename: str, backup_time: Optional[datetime] = None) -> bool:
        """
        Restore a file from backup.
        
        Args:
            filename: Name of file to restore
            backup_time: Specific backup time (default: most recent)
        
        Returns:
            True if restored successfully, False otherwise
        """
        # Implementation:
        # 1. Find backup file
        # 2. Validate backup file
        # 3. Copy backup to main location
        # 4. Log operation
        pass
    
    def list_backups(self, filename: str) -> List[Dict]:
        """
        List all available backups for a file.
        
        Args:
            filename: Name of file
        
        Returns:
            List of backup info (filename, timestamp, size)
        """
        # Implementation:
        # 1. Search backup directory
        # 2. Parse backup filenames
        # 3. Get file info (size, timestamp)
        # 4. Return sorted list
        pass
    
    def delete_old_backups(self, filename: str, keep_count: int = 10):
        """
        Delete old backups, keeping only the most recent N.
        
        Args:
            filename: Name of file
            keep_count: Number of backups to keep
        """
        # Implementation:
        # 1. List all backups for file
        # 2. Sort by timestamp
        # 3. Delete oldest backups beyond keep_count
        pass
    
    def export_data(self, export_path: Path) -> bool:
        """
        Export all data to specified directory.
        
        Args:
            export_path: Path to export directory
        
        Returns:
            True if export successful
        """
        # Implementation:
        # 1. Create export directory
        # 2. Copy all data files
        # 3. Create export manifest (timestamp, version)
        # 4. Log operation
        pass
    
    def import_data(self, import_path: Path) -> bool:
        """
        Import data from specified directory.
        
        Args:
            import_path: Path to import directory
        
        Returns:
            True if import successful
        """
        # Implementation:
        # 1. Validate import directory
        # 2. Create backups of current data
        # 3. Copy imported files
        # 4. Validate imported data
        # 5. Log operation
        pass
```

## Atomic Write Implementation

```python
def atomic_write_implementation(filepath: Path, data: str):
    """
    Implement atomic write to prevent data corruption.
    
    Steps:
    1. Write to temporary file
    2. Sync to disk (fsync)
    3. Rename temp file to target (atomic operation)
    
    This ensures that even if the system crashes during write,
    we either have the complete new file or the complete old file,
    never a partially written file.
    """
    import tempfile
    
    # Create temp file in same directory (ensures same filesystem)
    temp_dir = filepath.parent
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
        
    except Exception as e:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except:
            pass
        raise e
```

## JSON Serialization Helpers

```python
from datetime import date, datetime
from typing import Any

class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for datetime objects.
    """
    
    def default(self, obj: Any) -> Any:
        """Convert datetime objects to ISO format strings."""
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


def serialize_for_storage(data: List[Any]) -> str:
    """
    Serialize data to JSON string.
    
    Args:
        data: List of objects to serialize
    
    Returns:
        JSON string
    """
    # Convert objects to dictionaries
    dict_data = []
    for item in data:
        if hasattr(item, 'to_dict'):
            dict_data.append(item.to_dict())
        else:
            dict_data.append(item)
    
    # Serialize to JSON with pretty printing
    return json.dumps(
        dict_data,
        cls=DateTimeEncoder,
        indent=2,
        ensure_ascii=False,
        sort_keys=True
    )


def deserialize_from_storage(json_str: str, model_class: Any) -> List[Any]:
    """
    Deserialize JSON string to list of objects.
    
    Args:
        json_str: JSON string to parse
        model_class: Class with from_dict() method
    
    Returns:
        List of objects
    """
    # Parse JSON
    dict_data = json.loads(json_str)
    
    # Convert dictionaries to objects
    objects = []
    for item in dict_data:
        if hasattr(model_class, 'from_dict'):
            objects.append(model_class.from_dict(item))
        else:
            objects.append(item)
    
    return objects
```

## Error Recovery

```python
class StorageError(Exception):
    """Base exception for storage errors."""
    pass


class CorruptedDataError(StorageError):
    """Raised when data file is corrupted."""
    pass


class BackupNotFoundError(StorageError):
    """Raised when backup file is not found."""
    pass


def recover_from_corruption(storage: FileStorage, filename: str) -> List[Dict]:
    """
    Attempt to recover data from corrupted file.
    
    Recovery steps:
    1. Try to parse partial JSON
    2. Try to restore from latest backup
    3. Try to restore from older backups
    4. Return empty list if all recovery attempts fail
    
    Args:
        storage: FileStorage instance
        filename: Name of corrupted file
    
    Returns:
        Recovered data or empty list
    """
    logger = logging.getLogger('StorageRecovery')
    
    # Step 1: Try partial JSON parsing
    try:
        logger.info(f"Attempting partial JSON recovery for {filename}")
        # Try to fix common JSON errors
        # ... implementation
    except:
        logger.warning("Partial JSON recovery failed")
    
    # Step 2: Try latest backup
    try:
        logger.info(f"Attempting restore from latest backup")
        if storage.restore_from_backup(filename):
            return storage.load(filename)
    except:
        logger.warning("Latest backup restoration failed")
    
    # Step 3: Try older backups
    backups = storage.list_backups(filename)
    for backup in backups[1:]:  # Skip first (already tried)
        try:
            logger.info(f"Attempting restore from backup: {backup['filename']}")
            if storage.restore_from_backup(filename, backup['timestamp']):
                return storage.load(filename)
        except:
            continue
    
    # Step 4: All recovery attempts failed
    logger.error(f"All recovery attempts failed for {filename}")
    return []
```

## Configuration Management

```python
from typing import Dict, Any

class ConfigManager:
    """
    Manage application configuration.
    """
    
    DEFAULT_CONFIG = {
        'backup_enabled': True,
        'backup_count': 10,
        'auto_save': True,
        'auto_save_interval': 60,  # seconds
        'data_format': 'json',
        'date_format': '%Y-%m-%d',
        'time_format': '%H:%M:%S'
    }
    
    def __init__(self, storage: FileStorage):
        """
        Initialize config manager.
        
        Args:
            storage: FileStorage instance
        """
        self.storage = storage
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        try:
            data = self.storage.load('config.json')
            if data:
                return {**self.DEFAULT_CONFIG, **data[0]}
        except:
            pass
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save configuration to file."""
        self.storage.save('config.json', [self.config])
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
        self.save_config()
```

## Usage Examples

### Basic Usage

```python
# Initialize storage
storage = FileStorage()

# Save contacts
contacts_data = [contact.to_dict() for contact in contacts]
storage.save('contacts.json', contacts_data)

# Load contacts
contacts_data = storage.load('contacts.json')
contacts = [Contact.from_dict(data) for data in contacts_data]
```

### With Backup

```python
# Create backup before saving
storage.create_backup('contacts.json')
storage.save('contacts.json', contacts_data)

# List available backups
backups = storage.list_backups('contacts.json')
for backup in backups:
    print(f"Backup: {backup['filename']} - {backup['timestamp']}")

# Restore from backup
storage.restore_from_backup('contacts.json')
```

### With Error Handling

```python
try:
    # Try to load data
    data = storage.load('contacts.json')
except CorruptedDataError:
    # Attempt recovery
    data = recover_from_corruption(storage, 'contacts.json')
    if not data:
        # Start fresh if recovery fails
        data = []
```

### Export/Import

```python
# Export all data
export_path = Path('/path/to/export')
storage.export_data(export_path)

# Import data
import_path = Path('/path/to/import')
storage.import_data(import_path)
```

## Testing Requirements

### Unit Tests

```python
def test_storage_initialization():
    """Test storage creates necessary directories."""
    pass

def test_save_and_load_data():
    """Test saving and loading data."""
    pass

def test_atomic_write():
    """Test atomic write prevents corruption."""
    pass

def test_create_backup():
    """Test backup creation."""
    pass

def test_restore_from_backup():
    """Test restoration from backup."""
    pass

def test_delete_old_backups():
    """Test cleanup of old backups."""
    pass

def test_corrupted_file_recovery():
    """Test recovery from corrupted file."""
    pass

def test_export_import_data():
    """Test data export and import."""
    pass

def test_config_management():
    """Test configuration save/load."""
    pass
```

## Best Practices

1. **Always use atomic writes**: Prevents data corruption
2. **Regular backups**: Create backups before major operations
3. **Error handling**: Catch and handle all file I/O errors
4. **Logging**: Log all storage operations for debugging
5. **Validation**: Validate data before saving
6. **Clean up**: Remove old backups to save space

## Performance Considerations

- Use lazy loading for large datasets
- Implement caching for frequently accessed data
- Batch write operations
- Use compression for large files (gzip)
- Consider SQLite for larger datasets (>10,000 records)

## Future Enhancements

- Support for multiple storage backends (SQLite, MongoDB)
- Encryption for sensitive data
- Compression for large files
- Cloud sync integration
- Automatic conflict resolution
- Delta updates (save only changes)
- Transaction support

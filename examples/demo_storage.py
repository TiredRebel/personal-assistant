"""
Demo script for FileStorage functionality.

This script demonstrates various FileStorage operations.
"""

from __future__ import annotations

from datetime import datetime

from personal_assistant.storage.file_storage import FileStorage


def create_sample_contacts() -> list[dict[str, str]]:
    """Create sample contact data."""
    return [
        {
            "name": "Олександр Шевченко",
            "phone": "+380671111111",
            "email": "oleksandr@example.com",
            "birthday": "1985-03-10",
        },
        {
            "name": "Наталія Бондаренко",
            "phone": "+380672222222",
            "email": "natalia@example.com",
            "address": "вул. Хрещатик, 1, Київ",
        },
        {
            "name": "Дмитро Коваленко",
            "phone": "+380673333333",
        },
    ]


def create_sample_notes() -> list[dict]:
    """Create sample note data."""
    return [
        {
            "title": "Список покупок",
            "content": "Молоко, хліб, яйця, масло",
            "tags": ["shopping", "home"],
            "created": datetime.now().isoformat(),
        },
        {
            "title": "Ідея для проекту",
            "content": "Створити додаток для управління задачами",
            "tags": ["work", "ideas", "development"],
            "created": datetime.now().isoformat(),
        },
        {
            "title": "Нагадування",
            "content": "Зателефонувати лікарю в середу о 10:00",
            "tags": ["health", "reminder"],
            "created": datetime.now().isoformat(),
        },
    ]


def main() -> None:
    """Run demo."""
    print("=" * 70)
    print("  FileStorage Demo")
    print("=" * 70)

    # Initialize storage
    storage = FileStorage()
    print(f"\nStorage initialized: {storage.base_dir}")

    # Create sample data
    contacts = create_sample_contacts()
    notes = create_sample_notes()

    # Save data
    print("\n1. Saving contacts...")
    if storage.save("contacts.json", contacts):
        print(f"   ✓ Saved {len(contacts)} contacts")

    print("\n2. Saving notes...")
    if storage.save("notes.json", notes):
        print(f"   ✓ Saved {len(notes)} notes")

    # Load data
    print("\n3. Loading contacts...")
    loaded_contacts = storage.load("contacts.json")
    print(f"   ✓ Loaded {len(loaded_contacts)} contacts")
    for contact in loaded_contacts:
        print(f"     - {contact['name']}: {contact['phone']}")

    # Create backup
    print("\n4. Creating backup...")
    if storage.create_backup("contacts.json"):
        print("   ✓ Backup created")

    # List backups
    print("\n5. Listing backups...")
    backups = storage.list_backups("contacts.json")
    print(f"   ✓ Found {len(backups)} backup(s)")
    for backup in backups:
        print(f"     - {backup['filename']} ({backup['size_mb']} MB)")

    print("\n" + "=" * 70)
    print("Demo completed! Now you can use:")
    print("  python -m personal_assistant.main --storage-info")
    print("  python -m personal_assistant.main --list-backups contacts.json")
    print("=" * 70)


if __name__ == "__main__":
    main()

"""
Personal Assistant - Main Entry Point

Простий CLI інтерфейс для роботи зі сховищем даних.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from personal_assistant.storage.file_storage import FileStorage


def print_header(title: str) -> None:
    """Вивести заголовок."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def create_parser() -> argparse.ArgumentParser:
    """Створити парсер аргументів командного рядка."""
    parser = argparse.ArgumentParser(
        prog="personal-assistant",
        description="Personal Assistant - Керування контактами та нотатками",
        epilog="Приклад: python -m personal_assistant.main --storage-info",
    )

    parser.add_argument("--storage-dir", type=Path, help="Директорія сховища")
    parser.add_argument("--storage-info", action="store_true", help="Інформація про сховище")
    parser.add_argument("--backup", metavar="FILE", help="Створити резервну копію файлу")
    parser.add_argument("--list-backups", metavar="FILE", help="Список резервних копій")
    parser.add_argument("--restore", metavar="FILE", help="Відновити з резервної копії")
    parser.add_argument("--export", metavar="DIR", help="Експортувати дані")
    parser.add_argument("--import", metavar="DIR", dest="import_dir", help="Імпортувати дані")

    return parser


def show_storage_info(storage: FileStorage) -> None:
    """Показати інформацію про сховище."""
    print_header("Інформація про сховище")
    print(f"Директорія:      {storage.base_dir}")
    print(f"Резервні копії:  {storage.backup_dir}")
    print(f"Лог-файл:        {storage.log_file}")

    data_files = sorted(storage.base_dir.glob("*.json"))
    if not data_files:
        print("\nФайли даних не знайдено.")
        return

    print(f"\nФайли даних ({len(data_files)}):")
    print(f"{'Файл':<25} {'Розмір':<12} {'Копії':<10}")
    print("-" * 50)

    for file in data_files:
        size_kb = file.stat().st_size / 1024
        backup_count = len(storage.list_backups(file.name))
        print(f"{file.name:<25} {size_kb:>8.2f} KB  {backup_count:>5}")


def create_backup(storage: FileStorage, filename: str) -> None:
    """Створити резервну копію файлу."""
    print(f"Створення резервної копії {filename}...")
    if storage.create_backup(filename):
        backups = storage.list_backups(filename)
        if backups:
            print(f"✓ Створено: {backups[0]['filename']}")
    else:
        print("✗ Помилка створення резервної копії")


def list_backups(storage: FileStorage, filename: str) -> None:
    """Показати список резервних копій."""
    backups = storage.list_backups(filename)
    if not backups:
        print(f"⚠ Резервні копії для {filename} не знайдено")
        return

    print_header(f"Резервні копії: {filename}")
    for i, backup in enumerate(backups, 1):
        time_str = backup["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i:2}. {backup['filename']:<45} {time_str}")


def restore_backup(storage: FileStorage, filename: str) -> None:
    """Відновити файл з резервної копії."""
    print(f"Відновлення {filename}...")
    if storage.restore_from_backup(filename):
        print("✓ Файл відновлено успішно")
    else:
        print("✗ Помилка відновлення (немає резервних копій?)")


def export_data(storage: FileStorage, path: str) -> None:
    """Експортувати дані."""
    export_dir = Path(path).expanduser().resolve()
    print(f"Експорт до {export_dir}...")
    if storage.export_data(export_dir):
        print(f"✓ Дані експортовано: {export_dir}")
    else:
        print("✗ Помилка експорту")


def import_data(storage: FileStorage, path: str) -> None:
    """Імпортувати дані."""
    import_dir = Path(path).expanduser().resolve()
    if not import_dir.exists():
        print(f"✗ Директорію не знайдено: {import_dir}")
        return

    print("⚠ УВАГА: Поточні дані будуть замінені!")
    if input("Продовжити? (yes/no): ").lower() != "yes":
        print("Імпорт скасовано")
        return

    if storage.import_data(import_dir):
        print("✓ Дані імпортовано успішно")
    else:
        print("✗ Помилка імпорту")


def main() -> None:
    """Головна функція програми."""
    parser = create_parser()
    args = parser.parse_args()

    # Ініціалізація сховища
    storage = FileStorage(base_dir=args.storage_dir)

    # Виконання команд
    if args.storage_info:
        show_storage_info(storage)
    elif args.backup:
        create_backup(storage, args.backup)
    elif args.list_backups:
        list_backups(storage, args.list_backups)
    elif args.restore:
        restore_backup(storage, args.restore)
    elif args.export:
        export_data(storage, args.export)
    elif args.import_dir:
        import_data(storage, args.import_dir)
    else:
        # Інтерактивний режим
        print_header("Personal Assistant")
        print("Доступні команди:")
        print("  --storage-info              - Інформація про сховище")
        print("  --backup FILE               - Створити резервну копію")
        print("  --list-backups FILE         - Список резервних копій")
        print("  --restore FILE              - Відновити з копії")
        print("  --export DIR                - Експортувати дані")
        print("  --import DIR                - Імпортувати дані")
        print("\nВикористання: python -m personal_assistant.main --help")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nДо побачення!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Помилка: {e}", file=sys.stderr)
        sys.exit(1)

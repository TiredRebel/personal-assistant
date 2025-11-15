"""
Демонстрація автодоповнення команд у Personal Assistant

Запустіть цей скрипт і натисніть Tab для автодоповнення команд.
"""

# Інструкція для користувача
print("=" * 60)
print("  АВТОДОПОВНЕННЯ КОМАНД")
print("=" * 60)
print()
print("У Personal Assistant є автодоповнення команд!")
print()
print("Як використовувати:")
print("  1. Запустіть: uv run python -m personal_assistant.main")
print("  2. Введіть початок команди, наприклад: 'add'")
print("  3. Натисніть TAB - команда автоматично доповниться")
print()
print("Доступні команди для доповнення:")
print("  - add-contact")
print("  - add-note")
print("  - search-contact")
print("  - search-note")
print("  - list-contacts")
print("  - list-notes")
print("  - edit-contact")
print("  - edit-note")
print("  - delete-contact")
print("  - delete-note")
print("  - birthdays")
print("  - search-by-tag")
print("  - list-tags")
print("  - help")
print("  - stats")
print("  - clear")
print("  - exit")
print()
print("=" * 60)
print()

# Тест автодоповнення
print("ТЕСТ: Автодоповнення працює?")

try:
    # Спробуємо імпортувати readline
    try:
        import readline
        print("✓ readline доступний (підтримка Tab completion)")
    except ImportError:
        try:
            import pyreadline3 as readline  # type: ignore
            print("✓ pyreadline3 доступний (підтримка Tab completion)")
        except ImportError:
            print("✗ readline не доступний")
            print("  Для Windows встановіть: pip install pyreadline3")
            print("  Для Linux/Mac: readline вже має бути в системі")
except Exception as e:
    print(f"✗ Помилка: {e}")

print()
print("Для активації автодоповнення запустіть:")
print("  uv run python -m personal_assistant.main")
print()

# Керівництво по використанню FileStorage

## Зміст
- [Огляд](#огляд)
- [Початок роботи](#початок-роботи)
- [Основні операції](#основні-операції)
- [Робота з резервними копіями](#робота-з-резервними-копіями)
- [Експорт та імпорт даних](#експорт-та-імпорт-даних)
- [Обробка помилок](#обробка-помилок)
- [Приклади використання](#приклади-використання)

## Огляд

`FileStorage` - це клас для зберігання даних у JSON файлах з підтримкою:
- Атомарного запису (запобігає пошкодженню даних)
- Автоматичних резервних копій
- Відновлення після помилок
- Експорту/імпорту даних
- Логування всіх операцій

## Початок роботи

### Імпорт та ініціалізація

```python
from pathlib import Path
from personal_assistant.storage import FileStorage

# Створення сховища з директорією за замовчуванням (~/.personal_assistant)
storage = FileStorage()

# Або вказати власну директорію
custom_dir = Path('/path/to/custom/directory')
storage = FileStorage(base_dir=custom_dir)
```

### Структура директорій

Після ініціалізації автоматично створюється:

```
~/.personal_assistant/
├── contacts.json           # Файли даних (створюються при збереженні)
├── notes.json
├── storage.log            # Лог файл
└── backups/               # Директорія резервних копій
    ├── contacts_20251112_180000.json
    └── notes_20251112_180000.json
```

## Основні операції

### Збереження даних

```python
# Підготовка даних (список словників)
contacts = [
    {
        "name": "Іван Петренко",
        "phone": "+380501234567",
        "email": "ivan@example.com",
        "birthday": "1990-05-15"
    },
    {
        "name": "Марія Коваль",
        "phone": "+380509876543",
        "email": "maria@example.com"
    }
]

# Збереження в файл
success = storage.save('contacts.json', contacts)

if success:
    print("Дані успішно збережено!")
else:
    print("Помилка при збереженні даних")
```

### Збереження даних з моделями

```python
from datetime import date
from personal_assistant.models.contact import Contact

# Створення контактів
contact1 = Contact(
    name="Іван Петренко",
    phone="+380501234567",
    email="ivan@example.com",
    birthday=date(1990, 5, 15)
)

contact2 = Contact(
    name="Марія Коваль",
    phone="+380509876543"
)

# Конвертація в словники для збереження
contacts_data = [contact1.to_dict(), contact2.to_dict()]

# Збереження
storage.save('contacts.json', contacts_data)
```

### Завантаження даних

```python
# Завантаження даних з файлу
contacts_data = storage.load('contacts.json')

# Якщо файл не існує, повертається порожній список
if contacts_data:
    print(f"Завантажено {len(contacts_data)} контактів")
else:
    print("Файл порожній або не існує")

# Виведення даних
for contact in contacts_data:
    print(f"{contact['name']}: {contact['phone']}")
```

### Завантаження даних у моделі

```python
from personal_assistant.models.contact import Contact

# Завантаження даних
contacts_data = storage.load('contacts.json')

# Конвертація у об'єкти Contact
contacts = [Contact.from_dict(data) for data in contacts_data]

# Використання
for contact in contacts:
    print(f"{contact.name}: {contact.phone}")
    if contact.birthday:
        days = contact.days_until_birthday()
        print(f"  До дня народження: {days} днів")
```

## Робота з резервними копіями

### Автоматичне створення резервних копій

```python
# При збереженні автоматично створюється резервна копія
# якщо файл вже існує
storage.save('contacts.json', contacts_data)
# Резервна копія: contacts_20251112_180530.json
```

### Ручне створення резервної копії

```python
# Створення резервної копії вручну
success = storage.create_backup('contacts.json')

if success:
    print("Резервну копію створено")
else:
    print("Помилка створення резервної копії")
```

### Перегляд доступних резервних копій

```python
# Отримання списку всіх резервних копій
backups = storage.list_backups('contacts.json')

print(f"Знайдено {len(backups)} резервних копій:")
for backup in backups:
    print(f"  - {backup['filename']}")
    print(f"    Дата: {backup['timestamp']}")
    print(f"    Розмір: {backup['size_mb']} МБ")
    print()
```

**Приклад виводу:**
```
Знайдено 3 резервних копій:
  - contacts_20251112_180530.json
    Дата: 2025-11-12 18:05:30
    Розмір: 0.01 МБ

  - contacts_20251112_120000.json
    Дата: 2025-11-12 12:00:00
    Розмір: 0.01 МБ

  - contacts_20251111_200000.json
    Дата: 2025-11-11 20:00:00
    Розмір: 0.01 МБ
```

### Відновлення з резервної копії

```python
from datetime import datetime

# Відновлення з останньої резервної копії
success = storage.restore_from_backup('contacts.json')

if success:
    print("Дані відновлено з останньої резервної копії")

# Відновлення з конкретної резервної копії за датою
backup_time = datetime(2025, 11, 11, 20, 0, 0)
success = storage.restore_from_backup('contacts.json', backup_time)

if success:
    print(f"Дані відновлено з резервної копії від {backup_time}")
```

### Очищення старих резервних копій

```python
# Видалення старих резервних копій (залишити тільки 5 останніх)
storage.delete_old_backups('contacts.json', keep_count=5)
print("Старі резервні копії видалено")

# За замовчуванням зберігається 10 останніх копій
# Це відбувається автоматично при створенні нової резервної копії
```

## Експорт та імпорт даних

### Експорт даних

```python
from pathlib import Path

# Експорт всіх даних у директорію
export_path = Path('C:/Users/Username/Desktop/backup_2025_11_12')
success = storage.export_data(export_path)

if success:
    print(f"Дані експортовано до {export_path}")
    # Створено:
    # - contacts.json
    # - notes.json
    # - export_manifest.json (інформація про експорт)
```

**Структура експорту:**
```
backup_2025_11_12/
├── contacts.json
├── notes.json
└── export_manifest.json
```

**Вміст export_manifest.json:**
```json
{
  "export_date": "2025-11-12T18:30:00",
  "files": [
    "contacts.json",
    "notes.json"
  ],
  "version": "1.0.0"
}
```

### Імпорт даних

```python
# Імпорт даних з директорії
import_path = Path('C:/Users/Username/Desktop/backup_2025_11_12')
success = storage.import_data(import_path)

if success:
    print("Дані успішно імпортовано")
    # Автоматично створено резервні копії поточних даних
    # перед імпортом
```

**Важливо:** При імпорті автоматично створюються резервні копії поточних даних!

## Обробка помилок

### Типи виключень

```python
from personal_assistant.storage import (
    FileStorage,
    StorageError,
    CorruptedDataError,
    BackupNotFoundError
)
```

### Обробка пошкоджених файлів

```python
try:
    # Спроба завантажити дані
    contacts = storage.load('contacts.json')

except CorruptedDataError as e:
    print(f"Файл пошкоджено: {e}")
    # FileStorage автоматично спробує відновити з резервної копії
    # Якщо відновлення успішне, поверне дані
    # Інакше поверне порожній список
```

### Автоматичне відновлення

FileStorage автоматично намагається відновити дані при виявленні пошкодження:

```python
# Якщо файл пошкоджено, автоматично:
# 1. Виявляє помилку JSON
# 2. Шукає останню робочу резервну копію
# 3. Відновлює дані з резервної копії
# 4. Повертає відновлені дані

contacts = storage.load('contacts.json')
# Якщо файл пошкоджено, дані будуть відновлені автоматично
```

### Логування помилок

```python
# Всі операції логуються у файл storage.log
# Перегляд логів:
import os

log_file = storage.base_dir / 'storage.log'
with open(log_file, 'r', encoding='utf-8') as f:
    logs = f.read()
    print(logs)
```

## Приклади використання

### Приклад 1: Повний цикл роботи з контактами

```python
from pathlib import Path
from datetime import date
from personal_assistant.storage import FileStorage
from personal_assistant.models.contact import Contact

# Ініціалізація
storage = FileStorage()

# 1. Створення контактів
contacts = [
    Contact(
        name="Олександр Шевченко",
        phone="+380671111111",
        email="oleksandr@example.com",
        birthday=date(1985, 3, 10)
    ),
    Contact(
        name="Наталія Бондаренко",
        phone="+380672222222",
        email="natalia@example.com",
        address="вул. Хрещатик, 1, Київ"
    ),
    Contact(
        name="Дмитро Коваленко",
        phone="+380673333333"
    )
]

# 2. Збереження
contacts_data = [c.to_dict() for c in contacts]
storage.save('contacts.json', contacts_data)
print(f"Збережено {len(contacts)} контактів")

# 3. Завантаження
loaded_data = storage.load('contacts.json')
loaded_contacts = [Contact.from_dict(data) for data in loaded_data]

# 4. Виведення інформації
print("\nЗавантажені контакти:")
for contact in loaded_contacts:
    print(f"\n{contact.name}")
    print(f"  Телефон: {contact.phone}")
    if contact.email:
        print(f"  Email: {contact.email}")
    if contact.birthday:
        days = contact.days_until_birthday()
        print(f"  До дня народження: {days} днів")

# 5. Створення резервної копії
storage.create_backup('contacts.json')
print("\n✓ Резервну копію створено")
```

### Приклад 2: Робота з нотатками та тегами

```python
from datetime import datetime

# Структура нотатки
notes = [
    {
        "title": "Список покупок",
        "content": "Молоко, хліб, яйця, масло",
        "tags": ["shopping", "home"],
        "created": datetime.now().isoformat()
    },
    {
        "title": "Ідея для проекту",
        "content": "Створити додаток для управління задачами",
        "tags": ["work", "ideas", "development"],
        "created": datetime.now().isoformat()
    }
]

# Збереження нотаток
storage.save('notes.json', notes)

# Завантаження та фільтрація за тегом
all_notes = storage.load('notes.json')
work_notes = [note for note in all_notes if 'work' in note['tags']]

print(f"Знайдено {len(work_notes)} робочих нотаток:")
for note in work_notes:
    print(f"  - {note['title']}")
```

### Приклад 3: Резервне копіювання перед масовими змінами

```python
# Перед масовими змінами створюємо резервну копію
print("Створення резервної копії...")
storage.create_backup('contacts.json')

# Завантаження даних
contacts = storage.load('contacts.json')

# Масові зміни (наприклад, оновлення формату телефонів)
for contact in contacts:
    phone = contact['phone']
    if not phone.startswith('+'):
        contact['phone'] = '+38' + phone.lstrip('0')

# Збереження змін
storage.save('contacts.json', contacts)
print("✓ Зміни збережено")

# У разі помилки можна відновити:
# storage.restore_from_backup('contacts.json')
```

### Приклад 4: Перенесення даних між комп'ютерами

```python
from pathlib import Path

# На комп'ютері 1: Експорт
print("=== Експорт даних ===")
export_path = Path.home() / 'Desktop' / 'personal_assistant_backup'
storage1 = FileStorage()

if storage1.export_data(export_path):
    print(f"✓ Дані експортовано до {export_path}")
    print("  Скопіюйте цю папку на інший комп'ютер")

# На комп'ютері 2: Імпорт
print("\n=== Імпорт даних ===")
import_path = Path.home() / 'Desktop' / 'personal_assistant_backup'
storage2 = FileStorage()

if storage2.import_data(import_path):
    print("✓ Дані успішно імпортовано")

    # Перевірка
    contacts = storage2.load('contacts.json')
    print(f"  Завантажено {len(contacts)} контактів")
```

### Приклад 5: Моніторинг та обслуговування

```python
import os
from datetime import datetime

def print_storage_info(storage):
    """Виведення інформації про стан сховища"""
    print("\n=== Інформація про сховище ===")
    print(f"Директорія: {storage.base_dir}")

    # Перевірка файлів даних
    data_files = list(storage.base_dir.glob('*.json'))
    print(f"\nФайли даних: {len(data_files)}")
    for file in data_files:
        size = file.stat().st_size
        print(f"  - {file.name}: {size / 1024:.2f} КБ")

    # Інформація про резервні копії
    for file in data_files:
        backups = storage.list_backups(file.name)
        print(f"\nРезервні копії для {file.name}: {len(backups)}")
        for backup in backups[:3]:  # Показати тільки 3 останні
            print(f"  - {backup['filename']}")
            print(f"    {backup['timestamp']}, {backup['size_mb']} МБ")

# Використання
storage = FileStorage()
print_storage_info(storage)

# Очищення старих резервних копій
print("\n=== Очищення старих резервних копій ===")
for file in storage.base_dir.glob('*.json'):
    storage.delete_old_backups(file.name, keep_count=5)
    print(f"✓ Оброблено {file.name}")
```

### Приклад 6: Інтеграція з основним додатком

```python
class ContactManager:
    """Менеджер контактів з інтегрованим сховищем"""

    def __init__(self):
        self.storage = FileStorage()
        self.contacts = self.load_contacts()

    def load_contacts(self):
        """Завантаження всіх контактів"""
        data = self.storage.load('contacts.json')
        return [Contact.from_dict(d) for d in data]

    def save_contacts(self):
        """Збереження всіх контактів"""
        data = [c.to_dict() for c in self.contacts]
        return self.storage.save('contacts.json', data)

    def add_contact(self, contact: Contact):
        """Додавання нового контакту"""
        self.contacts.append(contact)
        self.save_contacts()
        print(f"✓ Контакт '{contact.name}' додано")

    def search_by_name(self, query: str):
        """Пошук контактів за іменем"""
        query = query.lower()
        return [c for c in self.contacts if query in c.name.lower()]

    def backup(self):
        """Створення резервної копії"""
        self.storage.create_backup('contacts.json')
        print("✓ Резервну копію створено")

    def show_backups(self):
        """Показати всі резервні копії"""
        backups = self.storage.list_backups('contacts.json')
        print(f"\nДоступно {len(backups)} резервних копій:")
        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup['timestamp']} - {backup['size_mb']} МБ")

# Використання
manager = ContactManager()

# Додавання контакту
new_contact = Contact(
    name="Петро Іваненко",
    phone="+380674444444",
    email="petro@example.com"
)
manager.add_contact(new_contact)

# Пошук
results = manager.search_by_name("петро")
print(f"Знайдено {len(results)} контакт(ів)")

# Резервне копіювання
manager.backup()
manager.show_backups()
```

## Кращі практики

### 1. Регулярне резервне копіювання
```python
# Створюйте резервні копії перед важливими операціями
storage.create_backup('contacts.json')
# ... виконання операцій ...
```

### 2. Перевірка успішності операцій
```python
# Завжди перевіряйте результат операцій
if storage.save('contacts.json', data):
    print("✓ Збережено")
else:
    print("✗ Помилка збереження")
    # Обробка помилки
```

### 3. Використання контекстних менеджерів для важливих операцій
```python
def safe_update(storage, filename, update_func):
    """Безпечне оновлення даних з автоматичним резервним копіюванням"""
    # Створення резервної копії
    storage.create_backup(filename)

    try:
        # Завантаження даних
        data = storage.load(filename)

        # Застосування змін
        updated_data = update_func(data)

        # Збереження
        if storage.save(filename, updated_data):
            print("✓ Оновлення успішне")
            return True
    except Exception as e:
        print(f"✗ Помилка: {e}")
        # Відновлення з резервної копії
        storage.restore_from_backup(filename)
        print("✓ Дані відновлено з резервної копії")
        return False

# Використання
def add_tag_to_all(data):
    for item in data:
        if 'tags' not in item:
            item['tags'] = []
        item['tags'].append('migrated')
    return data

safe_update(storage, 'notes.json', add_tag_to_all)
```

### 4. Періодичне очищення
```python
# Регулярно очищайте старі резервні копії
import schedule

def cleanup_old_backups():
    storage = FileStorage()
    for file in storage.base_dir.glob('*.json'):
        storage.delete_old_backups(file.name, keep_count=10)

# Виконувати щотижня
schedule.every().week.do(cleanup_old_backups)
```

## Довідка по API

### FileStorage.__init__(base_dir=None)
Ініціалізує сховище.
- **base_dir**: Path | None - директорія для зберігання (за замовчуванням `~/.personal_assistant`)

### FileStorage.save(filename, data)
Зберігає дані у файл з автоматичним резервним копіюванням.
- **filename**: str - ім'я файлу (напр. 'contacts.json')
- **data**: list[dict] - список словників для збереження
- **Повертає**: bool - True якщо успішно

### FileStorage.load(filename)
Завантажує дані з файлу.
- **filename**: str - ім'я файлу
- **Повертає**: list[dict] - список словників або [] якщо файл не існує

### FileStorage.create_backup(filename)
Створює резервну копію файлу.
- **filename**: str - ім'я файлу
- **Повертає**: bool - True якщо успішно

### FileStorage.restore_from_backup(filename, backup_time=None)
Відновлює файл з резервної копії.
- **filename**: str - ім'я файлу
- **backup_time**: datetime | None - час резервної копії (за замовчуванням остання)
- **Повертає**: bool - True якщо успішно

### FileStorage.list_backups(filename)
Повертає список всіх резервних копій.
- **filename**: str - ім'я файлу
- **Повертає**: list[dict] - список з інформацією про копії

### FileStorage.delete_old_backups(filename, keep_count=10)
Видаляє старі резервні копії.
- **filename**: str - ім'я файлу
- **keep_count**: int - скільки копій залишити

### FileStorage.export_data(export_path)
Експортує всі дані.
- **export_path**: Path - шлях до директорії експорту
- **Повертає**: bool - True якщо успішно

### FileStorage.import_data(import_path)
Імпортує дані.
- **import_path**: Path - шлях до директорії з даними
- **Повертає**: bool - True якщо успішно

## Підтримка та вирішення проблем

### Проблема: Файл не зберігається
```python
# Перевірте права доступу до директорії
import os
print(f"Директорія: {storage.base_dir}")
print(f"Існує: {storage.base_dir.exists()}")
print(f"Можна записати: {os.access(storage.base_dir, os.W_OK)}")
```

### Проблема: Дані пошкоджені
```python
# FileStorage автоматично відновить з резервної копії
# Або відновіть вручну:
storage.restore_from_backup('contacts.json')
```

### Проблема: Забрак місця для резервних копій
```python
# Зменшіть кількість копій, що зберігаються
storage.delete_old_backups('contacts.json', keep_count=3)
```

### Перегляд логів
```python
# Всі операції логуються
log_file = storage.base_dir / 'storage.log'
with open(log_file, 'r', encoding='utf-8') as f:
    print(f.read())
```

## Висновок

FileStorage надає надійний та зручний інтерфейс для роботи з даними у форматі JSON. Основні переваги:

- ✅ Автоматичне резервне копіювання
- ✅ Атомарний запис (захист від пошкодження)
- ✅ Автоматичне відновлення при помилках
- ✅ Повне логування операцій
- ✅ Простий API
- ✅ Підтримка експорту/імпорту

Для додаткової інформації див. документацію модулів:
- [STORAGE_MODULE.md](STORAGE_MODULE.md) - технічна специфікація
- [ARCHITECTURE.md](ARCHITECTURE.md) - архітектура системи

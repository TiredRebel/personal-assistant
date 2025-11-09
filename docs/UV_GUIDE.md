# Using UV for Package Management 🚀

## Що таке uv?

**uv** - це надшвидкий інсталятор Python пакетів, написаний на Rust. Він замінює pip та venv, але працює набагато швидше.

### Переваги uv
- ⚡ **10-100x швидше** ніж pip
- 🦀 Написаний на **Rust** для максимальної швидкості
- 🔄 **Повністю сумісний** з pip та pyproject.toml
- 📦 **Краще розв'язання залежностей**
- 🎯 **Все в одному**: замінює pip, pip-tools, і virtualenv

## Встановлення uv

### macOS та Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Альтернативно (через pip)
```bash
pip install uv
```

### Перевірка встановлення
```bash
uv --version
```

## Основні команди для цього проекту

### Початкове налаштування

```bash
# 1. Перейти в директорію проекту
cd personal-assistant

# 2. Створити віртуальне середовище
uv venv

# 3. Активувати віртуальне середовище
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# 4. Встановити проект з залежностями
uv pip install -e ".[dev]"
```

### Щоденна робота

```bash
# Активувати середовище (якщо ще не активовано)
source .venv/bin/activate  # або .venv\Scripts\activate на Windows

# Встановити нову залежність
uv pip install package-name

# Встановити залежності для розробки
uv pip install -e ".[dev]"

# Встановити залежності з кольоровим виводом
uv pip install -e ".[colors]"
```

### Запуск програми

```bash
# Варіант 1: Використовуючи uv run (автоматично активує venv)
uv run personal-assistant

# Варіант 2: Прямий виклик (якщо venv активовано)
personal-assistant

# Варіант 3: Як модуль
uv run python -m personal_assistant.main
```

### Тестування

```bash
# Запустити всі тести
uv run pytest

# Запустити з покриттям коду
uv run pytest --cov=src/personal_assistant --cov-report=html

# Запустити конкретний тест
uv run pytest tests/test_contacts.py -v

# Запустити конкретну тестову функцію
uv run pytest tests/test_contacts.py::test_contact_creation -v
```

### Якість коду

```bash
# Форматування коду (Black)
uv run black src/ tests/

# Лінтинг (Pylint)
uv run pylint src/

# Перевірка типів (MyPy)
uv run mypy src/

# Перевірка стилю (Ruff)
uv run ruff check src/

# Запустити всі перевірки
uv run black src/ tests/ && \
uv run pylint src/ && \
uv run mypy src/ && \
uv run pytest --cov
```

## Робота з залежностями

### Додавання нової залежності

```bash
# 1. Додати в pyproject.toml у секцію [project.dependencies]
# 2. Встановити
uv pip install -e .
```

### Оновлення залежностей

```bash
# Оновити конкретний пакет
uv pip install --upgrade package-name

# Переустановити всі залежності
uv pip install -e ".[dev]" --force-reinstall
```

### Синхронізація залежностей

```bash
# Синхронізувати з pyproject.toml
uv pip sync
```

## Порівняння з pip

### pip vs uv

| Дія | pip | uv |
|-----|-----|-----|
| Створити venv | `python -m venv venv` | `uv venv` |
| Активувати venv | `source venv/bin/activate` | `source .venv/bin/activate` |
| Встановити пакет | `pip install package` | `uv pip install package` |
| Встановити з pyproject | `pip install -e .` | `uv pip install -e .` |
| Запустити скрипт | `python script.py` | `uv run python script.py` |
| Швидкість | Базова | **10-100x швидше!** |

### Міграція з pip

Якщо у вас вже є проект з requirements.txt:

```bash
# 1. Створити venv з uv
uv venv

# 2. Активувати
source .venv/bin/activate

# 3. Встановити з requirements.txt
uv pip install -r requirements.txt

# 4. (Опціонально) Перенести в pyproject.toml
# Скопіюйте залежності в секцію [project.dependencies]
```

## Швидкі команди

### Розробка

```bash
# Ранковий workflow
source .venv/bin/activate
git pull
uv run pytest -v

# Написання коду
# ... код ...

# Перевірка якості перед commit
uv run black src/ tests/
uv run pylint src/
uv run pytest --cov

# Commit
git add .
git commit -m "feat: your changes"
git push
```

### Debugging

```bash
# Запустити з дебаггером
uv run python -m pdb -m personal_assistant.main

# Запустити конкретний тест з виводом
uv run pytest tests/test_contacts.py -v -s

# Переглянути встановлені пакети
uv pip list

# Перевірити залежності
uv pip check
```

## Troubleshooting

### Проблема: uv команда не знайдена

```bash
# Рішення 1: Перезавантажити термінал
# Рішення 2: Додати до PATH вручну
export PATH="$HOME/.cargo/bin:$PATH"

# Рішення 3: Переустановити
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Проблема: Помилка при створенні venv

```bash
# Видалити стару venv
rm -rf .venv

# Створити нову
uv venv

# Переустановити залежності
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Проблема: Пакет не встановлюється

```bash
# Спробувати з verbose
uv pip install package-name -v

# Очистити кеш
uv cache clean

# Спробувати ще раз
uv pip install package-name
```

### Проблема: Конфлікт залежностей

```bash
# uv автоматично розв'язує конфлікти краще ніж pip
# Але якщо є проблеми:

# 1. Видалити venv
rm -rf .venv

# 2. Створити чисту venv
uv venv

# 3. Встановити по одному
uv pip install package1
uv pip install package2
```

## Продвинуті функції

### Використання uv run

```bash
# uv run автоматично активує venv і запускає команду
uv run python script.py
uv run pytest
uv run black src/

# Не потрібно вручну активувати venv!
```

### Кеш

```bash
# Показати інформацію про кеш
uv cache dir

# Очистити кеш
uv cache clean

# Показати розмір кешу
uv cache prune --dry-run
```

### Встановлення конкретної версії Python

```bash
# uv може встановити потрібну версію Python
uv python install 3.11
uv python install 3.12

# Використати конкретну версію
uv venv --python 3.11
```

## Best Practices

### 1. Завжди використовуйте uv run

```bash
# ✅ GOOD - автоматична активація venv
uv run pytest
uv run black src/

# ❌ BAD - потребує ручної активації
source .venv/bin/activate
pytest
```

### 2. Використовуйте pyproject.toml

```toml
# pyproject.toml - єдине джерело істини для залежностей
[project]
dependencies = [
    "python-dateutil>=2.8.2",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.7.0",
]
```

### 3. Commit .venv до .gitignore

```bash
# .gitignore
.venv/
__pycache__/
*.pyc
```

### 4. Документуйте команди

```bash
# README.md
## Setup
uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"

## Run
uv run personal-assistant

## Test
uv run pytest --cov
```

## Шпаргалка команд

```bash
# Встановлення
curl -LsSf https://astral.sh/uv/install.sh | sh

# Створення проекту
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Розробка
uv run pytest
uv run black src/
uv run mypy src/

# Додавання пакету
uv pip install package-name

# Запуск
uv run personal-assistant

# Оновлення uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Додаткові ресурси

- 📖 [Офіційна документація uv](https://github.com/astral-sh/uv)
- 🚀 [uv vs pip benchmarks](https://github.com/astral-sh/uv#benchmarks)
- 💡 [Migration guide](https://github.com/astral-sh/uv/blob/main/MIGRATION.md)

---

**uv робить Python розробку швидшою та приємнішою! 🎉**

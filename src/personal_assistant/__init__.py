"""
Personal Assistant - A CLI tool for managing contacts and notes

This package provides:
- Contact management with validation
- Note management with tags
- Intelligent command parsing
- Data persistence with backups
"""

from __future__ import annotations

from typing import Final
from .models import *
from .services import *
from .storage import *
from .validators import *
from .cli import *

__version__: Final[str] = "1.0.0"
__author__: Final[str] = "Your Team Name"

# Package metadata
__all__: list[str] = [
    "models",
    "services",
    "storage",
    "validators",
    "cli",
]

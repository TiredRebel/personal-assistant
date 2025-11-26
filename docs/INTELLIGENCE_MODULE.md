# Intelligence Module Specification

## Overview
The intelligence module provides smart command parsing and interpretation, allowing users to interact with the assistant using natural language-like commands.

## Goals
- Understand user intent from various command formats
- Suggest corrections for typos and ambiguous commands
- Support flexible command syntax
- Learn from user patterns (future enhancement)

## Command Parser

### Class: `CommandParser`

```python
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
import re

class CommandParser:
    """
    Intelligent command parser that interprets user input.

    Features:
    - Fuzzy command matching
    - Natural language understanding
    - Command suggestions
    - Argument extraction
    """

    # Command patterns and aliases
    COMMAND_PATTERNS = {
        'add-contact': [
            'add contact', 'new contact', 'create contact',
            'add person', 'new person', 'save contact'
        ],
        'search-contact': [
            'find contact', 'search contact', 'look for contact',
            'find person', 'search person', 'where is'
        ],
        'list-contacts': [
            'list contacts', 'show contacts', 'all contacts',
            'show all contacts', 'display contacts'
        ],
        'edit-contact': [
            'edit contact', 'update contact', 'change contact',
            'modify contact'
        ],
        'delete-contact': [
            'delete contact', 'remove contact', 'erase contact',
            'drop contact'
        ],
        'birthdays': [
            'birthdays', 'upcoming birthdays', 'show birthdays',
            'birthday reminder', 'who has birthday'
        ],
        'add-note': [
            'add note', 'new note', 'create note',
            'write note', 'save note'
        ],
        'search-note': [
            'find note', 'search note', 'look for note',
            'search notes'
        ],
        'list-notes': [
            'list notes', 'show notes', 'all notes',
            'show all notes', 'display notes'
        ],
        'edit-note': [
            'edit note', 'update note', 'change note',
            'modify note'
        ],
        'delete-note': [
            'delete note', 'remove note', 'erase note',
            'drop note'
        ],
        'search-by-tag': [
            'search by tag', 'find by tag', 'search tag',
            'notes with tag', 'filter by tag'
        ],
        'list-tags': [
            'list tags', 'show tags', 'all tags',
            'available tags'
        ],
        'help': [
            'help', 'h', '?', 'commands', 'what can you do'
        ],
        'exit': [
            'exit', 'quit', 'bye', 'goodbye', 'q'
        ]
    }

    def __init__(self):
        """Initialize command parser."""
        self.command_map = self._build_command_map()

    def _build_command_map(self) -> Dict[str, str]:
        """
        Build a mapping from patterns to canonical commands.

        Returns:
            Dictionary mapping pattern to command name
        """
        command_map = {}
        for command, patterns in self.COMMAND_PATTERNS.items():
            for pattern in patterns:
                command_map[pattern.lower()] = command
        return command_map

    def parse(self, input_str: str) -> Optional[Dict]:
        """
        Parse user input into command and arguments.

        Args:
            input_str: Raw user input

        Returns:
            Dictionary with 'command' and 'args', or None if not recognized
        """
        input_str = input_str.strip().lower()

        # Try exact match first
        if input_str in self.command_map:
            return {
                'command': self.command_map[input_str],
                'args': {}
            }

        # Try fuzzy matching
        command, confidence = self._fuzzy_match_command(input_str)
        if command and confidence > 0.7:
            return {
                'command': command,
                'args': self._extract_arguments(input_str),
                'confidence': confidence
            }

        # Try natural language parsing
        parsed = self._parse_natural_language(input_str)
        if parsed:
            return parsed

        return None

    def _fuzzy_match_command(self, input_str: str) -> Tuple[Optional[str], float]:
        """
        Find the best matching command using fuzzy matching.

        Args:
            input_str: User input

        Returns:
            Tuple of (command_name, confidence_score)
        """
        best_match = None
        best_score = 0.0

        for pattern, command in self.command_map.items():
            # Calculate similarity
            score = SequenceMatcher(None, input_str, pattern).ratio()

            # Check if input starts with pattern
            if input_str.startswith(pattern):
                score += 0.2  # Bonus for prefix match

            # Check word overlap
            input_words = set(input_str.split())
            pattern_words = set(pattern.split())
            word_overlap = len(input_words & pattern_words) / len(pattern_words)
            score += word_overlap * 0.3

            if score > best_score:
                best_score = score
                best_match = command

        return best_match, best_score

    def _parse_natural_language(self, input_str: str) -> Optional[Dict]:
        """
        Parse natural language commands.

        Examples:
        - "show me all contacts" -> list-contacts
        - "find john's phone" -> search-contact with query "john"
        - "add a note about meeting" -> add-note

        Args:
            input_str: Natural language input

        Returns:
            Parsed command dictionary or None
        """
        # Intent patterns
        intent_patterns = {
            'add-contact': [
                r'(add|create|new|save)\s+(a\s+)?(contact|person)',
            ],
            'search-contact': [
                r'(find|search|look\s+for|where\s+is)\s+(.*?)\s*(phone|email|contact)?',
            ],
            'list-contacts': [
                r'(show|list|display)\s+(all\s+)?(contacts|people)',
            ],
            'add-note': [
                r'(add|create|new|write)\s+(a\s+)?(note)\s+(about\s+)?',
            ],
            'search-note': [
                r'(find|search|look\s+for)\s+(notes?)\s+(about\s+)?',
            ],
            'list-notes': [
                r'(show|list|display)\s+(all\s+)?(notes)',
            ],
            'birthdays': [
                r'(show|list|who\s+has)\s+.*birthday',
            ]
        }

        for command, patterns in intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, input_str, re.IGNORECASE)
                if match:
                    # Extract query/arguments from the match
                    args = {}
                    if len(match.groups()) > 2 and match.group(2):
                        args['query'] = match.group(2).strip()

                    return {
                        'command': command,
                        'args': args,
                        'confidence': 0.85
                    }

        return None

    def _extract_arguments(self, input_str: str) -> Dict:
        """
        Extract arguments from command string.

        Args:
            input_str: Command string

        Returns:
            Dictionary of extracted arguments
        """
        args = {}

        # Extract quoted strings
        quoted = re.findall(r'"([^"]*)"', input_str)
        if quoted:
            args['values'] = quoted

        # Extract options (--key value)
        options = re.findall(r'--(\w+)\s+([^\s--]+)', input_str)
        for key, value in options:
            args[key] = value

        return args

    def suggest_commands(self, input_str: str, max_suggestions: int = 3) -> List[str]:
        """
        Suggest commands based on partial or misspelled input.

        Args:
            input_str: User input
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggested commands
        """
        input_str = input_str.strip().lower()
        suggestions = []

        # Calculate similarity scores for all commands
        scores = []
        for pattern, command in self.command_map.items():
            score = SequenceMatcher(None, input_str, pattern).ratio()

            # Bonus for matching first letters
            if pattern.startswith(input_str[:2]):
                score += 0.2

            scores.append((command, pattern, score))

        # Sort by score and remove duplicates
        scores.sort(key=lambda x: x[2], reverse=True)
        seen_commands = set()

        for command, pattern, score in scores:
            if command not in seen_commands and score > 0.4:
                suggestions.append(f"{command} ({pattern})")
                seen_commands.add(command)
                if len(suggestions) >= max_suggestions:
                    break

        return suggestions

    def get_command_help(self, command: str) -> str:
        """
        Get help text for a specific command.

        Args:
            command: Command name

        Returns:
            Help text string
        """
        help_texts = {
            'add-contact': """
Add a new contact to your address book.
Usage: add-contact
      You will be prompted for contact details.
            """,
            'search-contact': """
Search for contacts by name, phone, or email.
Usage: search-contact
      You will be prompted for a search query.
            """,
            'add-note': """
Create a new note with optional tags.
Usage: add-note
      You will be prompted for note content and tags.
            """,
            'search-by-tag': """
Search notes by tags (can specify multiple tags).
Usage: search-by-tag
      You will be prompted for tags.
            """
        }

        return help_texts.get(command, "No help available for this command.")


class SmartCommandParser(CommandParser):
    """
    Enhanced command parser with learning capabilities.
    """

    def __init__(self):
        super().__init__()
        self.command_history = []
        self.user_patterns = {}

    def learn_from_usage(self, input_str: str, selected_command: str):
        """
        Learn from user's command usage to improve suggestions.

        Args:
            input_str: Original user input
            selected_command: Command that was executed
        """
        # Record the pattern
        input_pattern = input_str.strip().lower()

        if selected_command not in self.user_patterns:
            self.user_patterns[selected_command] = []

        if input_pattern not in self.user_patterns[selected_command]:
            self.user_patterns[selected_command].append(input_pattern)

        # Keep command history
        self.command_history.append({
            'input': input_str,
            'command': selected_command,
            'timestamp': datetime.now()
        })

    def suggest_based_on_history(self) -> List[str]:
        """
        Suggest commands based on user's history.

        Returns:
            List of frequently used commands
        """
        if not self.command_history:
            return []

        # Count command frequency
        command_counts = {}
        for entry in self.command_history:
            cmd = entry['command']
            command_counts[cmd] = command_counts.get(cmd, 0) + 1

        # Return top commands
        sorted_commands = sorted(
            command_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [cmd for cmd, count in sorted_commands[:5]]
```

## Intent Recognition

### Class: `IntentRecognizer`

```python
class IntentRecognizer:
    """
    Recognize user intent from natural language input.
    """

    # Action keywords
    ACTION_KEYWORDS = {
        'add': ['add', 'create', 'new', 'make', 'insert', 'save'],
        'search': ['find', 'search', 'look for', 'where', 'locate'],
        'edit': ['edit', 'update', 'change', 'modify', 'alter'],
        'delete': ['delete', 'remove', 'erase', 'drop', 'destroy'],
        'list': ['list', 'show', 'display', 'view', 'all'],
    }

    # Entity keywords
    ENTITY_KEYWORDS = {
        'contact': ['contact', 'person', 'phone', 'number'],
        'note': ['note', 'memo', 'reminder', 'text'],
        'birthday': ['birthday', 'birth date', 'born'],
        'tag': ['tag', 'label', 'category'],
    }

    @classmethod
    def recognize_intent(cls, text: str) -> Dict:
        """
        Recognize intent from text.

        Args:
            text: User input text

        Returns:
            Dictionary with action and entity
        """
        text_lower = text.lower()

        # Detect action
        action = None
        for act, keywords in cls.ACTION_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                action = act
                break

        # Detect entity
        entity = None
        for ent, keywords in cls.ENTITY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                entity = ent
                break

        return {
            'action': action,
            'entity': entity,
            'confidence': 0.8 if action and entity else 0.5
        }

    @classmethod
    def extract_parameters(cls, text: str, intent: Dict) -> Dict:
        """
        Extract parameters based on recognized intent.

        Args:
            text: User input text
            intent: Recognized intent

        Returns:
            Dictionary of extracted parameters
        """
        params = {}

        # Extract names (capitalized words)
        names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        if names:
            params['name'] = names[0]

        # Extract phone numbers
        phones = re.findall(
            r'\+?\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{1,4}[\s-]?\d{1,4}[\s-]?\d{1,9}',
            text
        )
        if phones:
            params['phone'] = phones[0]

        # Extract emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            params['email'] = emails[0]

        # Extract tags (words starting with #)
        tags = re.findall(r'#(\w+)', text)
        if tags:
            params['tags'] = tags

        return params
```

## Usage Examples

### Basic Command Parsing

```python
parser = CommandParser()

# Parse exact command
result = parser.parse("add contact")
# Returns: {'command': 'add-contact', 'args': {}}

# Parse with typo
result = parser.parse("add conact")
# Returns: {'command': 'add-contact', 'args': {}, 'confidence': 0.85}

# Parse natural language
result = parser.parse("show me all contacts")
# Returns: {'command': 'list-contacts', 'args': {}}

# Parse with arguments
result = parser.parse('search contact "John Doe"')
# Returns: {'command': 'search-contact', 'args': {'values': ['John Doe']}}
```

### Command Suggestions

```python
# Get suggestions for typo
suggestions = parser.suggest_commands("add contct")
# Returns: ['add-contact (add contact)', 'add-note (add note)', ...]

# Get suggestions for partial input
suggestions = parser.suggest_commands("sea")
# Returns: ['search-contact (search contact)', 'search-note (search note)', ...]
```

### Intent Recognition

```python
recognizer = IntentRecognizer()

# Recognize intent
text = "I want to add a new contact John Doe"
intent = recognizer.recognize_intent(text)
# Returns: {'action': 'add', 'entity': 'contact', 'confidence': 0.8}

# Extract parameters
params = recognizer.extract_parameters(text, intent)
# Returns: {'name': 'John Doe'}
```

### Smart Parser with Learning

```python
smart_parser = SmartCommandParser()

# Use command
result = smart_parser.parse("add person")
# User executes the command...

# Learn from usage
smart_parser.learn_from_usage("add person", "add-contact")

# Next time, "add person" will have higher confidence
suggestions = smart_parser.suggest_based_on_history()
# Returns most frequently used commands
```

## Testing Requirements

```python
def test_exact_command_match():
    """Test exact command matching."""
    parser = CommandParser()
    result = parser.parse("add contact")
    assert result['command'] == 'add-contact'

def test_fuzzy_command_match():
    """Test fuzzy command matching."""
    parser = CommandParser()
    result = parser.parse("add conact")  # typo
    assert result['command'] == 'add-contact'
    assert result['confidence'] > 0.7

def test_natural_language_parsing():
    """Test natural language command parsing."""
    parser = CommandParser()
    result = parser.parse("show me all contacts")
    assert result['command'] == 'list-contacts'

def test_command_suggestions():
    """Test command suggestions."""
    parser = CommandParser()
    suggestions = parser.suggest_commands("add con")
    assert 'add-contact' in [s.split()[0] for s in suggestions]

def test_intent_recognition():
    """Test intent recognition."""
    intent = IntentRecognizer.recognize_intent("add a new contact")
    assert intent['action'] == 'add'
    assert intent['entity'] == 'contact'

def test_parameter_extraction():
    """Test parameter extraction."""
    params = IntentRecognizer.extract_parameters(
        "Add contact John Doe +380501234567",
        {'action': 'add', 'entity': 'contact'}
    )
    assert 'name' in params
    assert 'phone' in params
```

## Best Practices

1. **Fuzzy matching threshold**: Use confidence scores to avoid false positives
2. **User feedback**: Ask for confirmation on low-confidence matches
3. **Learning**: Record successful commands to improve suggestions
4. **Context awareness**: Consider previous commands in the session
5. **Fallback**: Always provide a way to see available commands

## Future Enhancements

- Machine learning-based intent recognition
- Context-aware parsing (remember previous commands)
- Multi-turn dialogue support
- Voice command support
- Autocomplete as user types
- Personalized command shortcuts
- Command macros (combine multiple commands)

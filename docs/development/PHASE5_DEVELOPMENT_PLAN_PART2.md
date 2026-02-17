# Phase 5: Implementation & Development Plan - Part 2

## Continuation of Detailed Implementation Steps

---

## PHASE 5.2: Configuration System

**Duration:** 2-3 days  
**Branch:** `feature/configuration-system`  
**Dependencies:** Phase 5.1 (Config model)

### Overview

Build a robust configuration management system that handles user preferences, application settings, and persistent storage.

### Success Criteria

- [ ] ConfigManager class implemented
- [ ] Default config creation and initialization
- [ ] Config file loading/saving with atomic writes
- [ ] Config validation and migration
- [ ] Environment variable overrides
- [ ] Unit tests with 85%+ coverage

### Step-by-Step Implementation

#### Step 2.1: Create ConfigManager

**File:** `arenaagent/config/manager.py`

**Purpose:** Manage application configuration with persistence

**Implementation Checklist:**

- [ ] Create `ConfigManager` class with methods:
  - `__init__(config_dir: Optional[str] = None)` - Initialize manager
  - `load() -> Config` - Load config from file or create default
  - `save(config: Config) -> None` - Save config to file (atomic write)
  - `get() -> Config` - Get current config
  - `update(**kwargs) -> None` - Update specific config values
  - `reset() -> Config` - Reset to default configuration
  - `get_config_path() -> Path` - Get config file path

- [ ] Implement features:
  - Atomic file writes (write to temp, then rename)
  - Config file validation
  - Automatic backup before save
  - Config migration for version updates
  - Environment variable overrides

**Key Methods Implementation Guide:**

```python
"""Configuration management."""

from pathlib import Path
from typing import Optional
import json
import os
import shutil
from datetime import datetime

from arenaagent.models.config import Config


class ConfigManager:
    """Manages application configuration."""
    
    DEFAULT_CONFIG_DIR = Path.home() / ".arenaagent"
    CONFIG_FILENAME = "config.json"
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_dir = Path(config_dir) if config_dir else self.DEFAULT_CONFIG_DIR
        self.config_path = self.config_dir / self.CONFIG_FILENAME
        self._config: Optional[Config] = None
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Config:
        """Load configuration from file or create default."""
        pass
    
    def save(self, config: Config) -> None:
        """Save configuration to file with atomic write."""
        pass
    
    def get(self) -> Config:
        """Get current configuration."""
        pass
    
    def update(self, **kwargs) -> None:
        """Update specific configuration values."""
        pass
    
    def reset(self) -> Config:
        """Reset to default configuration."""
        pass
```

**Test File:** `tests/unit/test_config_manager.py`

**Test Cases:**
```python
def test_load_default_config_when_no_file_exists()
def test_load_existing_config_from_file()
def test_save_config_with_atomic_write()
def test_update_specific_config_values()
def test_reset_to_default_creates_backup()
def test_environment_variable_overrides()
def test_handle_corrupted_config_file()
def test_config_validation_on_save()
def test_config_directory_creation()
```

---

#### Step 2.2: Create Config Package Init

**File:** `arenaagent/config/__init__.py`

```python
"""Configuration management for ArenaAgent."""

from arenaagent.config.manager import ConfigManager

__all__ = ["ConfigManager"]
```

---

### Phase 5.2 Completion Checklist

- [ ] ConfigManager implemented with all features
- [ ] Atomic file writes working
- [ ] Environment variable overrides working
- [ ] Config validation before save
- [ ] All unit tests passing (10+ tests)
- [ ] Code coverage ≥ 85%
- [ ] Documentation updated

### Git Workflow

```bash
git checkout -b feature/configuration-system
git add arenaagent/config/manager.py tests/unit/test_config_manager.py
git commit -m "feat: implement ConfigManager with atomic writes and env overrides"
git add arenaagent/config/__init__.py
git commit -m "feat: export ConfigManager in package init"
make test && make lint && make typecheck
git checkout develop
git merge feature/configuration-system
git branch -d feature/configuration-system
```

---

## PHASE 5.3: Session Management

**Duration:** 3-4 days  
**Branch:** `feature/session-management`  
**Dependencies:** Phase 5.1 (Session model), Phase 5.2 (Config)

### Overview

Build session management system for creating, loading, saving, and archiving conversation sessions.

### Success Criteria

- [ ] SessionManager class implemented
- [ ] CRUD operations for sessions
- [ ] Session persistence to JSON files
- [ ] Session listing and filtering
- [ ] Session archiving
- [ ] Active session tracking
- [ ] Unit tests with 85%+ coverage

### Implementation Files

#### Step 3.1: Create SessionManager

**File:** `arenaagent/session/manager.py`

**Purpose:** Manage conversation sessions

**Key Features:**
- Create new sessions
- Load/save sessions from/to disk
- List all sessions (active and archived)
- Get current active session
- Archive old sessions
- Delete sessions
- Session directory management

**Class Structure:**

```python
"""Session management."""

from pathlib import Path
from typing import List, Optional
from datetime import datetime
import json

from arenaagent.models.session import Session
from arenaagent.models.message import Message


class SessionManager:
    """Manages conversation sessions."""
    
    DEFAULT_SESSION_DIR = Path.home() / ".arenaagent" / "sessions"
    
    def __init__(self, session_dir: Optional[str] = None):
        """Initialize session manager."""
        self.session_dir = Path(session_dir) if session_dir else self.DEFAULT_SESSION_DIR
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self._active_session: Optional[Session] = None
    
    def create_session(self, name: str, working_directory: Optional[str] = None) -> Session:
        """Create a new session."""
        pass
    
    def load_session(self, session_id: str) -> Session:
        """Load a session by ID."""
        pass
    
    def save_session(self, session: Session) -> None:
        """Save a session to disk."""
        pass
    
    def list_sessions(self, include_archived: bool = False) -> List[Session]:
        """List all sessions."""
        pass
    
    def get_active_session(self) -> Optional[Session]:
        """Get the currently active session."""
        pass
    
    def set_active_session(self, session: Session) -> None:
        """Set the active session."""
        pass
    
    def archive_session(self, session_id: str) -> None:
        """Archive a session."""
        pass
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        pass
    
    def get_session_path(self, session_id: str) -> Path:
        """Get path to session file."""
        pass
```

**Test File:** `tests/unit/test_session_manager.py`

**Test Cases:**
```python
def test_create_new_session()
def test_save_session_to_disk()
def test_load_session_from_disk()
def test_list_active_sessions()
def test_list_all_sessions_including_archived()
def test_set_and_get_active_session()
def test_archive_session()
def test_delete_session()
def test_session_directory_creation()
def test_session_not_found_error()
```

---

#### Step 3.2: Create Session Package Init

**File:** `arenaagent/session/__init__.py`

```python
"""Session management for ArenaAgent."""

from arenaagent.session.manager import SessionManager

__all__ = ["SessionManager"]
```

---

### Phase 5.3 Completion Checklist

- [ ] SessionManager fully implemented
- [ ] All CRUD operations working
- [ ] Session persistence verified
- [ ] Active session tracking working
- [ ] All unit tests passing (15+ tests)
- [ ] Code coverage ≥ 85%

### Git Workflow

```bash
git checkout -b feature/session-management
git add arenaagent/session/manager.py tests/unit/test_session_manager.py
git commit -m "feat: implement SessionManager with CRUD operations"
git add arenaagent/session/__init__.py
git commit -m "feat: export SessionManager in package init"
make test && make lint
git checkout develop
git merge feature/session-management
```

---

## PHASE 5.4: Utilities & Helpers

**Duration:** 2-3 days  
**Branch:** `feature/utilities`  
**Dependencies:** Phase 5.2 (Config)

### Overview

Build utility modules for logging, formatting, validation, and common helpers.

### Modules to Implement

---

#### Step 4.1: Logger Utility

**File:** `arenaagent/utils/logger.py`

**Purpose:** Centralized logging configuration

**Features:**
- File and console handlers
- Rotating file logs
- Colored console output (using Rich)
- Log levels from config
- Module-specific loggers

**Implementation Guide:**

```python
"""Logging utilities."""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from typing import Optional


def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    console: bool = True,
    file: bool = True
) -> logging.Logger:
    """Setup and configure logger.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
        console: Enable console logging
        file: Enable file logging
        
    Returns:
        Configured logger instance
    """
    pass


def get_logger(name: str) -> logging.Logger:
    """Get logger by name."""
    pass
```

**Test File:** `tests/unit/test_logger.py`

---

#### Step 4.2: Formatters Utility

**File:** `arenaagent/utils/formatters.py`

**Purpose:** Format data for display

**Features:**
- Format messages for Rich display
- Format execution results
- Format timestamps
- Syntax highlighting for code
- Table formatting helpers

**Key Functions:**

```python
"""Formatting utilities."""

from rich.syntax import Syntax
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
from typing import List, Dict, Any

from arenaagent.models.message import Message
from arenaagent.models.execution import ExecutionResult


def format_message(message: Message) -> Panel:
    """Format a message for display."""
    pass


def format_execution_result(result: ExecutionResult) -> Panel:
    """Format execution result for display."""
    pass


def format_code(code: str, language: str = "python") -> Syntax:
    """Format code with syntax highlighting."""
    pass


def format_timestamp(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    pass


def create_table(headers: List[str], rows: List[List[Any]]) -> Table:
    """Create a Rich table."""
    pass
```

**Test File:** `tests/unit/test_formatters.py`

---

#### Step 4.3: Validators Utility

**File:** `arenaagent/utils/validators.py`

**Purpose:** Validation functions

**Features:**
- Validate file paths
- Validate URLs
- Validate command safety
- Validate JSON structure

**Key Functions:**

```python
"""Validation utilities."""

from pathlib import Path
from typing import Any
import re


def validate_path(path: str, must_exist: bool = False) -> bool:
    """Validate file/directory path."""
    pass


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pass


def is_safe_command(command: str) -> bool:
    """Check if command is safe to execute."""
    pass


def validate_json_structure(data: Any, required_keys: list) -> bool:
    """Validate JSON structure has required keys."""
    pass
```

**Test File:** `tests/unit/test_validators.py`

---

#### Step 4.4: File Helpers Utility

**File:** `arenaagent/utils/file_helpers.py`

**Purpose:** File operation helpers

**Features:**
- Atomic file writes
- Safe file operations
- Directory management
- File size utilities

**Key Functions:**

```python
"""File operation utilities."""

from pathlib import Path
from typing import Union
import shutil


def atomic_write(file_path: Path, content: str) -> None:
    """Write file atomically (temp + rename)."""
    pass


def safe_delete(file_path: Path) -> bool:
    """Safely delete file with error handling."""
    pass


def ensure_directory(dir_path: Path) -> None:
    """Ensure directory exists, create if not."""
    pass


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    pass


def copy_with_backup(src: Path, dst: Path) -> None:
    """Copy file, backing up destination if it exists."""
    pass
```

**Test File:** `tests/unit/test_file_helpers.py`

---

#### Step 4.5: Utils Package Init

**File:** `arenaagent/utils/__init__.py`

```python
"""Utility modules for ArenaAgent."""

from arenaagent.utils.logger import setup_logger, get_logger
from arenaagent.utils.formatters import (
    format_message,
    format_execution_result,
    format_code,
    format_timestamp,
    create_table,
)
from arenaagent.utils.validators import (
    validate_path,
    validate_url,
    is_safe_command,
    validate_json_structure,
)
from arenaagent.utils.file_helpers import (
    atomic_write,
    safe_delete,
    ensure_directory,
    get_file_size,
    copy_with_backup,
)

__all__ = [
    "setup_logger",
    "get_logger",
    "format_message",
    "format_execution_result",
    "format_code",
    "format_timestamp",
    "create_table",
    "validate_path",
    "validate_url",
    "is_safe_command",
    "validate_json_structure",
    "atomic_write",
    "safe_delete",
    "ensure_directory",
    "get_file_size",
    "copy_with_backup",
]
```

---

### Phase 5.4 Completion Checklist

- [ ] Logger utility implemented
- [ ] Formatters utility implemented
- [ ] Validators utility implemented
- [ ] File helpers utility implemented
- [ ] All utilities tested (20+ tests total)
- [ ] Code coverage ≥ 85%
- [ ] Package init exports all utilities

### Git Workflow

```bash
git checkout -b feature/utilities

# Implement each utility module
git add arenaagent/utils/logger.py tests/unit/test_logger.py
git commit -m "feat: implement logger utility with Rich handler"

git add arenaagent/utils/formatters.py tests/unit/test_formatters.py
git commit -m "feat: implement formatters utility"

git add arenaagent/utils/validators.py tests/unit/test_validators.py
git commit -m "feat: implement validators utility"

git add arenaagent/utils/file_helpers.py tests/unit/test_file_helpers.py
git commit -m "feat: implement file helpers utility"

git add arenaagent/utils/__init__.py
git commit -m "feat: export all utilities in package init"

make test && make lint
git checkout develop
git merge feature/utilities
```

---


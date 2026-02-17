# Phase 5: Implementation & Development Plan

## Document Overview

This document provides a comprehensive, step-by-step guide for implementing ArenaAgent from scratch. Follow this plan sequentially to build a fully functional AI coding assistant.

**Version:** 1.0  
**Status:** Ready for Development  
**Estimated Timeline:** 6-8 weeks  
**Last Updated:** 2026-02-17

---

## Table of Contents

1. [Development Philosophy](#development-philosophy)
2. [Pre-Development Checklist](#pre-development-checklist)
3. [Phase Overview](#phase-overview)
4. [Detailed Implementation Steps](#detailed-implementation-steps)
5. [Testing Strategy](#testing-strategy)
6. [Quality Assurance](#quality-assurance)
7. [Deployment Checklist](#deployment-checklist)

---

## Development Philosophy

### Core Principles

1. **Feature-by-Feature Development**
   - Complete one feature entirely before moving to next
   - Each feature must be tested and verified
   - No partial implementations

2. **Modular Architecture**
   - Single Responsibility Principle
   - Loose coupling, high cohesion
   - Reusable components

3. **Branch-Based Workflow**
   - One branch per feature
   - Never commit to main/develop directly
   - Merge only after tests pass

4. **Test-Driven Mindset**
   - Write tests alongside code
   - Minimum 80% code coverage
   - Integration tests for critical paths

---

## Pre-Development Checklist

Before starting implementation, ensure:

- [ ] Development environment setup complete
- [ ] Virtual environment activated
- [ ] Dependencies installed (`make install-dev`)
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Git repository initialized
- [ ] All design documents reviewed
- [ ] This development plan reviewed and understood

### Environment Verification

Run these commands to verify setup:

```bash
# Verify Python version
python --version  # Should be 3.11+

# Verify dependencies
pip list | grep playwright
pip list | grep click
pip list | grep rich

# Verify pre-commit
pre-commit --version

# Run setup verification script
python scripts/verify_setup.py
```

**Expected Output:** All checks should pass ✅

---

## 📚 Complete Development Plan Structure

This comprehensive development plan is divided into **6 parts** for easier navigation:

### Document Index

1. **[PHASE5_DEVELOPMENT_PLAN.md](PHASE5_DEVELOPMENT_PLAN.md)** (This Document)
   - Development Philosophy
   - Pre-Development Checklist
   - Phase Overview & Timeline
   - **Phase 5.1: Core Data Models** (Detailed)

2. **[PHASE5_DEVELOPMENT_PLAN_PART2.md](PHASE5_DEVELOPMENT_PLAN_PART2.md)**
   - **Phase 5.2: Configuration System**
   - **Phase 5.3: Session Management**
   - **Phase 5.4: Utilities & Helpers**

3. **[PHASE5_DEVELOPMENT_PLAN_PART3.md](PHASE5_DEVELOPMENT_PLAN_PART3.md)**
   - **Phase 5.5: Browser Automation**
   - **Phase 5.6: Code Executor**
   - **Phase 5.7: File Operations**

4. **[PHASE5_DEVELOPMENT_PLAN_PART4.md](PHASE5_DEVELOPMENT_PLAN_PART4.md)**
   - **Phase 5.8: Core Agent Logic**
   - **Phase 5.9: CLI Interface**

5. **[PHASE5_DEVELOPMENT_PLAN_PART5.md](PHASE5_DEVELOPMENT_PLAN_PART5.md)**
   - **Phase 5.10: Integration & Testing**
   - **Phase 5.11: Polish & Documentation**

6. **[PHASE5_DEVELOPMENT_PLAN_PART6.md](PHASE5_DEVELOPMENT_PLAN_PART6.md)**
   - **Phase 5.12: Final QA & Release**
   - Project Summary
   - Post-Release Tasks
   - Next Steps

### Quick Navigation Guide

**Just Starting?** → Read this document first, then proceed to Part 2

**Building Core Components?** → Parts 1-3 (Models, Config, Session, Utils, Browser, Executor, Files)

**Integrating Everything?** → Part 4 (Core Agent, CLI)

**Testing & Documentation?** → Part 5 (Tests, Docs, Examples)

**Ready to Release?** → Part 6 (QA, Release, Next Steps)

---

## Phase Overview

### Timeline and Milestones

| Phase | Focus Area | Duration | Deliverables |
|-------|-----------|----------|--------------|
| 5.1 | Core Data Models | 3-4 days | Message, Session, Config, ExecutionResult models |
| 5.2 | Configuration System | 2-3 days | Config management, settings, persistence |
| 5.3 | Session Management | 3-4 days | Session CRUD, history, context tracking |
| 5.4 | Utilities & Helpers | 2-3 days | Logging, formatters, validators |
| 5.5 | Browser Automation | 5-7 days | Playwright integration, LM Arena connector |
| 5.6 | Code Executor | 4-5 days | Safe subprocess execution, output capture |
| 5.7 | File Operations | 3-4 days | File tracking, backup/restore, diff generation |
| 5.8 | Core Agent Logic | 5-7 days | AgentCore, request/response, error recovery |
| 5.9 | CLI Interface | 4-5 days | Click commands, Rich UI, user interaction |
| 5.10 | Integration & Testing | 5-7 days | End-to-end tests, integration tests |
| 5.11 | Polish & Documentation | 3-4 days | API docs, user guide, examples |
| 5.12 | Final QA & Release | 2-3 days | Final testing, release prep |

**Total Estimated Time:** 6-8 weeks

### Dependency Graph

```
Phase 5.1 (Data Models)
    ↓
Phase 5.2 (Configuration) + Phase 5.4 (Utilities)
    ↓
Phase 5.3 (Session Management)
    ↓
Phase 5.5 (Browser) + Phase 5.6 (Executor) + Phase 5.7 (Files)
    ↓
Phase 5.8 (Core Agent)
    ↓
Phase 5.9 (CLI)
    ↓
Phase 5.10 (Integration Testing)
    ↓
Phase 5.11 (Documentation)
    ↓
Phase 5.12 (Release)
```

---

## Detailed Implementation Steps

---

## PHASE 5.1: Core Data Models (Foundation)

**Duration:** 3-4 days  
**Branch:** `feature/core-data-models`  
**Priority:** CRITICAL (Foundation for everything)

### Overview

Build the core data structures that represent messages, sessions, configurations, and execution results. These models are the backbone of the entire application.

### Success Criteria

- [ ] All model classes implemented with type hints
- [ ] JSON serialization/deserialization working
- [ ] Validation logic implemented
- [ ] Unit tests with 90%+ coverage
- [ ] Models documented with docstrings

### Step-by-Step Implementation

#### Step 1.1: Create Message Model

**File:** `arenaagent/models/message.py`

**Purpose:** Represent a single message in a conversation (user or assistant)

**Implementation Checklist:**

- [ ] Create `Message` class with attributes:
  - `id`: str (UUID)
  - `role`: Literal["user", "assistant", "system"]
  - `content`: str
  - `timestamp`: datetime
  - `model`: Optional[str] (which LM Arena model was used)
  - `metadata`: Dict[str, Any] (arbitrary data)

- [ ] Implement methods:
  - `to_dict() -> dict` - Serialize to JSON-compatible dict
  - `from_dict(data: dict) -> Message` - Deserialize from dict
  - `__repr__()` - Human-readable representation
  - `__str__()` - String representation

- [ ] Add validation:
  - Role must be valid
  - Content cannot be empty
  - Timestamp format validation
  - UUID format validation

**Expected Code Structure:**

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, Literal
import uuid
import json

@dataclass
class Message:
    """Represents a single message in a conversation."""
    
    role: Literal["user", "assistant", "system"]
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    model: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert message to JSON-compatible dictionary."""
        # Implementation here
        pass
    
    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Create message from dictionary."""
        # Implementation here
        pass
    
    def validate(self) -> None:
        """Validate message data."""
        # Implementation here
        pass
```

**Test File:** `tests/unit/test_message.py`

**Test Cases to Write:**

```python
def test_message_creation():
    """Test creating a message with default values."""
    pass

def test_message_serialization():
    """Test converting message to dict."""
    pass

def test_message_deserialization():
    """Test creating message from dict."""
    pass

def test_message_validation_invalid_role():
    """Test validation fails for invalid role."""
    pass

def test_message_validation_empty_content():
    """Test validation fails for empty content."""
    pass

def test_message_timestamp_format():
    """Test timestamp is properly formatted."""
    pass
```

**Expected Output:**

```bash
pytest tests/unit/test_message.py -v

test_message.py::test_message_creation PASSED
test_message.py::test_message_serialization PASSED
test_message.py::test_message_deserialization PASSED
test_message.py::test_message_validation_invalid_role PASSED
test_message.py::test_message_validation_empty_content PASSED
test_message.py::test_message_timestamp_format PASSED

6 passed in 0.05s
```

---

#### Step 1.2: Create Session Model

**File:** `arenaagent/models/session.py`

**Purpose:** Represent a conversation session with message history

**Implementation Checklist:**

- [ ] Create `Session` class with attributes:
  - `id`: str (UUID)
  - `name`: str (user-friendly session name)
  - `created_at`: datetime
  - `updated_at`: datetime
  - `messages`: List[Message]
  - `status`: Literal["active", "archived", "error"]
  - `working_directory`: str (where code executes)
  - `metadata`: Dict[str, Any]

- [ ] Implement methods:
  - `add_message(message: Message) -> None`
  - `get_messages(role: Optional[str] = None) -> List[Message]`
  - `get_context(max_messages: int = 10) -> str`
  - `to_dict() -> dict`
  - `from_dict(data: dict) -> Session`
  - `save(path: str) -> None` - Save to JSON file
  - `load(path: str) -> Session` - Load from JSON file
  - `archive() -> None` - Mark session as archived

- [ ] Add validation:
  - Name cannot be empty
  - Working directory must exist
  - Messages must be valid Message objects
  - Status must be valid

**Expected Code Structure:**

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pathlib import Path
import json
import uuid

from arenaagent.models.message import Message

@dataclass
class Session:
    """Represents a conversation session."""
    
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: List[Message] = field(default_factory=list)
    status: Literal["active", "archived", "error"] = "active"
    working_directory: str = field(default_factory=lambda: str(Path.cwd()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: Message) -> None:
        """Add a message to the session."""
        # Implementation here
        pass
    
    def get_messages(self, role: Optional[str] = None) -> List[Message]:
        """Get messages, optionally filtered by role."""
        # Implementation here
        pass
    
    def get_context(self, max_messages: int = 10) -> str:
        """Get conversation context as formatted string."""
        # Implementation here
        pass
    
    def to_dict(self) -> dict:
        """Convert session to JSON-compatible dictionary."""
        # Implementation here
        pass
    
    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create session from dictionary."""
        # Implementation here
        pass
    
    def save(self, path: str) -> None:
        """Save session to JSON file."""
        # Implementation here
        pass
    
    @classmethod
    def load(cls, path: str) -> "Session":
        """Load session from JSON file."""
        # Implementation here
        pass
    
    def archive(self) -> None:
        """Archive this session."""
        # Implementation here
        pass
```

**Test File:** `tests/unit/test_session.py`

**Test Cases to Write:**

```python
def test_session_creation()
def test_add_message()
def test_get_messages_all()
def test_get_messages_by_role()
def test_session_serialization()
def test_session_deserialization()
def test_session_save_to_file()
def test_session_load_from_file()
def test_session_archive()
def test_get_context()
```

**Expected Output:**
- All tests pass
- Session can be saved/loaded from JSON
- Message history preserved correctly

---

#### Step 1.3: Create Configuration Model

**File:** `arenaagent/models/config.py`

**Purpose:** Represent user configuration and preferences

**Implementation Checklist:**

- [ ] Create `Config` class with attributes:
  - `browser_headless`: bool (run browser in background)
  - `browser_user_data_dir`: str (persistent browser profile)
  - `default_model`: str (preferred LM Arena model)
  - `auto_execute`: bool (automatically run generated code)
  - `max_retries`: int (error recovery attempts)
  - `session_timeout`: int (minutes before session expires)
  - `working_directory`: str (default workspace)
  - `log_level`: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
  - `lm_arena_url`: str (LM Arena website URL)

- [ ] Implement methods:
  - `to_dict() -> dict`
  - `from_dict(data: dict) -> Config`
  - `save(path: str) -> None`
  - `load(path: str) -> Config`
  - `get_default() -> Config` - Returns default configuration
  - `validate() -> None`

- [ ] Add validation:
  - max_retries must be positive
  - session_timeout must be positive
  - log_level must be valid
  - URLs must be valid format

**Expected Code Structure:**

```python
from dataclasses import dataclass, field
from typing import Literal
from pathlib import Path
import json

@dataclass
class Config:
    """Application configuration."""
    
    # Browser settings
    browser_headless: bool = True
    browser_user_data_dir: str = field(
        default_factory=lambda: str(Path.home() / ".arenaagent" / "browser_data")
    )
    
    # Model settings
    default_model: str = "claude-3-sonnet"
    
    # Execution settings
    auto_execute: bool = True
    max_retries: int = 3
    session_timeout: int = 60  # minutes
    
    # Directory settings
    working_directory: str = field(default_factory=lambda: str(Path.cwd()))
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    
    # LM Arena
    lm_arena_url: str = "https://lmarena.ai"
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        pass
    
    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create config from dictionary."""
        pass
    
    def save(self, path: str) -> None:
        """Save config to JSON file."""
        pass
    
    @classmethod
    def load(cls, path: str) -> "Config":
        """Load config from JSON file."""
        pass
    
    @classmethod
    def get_default(cls) -> "Config":
        """Get default configuration."""
        return cls()
    
    def validate(self) -> None:
        """Validate configuration values."""
        pass
```

**Test File:** `tests/unit/test_config.py`

**Test Cases:**
- Default config creation
- Config serialization/deserialization
- Config save/load
- Validation tests
- Invalid value handling

---

#### Step 1.4: Create ExecutionResult Model

**File:** `arenaagent/models/execution.py`

**Purpose:** Represent the result of code execution

**Implementation Checklist:**

- [ ] Create `ExecutionResult` class with attributes:
  - `command`: str (command that was executed)
  - `stdout`: str (standard output)
  - `stderr`: str (standard error)
  - `exit_code`: int (process exit code)
  - `duration`: float (execution time in seconds)
  - `timestamp`: datetime
  - `success`: bool (True if exit_code == 0)
  - `working_directory`: str
  - `environment_vars`: Dict[str, str]

- [ ] Implement methods:
  - `to_dict() -> dict`
  - `from_dict(data: dict) -> ExecutionResult`
  - `is_error() -> bool`
  - `get_error_message() -> str`
  - `__repr__()`

**Expected Code Structure:**

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict

@dataclass
class ExecutionResult:
    """Result of code execution."""
    
    command: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    working_directory: str = ""
    environment_vars: Dict[str, str] = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.exit_code == 0
    
    def is_error(self) -> bool:
        """Check if execution resulted in error."""
        return not self.success
    
    def get_error_message(self) -> str:
        """Get formatted error message."""
        pass
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        pass
    
    @classmethod
    def from_dict(cls, data: dict) -> "ExecutionResult":
        """Create from dictionary."""
        pass
```

**Test File:** `tests/unit/test_execution.py`

**Test Cases:**
- Successful execution result
- Failed execution result
- Error message formatting
- Serialization/deserialization

---

#### Step 1.5: Create Models Package Init

**File:** `arenaagent/models/__init__.py`

**Purpose:** Export all models for easy importing

**Implementation:**

```python
"""Data models for ArenaAgent."""

from arenaagent.models.message import Message
from arenaagent.models.session import Session
from arenaagent.models.config import Config
from arenaagent.models.execution import ExecutionResult

__all__ = [
    "Message",
    "Session",
    "Config",
    "ExecutionResult",
]
```

---

### Phase 5.1 Completion Checklist

- [ ] All model files created and implemented
- [ ] Type hints on all methods and attributes
- [ ] Comprehensive docstrings (Google style)
- [ ] All unit tests written and passing
- [ ] Code coverage ≥ 90%
- [ ] Code formatted with black and isort
- [ ] No mypy type errors
- [ ] No pylint warnings
- [ ] All tests pass in CI pipeline
- [ ] Documentation updated

### Verification Commands

```bash
# Run tests
pytest tests/unit/test_message.py -v
pytest tests/unit/test_session.py -v
pytest tests/unit/test_config.py -v
pytest tests/unit/test_execution.py -v

# Check coverage
pytest tests/unit/ --cov=arenaagent.models --cov-report=term-missing

# Type check
mypy arenaagent/models/

# Format code
black arenaagent/models/
isort arenaagent/models/

# Lint
pylint arenaagent/models/
```

### Expected Final Output

```
Tests: 40+ tests, all passing
Coverage: 90%+ for models module
Type Checking: 0 errors
Linting: 0 errors, score > 9.0/10
```

### Git Workflow

```bash
# Create branch
git checkout -b feature/core-data-models

# Implement and test each model
git add arenaagent/models/message.py tests/unit/test_message.py
git commit -m "feat: implement Message model with tests"

git add arenaagent/models/session.py tests/unit/test_session.py
git commit -m "feat: implement Session model with tests"

git add arenaagent/models/config.py tests/unit/test_config.py
git commit -m "feat: implement Config model with tests"

git add arenaagent/models/execution.py tests/unit/test_execution.py
git commit -m "feat: implement ExecutionResult model with tests"

git add arenaagent/models/__init__.py
git commit -m "feat: export all models in __init__"

# Final verification
make test
make lint
make typecheck

# Merge to develop
git checkout develop
git merge feature/core-data-models
git push origin develop

# Delete feature branch
git branch -d feature/core-data-models
```

---


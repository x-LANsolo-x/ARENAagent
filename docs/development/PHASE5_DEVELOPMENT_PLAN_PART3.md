# Phase 5: Implementation & Development Plan - Part 3

## Advanced Implementation Phases

---

## PHASE 5.5: Browser Automation

**Duration:** 5-7 days  
**Branch:** `feature/browser-automation`  
**Dependencies:** Phase 5.2 (Config), Phase 5.4 (Utils)  
**Priority:** HIGH (Core functionality)

### Overview

Build browser automation using Playwright to interact with LM Arena. This is one of the most critical components as it enables communication with the AI.

### Success Criteria

- [ ] Browser controller implemented
- [ ] LM Arena connector working
- [ ] Message sending/receiving functional
- [ ] Session persistence across browser restarts
- [ ] Error handling and retries
- [ ] Screenshot capture for debugging
- [ ] Integration tests with mock browser
- [ ] Code coverage ≥ 75%

---

### Step 5.1: Browser Controller

**File:** `arenaagent/browser/controller.py`

**Purpose:** Manage Playwright browser lifecycle and state

**Implementation Checklist:**

- [ ] Create `BrowserController` class
- [ ] Async browser launch and management
- [ ] Persistent browser context (user data dir)
- [ ] Page management
- [ ] Browser cleanup on exit
- [ ] Screenshot capture
- [ ] Error recovery

**Key Implementation:**

```python
"""Browser controller using Playwright."""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from pathlib import Path
from typing import Optional
import asyncio

from arenaagent.models.config import Config
from arenaagent.utils.logger import get_logger


class BrowserController:
    """Manages Playwright browser instance."""
    
    def __init__(self, config: Config):
        """Initialize browser controller.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
    
    async def start(self) -> None:
        """Start the browser and create persistent context."""
        self.logger.info("Starting browser...")
        
        # Start Playwright
        self._playwright = await async_playwright().start()
        
        # Launch browser
        self._browser = await self._playwright.chromium.launch(
            headless=self.config.browser_headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Create persistent context
        user_data_dir = Path(self.config.browser_user_data_dir)
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        self._context = await self._browser.new_context(
            user_data_dir=str(user_data_dir),
            viewport={'width': 1280, 'height': 720}
        )
        
        # Create page
        self._page = await self._context.new_page()
        
        self.logger.info("Browser started successfully")
    
    async def stop(self) -> None:
        """Stop the browser and cleanup."""
        self.logger.info("Stopping browser...")
        
        if self._page:
            await self._page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        
        self.logger.info("Browser stopped")
    
    async def get_page(self) -> Page:
        """Get the current page."""
        if not self._page:
            raise RuntimeError("Browser not started. Call start() first.")
        return self._page
    
    async def is_running(self) -> bool:
        """Check if browser is running."""
        return self._browser is not None and self._browser.is_connected()
    
    async def restart(self) -> None:
        """Restart the browser."""
        await self.stop()
        await self.start()
    
    async def screenshot(self, path: str) -> None:
        """Take a screenshot."""
        if self._page:
            await self._page.screenshot(path=path)
            self.logger.debug(f"Screenshot saved to {path}")
```

**Test File:** `tests/unit/test_browser_controller.py`

**Test Cases:**
```python
@pytest.mark.asyncio
async def test_start_browser()
async def test_stop_browser()
async def test_get_page()
async def test_is_running()
async def test_restart_browser()
async def test_screenshot()
async def test_browser_not_started_error()
```

---

### Step 5.2: LM Arena Connector

**File:** `arenaagent/browser/lm_arena.py`

**Purpose:** Interact with LM Arena website

**Implementation Checklist:**

- [ ] Navigate to LM Arena
- [ ] Wait for page load
- [ ] Select model from dropdown
- [ ] Send messages to chat
- [ ] Wait for and extract responses
- [ ] Handle rate limits
- [ ] Detect and handle errors
- [ ] Retry logic

**Key Implementation:**

```python
"""LM Arena connector."""

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout
from typing import Optional
import asyncio

from arenaagent.browser.controller import BrowserController
from arenaagent.models.config import Config
from arenaagent.utils.logger import get_logger


class LMArenaConnector:
    """Connects to and interacts with LM Arena."""
    
    # CSS Selectors (Update these based on actual LM Arena structure)
    CHAT_INPUT_SELECTOR = "textarea[placeholder*='message']"
    SEND_BUTTON_SELECTOR = "button[type='submit']"
    RESPONSE_SELECTOR = ".assistant-message:last-child"
    MODEL_SELECTOR = "select[name='model']"
    
    def __init__(self, browser_controller: BrowserController, config: Config):
        """Initialize LM Arena connector.
        
        Args:
            browser_controller: Browser controller instance
            config: Application configuration
        """
        self.browser = browser_controller
        self.config = config
        self.logger = get_logger(__name__)
        self._page: Optional[Page] = None
    
    async def connect(self) -> None:
        """Connect to LM Arena."""
        self.logger.info("Connecting to LM Arena...")
        
        self._page = await self.browser.get_page()
        
        # Navigate to LM Arena
        await self._page.goto(self.config.lm_arena_url, wait_until="networkidle")
        
        self.logger.info("Connected to LM Arena")
    
    async def select_model(self, model: str) -> None:
        """Select a specific model.
        
        Args:
            model: Model name to select
        """
        if not self._page:
            raise RuntimeError("Not connected. Call connect() first.")
        
        self.logger.info(f"Selecting model: {model}")
        
        try:
            await self._page.select_option(self.MODEL_SELECTOR, model)
            await asyncio.sleep(1)  # Wait for model to load
        except Exception as e:
            self.logger.warning(f"Could not select model: {e}")
    
    async def send_message(self, message: str) -> None:
        """Send a message to the chat.
        
        Args:
            message: Message to send
        """
        if not self._page:
            raise RuntimeError("Not connected. Call connect() first.")
        
        self.logger.info("Sending message to LM Arena")
        
        # Wait for chat input to be available
        await self._page.wait_for_selector(self.CHAT_INPUT_SELECTOR, timeout=10000)
        
        # Type message
        await self._page.fill(self.CHAT_INPUT_SELECTOR, message)
        
        # Click send button
        await self._page.click(self.SEND_BUTTON_SELECTOR)
        
        self.logger.info("Message sent")
    
    async def get_response(self, timeout: int = 60000) -> str:
        """Wait for and get the response.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            The assistant's response text
        """
        if not self._page:
            raise RuntimeError("Not connected. Call connect() first.")
        
        self.logger.info("Waiting for response...")
        
        try:
            # Wait for response to appear
            await self._page.wait_for_selector(
                self.RESPONSE_SELECTOR,
                timeout=timeout,
                state="visible"
            )
            
            # Extract response text
            response = await self._page.text_content(self.RESPONSE_SELECTOR)
            
            self.logger.info("Response received")
            return response.strip() if response else ""
            
        except PlaywrightTimeout:
            self.logger.error("Timeout waiting for response")
            raise TimeoutError("No response from LM Arena within timeout")
    
    async def is_ready(self) -> bool:
        """Check if LM Arena is ready for interaction."""
        if not self._page:
            return False
        
        try:
            await self._page.wait_for_selector(self.CHAT_INPUT_SELECTOR, timeout=5000)
            return True
        except:
            return False
    
    async def handle_rate_limit(self) -> None:
        """Handle rate limiting by waiting."""
        self.logger.warning("Rate limit detected, waiting...")
        await asyncio.sleep(30)  # Wait 30 seconds
```

**Test File:** `tests/integration/test_lm_arena.py`

**Test Cases:**
```python
@pytest.mark.asyncio
async def test_connect_to_lm_arena()
async def test_select_model()
async def test_send_message()
async def test_get_response()
async def test_is_ready()
async def test_timeout_on_no_response()
```

---

### Step 5.3: Browser Package Init

**File:** `arenaagent/browser/__init__.py`

```python
"""Browser automation for ArenaAgent."""

from arenaagent.browser.controller import BrowserController
from arenaagent.browser.lm_arena import LMArenaConnector

__all__ = ["BrowserController", "LMArenaConnector"]
```

---

### Phase 5.5 Completion Checklist

- [ ] BrowserController fully implemented
- [ ] LMArenaConnector fully implemented
- [ ] Browser starts and stops correctly
- [ ] Messages can be sent to LM Arena
- [ ] Responses can be received
- [ ] Error handling works
- [ ] All tests passing (10+ tests)
- [ ] Code coverage ≥ 75%

### Git Workflow

```bash
git checkout -b feature/browser-automation

git add arenaagent/browser/controller.py tests/unit/test_browser_controller.py
git commit -m "feat: implement BrowserController with Playwright"

git add arenaagent/browser/lm_arena.py tests/integration/test_lm_arena.py
git commit -m "feat: implement LMArenaConnector for chat interaction"

git add arenaagent/browser/__init__.py
git commit -m "feat: export browser components"

make test
git checkout develop
git merge feature/browser-automation
```

---

## PHASE 5.6: Code Executor

**Duration:** 4-5 days  
**Branch:** `feature/code-executor`  
**Dependencies:** Phase 5.1 (ExecutionResult), Phase 5.4 (Utils)

### Overview

Build safe code execution system with subprocess management, output capture, and security validations.

### Success Criteria

- [ ] CommandExecutor implemented
- [ ] Safe subprocess execution
- [ ] Real-time output capture
- [ ] Timeout handling
- [ ] Process cleanup
- [ ] Security validations
- [ ] Unit and integration tests
- [ ] Code coverage ≥ 80%

---

### Implementation

**File:** `arenaagent/executor/command.py`

**Purpose:** Execute shell commands safely

**Key Features:**
- Execute commands in subprocess
- Capture stdout/stderr in real-time
- Handle timeouts
- Process cleanup
- Environment variable management
- Working directory support
- Command validation

**Implementation:**

```python
"""Command execution."""

import subprocess
import asyncio
from pathlib import Path
from typing import Optional, Dict
import time
from datetime import datetime

from arenaagent.models.execution import ExecutionResult
from arenaagent.utils.logger import get_logger
from arenaagent.utils.validators import is_safe_command


class CommandExecutor:
    """Executes shell commands safely."""
    
    # Dangerous commands that should be blocked
    DANGEROUS_COMMANDS = [
        'rm -rf /',
        'mkfs',
        'dd if=/dev/zero',
        'fork bomb',
        ':(){:|:&};:',
    ]
    
    def __init__(self, working_directory: Optional[str] = None, timeout: int = 300):
        """Initialize command executor.
        
        Args:
            working_directory: Directory to execute commands in
            timeout: Maximum execution time in seconds
        """
        self.working_directory = Path(working_directory) if working_directory else Path.cwd()
        self.timeout = timeout
        self.logger = get_logger(__name__)
    
    async def execute(
        self,
        command: str,
        env: Optional[Dict[str, str]] = None,
        capture_output: bool = True
    ) -> ExecutionResult:
        """Execute a command.
        
        Args:
            command: Command to execute
            env: Environment variables
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            ExecutionResult with output and exit code
        """
        # Validate command
        if not is_safe_command(command):
            self.logger.error(f"Unsafe command blocked: {command}")
            return ExecutionResult(
                command=command,
                stderr="Command blocked for security reasons",
                exit_code=1,
                working_directory=str(self.working_directory)
            )
        
        self.logger.info(f"Executing command: {command}")
        start_time = time.time()
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
                cwd=str(self.working_directory),
                env=env
            )
            
            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            duration = time.time() - start_time
            
            result = ExecutionResult(
                command=command,
                stdout=stdout.decode() if stdout else "",
                stderr=stderr.decode() if stderr else "",
                exit_code=process.returncode or 0,
                duration=duration,
                timestamp=datetime.now(),
                working_directory=str(self.working_directory),
                environment_vars=env or {}
            )
            
            if result.success:
                self.logger.info(f"Command executed successfully in {duration:.2f}s")
            else:
                self.logger.warning(f"Command failed with exit code {result.exit_code}")
            
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"Command timed out after {self.timeout}s")
            return ExecutionResult(
                command=command,
                stderr=f"Command timed out after {self.timeout} seconds",
                exit_code=124,  # Standard timeout exit code
                duration=self.timeout,
                working_directory=str(self.working_directory)
            )
        
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return ExecutionResult(
                command=command,
                stderr=str(e),
                exit_code=1,
                duration=time.time() - start_time,
                working_directory=str(self.working_directory)
            )
    
    def set_working_directory(self, directory: str) -> None:
        """Set working directory for command execution."""
        self.working_directory = Path(directory)
        self.logger.info(f"Working directory set to: {directory}")
```

**Test File:** `tests/unit/test_command_executor.py`

**Test Cases:**
```python
@pytest.mark.asyncio
async def test_execute_simple_command()
async def test_execute_command_with_output()
async def test_execute_command_with_error()
async def test_command_timeout()
async def test_unsafe_command_blocked()
async def test_custom_working_directory()
async def test_environment_variables()
async def test_execution_result_details()
```

---

### Executor Package Init

**File:** `arenaagent/executor/__init__.py`

```python
"""Code execution for ArenaAgent."""

from arenaagent.executor.command import CommandExecutor

__all__ = ["CommandExecutor"]
```

---

### Phase 5.6 Completion Checklist

- [ ] CommandExecutor implemented
- [ ] Command validation working
- [ ] Timeout handling working
- [ ] Output capture working
- [ ] Security checks in place
- [ ] All tests passing (10+ tests)
- [ ] Code coverage ≥ 80%

### Git Workflow

```bash
git checkout -b feature/code-executor
git add arenaagent/executor/command.py tests/unit/test_command_executor.py
git commit -m "feat: implement CommandExecutor with safety checks"
git add arenaagent/executor/__init__.py
git commit -m "feat: export CommandExecutor"
make test
git checkout develop
git merge feature/code-executor
```

---

## PHASE 5.7: File Operations

**Duration:** 3-4 days  
**Branch:** `feature/file-operations`  
**Dependencies:** Phase 5.4 (Utils)

### Overview

Build file tracking, backup, and modification management system.

### Success Criteria

- [ ] FileTracker implemented
- [ ] Backup/restore functionality
- [ ] File diff generation
- [ ] File monitoring
- [ ] Rollback support
- [ ] Unit tests with 85%+ coverage

---

### Implementation Files

#### File Tracker

**File:** `arenaagent/files/tracker.py`

**Purpose:** Track file modifications and changes

**Key Features:**
- Track which files are modified
- Create snapshots before changes
- Generate diffs between versions
- Restore previous versions
- List all tracked files

**Implementation:**

```python
"""File tracking and monitoring."""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import difflib

from arenaagent.utils.logger import get_logger
from arenaagent.utils.file_helpers import atomic_write


class FileTracker:
    """Tracks file modifications."""
    
    def __init__(self, working_directory: str):
        """Initialize file tracker.
        
        Args:
            working_directory: Directory to track files in
        """
        self.working_directory = Path(working_directory)
        self.logger = get_logger(__name__)
        self._tracked_files: Dict[str, Dict] = {}
    
    def track_file(self, file_path: str) -> None:
        """Start tracking a file.
        
        Args:
            file_path: Path to file to track
        """
        path = Path(file_path)
        
        if not path.exists():
            self.logger.warning(f"File does not exist: {file_path}")
            return
        
        # Calculate file hash
        file_hash = self._calculate_hash(path)
        
        # Store file info
        self._tracked_files[str(path)] = {
            'path': str(path),
            'original_hash': file_hash,
            'current_hash': file_hash,
            'tracked_at': datetime.now(),
            'modified': False
        }
        
        self.logger.info(f"Now tracking: {file_path}")
    
    def is_modified(self, file_path: str) -> bool:
        """Check if a tracked file has been modified.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is modified, False otherwise
        """
        if file_path not in self._tracked_files:
            return False
        
        path = Path(file_path)
        if not path.exists():
            return True  # File was deleted
        
        current_hash = self._calculate_hash(path)
        original_hash = self._tracked_files[file_path]['original_hash']
        
        return current_hash != original_hash
    
    def get_modified_files(self) -> List[str]:
        """Get list of modified tracked files.
        
        Returns:
            List of file paths that have been modified
        """
        modified = []
        
        for file_path in self._tracked_files:
            if self.is_modified(file_path):
                modified.append(file_path)
        
        return modified
    
    def get_diff(self, file_path: str) -> Optional[str]:
        """Get diff for a modified file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Unified diff string, or None if not modified
        """
        if not self.is_modified(file_path):
            return None
        
        # This is simplified - in reality you'd store original content
        # or use git for diffing
        return f"File {file_path} has been modified"
    
    def untrack_file(self, file_path: str) -> None:
        """Stop tracking a file."""
        if file_path in self._tracked_files:
            del self._tracked_files[file_path]
            self.logger.info(f"Stopped tracking: {file_path}")
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        return sha256.hexdigest()
```

---

#### Backup Manager

**File:** `arenaagent/files/backup.py`

**Purpose:** Manage file backups

**Key Features:**
- Create timestamped backups
- Restore from backup
- List all backups
- Cleanup old backups
- Backup verification

**Implementation:**

```python
"""File backup management."""

from pathlib import Path
from typing import List, Optional
from datetime import datetime
import shutil

from arenaagent.utils.logger import get_logger


class BackupManager:
    """Manages file backups."""
    
    def __init__(self, backup_dir: Optional[str] = None):
        """Initialize backup manager.
        
        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = Path(backup_dir) if backup_dir else Path.home() / ".arenaagent" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)
    
    def create_backup(self, file_path: str) -> str:
        """Create a backup of a file.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file
        """
        source = Path(file_path)
        
        if not source.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Create timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source.name}.{timestamp}.backup"
        backup_path = self.backup_dir / backup_name
        
        # Copy file
        shutil.copy2(source, backup_path)
        
        self.logger.info(f"Created backup: {backup_path}")
        return str(backup_path)
    
    def restore_backup(self, backup_path: str, target_path: str) -> None:
        """Restore a file from backup.
        
        Args:
            backup_path: Path to backup file
            target_path: Path to restore to
        """
        source = Path(backup_path)
        target = Path(target_path)
        
        if not source.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        # Restore file
        shutil.copy2(source, target)
        
        self.logger.info(f"Restored backup to: {target_path}")
    
    def list_backups(self, file_name: Optional[str] = None) -> List[str]:
        """List all backups, optionally filtered by filename.
        
        Args:
            file_name: Filter by original filename
            
        Returns:
            List of backup file paths
        """
        backups = []
        
        for backup_file in self.backup_dir.glob("*.backup"):
            if file_name is None or backup_file.name.startswith(file_name):
                backups.append(str(backup_file))
        
        return sorted(backups, reverse=True)  # Most recent first
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Delete old backups, keeping only the most recent.
        
        Args:
            keep_count: Number of backups to keep per file
            
        Returns:
            Number of backups deleted
        """
        deleted_count = 0
        
        # Group backups by original filename
        backup_groups: Dict[str, List[Path]] = {}
        
        for backup_file in self.backup_dir.glob("*.backup"):
            # Extract original filename
            original_name = backup_file.name.split('.')[0]
            
            if original_name not in backup_groups:
                backup_groups[original_name] = []
            
            backup_groups[original_name].append(backup_file)
        
        # Delete old backups
        for backups in backup_groups.values():
            backups.sort(reverse=True)  # Most recent first
            
            for old_backup in backups[keep_count:]:
                old_backup.unlink()
                deleted_count += 1
                self.logger.debug(f"Deleted old backup: {old_backup}")
        
        self.logger.info(f"Cleaned up {deleted_count} old backups")
        return deleted_count
```

---

### Files Package Init

**File:** `arenaagent/files/__init__.py`

```python
"""File operations for ArenaAgent."""

from arenaagent.files.tracker import FileTracker
from arenaagent.files.backup import BackupManager

__all__ = ["FileTracker", "BackupManager"]
```

---

### Phase 5.7 Completion Checklist

- [ ] FileTracker implemented
- [ ] BackupManager implemented
- [ ] File tracking working
- [ ] Backup creation working
- [ ] Restore working
- [ ] All tests passing (15+ tests)
- [ ] Code coverage ≥ 85%

### Git Workflow

```bash
git checkout -b feature/file-operations
git add arenaagent/files/tracker.py tests/unit/test_file_tracker.py
git commit -m "feat: implement FileTracker for file monitoring"
git add arenaagent/files/backup.py tests/unit/test_backup_manager.py
git commit -m "feat: implement BackupManager for file backups"
git add arenaagent/files/__init__.py
git commit -m "feat: export file operation components"
make test
git checkout develop
git merge feature/file-operations
```

---


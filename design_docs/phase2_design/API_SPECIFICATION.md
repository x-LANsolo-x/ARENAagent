# ArenaAgent - API Specification

## Internal API Contracts Between Modules

---

## 1. BROWSER CONNECTOR API

### Module: `arenaagent/browser_connector.py`

### Class: `BrowserConnector`

#### Constructor

```python
def __init__(self, config: Config):
    """
    Initialize browser connector
    
    Args:
        config: Configuration object
    """
```

#### Public Methods

##### `launch(headless: bool = True) -> bool`

```python
def launch(self, headless: bool = True) -> bool:
    """
    Launch Playwright browser with persistent profile
    
    Args:
        headless: Run in headless mode (default: True)
    
    Returns:
        bool: True if successful
    
    Raises:
        BrowserLaunchError: If browser fails to start
        ProfileCorruptedError: If browser profile is corrupted
    
    Side Effects:
        - Creates browser profile directory if not exists
        - Launches Chromium process
        - Stores browser instance in self.browser
    """
```

##### `navigate_to_lm_arena() -> bool`

```python
def navigate_to_lm_arena(self) -> bool:
    """
    Navigate to LM Arena chat interface
    
    Returns:
        bool: True if page loaded successfully
    
    Raises:
        NavigationError: If page fails to load
        NetworkError: If no internet connection
    
    Side Effects:
        - Navigates to https://chat.lmsys.org
        - Waits for page to be fully loaded
    """
```

##### `wait_for_login(timeout: int = 300) -> bool`

```python
def wait_for_login(self, timeout: int = 300) -> bool:
    """
    Wait for user to complete Google login
    
    Args:
        timeout: Maximum wait time in seconds (default: 5 minutes)
    
    Returns:
        bool: True if login detected within timeout
    
    Detection Method:
        - Checks for presence of chat textarea element
        - Detects URL change from login page to chat
    """
```

##### `send_message(message: str) -> bool`

```python
def send_message(self, message: str) -> bool:
    """
    Send message to LM Arena chat
    
    Args:
        message: Text message to send
    
    Returns:
        bool: True if message sent successfully
    
    Raises:
        NotLoggedInError: If user is not logged in
        SendError: If message fails to send
    
    Side Effects:
        - Types message into textarea
        - Clicks send button
        - Waits for message to be sent
    
    DOM Interaction:
        - Selector: textarea[placeholder*="Enter"]
        - Action: fill(message)
        - Selector: button[aria-label="Send"]
        - Action: click()
    """
```

##### `extract_response(timeout: int = 60) -> str`

```python
def extract_response(self, timeout: int = 60) -> str:
    """
    Wait for and extract AI response from chat
    
    Args:
        timeout: Maximum wait time in seconds
    
    Returns:
        str: Response text from model
    
    Raises:
        TimeoutError: If response not received within timeout
        ExtractionError: If response cannot be parsed from DOM
    
    Detection:
        - Waits for "Stop generating" button to disappear
        - Extracts text from last message div
    
    DOM Interaction:
        - Wait for: button:has-text("Stop generating") to disappear
        - Selector: div[class*="message-content"]:last-child
        - Action: innerText()
    """
```

##### `is_running() -> bool`

```python
def is_running(self) -> bool:
    """
    Check if browser is still running
    
    Returns:
        bool: True if browser process is alive
    """
```

##### `close() -> None`

```python
def close(self) -> None:
    """
    Close browser and cleanup resources
    
    Side Effects:
        - Closes all browser pages
        - Terminates Chromium process
        - Profile remains on disk for next launch
    """
```

---

## 2. SESSION MANAGER API

### Module: `arenaagent/session_manager.py`

### Class: `SessionManager`

#### Constructor

```python
def __init__(self, config: Config):
    """
    Initialize session manager
    
    Args:
        config: Configuration object
    
    Side Effects:
        - Creates sessions directory if not exists
        - Loads session index
    """
```

#### Public Methods

##### `create_session() -> str`

```python
def create_session(self) -> str:
    """
    Create new session
    
    Returns:
        str: Session ID (UUID)
    
    Side Effects:
        - Creates session directory: ~/.arenaagent/sessions/{session_id}/
        - Creates metadata.json
        - Creates empty conversation_history.json
        - Updates session index
    
    Files Created:
        - metadata.json: Session metadata
        - conversation_history.json: Empty message list
        - file_index.json: Empty file list
        - execution_log.json: Empty execution list
    """
```

##### `load_session(session_id: str) -> Session`

```python
def load_session(self, session_id: str) -> Session:
    """
    Load existing session
    
    Args:
        session_id: UUID of session to load
    
    Returns:
        Session: Session object with all data
    
    Raises:
        SessionNotFoundError: If session doesn't exist
        CorruptedSessionError: If JSON is corrupted
    
    Recovery:
        - If corrupted: Archive and create new session
        - If missing files: Create with defaults
    """
```

##### `load_latest_session() -> str`

```python
def load_latest_session(self) -> str:
    """
    Load most recent session
    
    Returns:
        str: Session ID of most recent session
    
    Fallback:
        - If no sessions exist: Create new session
    """
```

##### `save_message(message: Message) -> bool`

```python
def save_message(self, message: Message) -> bool:
    """
    Append message to current session
    
    Args:
        message: Message object to save
    
    Returns:
        bool: True if saved successfully
    
    Side Effects:
        - Appends to conversation_history.json
        - Updates metadata.last_updated timestamp
        - Atomic write (temp file + rename)
    
    Data Persistence:
        - Immediate write (no buffering)
        - Atomic operation (no partial writes)
    """
```

##### `get_context(session_id: str, max_tokens: int = 50000) -> List[Message]`

```python
def get_context(self, session_id: str, max_tokens: int = 50000) -> List[Message]:
    """
    Get conversation context for prompt
    
    Args:
        session_id: Session to get context from
        max_tokens: Maximum context window size
    
    Returns:
        List[Message]: Recent messages that fit in token limit
    
    Strategy:
        - Always include last 10 messages
        - Include earlier messages if tokens allow
        - Summarize very old messages (future feature)
    
    Token Estimation:
        - ~4 characters per token (rough estimate)
    """
```

##### `get_messages(session_id: str, limit: int = 10) -> List[Message]`

```python
def get_messages(self, session_id: str, limit: int = 10) -> List[Message]:
    """
    Get recent messages for display
    
    Args:
        session_id: Session ID
        limit: Number of messages to return
    
    Returns:
        List[Message]: Most recent N messages
    """
```

##### `list_sessions() -> List[SessionMeta]`

```python
def list_sessions(self) -> List[SessionMeta]:
    """
    List all sessions with metadata
    
    Returns:
        List[SessionMeta]: All sessions, sorted by last_updated
    
    SessionMeta Fields:
        - session_id: str
        - created_at: datetime
        - last_updated: datetime
        - message_count: int
        - model: str
    """
```

##### `archive_session(session_id: str) -> bool`

```python
def archive_session(self, session_id: str) -> bool:
    """
    Archive corrupted or old session
    
    Args:
        session_id: Session to archive
    
    Returns:
        bool: True if archived successfully
    
    Side Effects:
        - Moves to ~/.arenaagent/sessions/.archive/{session_id}/
        - Removes from active session index
    """
```

---

## 3. EXECUTOR ENGINE API

### Module: `arenaagent/executor.py`

### Class: `ExecutorEngine`

#### Constructor

```python
def __init__(self, config: Config):
    """
    Initialize executor engine
    
    Args:
        config: Configuration object
    """
```

#### Public Methods

##### `execute(code: str, language: str, timeout: int = 60) -> ExecutionResult`

```python
def execute(self, code: str, language: str, timeout: int = 60) -> ExecutionResult:
    """
    Execute code in subprocess
    
    Args:
        code: Code to execute
        language: Language (python, bash, sh, node)
        timeout: Max execution time in seconds
    
    Returns:
        ExecutionResult with stdout, stderr, exit_code
    
    Raises:
        UnsupportedLanguageError: If language not supported
        TimeoutError: If execution exceeds timeout
    
    Supported Languages:
        - python: python -c "code"
        - bash/sh: bash -c "code"
        - node: node -e "code"
    
    Safety:
        - Runs in subprocess (isolated)
        - Timeout enforcement
        - No shell=True (prevents injection)
    """
```

**ExecutionResult Schema:**
```python
@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    success: bool  # exit_code == 0
    timed_out: bool
```

##### `parse_error(stderr: str, exit_code: int) -> ErrorInfo`

```python
def parse_error(self, stderr: str, exit_code: int) -> ErrorInfo:
    """
    Parse error from stderr into structured format
    
    Args:
        stderr: Error output from execution
        exit_code: Process exit code
    
    Returns:
        ErrorInfo: Structured error information
    
    Error Types Detected:
        - ModuleNotFoundError (Python)
        - SyntaxError (Python)
        - NameError (Python)
        - Command not found (Bash)
        - Permission denied
        - Generic runtime errors
    """
```

**ErrorInfo Schema:**
```python
@dataclass
class ErrorInfo:
    error_type: str  # "missing_module", "syntax_error", etc.
    message: str  # Clean error message
    suggested_fix: str  # Human-readable suggestion
    raw_stderr: str  # Full stderr for debugging
```

##### `validate_command(command: str) -> ValidationResult`

```python
def validate_command(self, command: str) -> ValidationResult:
    """
    Validate command for safety before execution
    
    Args:
        command: Command to validate
    
    Returns:
        ValidationResult: Safe/unsafe with reason
    
    Blocked Patterns:
        - rm -rf / (destructive deletion)
        - DROP TABLE (database destruction)
        - sudo (privilege escalation)
        - curl ... | bash (remote code execution)
        - > /dev/sda (disk overwrite)
    
    Severity Levels:
        - SAFE: Execute without warning
        - WARNING: Ask user confirmation
        - BLOCKED: Never execute
    """
```

**ValidationResult Schema:**
```python
@dataclass
class ValidationResult:
    safe: bool
    severity: str  # "SAFE", "WARNING", "BLOCKED"
    reason: str
    blocked_pattern: Optional[str]
```

##### `list_processes() -> List[ProcessInfo]`

```python
def list_processes(self) -> List[ProcessInfo]:
    """
    List background processes started by executor
    
    Returns:
        List[ProcessInfo]: Running processes
    
    Use Case:
        - Servers started by user (Flask, Node.js)
        - Long-running scripts
    """
```

**ProcessInfo Schema:**
```python
@dataclass
class ProcessInfo:
    pid: int
    command: str
    started_at: datetime
    status: str  # "running", "stopped"
```

##### `kill_process(pid: int) -> bool`

```python
def kill_process(self, pid: int) -> bool:
    """
    Terminate background process
    
    Args:
        pid: Process ID to kill
    
    Returns:
        bool: True if killed successfully
    """
```

---

## 4. FILE MANAGER API

### Module: `arenaagent/file_manager.py`

### Class: `FileManager`

#### Constructor

```python
def __init__(self, config: Config):
    """
    Initialize file manager
    
    Args:
        config: Configuration object
    
    Side Effects:
        - Creates workspace directory if not exists
    """
```

#### Public Methods

##### `create_file(path: str, content: str, backup: bool = True) -> bool`

```python
def create_file(self, path: str, content: str, backup: bool = True) -> bool:
    """
    Create new file or overwrite existing
    
    Args:
        path: File path (relative to workspace or absolute)
        content: File content
        backup: Create backup if file exists (default: True)
    
    Returns:
        bool: True if created successfully
    
    Raises:
        PermissionError: If cannot write to path
        DiskFullError: If no disk space
    
    Side Effects:
        - Creates parent directories if needed
        - If file exists and backup=True: Creates .backup.TIMESTAMP
        - Uses atomic write (temp + rename)
    
    Workflow:
        1. Check if file exists
        2. If exists and backup: create_backup()
        3. Atomic write to path
        4. Update file_index.json
    """
```

##### `create_backup(path: str) -> str`

```python
def create_backup(self, path: str) -> str:
    """
    Create timestamped backup of file
    
    Args:
        path: File to backup
    
    Returns:
        str: Path to backup file
    
    Backup Format:
        - {original_path}.backup.{unix_timestamp}
        - Example: app.py.backup.1707300000
    
    Metadata Preserved:
        - File permissions
        - Modification time (in backup metadata)
    """
```

##### `atomic_write(path: str, content: str) -> bool`

```python
def atomic_write(self, path: str, content: str) -> bool:
    """
    Write file atomically (no partial writes)
    
    Args:
        path: Destination path
        content: File content
    
    Returns:
        bool: True if successful
    
    Method:
        1. Write to temp file in same directory
        2. fsync() to ensure disk write
        3. os.replace() (atomic on all platforms)
    
    Guarantees:
        - File never in partial state
        - Either old content or new content (never mixed)
        - Works across system crashes
    """
```

##### `rollback(path: str, timestamp: int = None) -> bool`

```python
def rollback(self, path: str, timestamp: int = None) -> bool:
    """
    Restore file from backup
    
    Args:
        path: File to restore
        timestamp: Specific backup timestamp (default: most recent)
    
    Returns:
        bool: True if restored successfully
    
    Raises:
        NoBackupError: If no backups exist
    
    Workflow:
        1. List backups for file
        2. If timestamp provided: Use specific backup
        3. Else: Use most recent
        4. Restore with atomic write
        5. Current file becomes new backup
    """
```

##### `list_backups(path: str) -> List[BackupInfo]`

```python
def list_backups(self, path: str) -> List[BackupInfo]:
    """
    List all backups for a file
    
    Args:
        path: File to check
    
    Returns:
        List[BackupInfo]: All backups, sorted by timestamp
    """
```

**BackupInfo Schema:**
```python
@dataclass
class BackupInfo:
    path: str  # Backup file path
    timestamp: int  # Unix timestamp
    created_at: datetime
    size_bytes: int
```

##### `generate_diff(old_content: str, new_content: str) -> str`

```python
def generate_diff(self, old_content: str, new_content: str) -> str:
    """
    Generate unified diff between two versions
    
    Args:
        old_content: Original content
        new_content: Modified content
    
    Returns:
        str: Unified diff format (like git diff)
    
    Use Case:
        - Show user what will change before applying
    """
```

##### `cleanup_old_backups(days: int = 30) -> int`

```python
def cleanup_old_backups(self, days: int = 30) -> int:
    """
    Delete backups older than N days
    
    Args:
        days: Age threshold
    
    Returns:
        int: Number of backups deleted
    
    Preservation:
        - Always keep at least 5 most recent backups per file
        - Even if older than threshold
    """
```

---

## 5. CONFIG MANAGER API

### Module: `arenaagent/config.py`

### Class: `ConfigManager`

#### Static Methods

##### `load() -> Config`

```python
@staticmethod
def load() -> Config:
    """
    Load configuration from file
    
    Returns:
        Config: Configuration object
    
    Fallback:
        - If config file doesn't exist: Create with defaults
        - If corrupted: Use defaults, warn user
    
    Location:
        - ~/.arenaagent/config.json
    """
```

##### `save(config: Config) -> bool`

```python
@staticmethod
def save(config: Config) -> bool:
    """
    Save configuration to file
    
    Args:
        config: Configuration object
    
    Returns:
        bool: True if saved successfully
    
    Method:
        - Atomic write (temp + rename)
    """
```

##### `get_default() -> Config`

```python
@staticmethod
def get_default() -> Config:
    """
    Get default configuration
    
    Returns:
        Config: Default configuration object
    """
```

**Config Schema:**
```python
@dataclass
class Config:
    version: str = "1.0"
    default_model: str = "claude-3.5-sonnet"
    default_workspace: str = "~/arenaagent_workspace/"
    
    @dataclass
    class Browser:
        profile_path: str = "~/.arenaagent/browser/"
        headless: bool = True
        timeout: int = 30
    
    @dataclass
    class Execution:
        auto_approve: bool = False
        timeout: int = 60
        max_retries: int = 3
    
    @dataclass
    class Files:
        auto_backup: bool = True
        backup_retention_days: int = 30
    
    @dataclass
    class Session:
        auto_save: bool = True
        context_window_tokens: int = 50000
```

---

*Continued in DATABASE_SCHEMA.md...*
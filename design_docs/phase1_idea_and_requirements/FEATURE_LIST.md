# ArenaAgent - Detailed Feature List

## Phase 1: Core Features (MVP)

---

## Feature 1: Persistent Browser Session Management

### Feature ID: F001
### Priority: CRITICAL (Must-Have)
### Status: Not Started

### Description:
Maintain a persistent Chromium browser profile that preserves LM Arena login state across all application sessions, eliminating the need for repeated authentication.

### User Story:
**As a** student developer  
**I want** to log in to LM Arena only once  
**So that** I don't waste time re-authenticating every time I use the tool

### Acceptance Criteria:

1. **Initial Setup:**
   - [ ] Running `arenaagent init` opens browser to chat.lmsys.org
   - [ ] User can log in with Google account
   - [ ] Browser profile saved to `~/.arenaagent/browser/`
   - [ ] Setup completes with success message

2. **Persistent Profile:**
   - [ ] Subsequent runs use saved profile automatically
   - [ ] No login prompt if session is valid
   - [ ] Cookies persist across system restarts
   - [ ] Profile works on all supported OS (Windows/Mac/Linux)

3. **Session Expiry Handling:**
   - [ ] Detect when login session has expired
   - [ ] Display clear message: "Session expired, please re-login"
   - [ ] Auto-open browser for re-authentication
   - [ ] Resume normal operation after re-login

4. **Profile Corruption Recovery:**
   - [ ] Detect corrupted profile on startup
   - [ ] Offer to recreate profile automatically
   - [ ] Preserve session data even if profile needs recreation
   - [ ] Clear error messages for troubleshooting

### Technical Specifications:

**Browser:**
- Playwright Chromium (persistent context)
- Profile directory: `~/.arenaagent/browser/`
- Headless mode by default (configurable to headful for debugging)

**Profile Contents:**
- Cookies (authentication state)
- Local storage (LM Arena preferences)
- Session storage (temporary data)

**Configuration:**
```python
browser_config = {
    "user_data_dir": "~/.arenaagent/browser/",
    "headless": True,
    "args": [
        "--no-sandbox",
        "--disable-dev-shm-usage"
    ]
}
```

### Error Handling:

| Error Scenario | Detection | Recovery |
|----------------|-----------|----------|
| Profile not found | Check directory existence | Run init wizard |
| Profile corrupted | Chromium launch fails | Delete + recreate |
| Session expired | Login page detected | Prompt re-authentication |
| Browser crash | Process exit code | Restart browser, restore session |

### Testing Requirements:

- [ ] Unit test: Profile creation
- [ ] Unit test: Profile loading
- [ ] Integration test: Login persistence across restarts
- [ ] Integration test: Expiry detection
- [ ] Manual test: All 3 OS platforms

### Dependencies:
- Playwright >= 1.40.0
- Chromium browser (auto-installed)

### Estimated Effort: 3-4 days

---

## Feature 2: Local Conversation Persistence

### Feature ID: F002
### Priority: CRITICAL (Must-Have)
### Status: Not Started

### Description:
Store all conversation history locally in JSON format, enabling context to persist indefinitely across sessions, restarts, and even system crashes.

### User Story:
**As a** developer working on a multi-day project  
**I want** my conversation context to persist forever  
**So that** I can continue where I left off without re-explaining everything

### Acceptance Criteria:

1. **Session Creation:**
   - [ ] New session auto-created on first command
   - [ ] Session ID is UUID v4
   - [ ] Session directory: `~/.arenaagent/sessions/[session_id]/`
   - [ ] Metadata file created with timestamp, model, workspace path

2. **Message Storage:**
   - [ ] Every user prompt saved before sending to LM Arena
   - [ ] Every model response saved after receiving
   - [ ] Timestamps on all messages
   - [ ] File created/modified tracking per message

3. **Session Resumption:**
   - [ ] Detect existing session on startup
   - [ ] Load conversation history automatically
   - [ ] Display session info: "Loaded session [id], 15 messages"
   - [ ] Include history in context when sending new prompts

4. **Session Management:**
   - [ ] Command: `arenaagent history` shows all messages
   - [ ] Command: `arenaagent sessions` lists all sessions
   - [ ] Command: `arenaagent switch [session_id]` changes active session
   - [ ] Command: `arenaagent new` starts fresh session

5. **Data Integrity:**
   - [ ] Atomic writes (temp file + rename)
   - [ ] Corruption detection on load
   - [ ] Automatic backup before overwrites
   - [ ] Graceful handling of corrupted JSON

### Technical Specifications:

**Session Directory Structure:**
```
~/.arenaagent/sessions/[session_id]/
├── conversation_history.json
├── file_index.json
├── execution_log.json
└── metadata.json
```

**conversation_history.json Schema:**
```json
{
  "session_id": "a1b2c3d4-...",
  "created_at": "2026-02-17T10:30:00Z",
  "last_updated": "2026-02-17T15:45:00Z",
  "model": "claude-3.5-sonnet",
  "workspace": "/home/user/arenaagent_workspace/",
  "messages": [
    {
      "id": 1,
      "timestamp": "2026-02-17T10:30:15Z",
      "role": "user",
      "content": "create a Flask REST API for todo list",
      "metadata": {}
    },
    {
      "id": 2,
      "timestamp": "2026-02-17T10:30:23Z",
      "role": "assistant",
      "content": "[full model response]",
      "metadata": {
        "files_created": ["app.py"],
        "files_modified": [],
        "execution_attempted": true,
        "execution_success": false
      }
    }
  ]
}
```

**Context Window Management:**
- Include full history if < 50k tokens
- If > 50k tokens: Keep recent 30k + summarize older messages
- Always preserve: Last 10 messages, all file operations

### Error Handling:

| Error Scenario | Detection | Recovery |
|----------------|-----------|----------|
| JSON corrupted | Parse error on load | Archive corrupted, start fresh |
| Disk full | Write failure | Warn user, continue in-memory only |
| Permission denied | File access error | Check permissions, guide user |
| Session conflict | Multiple processes | Lock file mechanism |

### Testing Requirements:

- [ ] Unit test: Session creation
- [ ] Unit test: Message append
- [ ] Unit test: JSON serialization/deserialization
- [ ] Integration test: Session resume after restart
- [ ] Integration test: Corruption recovery
- [ ] Load test: 1,000+ message session

### Dependencies:
- Python json module (stdlib)
- pathlib (stdlib)

### Estimated Effort: 2-3 days

---

## Feature 3: Autonomous Code Execution

### Feature ID: F003
### Priority: CRITICAL (Must-Have)
### Status: Not Started

### Description:
Automatically detect, extract, and execute code blocks from model responses with user approval, capturing all output for immediate feedback.

### User Story:
**As a** developer testing generated code  
**I want** code to execute automatically  
**So that** I can see if it works without manual copy-paste

### Acceptance Criteria:

1. **Code Detection:**
   - [ ] Detect markdown code blocks: ` ```language ... ``` `
   - [ ] Support languages: Python, Bash, JavaScript, Shell
   - [ ] Extract file path hints from context
   - [ ] Identify execution intent from response text

2. **User Approval Flow:**
   - [ ] Display code preview before execution
   - [ ] Prompt: `[C]reate file, [R]un, [V]iew full code, [S]kip`
   - [ ] User can view full code before deciding
   - [ ] Default timeout: 60 seconds for user input

3. **Execution:**
   - [ ] Python: `python <file>` or `python -c "<code>"`
   - [ ] Bash: `bash <file>` or `bash -c "<code>"`
   - [ ] Node.js: `node <file>`
   - [ ] Capture stdout in real-time
   - [ ] Capture stderr in real-time
   - [ ] Capture exit code

4. **Output Display:**
   - [ ] Stream output to terminal as it happens
   - [ ] Syntax highlight errors (red)
   - [ ] Clear success/failure indicator
   - [ ] Execution time displayed

5. **Background Processes:**
   - [ ] Detect long-running processes (servers)
   - [ ] Option to run in background
   - [ ] PID tracking for later termination
   - [ ] Command: `arenaagent ps` shows running processes

### Technical Specifications:

**Code Block Parsing:**
```python
import re

def extract_code_blocks(response: str) -> List[CodeBlock]:
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)
    return [
        CodeBlock(language=lang or 'text', code=code.strip())
        for lang, code in matches
    ]
```

**Execution Engine:**
```python
import subprocess

def execute_code(code: str, language: str, timeout: int = 60):
    if language == 'python':
        process = subprocess.Popen(
            ['python', '-c', code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    
    stdout, stderr = process.communicate(timeout=timeout)
    return {
        'stdout': stdout,
        'stderr': stderr,
        'exit_code': process.returncode,
        'success': process.returncode == 0
    }
```

**Safety Checks:**
- Block destructive patterns: `rm -rf`, `DROP TABLE`, `sudo`
- Workspace isolation (optional chroot)
- Timeout enforcement (prevent infinite loops)
- Resource limits (optional memory/CPU caps)

### Error Handling:

| Error Scenario | Detection | Recovery |
|----------------|-----------|----------|
| Timeout | Process exceeds 60s | Kill process, show partial output |
| Missing interpreter | Command not found | Show installation instructions |
| Permission denied | Exit code 126 | Check file permissions |
| Syntax error | Exit code 1 | Trigger error recovery loop |

### Testing Requirements:

- [ ] Unit test: Code block extraction
- [ ] Unit test: Python execution
- [ ] Unit test: Bash execution
- [ ] Integration test: End-to-end execution flow
- [ ] Security test: Destructive command blocking
- [ ] Performance test: Long-running process handling

### Dependencies:
- Python subprocess module (stdlib)
- re module (stdlib)

### Estimated Effort: 4-5 days

---

## Feature 4: Automatic Error Recovery Loop

### Feature ID: F004
### Priority: HIGH (Should-Have)
### Status: Not Started

### Description:
Automatically detect execution failures, send error details back to the model, and retry execution with the generated fix (up to 3 attempts).

### User Story:
**As a** developer encountering errors  
**I want** the AI to automatically fix common errors  
**So that** I don't waste time debugging missing dependencies or syntax issues

### Acceptance Criteria:

1. **Error Detection:**
   - [ ] Detect non-zero exit codes
   - [ ] Parse error tracebacks (Python, Node.js, Bash)
   - [ ] Extract meaningful error messages
   - [ ] Identify error type (syntax, import, runtime)

2. **Feedback to Model:**
   - [ ] Construct error report with context
   - [ ] Include: Error message, traceback, original code
   - [ ] Send to LM Arena with prompt: "Fix this error"
   - [ ] Maintain conversation context

3. **Fix Application:**
   - [ ] Extract fix from model response
   - [ ] Identify fix type: New code, install command, config change
   - [ ] Prompt user: "Execute fix? [Y/n]"
   - [ ] Apply fix and retry execution

4. **Retry Logic:**
   - [ ] Maximum 3 retry attempts
   - [ ] After each failure, increment retry counter
   - [ ] After 3 failures, stop and display full log
   - [ ] User can manually intervene at any point

5. **Learning Patterns:**
   - [ ] Cache common error → fix patterns
   - [ ] Example: "ModuleNotFoundError: flask" → "pip install flask"
   - [ ] Apply cached fixes without model call (optional optimization)

### Technical Specifications:

**Error Parsing:**
```python
def parse_error(stderr: str, exit_code: int) -> ErrorInfo:
    # Python errors
    if 'ModuleNotFoundError' in stderr:
        module = re.search(r"No module named '(\w+)'", stderr).group(1)
        return ErrorInfo(
            type='missing_module',
            message=f"Missing Python module: {module}",
            suggested_fix=f"pip install {module}"
        )
    
    # Syntax errors
    if 'SyntaxError' in stderr:
        return ErrorInfo(
            type='syntax_error',
            message=extract_syntax_error(stderr),
            suggested_fix="Review code syntax"
        )
    
    # Generic error
    return ErrorInfo(
        type='runtime_error',
        message=stderr,
        suggested_fix="Ask model to debug"
    )
```

**Retry Loop:**
```python
max_retries = 3
for attempt in range(max_retries):
    result = execute_code(code)
    
    if result['success']:
        break
    
    # Error detected
    error_info = parse_error(result['stderr'], result['exit_code'])
    
    # Send to model
    fix_response = send_to_model(f"Error: {error_info.message}\n\nOriginal code: {code}\n\nFix this error.")
    
    # Extract and apply fix
    fix = extract_fix(fix_response)
    if user_approves(fix):
        code = apply_fix(code, fix)
    else:
        break  # User intervention needed
```

### Error Handling:

| Error Scenario | Detection | Recovery |
|----------------|-----------|----------|
| Model gives unhelpful fix | Exit code still non-zero after retry | Stop, show all attempts to user |
| Network fails during retry | Timeout on model call | Cache error, retry later |
| User denies fix | User input 'n' | Stop loop, show error log |
| 3 retries exhausted | Counter reaches max | Display: "Unable to auto-fix, manual intervention needed" |

### Testing Requirements:

- [ ] Unit test: Error parsing (Python, Bash, Node.js)
- [ ] Unit test: Retry counter logic
- [ ] Integration test: Common error (missing module) auto-fixed
- [ ] Integration test: Unfixable error stops after 3 tries
- [ ] Edge case test: Model gives wrong fix

### Dependencies:
- Execution engine (F003)
- LM Arena connector
- Error pattern library

### Estimated Effort: 3-4 days

---

## Feature 5: Safe File Operations with Auto-Backup

### Feature ID: F005
### Priority: HIGH (Should-Have)
### Status: Not Started

### Description:
Ensure all file modifications are safe by creating automatic timestamped backups before changes and using atomic writes to prevent corruption.

### User Story:
**As a** developer letting AI modify my code  
**I want** automatic backups before every change  
**So that** I can undo bad AI edits without losing work

### Acceptance Criteria:

1. **Backup Creation:**
   - [ ] Before overwriting file, create backup: `file.backup.TIMESTAMP`
   - [ ] Timestamp format: Unix epoch (sortable)
   - [ ] Preserve original file permissions
   - [ ] Never fail silently (warn if backup fails)

2. **Atomic Writes:**
   - [ ] Write to temp file first: `file.tmp.RANDOM`
   - [ ] After successful write, rename to target
   - [ ] OS-level atomic operation (prevents partial writes)
   - [ ] Cleanup temp files on error

3. **Diff Preview:**
   - [ ] Before applying changes, show diff
   - [ ] Use unified diff format (like Git)
   - [ ] Highlight additions (green) and deletions (red)
   - [ ] Prompt: `[A]pply, [R]eject, [V]iew full diff`

4. **Rollback:**
   - [ ] Command: `arenaagent rollback <file>`
   - [ ] List available backups with timestamps
   - [ ] User selects which backup to restore
   - [ ] Confirm before overwriting current file

5. **Backup Management:**
   - [ ] Auto-delete backups older than 30 days (configurable)
   - [ ] Command: `arenaagent cleanup-backups` (manual trigger)
   - [ ] Preserve at least 5 most recent backups per file
   - [ ] Disk space warning if backups exceed 1GB

### Technical Specifications:

**Backup Function:**
```python
import shutil
import time

def create_backup(file_path: str) -> str:
    timestamp = int(time.time())
    backup_path = f"{file_path}.backup.{timestamp}"
    
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)  # Preserve metadata
        return backup_path
    
    return None
```

**Atomic Write:**
```python
import tempfile
import os

def atomic_write(file_path: str, content: str):
    # Create backup first
    backup_path = create_backup(file_path)
    
    # Write to temp file
    fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(file_path))
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        
        # Atomic rename
        os.replace(temp_path, file_path)
    except:
        # Cleanup on failure
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
```

**Diff Generation:**
```python
import difflib

def generate_diff(old_content: str, new_content: str) -> str:
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile='current',
        tofile='modified'
    )
    return ''.join(diff)
```

### Error Handling:

| Error Scenario | Detection | Recovery |
|----------------|-----------|----------|
| Backup creation fails | Permission/disk error | Abort modification, warn user |
| Atomic write fails | Exception during write | Restore from backup automatically |
| Disk full | OS error 28 | Stop, warn user, cleanup temp files |
| Diff tool missing | difflib import fails | Skip diff, allow blind apply (warn) |

### Testing Requirements:

- [ ] Unit test: Backup creation
- [ ] Unit test: Atomic write
- [ ] Unit test: Diff generation
- [ ] Integration test: Full modify → backup → restore cycle
- [ ] Edge case test: Disk full scenario
- [ ] Performance test: Large file (10MB+) atomic write

### Dependencies:
- shutil (stdlib)
- tempfile (stdlib)
- difflib (stdlib)

### Estimated Effort: 2-3 days

---

## Phase 2 Features (Post-MVP)

### Feature 6: Multi-Model Selection
**Priority:** MEDIUM  
**Estimated Effort:** 2 days  
**Description:** Allow user to choose between Claude, GPT-4, Gemini, etc.

### Feature 7: Advanced Error Parsing
**Priority:** LOW  
**Estimated Effort:** 3 days  
**Description:** Handle 50+ error types with intelligent suggestions

### Feature 8: Session Export
**Priority:** LOW  
**Estimated Effort:** 1 day  
**Description:** Export conversation as Markdown for documentation

---

## Feature Summary Table

| ID | Feature | Priority | Effort | Dependencies |
|----|---------|----------|--------|--------------|
| F001 | Persistent Browser Session | CRITICAL | 3-4d | Playwright |
| F002 | Conversation Persistence | CRITICAL | 2-3d | None |
| F003 | Code Execution | CRITICAL | 4-5d | None |
| F004 | Error Recovery Loop | HIGH | 3-4d | F003 |
| F005 | File Backup System | HIGH | 2-3d | None |

**Total Estimated Effort:** 14-19 days (~3-4 weeks)

---

## Feature Development Order

1. **F002** - Conversation Persistence (foundation for all features)
2. **F001** - Browser Session (enables LM Arena communication)
3. **F003** - Code Execution (core value proposition)
4. **F005** - File Backup (safety before iteration)
5. **F004** - Error Recovery (polish, makes it "magical")

---

*Document Version: 1.0*  
*Last Updated: 2026-02-17*  
*Status: Ready for Implementation*
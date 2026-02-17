# ArenaAgent - Data Flow Documentation

## Component Interactions and Data Movement

---

## 1. INITIALIZATION FLOW

### Command: `arenaagent init`

```
┌─────────┐
│  User   │ Runs: arenaagent init
└────┬────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ CLI Interface (cli.py)                  │
│ @cli.command('init')                    │
└────┬────────────────────────────────────┘
     │
     │ Call: agent.initialize(headless=False)
     ▼
┌─────────────────────────────────────────┐
│ Agent Core (agent.py)                   │
│ AgentCore.initialize()                  │
└────┬────────────────────────────────────┘
     │
     ├──► Step 1: Create directories
     │    └─► Create: ~/.arenaagent/
     │        Create: ~/.arenaagent/sessions/
     │        Create: ~/.arenaagent/browser/
     │
     ├──► Step 2: Launch browser
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ BrowserConnector             │
     │   │ .launch(headless=False)      │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Uses: Playwright
     │        ▼
     │   ┌──────────────────────────────┐
     │   │ Playwright Browser           │
     │   │ - User data dir:             │
     │   │   ~/.arenaagent/browser/     │
     │   │ - Launches Chromium          │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Navigate to: chat.lmsys.org
     │        ▼
     │   ┌──────────────────────────────┐
     │   │ LM Arena Website             │
     │   │ - Shows login page           │
     │   └──────────────────────────────┘
     │
     ├──► Step 3: Wait for user login
     │    │ Display: "Please log in..."
     │    │ Wait: User completes Google OAuth
     │    │ Detect: Chat textarea appears
     │    └─► Login successful
     │
     ├──► Step 4: Save profile
     │    │ Browser cookies saved to:
     │    └─► ~/.arenaagent/browser/Default/Cookies
     │
     ├──► Step 5: Create session
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ SessionManager               │
     │   │ .create_session()            │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Generate: UUID v4
     │        │ Create directory:
     │        │   ~/.arenaagent/sessions/{uuid}/
     │        │
     │        ├─► Write: metadata.json
     │        │   {
     │        │     "session_id": "uuid",
     │        │     "created_at": "2026-02-17T10:30:00Z",
     │        │     "model": "claude-3.5-sonnet",
     │        │     "workspace": "~/arenaagent_workspace/"
     │        │   }
     │        │
     │        ├─► Write: conversation_history.json
     │        │   {
     │        │     "session_id": "uuid",
     │        │     "messages": []
     │        │   }
     │        │
     │        ├─► Write: file_index.json
     │        │   {
     │        │     "session_id": "uuid",
     │        │     "files": []
     │        │   }
     │        │
     │        └─► Write: execution_log.json
     │            {
     │              "session_id": "uuid",
     │              "executions": []
     │            }
     │
     └──► Step 6: Return success
          │
          ▼
     ┌─────────────────────────────┐
     │ CLI Display                 │
     │ ✓ Setup complete!           │
     │ Session: {uuid}             │
     └─────────────────────────────┘
```

**Data Created:**
- Browser profile with cookies
- Session directory with 4 JSON files
- Default workspace directory

**Data Flow Direction:**
CLI → Agent Core → BrowserConnector → Playwright → LM Arena  
CLI → Agent Core → SessionManager → File System

---

## 2. SEND PROMPT FLOW

### Command: `arenaagent ask "create Flask app"`

```
┌─────────┐
│  User   │ Types: arenaagent ask "create Flask app"
└────┬────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ CLI Interface (cli.py)                  │
│ @cli.command('ask')                     │
│ - Parse: prompt = "create Flask app"    │
└────┬────────────────────────────────────┘
     │
     │ Call: agent.send_prompt(prompt)
     ▼
┌─────────────────────────────────────────┐
│ Agent Core (agent.py)                   │
│ AgentCore.send_prompt()                 │
└────┬────────────────────────────────────┘
     │
     ├──► Step 1: Load session context
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ SessionManager               │
     │   │ .get_context(session_id)     │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Read: conversation_history.json
     │        │ Extract: Last 10 messages
     │        │ Estimate tokens: ~2000
     │        │
     │        ▼
     │   ┌──────────────────────────────┐
     │   │ Return: List[Message]        │
     │   │ - 10 previous messages       │
     │   └──────────────────────────────┘
     │
     ├──► Step 2: Construct full prompt
     │    │ Combine: context + new prompt
     │    │ Result:
     │    │   "Previous conversation:
     │    │    user: ...
     │    │    assistant: ...
     │    │    
     │    │    Current request: create Flask app"
     │    │
     ├──► Step 3: Send to LM Arena
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ BrowserConnector             │
     │   │ .send_message(full_prompt)   │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Find element: textarea
     │        │ Type: full_prompt
     │        │ Click: Send button
     │        │
     │        ▼
     │   ┌──────────────────────────────┐
     │   │ LM Arena                     │
     │   │ - Receives prompt            │
     │   │ - Sends to Claude API        │
     │   │ - Streams response           │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Response streaming...
     │        │ Wait for completion
     │        ▼
     │   ┌──────────────────────────────┐
     │   │ BrowserConnector             │
     │   │ .extract_response()          │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Wait: "Stop generating" disappears
     │        │ Extract: Last message div text
     │        │
     │        ▼
     │   ┌──────────────────────────────┐
     │   │ Return: response_text        │
     │   │ "I'll create a Flask app..." │
     │   │ ```python                    │
     │   │ from flask import Flask      │
     │   │ ...                          │
     │   │ ```                          │
     │   └──────────────────────────────┘
     │
     ├──► Step 4: Save user message
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ SessionManager               │
     │   │ .save_message(Message)       │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Read: conversation_history.json
     │        │ Append: {
     │        │   "id": 1,
     │        │   "role": "user",
     │        │   "content": "create Flask app",
     │        │   "timestamp": "2026-02-17T10:30:15Z"
     │        │ }
     │        │ Write atomically
     │        │
     ├──► Step 5: Parse response
     │    │ Extract code blocks:
     │    │ - Language: python
     │    │ - Code: "from flask import Flask..."
     │    │ Detect file name: "app.py"
     │    │
     ├──► Step 6: Create file
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ FileManager                  │
     │   │ .create_file(path, content)  │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Check: File exists? No
     │        │ Write atomically:
     │        │   workspace/app.py
     │        │
     │        ├─► Update: file_index.json
     │        │   {
     │        │     "files": [
     │        │       {
     │        │         "path": "workspace/app.py",
     │        │         "created_at": "2026-02-17T10:30:25Z",
     │        │         "hash": "abc123...",
     │        │         "backups": []
     │        │       }
     │        │     ]
     │        │   }
     │        │
     ├──► Step 7: Execute code
     │    │ Ask user approval
     │    │ User: Y
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ ExecutorEngine               │
     │   │ .execute(code, "python")     │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Validate: Check for rm -rf, etc.
     │        │ Safe: ✓
     │        │ Run: python app.py
     │        │
     │        ▼
     │   ┌──────────────────────────────┐
     │   │ OS Subprocess                │
     │   │ python app.py                │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Output:
     │        │   stderr: "ModuleNotFoundError:
     │        │            No module named 'flask'"
     │        │   exit_code: 1
     │        │
     │        ▼
     │   ┌──────────────────────────────┐
     │   │ ExecutorEngine               │
     │   │ Return: ExecutionResult      │
     │   │ - success: False             │
     │   │ - stderr: "ModuleNotFound.." │
     │   └──────────────────────────────┘
     │
     ├──► Step 8: Log execution
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ SessionManager               │
     │   │ Update: execution_log.json   │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Append: {
     │        │   "id": 1,
     │        │   "command": "python app.py",
     │        │   "exit_code": 1,
     │        │   "stderr": "ModuleNotFoundError...",
     │        │   "error_type": "missing_module"
     │        │ }
     │        │
     ├──► Step 9: Error recovery
     │    │ Detect: exit_code != 0
     │    │ Parse error type: missing_module
     │    │ Extract module: flask
     │    │
     │    │ Send to model:
     │    │   "Error: ModuleNotFoundError: 
     │    │    No module named 'flask'
     │    │    Please fix."
     │    │
     │    │ [Loop back to Step 3]
     │    │ Model responds: "pip install flask"
     │    │ Execute: pip install flask
     │    │ Success: ✓
     │    │ Retry: python app.py
     │    │ Success: ✓
     │    │
     ├──► Step 10: Save assistant message
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ SessionManager               │
     │   │ .save_message(Message)       │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Append: {
     │        │   "id": 2,
     │        │   "role": "assistant",
     │        │   "content": "I'll create...",
     │        │   "metadata": {
     │        │     "files_created": ["app.py"],
     │        │     "execution_success": true
     │        │   }
     │        │ }
     │        │
     └──► Step 11: Display results
          │
          ▼
     ┌─────────────────────────────┐
     │ CLI Display (Rich)          │
     │ ✓ Created: app.py           │
     │ ✓ Running: python app.py    │
     │                             │
     │ Output:                     │
     │  * Running on http://...    │
     └─────────────────────────────┘
```

**Data Modified:**
- conversation_history.json (2 messages appended)
- file_index.json (1 file entry added)
- execution_log.json (2 executions logged)
- metadata.json (last_updated, message_count incremented)
- app.py (created in workspace)

**Data Flow Summary:**
1. User Input → CLI
2. CLI → Agent Core
3. Agent Core → SessionManager (read context)
4. SessionManager → File System (read JSON)
5. Agent Core → BrowserConnector → LM Arena (send prompt)
6. LM Arena → BrowserConnector → Agent Core (receive response)
7. Agent Core → FileManager → File System (create file)
8. Agent Core → ExecutorEngine → OS Subprocess (execute)
9. Agent Core → SessionManager → File System (save all data)
10. Agent Core → CLI → User (display results)

---

## 3. FILE MODIFICATION FLOW

### Scenario: User asks to modify existing file

```
User: "add authentication to app.py"
     │
     ▼
Agent detects: app.py already exists
     │
     ├──► Read current content
     │    │ FileManager.read_file("app.py")
     │    │ Content: [existing Flask code]
     │    │
     ├──► Create backup
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ FileManager                  │
     │   │ .create_backup("app.py")     │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Copy: app.py → app.py.backup.1707300025
     │        │ Update: file_index.json
     │        │   "backups": [
     │        │     {
     │        │       "path": "app.py.backup.1707300025",
     │        │       "timestamp": 1707300025
     │        │     }
     │        │   ]
     │        │
     ├──► Send to model
     │    │ Prompt: "Modify app.py to add authentication
     │    │          Current code: [paste code]
     │    │          Add JWT authentication"
     │    │
     │    │ Model responds with new code
     │    │
     ├──► Generate diff
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ FileManager                  │
     │   │ .generate_diff(old, new)     │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Output:
     │        │ --- app.py (original)
     │        │ +++ app.py (modified)
     │        │ @@ -1,5 +1,7 @@
     │        │  from flask import Flask
     │        │ +from flask_jwt_extended import JWTManager
     │        │  ...
     │        │
     ├──► Show diff to user
     │    │ Display with syntax highlighting
     │    │ Prompt: [A]pply, [R]eject, [V]iew full
     │    │ User: A
     │    │
     ├──► Atomic write
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ FileManager                  │
     │   │ .atomic_write("app.py", new) │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Write: app.py.tmp.abc123
     │        │ fsync()
     │        │ Rename: app.py.tmp.abc123 → app.py
     │        │
     │        │ Update: file_index.json
     │        │   "last_modified": "2026-02-17T15:45:12Z"
     │        │   "modification_count": 1
     │        │   "hash_sha256": "new_hash"
     │        │
     └──► Complete
          Display: ✓ Modified: app.py
```

**Data Flow:**
User → Agent → FileManager (backup) → FileManager (diff) → FileManager (write) → SessionManager (log)

**Guarantees:**
- Original file backed up before modification
- Atomic write (never partial file)
- Full audit trail in file_index.json

---

## 4. SESSION RESUMPTION FLOW

### Scenario: User closes terminal, reopens later

```
Day 1: User creates session, works on project
       Session ID: abc-123
       Files created: app.py, config.py
       Messages: 10
       
       User closes terminal (Ctrl+C)
       
Day 2: User opens new terminal
       Runs: arenaagent ask "add logging"
       
       │
       ▼
┌─────────────────────────────────────────┐
│ Agent Core (agent.py)                   │
│ - No active session in memory           │
└────┬────────────────────────────────────┘
     │
     ├──► Step 1: Load latest session
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ SessionManager               │
     │   │ .load_latest_session()       │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Scan: ~/.arenaagent/sessions/
     │        │ Find all: metadata.json files
     │        │ Sort by: last_updated
     │        │ Select: Most recent
     │        │
     │        │ Found: abc-123/metadata.json
     │        │   last_updated: Day 1, 5pm
     │        │
     │        ├─► Load: abc-123/conversation_history.json
     │        │   Messages: 10 (all previous messages)
     │        │
     │        ├─► Load: abc-123/file_index.json
     │        │   Files: app.py, config.py
     │        │
     │        └─► Load: abc-123/execution_log.json
     │            Executions: 15
     │        │
     │        ▼
     │   ┌──────────────────────────────┐
     │   │ Return: Session object       │
     │   │ - ID: abc-123                │
     │   │ - Full context loaded        │
     │   └──────────────────────────────┘
     │
     ├──► Step 2: Send new prompt with context
     │    │ Model receives:
     │    │   "Previous conversation:
     │    │    [summary of 10 messages]
     │    │    Files created: app.py, config.py
     │    │    
     │    │    Current request: add logging"
     │    │
     │    │ Model knows full context!
     │    │ Generates logging code for existing files
     │    │
     └──► Step 3: Continue as normal
          Files modified with full awareness
          Session updated: message 11, 12, ...
```

**Key Point:**
- No data lost across restarts
- Full context restored automatically
- User doesn't need to re-explain anything

---

## 5. ERROR RECOVERY DATA FLOW

### Scenario: Code execution fails, automatic retry

```
Execution fails
     │
     ▼
┌─────────────────────────────────────────┐
│ ExecutorEngine                          │
│ ExecutionResult: exit_code=1            │
└────┬────────────────────────────────────┘
     │
     ├──► Parse error
     │    │ stderr: "ModuleNotFoundError: 
     │    │          No module named 'flask'"
     │    │
     │    ▼
     │   ┌──────────────────────────────┐
     │   │ ExecutorEngine               │
     │   │ .parse_error(stderr)         │
     │   └────┬─────────────────────────┘
     │        │
     │        │ Pattern match:
     │        │   "ModuleNotFoundError"
     │        │ Extract: module="flask"
     │        │
     │        ▼
     │   ┌──────────────────────────────┐
     │   │ Return: ErrorInfo            │
     │   │ - type: "missing_module"     │
     │   │ - message: "Missing: flask"  │
     │   │ - suggested_fix:             │
     │   │   "pip install flask"        │
     │   └──────────────────────────────┘
     │
     ├──► Send to model for fix
     │    │ Construct prompt:
     │    │   "The code resulted in error:
     │    │    ModuleNotFoundError: No module named 'flask'
     │    │    
     │    │    Please fix this error."
     │    │
     │    │ Send via BrowserConnector
     │    │ Model response:
     │    │   "Install Flask:
     │    │    ```bash
     │    │    pip install flask
     │    │    ```"
     │    │
     ├──► Parse fix
     │    │ Extract: bash command
     │    │ Command: "pip install flask"
     │    │
     ├──► Execute fix
     │    │ Run: pip install flask
     │    │ Success: ✓
     │    │
     │    │ Log to execution_log.json:
     │    │   {
     │    │     "id": 2,
     │    │     "command": "pip install flask",
     │    │     "exit_code": 0,
     │    │     "retry_attempt": 0
     │    │   }
     │    │
     ├──► Retry original execution
     │    │ Run: python app.py
     │    │ Success: ✓
     │    │
     │    │ Log to execution_log.json:
     │    │   {
     │    │     "id": 3,
     │    │     "command": "python app.py",
     │    │     "exit_code": 0,
     │    │     "retry_attempt": 1
     │    │   }
     │    │
     └──► Save conversation
          Message sequence:
          1. User: "create Flask app"
          2. Assistant: [code with Flask]
          3. System: "Error: ModuleNotFoundError"
          4. Assistant: "Install Flask: pip install..."
          
          Full audit trail preserved!
```

**Data Persisted:**
- All error messages
- All fix attempts
- Retry count
- Final success/failure state

**Recovery Strategy:**
1. Detect error → Parse → Send to model
2. Model suggests fix → Execute fix
3. Retry original → Log all steps
4. Maximum 3 attempts → Then stop

---

## 6. DATA PERSISTENCE GUARANTEES

### Write Operations:

```
Any data modification follows this pattern:

1. Prepare data in memory
2. Write to temp file
   └─► {target}.tmp.{random_id}
3. Flush to disk
   └─► fsync() ensures physical write
4. Atomic rename
   └─► os.replace(tmp, target)
       (Atomic on all platforms)

Result: Either old data or new data
        Never partial/corrupted data
```

### Read Operations:

```
All JSON reads follow this pattern:

1. Open file
2. Read content
3. Try: json.loads()
4. Except JSONDecodeError:
   ├─► Log error
   ├─► Archive corrupted file
   ├─► Return default/empty
   └─► Warn user

Result: System never crashes on corrupted data
```

---

## 7. CONCURRENT ACCESS HANDLING

### Problem:
What if user runs two `arenaagent` processes simultaneously?

### Solution:

```
Process 1: arenaagent ask "create app.py"
Process 2: arenaagent ask "create config.py"
           (started while Process 1 running)

Both processes:
├─► Load same session (abc-123)
├─► Send different prompts to LM Arena
└─► Try to write to conversation_history.json

Race condition detected!

Mitigation:
┌─────────────────────────────────────────┐
│ SessionManager                          │
│ Before write:                           │
│ 1. Read current message count           │
│ 2. New message ID = count + 1           │
│ 3. Write with message ID                │
│ 4. If write fails (file changed):       │
│    └─► Re-read, re-number, re-write     │
└─────────────────────────────────────────┘

Result: Both processes succeed
        Messages properly ordered
        No data loss
```

**Note:** Concurrent access is rare (single-user tool) but handled gracefully.

---

## 8. DATA FLOW SUMMARY TABLE

| Operation | Data Read From | Data Written To | External Calls |
|-----------|---------------|-----------------|----------------|
| **init** | None | config.json, session JSONs | LM Arena (login) |
| **ask** | conversation_history.json, file_index.json | All session JSONs, workspace files | LM Arena (prompt), OS (execute) |
| **history** | conversation_history.json | None | None |
| **sessions** | All metadata.json | None | None |
| **rollback** | file_index.json | Workspace file | None |
| **ps** | execution_log.json | None | OS (process list) |

---

*Data flow documentation complete. See ARCHITECTURE.md for component details.*
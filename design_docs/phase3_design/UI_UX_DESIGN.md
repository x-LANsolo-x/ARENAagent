# ArenaAgent - UI/UX Design

## Phase 3: CLI Interface Design

---

## 1. DESIGN PHILOSOPHY

### Core Principles:

1. **Clarity Over Cleverness**
   - Clear, explicit messages
   - No hidden magic
   - User always knows what's happening

2. **Progressive Disclosure**
   - Show only what user needs now
   - Details available with flags (--verbose)
   - Don't overwhelm with information

3. **Fail Gracefully**
   - Errors are helpful, not cryptic
   - Always suggest next action
   - Never leave user stuck

4. **Feedback is Immediate**
   - Show progress for long operations
   - Confirm actions before executing
   - Display results clearly

5. **Consistency**
   - Same patterns across all commands
   - Predictable flag names
   - Uniform output formatting

---

## 2. CLI COMMAND STRUCTURE

### Command Hierarchy:

```
arenaagent
├── init                    # One-time setup
├── ask <prompt>            # Main command (send prompt)
├── history                 # View conversation
├── sessions                # List all sessions
├── rollback <file>         # Restore file backup
├── ps                      # Show running processes
├── kill <pid>              # Stop background process
├── config                  # View/edit configuration
│   ├── show
│   ├── set <key> <value>
│   └── reset
└── version                 # Show version info
```

### Command Syntax Patterns:

```bash
# Pattern 1: Simple command
arenaagent <command>

# Pattern 2: Command with argument
arenaagent <command> <argument>

# Pattern 3: Command with flags
arenaagent <command> --flag1 --flag2=value

# Pattern 4: Nested commands
arenaagent <command> <subcommand> <argument>
```

---

## 3. TERMINAL OUTPUT DESIGN

### Color Scheme (Using Rich):

```python
# Status Colors
SUCCESS = "green"       # ✓ Actions completed
ERROR = "red"          # ✗ Errors and failures
WARNING = "yellow"     # ⚠ Warnings and cautions
INFO = "blue"          # ℹ Information messages
PROMPT = "cyan"        # User input prompts
CODE = "magenta"       # Code snippets
PATH = "dim"           # File paths

# Semantic Colors
USER_MESSAGE = "cyan"
ASSISTANT_MESSAGE = "green"
SYSTEM_MESSAGE = "yellow"
```

### Typography Hierarchy:

```
[TITLE]        # Bold, large (for major sections)
[HEADING]      # Bold (for command names)
[BODY]         # Normal (for descriptions)
[DETAIL]       # Dim (for metadata)
[CODE]         # Monospace, highlighted
```

### Icons/Symbols:

```
✓  Success
✗  Error
⚠  Warning
ℹ  Info
🔧 Setup/Configuration
💬 Message/Chat
📝 File operation
⚙️  Processing
🚀 Execution
📁 Directory/Session
🔍 Search/Find
⏱️  Time/Duration
```

---

## 4. COMMAND DESIGNS

### 4.1 `arenaagent init`

**Purpose:** First-time setup

**Output Design:**
```
🔧 ArenaAgent Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1/3: Creating directories
  ✓ Created: ~/.arenaagent/
  ✓ Created: ~/.arenaagent/sessions/
  ✓ Created: ~/arenaagent_workspace/

Step 2/3: Setting up browser profile
  🌐 Opening browser to LM Arena...
  
  ┌─────────────────────────────────────────────────────┐
  │                                                     │
  │  Please log in to LM Arena in the browser window   │
  │  using your Google account.                        │
  │                                                     │
  │  The browser will close automatically after login. │
  │                                                     │
  └─────────────────────────────────────────────────────┘
  
  ⏱️  Waiting for login... (timeout: 5 minutes)
  
  ✓ Login successful!
  ✓ Browser profile saved

Step 3/3: Creating initial session
  ✓ Session created: a1b2c3d4
  ✓ Default workspace: ~/arenaagent_workspace/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Setup complete!

Next steps:
  • Try: arenaagent ask "create a Python script"
  • Help: arenaagent --help
  • Docs: https://github.com/arenaagent/docs
```

**User Flow:**
1. User runs command
2. See progress for each step
3. Browser opens (headful)
4. User logs in
5. Browser closes automatically
6. Success message with next steps

---

### 4.2 `arenaagent ask "create Flask app"`

**Purpose:** Send prompt to AI

**Output Design:**
```
🔧 ArenaAgent v1.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 Workspace: ~/arenaagent_workspace/
🤖 Model: Claude-3.5-Sonnet
💬 Session: a1b2c3d4 (15 messages)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 Sending request...
   "create a Flask REST API for todo list"

⏱️  Waiting for response... [━━━━━━━━━━━━━━━━━━━━━] 5s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Assistant:

I'll create a Flask REST API for a todo list with basic CRUD operations.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Code Found: app.py (52 lines)

╭─────────────────────────── app.py ────────────────────────────╮
│                                                                │
│ from flask import Flask, jsonify, request                     │
│                                                                │
│ app = Flask(__name__)                                          │
│ todos = []                                                     │
│                                                                │
│ @app.route('/todos', methods=['GET'])                          │
│ def get_todos():                                               │
│     return jsonify(todos)                                      │
│                                                                │
│ @app.route('/todos', methods=['POST'])                         │
│ def create_todo():                                             │
│     todo = request.json                                        │
│     todos.append(todo)                                         │
│     return jsonify(todo), 201                                  │
│                                                                │
│ if __name__ == '__main__':                                     │
│     app.run(debug=True)                                        │
│                                                                │
╰────────────────────────────────────────────────────────────────╯

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What would you like to do?

  [C] Create file only
  [R] Create and run
  [V] View full code
  [S] Skip
  [Q] Quit

Your choice: █
```

**If user chooses [R] (Create and run):**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Creating file...
   ✓ Created: ~/arenaagent_workspace/app.py

🚀 Executing: python app.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✗ Execution failed (exit code: 1)

Error Output:
╭──────────────────────────────────────────────────────╮
│ Traceback (most recent call last):                  │
│   File "app.py", line 1, in <module>                │
│     from flask import Flask, jsonify, request       │
│ ModuleNotFoundError: No module named 'flask'        │
╰──────────────────────────────────────────────────────╯

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️  Auto-recovery: Sending error to model...

💬 Model response:

You need to install Flask first:

╭─────────────────────────────────────────────────────╮
│ pip install flask                                   │
╰─────────────────────────────────────────────────────╯

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Execute this fix? [Y/n]: █
```

**If user chooses [Y]:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Executing: pip install flask

⏱️  Running... [━━━━━━━━━━━━━━━━━━━━━] 3.2s

Output:
  Collecting flask
  Downloading Flask-3.0.0-py3-none-any.whl
  Installing collected packages: flask
  Successfully installed Flask-3.0.0

✓ Installation complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔁 Retrying original command...

🚀 Executing: python app.py

⏱️  Running...

Output:
  * Serving Flask app 'app'
  * Debug mode: on
  * Running on http://127.0.0.1:5000
  * Press CTRL+C to quit

✓ Server started successfully (PID: 12345)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Success!

Summary:
  ✓ Created: app.py
  ✓ Installed: flask
  ✓ Running: python app.py (PID: 12345)

Next steps:
  • Test: curl http://127.0.0.1:5000/todos
  • Stop: arenaagent kill 12345
  • Continue: arenaagent ask "add authentication"
```

**User Flow:**
1. User sends prompt
2. See session info (context awareness)
3. Watch request being sent
4. See AI response
5. Review generated code
6. Choose action (create/run/skip)
7. See execution results
8. If error: Automatic recovery flow
9. Final success summary with next steps

---

### 4.3 `arenaagent history`

**Purpose:** View conversation history

**Output Design:**
```
📜 Conversation History
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Session: a1b2c3d4
Created: 2026-02-17 10:30 AM
Messages: 15
Model: Claude-3.5-Sonnet

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] 10:30:15 AM
👤 You:
  create a Flask REST API for todo list

[2] 10:30:23 AM
🤖 Assistant:
  I'll create a Flask REST API for a todo list...
  
  📝 Created: app.py
  ✗ Execution failed: ModuleNotFoundError

[3] 10:30:30 AM
⚙️  System:
  Error: ModuleNotFoundError: No module named 'flask'

[4] 10:31:05 AM
🤖 Assistant:
  Install Flask first: pip install flask
  
  ✓ Executed: pip install flask
  ✓ Executed: python app.py

[5] 11:15:00 AM
👤 You:
  add authentication to the API

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Options:
  • View more: arenaagent history --limit 20
  • Export: arenaagent history --export session.md
  • New session: arenaagent sessions new
```

---

### 4.4 `arenaagent sessions`

**Purpose:** List all sessions

**Output Design:**
```
📂 Sessions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────┬─────────────────────┬──────────┬────────┐
│ ID       │ Created             │ Messages │ Files  │
├──────────┼─────────────────────┼──────────┼────────┤
│ a1b2c3d4 │ 2026-02-17 10:30 AM │ 15       │ 3      │ ✓ Active
│ e5f6g7h8 │ 2026-02-16 02:15 PM │ 8        │ 1      │
│ i9j0k1l2 │ 2026-02-15 09:00 AM │ 24       │ 7      │
└──────────┴─────────────────────┴──────────┴────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commands:
  • View: arenaagent history --session e5f6g7h8
  • Switch: arenaagent sessions switch e5f6g7h8
  • New: arenaagent sessions new
  • Archive: arenaagent sessions archive i9j0k1l2
```

---

### 4.5 `arenaagent rollback app.py`

**Purpose:** Restore file from backup

**Output Design:**
```
🔄 Rollback File
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

File: ~/arenaagent_workspace/app.py

Available backups:

┌────┬──────────────────────┬────────┬──────────┐
│ #  │ Created              │ Size   │ Changes  │
├────┼──────────────────────┼────────┼──────────┤
│ 1  │ 2026-02-17 03:45 PM  │ 1.2 KB │ +15 -3   │
│ 2  │ 2026-02-17 11:20 AM  │ 950 B  │ +8 -0    │
│ 3  │ 2026-02-17 10:30 AM  │ 892 B  │ Initial  │
└────┴──────────────────────┴────────┴──────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select backup to restore [1-3] or [Q]uit: █
```

**If user selects backup #2:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Preview changes:

╭────────────────────── Diff ───────────────────────╮
│ --- app.py (current)                              │
│ +++ app.py (backup from 11:20 AM)                 │
│ @@ -1,7 +1,5 @@                                   │
│  from flask import Flask, jsonify, request        │
│ -from flask_jwt_extended import JWTManager        │
│ -                                                 │
│  app = Flask(__name__)                            │
│ -jwt = JWTManager(app)                            │
│                                                   │
╰───────────────────────────────────────────────────╯

⚠️  This will remove JWT authentication

Restore this version? [y/N]: █
```

---

### 4.6 `arenaagent ps`

**Purpose:** Show running background processes

**Output Design:**
```
⚙️  Running Processes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌───────┬──────────────────────────────┬────────────┬────────┐
│ PID   │ Command                      │ Started    │ Status │
├───────┼──────────────────────────────┼────────────┼────────┤
│ 12345 │ python app.py                │ 10:31 AM   │ 🟢 Running │
│ 12456 │ node server.js               │ 11:45 AM   │ 🟢 Running │
└───────┴──────────────────────────────┴────────────┴────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commands:
  • Stop: arenaagent kill 12345
  • Logs: arenaagent logs 12345
  • Stop all: arenaagent kill --all
```

---

## 5. INTERACTIVE PROMPTS DESIGN

### Confirmation Prompt Pattern:

```
╭─────────────────────────────────────────────────────╮
│ [ICON] [MESSAGE]                                    │
│                                                     │
│ [DETAILS]                                           │
│                                                     │
│ [QUESTION]                                          │
│                                                     │
│ [OPTIONS]                                           │
╰─────────────────────────────────────────────────────╯
```

### Example: File Overwrite

```
╭─────────────────────────────────────────────────────╮
│ ⚠️  File Already Exists                              │
│                                                     │
│ File: app.py                                        │
│ Size: 1.2 KB                                        │
│ Last modified: 2 hours ago                          │
│                                                     │
│ Overwrite this file?                                │
│                                                     │
│ [O] Overwrite (with backup)                         │
│ [R] Rename new file                                 │
│ [D] Show diff                                       │
│ [C] Cancel                                          │
╰─────────────────────────────────────────────────────╯

Your choice: █
```

### Example: Destructive Command

```
╭─────────────────────────────────────────────────────╮
│ ⚠️⚠️⚠️  DANGEROUS COMMAND DETECTED  ⚠️⚠️⚠️               │
│                                                     │
│ Command: rm -rf /                                   │
│ Impact: DELETES ENTIRE SYSTEM                       │
│                                                     │
│ This command is BLOCKED for your safety.            │
│                                                     │
│ If you need to delete files, please specify        │
│ exact paths within your workspace.                  │
│                                                     │
│ [Press any key to continue]                         │
╰─────────────────────────────────────────────────────╯
```

---

## 6. PROGRESS INDICATORS

### Spinner (for quick operations < 3s):

```
⏱️  Loading session... ⣾
```

### Progress Bar (for longer operations):

```
⏱️  Installing dependencies...
[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] 75% (3/4)

  ✓ flask-3.0.0
  ✓ requests-2.31.0
  ✓ click-8.1.0
  ⏳ playwright-1.40.0
```

### Indeterminate Progress (waiting for LM Arena):

```
💬 Waiting for response...
[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] 5s
```

---

## 7. ERROR MESSAGE DESIGN

### Error Message Pattern:

```
✗ [ERROR TYPE]

Problem:
  [DESCRIPTION OF WHAT WENT WRONG]

Details:
  [TECHNICAL ERROR MESSAGE]

Suggestions:
  • [ACTION 1]
  • [ACTION 2]
  • [ACTION 3]

Help:
  • Docs: [URL]
  • Issue: [GITHUB URL]
```

### Example: Network Error

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✗ Network Error

Problem:
  Cannot reach LM Arena (chat.lmsys.org)

Details:
  Connection timeout after 30 seconds
  DNS resolution failed

Suggestions:
  • Check your internet connection
  • Verify you can access https://chat.lmsys.org in browser
  • Check if firewall is blocking access
  • Try again: arenaagent ask "your prompt"

Status:
  ✓ Your work is saved (no data lost)
  ✓ Session will resume when online

Help:
  • Troubleshooting: https://arenaagent.dev/docs/network
  • Report issue: https://github.com/arenaagent/issues

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Example: Session Corrupted

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✗ Session Data Corrupted

Problem:
  Session file cannot be read (JSON parse error)

Details:
  File: ~/.arenaagent/sessions/a1b2c3d4/conversation_history.json
  Error: Unexpected end of JSON input at line 234

Recovery:
  ✓ Corrupted session archived to: sessions/.archive/a1b2c3d4/
  ✓ Created new session: e5f6g7h8
  ✓ Your workspace files are safe

What was lost:
  ✗ Conversation history (15 messages)
  ✓ All created files are intact

Continue with new session? [Y/n]: █

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 8. SUCCESS MESSAGE DESIGN

### Success Pattern:

```
✅ [ACTION COMPLETED]

Summary:
  ✓ [ITEM 1]
  ✓ [ITEM 2]
  ✓ [ITEM 3]

Results:
  [KEY INFORMATION]

Next steps:
  • [SUGGESTION 1]
  • [SUGGESTION 2]
```

---

## 9. HELP TEXT DESIGN

### `arenaagent --help`

```
🔧 ArenaAgent v1.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Free AI coding assistant using LM Arena

USAGE:
  arenaagent <command> [options]

COMMANDS:
  init                    Set up ArenaAgent (one-time)
  ask <prompt>            Send a prompt to the AI
  history                 View conversation history
  sessions                Manage sessions
  rollback <file>         Restore file from backup
  ps                      Show running processes
  kill <pid>              Stop background process
  config                  View/edit configuration

FLAGS:
  -h, --help              Show this help message
  -v, --version           Show version
  --verbose               Show detailed output
  --dry-run               Show what would happen

EXAMPLES:
  arenaagent init
  arenaagent ask "create a Flask app"
  arenaagent ask "add tests" --model gpt-4
  arenaagent history --limit 20
  arenaagent rollback app.py

DOCUMENTATION:
  https://arenaagent.dev/docs

SUPPORT:
  https://github.com/arenaagent/issues
```

---

*Continued in USER_FLOWS.md...*
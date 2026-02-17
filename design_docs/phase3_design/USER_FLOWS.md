# ArenaAgent - User Flow Diagrams

## Complete User Interaction Flows

---

## FLOW 1: FIRST-TIME USER SETUP

### User Journey Map:

```
New User → Install → Initialize → First Prompt → Success
```

### Detailed Flow:

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Installation                                         │
└──────────────────────────────────────────────────────────────┘

User Action:
  Terminal: pip install arenaagent

System Response:
  Installing packages...
  ✓ arenaagent-1.0.0 installed
  
Next: arenaagent --help

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Read Help                                            │
└──────────────────────────────────────────────────────────────┘

User Action:
  Terminal: arenaagent --help

System Response:
  [Shows help text with commands]
  
Next: arenaagent init

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────────────────────────────────────────────────┐
│ STEP 3: Initialize                                           │
└──────────────────────────────────────────────────────────────┘

User Action:
  Terminal: arenaagent init

System Response:
  🔧 ArenaAgent Setup
  
  Step 1/3: Creating directories
    ✓ Created: ~/.arenaagent/
  
  Step 2/3: Setting up browser profile
    🌐 Opening browser to LM Arena...
    
    ┌─────────────────────────────────────────┐
    │ Please log in with your Google account │
    └─────────────────────────────────────────┘
    
User Action:
  [Browser opens]
  Clicks "Sign in with Google"
  Enters credentials
  Completes login
  
System Response:
    ✓ Login successful!
    ✓ Browser profile saved
  
  Step 3/3: Creating initial session
    ✓ Session created: a1b2c3d4
  
  ✅ Setup complete!
  
  Next: arenaagent ask "create a Python script"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────────────────────────────────────────────────┐
│ STEP 4: First Prompt                                         │
└──────────────────────────────────────────────────────────────┘

User Action:
  Terminal: arenaagent ask "create a hello world script"

System Response:
  💬 Sending request...
  ⏱️  Waiting for response...
  
  🤖 Assistant: [code response]
  
  📝 Code Found: hello.py
  
  [C]reate file, [R]un, [V]iew, [S]kip
  
User Action:
  Presses: R

System Response:
  ✓ Created: hello.py
  🚀 Executing: python hello.py
  
  Output:
    Hello, World!
  
  ✅ Success!
  
User Emotion: 😊 It works! I'm ready to build!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OUTCOME: User successfully set up and used ArenaAgent
TIME: ~5-10 minutes
FRICTION POINTS: Login (necessary), waiting for response
SATISFACTION: High (immediate value)
```

---

## FLOW 2: DAILY USAGE - BUILDING A PROJECT

### User Journey Map:

```
User with Idea → Create → Iterate → Fix Errors → Deploy
```

### Detailed Flow:

```
┌──────────────────────────────────────────────────────────────┐
│ SCENARIO: Build a Flask REST API                             │
└──────────────────────────────────────────────────────────────┘

DAY 1, 10:00 AM - Initial Creation

User Action:
  arenaagent ask "create a Flask REST API for a blog"

Flow:
  → System sends prompt to LM Arena
  → Model generates Flask code
  → System creates app.py
  → User chooses [R]un
  → Error: ModuleNotFoundError: flask
  → Auto-recovery: Install flask
  → Retry: Success
  → Server running

Outcome:
  ✓ app.py created
  ✓ flask installed
  ✓ Server running on port 5000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DAY 1, 11:30 AM - Add Feature

User Action:
  arenaagent ask "add authentication with JWT"

Flow:
  → System loads context (knows about app.py)
  → Model modifies app.py
  → Shows diff preview
  → User confirms [A]pply
  → Backup created automatically
  → File updated
  → Server restarted

Outcome:
  ✓ app.py modified (with backup)
  ✓ Authentication added
  ✓ Server restarted

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DAY 1, 2:00 PM - Add Database

User Action:
  arenaagent ask "add SQLite database for posts"

Flow:
  → Model generates database code
  → Creates models.py
  → Modifies app.py to use database
  → User runs migrations
  → Tests endpoints

Outcome:
  ✓ models.py created
  ✓ app.py updated
  ✓ Database schema created

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DAY 1, 3:00 PM - User closes terminal

Session State:
  ✓ All conversation saved
  ✓ All files intact
  ✓ Context preserved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DAY 2, 9:00 AM - User resumes

User Action:
  arenaagent ask "add API documentation with Swagger"

Flow:
  → System loads yesterday's session
  → Full context restored (app.py, models.py, all messages)
  → Model knows entire project history
  → Generates Swagger integration
  → User applies changes

Outcome:
  ✓ Context seamlessly resumed
  ✓ No need to re-explain project
  ✓ Documentation added

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOTAL OUTCOME:
  - Project completed in 2 days
  - 4 features implemented
  - 0 manual debugging
  - Full audit trail preserved
```

---

## FLOW 3: ERROR RECOVERY JOURNEY

### User Journey Map:

```
Execute Code → Error → Auto-Fix → Retry → Success
```

### Detailed Flow:

```
┌──────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO 1: Missing Dependency                         │
└──────────────────────────────────────────────────────────────┘

User sees:
  ✗ Execution failed
  Error: ModuleNotFoundError: No module named 'flask'
  
  ⚙️  Auto-recovery: Sending error to model...

Behind the scenes:
  1. Executor detects exit_code=1
  2. Parses stderr → identifies "missing_module"
  3. Sends to model: "Error: ModuleNotFoundError..."
  4. Model responds: "pip install flask"
  5. Prompts user for approval

User action:
  Execute fix? [Y/n]: Y

Result:
  ✓ Installed flask
  🔁 Retrying original command
  ✓ Success!

User emotion: 😌 Relieved - didn't have to debug

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO 2: Syntax Error                               │
└──────────────────────────────────────────────────────────────┘

User sees:
  ✗ Execution failed
  Error: SyntaxError: invalid syntax (line 12)
  
  ⚙️  Auto-recovery: Sending error to model...

Model analyzes:
  → Reviews code at line 12
  → Identifies missing colon
  → Generates corrected version

User action:
  View diff? [Y/n]: Y
  
  [Shows before/after]
  
  Apply fix? [Y/n]: Y

Result:
  ✓ File updated (backup created)
  🔁 Retrying
  ✓ Success!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO 3: Unfixable Error (after 3 retries)          │
└──────────────────────────────────────────────────────────────┘

Retry 1: Model suggests fix → Still fails
Retry 2: Model tries different approach → Still fails  
Retry 3: Model suggests workaround → Still fails

User sees:
  ✗ Unable to auto-fix after 3 attempts
  
  Last error: [error message]
  
  Suggestions:
    • Manual debugging may be needed
    • Review error log: arenaagent logs
    • Ask for help: arenaagent ask "how to fix [error]"
  
  Files:
    ✓ All backups preserved
    ✓ Execution log saved

User action:
  Can investigate manually or ask different question

User emotion: 😕 Stuck, but has all information needed
```

---

## FLOW 4: FILE MODIFICATION JOURNEY

### Detailed Flow:

```
┌──────────────────────────────────────────────────────────────┐
│ SCENARIO: Modify existing file                               │
└──────────────────────────────────────────────────────────────┘

Initial state:
  app.py exists (1.2 KB, last modified 2 hours ago)

User action:
  arenaagent ask "refactor app.py to use blueprints"

Flow:

[1] System detects: app.py exists
    → Reads current content
    → Creates backup: app.py.backup.1707300000

[2] Sends to model with context:
    "Current code: [paste app.py content]
     Refactor to use blueprints"

[3] Model responds with refactored code

[4] System generates diff:
    --- app.py (current)
    +++ app.py (proposed)
    @@ -1,5 +1,8 @@
     from flask import Flask
    +from blueprints.auth import auth_bp
    +from blueprints.posts import posts_bp
    
     app = Flask(__name__)
    +app.register_blueprint(auth_bp)
    
[5] User sees diff preview:
    ╭────────────── Changes ──────────────╮
    │ + Added: Blueprint imports          │
    │ + Registered 2 blueprints           │
    │ ~ Modified: App structure           │
    │ Total: +15 lines, -3 lines          │
    ╰─────────────────────────────────────╯
    
    [A]pply, [R]eject, [V]iew full diff

[6] User chooses: A

[7] System:
    ✓ Backup created: app.py.backup.1707300000
    ✓ Applied changes atomically
    ✓ Updated file_index.json

[8] User satisfaction: 😊 Safe changes with backup

Rollback available:
  arenaagent rollback app.py
```

---

## FLOW 5: SESSION MANAGEMENT JOURNEY

### Detailed Flow:

```
┌──────────────────────────────────────────────────────────────┐
│ SCENARIO: Working on multiple projects                       │
└──────────────────────────────────────────────────────────────┘

MORNING: Project A (Blog API)

User:
  arenaagent ask "add pagination to blog posts"
  
  Session: abc-123
  Context: Blog API project

AFTERNOON: Switch to Project B (Discord Bot)

User:
  arenaagent sessions new
  
System:
  ✓ Created new session: def-456
  ✓ New workspace: ~/arenaagent_workspace_2/

User:
  arenaagent ask "create a Discord bot"
  
  Session: def-456
  Context: Fresh, no history

EVENING: Back to Project A

User:
  arenaagent sessions
  
  Shows:
    abc-123 (Blog API) - 25 messages
    def-456 (Discord Bot) - 8 messages

User:
  arenaagent sessions switch abc-123

System:
  ✓ Switched to session: abc-123
  ✓ Loaded context: 25 messages
  ✓ Workspace: ~/arenaagent_workspace/

User:
  arenaagent ask "add caching to API"
  
  Model remembers: Full blog API context!

Benefits:
  ✓ Multiple projects isolated
  ✓ Context preserved for each
  ✓ Easy switching
  ✓ No confusion between projects
```

---

*Continued in SYSTEM_FLOWS.md...*
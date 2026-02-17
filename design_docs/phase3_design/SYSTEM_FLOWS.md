# ArenaAgent - System Flow Diagrams

## Visual System Interaction Diagrams

---

## DIAGRAM 1: COMPLETE SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                              │
│                                                                 │
│  Developer using terminal (CLI)                                 │
│                                                                 │
│  Actions:                                                       │
│  • Types commands                                               │
│  • Approves operations                                          │
│  • Reviews outputs                                              │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ CLI Interface (Click + Rich)                            │   │
│  │                                                         │   │
│  │ • Command parsing                                       │   │
│  │ • Output formatting                                     │   │
│  │ • User prompts                                          │   │
│  │ • Progress indicators                                   │   │
│  │                                                         │   │
│  │ Commands: init, ask, history, sessions, rollback, ps    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Agent Core (Orchestrator)                               │   │
│  │                                                         │   │
│  │ Responsibilities:                                       │   │
│  │ • Workflow orchestration                                │   │
│  │ • Service coordination                                  │   │
│  │ • Error recovery logic                                  │   │
│  │ • Context management                                    │   │
│  │ • State tracking                                        │   │
│  │                                                         │   │
│  │ Key Methods:                                            │   │
│  │ • initialize()                                          │   │
│  │ • send_prompt()                                         │   │
│  │ • handle_error()                                        │   │
│  │ • process_response()                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└──┬────────┬──────────┬──────────┬──────────┬────────────────────┘
   │        │          │          │          │
   ▼        ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                               │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Browser  │  │ Session  │  │ Executor │  │   File   │       │
│  │Connector │  │ Manager  │  │  Engine  │  │ Manager  │       │
│  │          │  │          │  │          │  │          │       │
│  │ • launch │  │ • create │  │ • execute│  │ • create │       │
│  │ • send   │  │ • load   │  │ • parse  │  │ • backup │       │
│  │ • extract│  │ • save   │  │ • retry  │  │ • rollbk │       │
│  │ • close  │  │ • list   │  │ • valid  │  │ • atomic │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │              │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                         │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Playwright│  │   JSON   │  │subprocess│  │ pathlib  │       │
│  │(Chromium)│  │  Files   │  │   (OS)   │  │File Systm│       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │              │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SYSTEMS                             │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │LM Arena  │  │  ~/.     │  │OS Process│  │Workspace │       │
│  │(Browser) │  │arenaagent│  │ Manager  │  │Directory │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## DIAGRAM 2: REQUEST-RESPONSE FLOW

```
USER TYPES COMMAND
        │
        ├─→ "arenaagent ask 'create Flask app'"
        │
        ▼
┌────────────────────────┐
│  CLI INTERFACE         │
│  (Click framework)     │
└───────┬────────────────┘
        │
        ├─→ Parse: command="ask", prompt="create Flask app"
        │
        ▼
┌────────────────────────┐
│  AGENT CORE            │
│  send_prompt()         │
└───────┬────────────────┘
        │
        ├─→ Step 1: Load context
        │
        ▼
┌────────────────────────┐
│  SESSION MANAGER       │
│  get_context()         │
└───────┬────────────────┘
        │
        ├─→ Read: conversation_history.json
        ├─→ Return: Last 10 messages
        │
        ▼
┌────────────────────────┐
│  AGENT CORE            │
│  Construct full prompt │
└───────┬────────────────┘
        │
        ├─→ Combine: context + new prompt
        │
        ▼
┌────────────────────────┐
│  BROWSER CONNECTOR     │
│  send_message()        │
└───────┬────────────────┘
        │
        ├─→ Find textarea element
        ├─→ Type message
        ├─→ Click send button
        │
        ▼
┌────────────────────────┐
│  LM ARENA              │
│  (External service)    │
└───────┬────────────────┘
        │
        ├─→ Process with Claude API
        ├─→ Stream response
        │
        ▼
┌────────────────────────┐
│  BROWSER CONNECTOR     │
│  extract_response()    │
└───────┬────────────────┘
        │
        ├─→ Wait for completion
        ├─→ Extract from DOM
        │
        ▼
┌────────────────────────┐
│  AGENT CORE            │
│  process_response()    │
└───────┬────────────────┘
        │
        ├─→ Parse code blocks
        ├─→ Detect file operations
        │
        ▼
┌────────────────────────┐
│  FILE MANAGER          │
│  create_file()         │
└───────┬────────────────┘
        │
        ├─→ Create backup (if exists)
        ├─→ Atomic write
        │
        ▼
┌────────────────────────┐
│  EXECUTOR ENGINE       │
│  execute()             │
└───────┬────────────────┘
        │
        ├─→ Validate command
        ├─→ Run subprocess
        ├─→ Capture output
        │
        ▼
   ┌─────────┐
   │SUCCESS? │
   └────┬────┘
        │
    ┌───┴───┐
    │       │
   Yes      No
    │       │
    ▼       ▼
 Display  ERROR
 Results  RECOVERY
           LOOP
```

---

## DIAGRAM 3: ERROR RECOVERY FLOW

```
CODE EXECUTION FAILS
        │
        ├─→ exit_code = 1
        ├─→ stderr contains error
        │
        ▼
┌────────────────────────────────────┐
│  EXECUTOR ENGINE                   │
│  parse_error()                     │
└───────┬────────────────────────────┘
        │
        ├─→ Pattern matching:
        │   • ModuleNotFoundError
        │   • SyntaxError
        │   • RuntimeError
        │   • etc.
        │
        ▼
┌────────────────────────────────────┐
│  ERROR INFO                        │
│  - type: "missing_module"          │
│  - message: "No module named flask"│
│  - suggested_fix: "pip install X"  │
└───────┬────────────────────────────┘
        │
        ▼
┌────────────────────────────────────┐
│  AGENT CORE                        │
│  handle_error()                    │
└───────┬────────────────────────────┘
        │
        ├─→ retry_count < max_retries?
        │
        ▼
      Yes ──→ Continue to recovery
        │
      No  ──→ Display final error & stop
        │
        ▼
┌────────────────────────────────────┐
│  BROWSER CONNECTOR                 │
│  Send error to model               │
└───────┬────────────────────────────┘
        │
        ├─→ Prompt: "Error: [details]
        │            Please fix."
        │
        ▼
┌────────────────────────────────────┐
│  LM ARENA                          │
│  Generate fix                      │
└───────┬────────────────────────────┘
        │
        ├─→ Response: "Install flask:
        │             pip install flask"
        │
        ▼
┌────────────────────────────────────┐
│  AGENT CORE                        │
│  Parse fix                         │
└───────┬────────────────────────────┘
        │
        ├─→ Extract: command="pip install flask"
        │
        ▼
┌────────────────────────────────────┐
│  USER APPROVAL                     │
│  "Execute fix? [Y/n]"              │
└───────┬────────────────────────────┘
        │
    ┌───┴───┐
    │       │
   Yes      No
    │       │
    ▼       └──→ STOP
┌────────────────────────────────────┐
│  EXECUTOR ENGINE                   │
│  execute(fix_command)              │
└───────┬────────────────────────────┘
        │
        ├─→ Run: pip install flask
        │
        ▼
┌────────────────────────────────────┐
│  EXECUTOR ENGINE                   │
│  Retry original command            │
└───────┬────────────────────────────┘
        │
        ├─→ retry_count++
        │
        ▼
   ┌─────────┐
   │SUCCESS? │
   └────┬────┘
        │
    ┌───┴───┐
    │       │
   Yes      No
    │       │
    ▼       └──→ LOOP BACK (max 3 times)
  DONE
```

---

## DIAGRAM 4: FILE MODIFICATION FLOW

```
USER: "modify app.py"
        │
        ▼
┌────────────────────────────────────┐
│  FILE MANAGER                      │
│  Check if file exists              │
└───────┬────────────────────────────┘
        │
    ┌───┴───┐
    │       │
  Exists  Not exist
    │       │
    ▼       └──→ create_file() → DONE
┌────────────────────────────────────┐
│  FILE MANAGER                      │
│  create_backup()                   │
└───────┬────────────────────────────┘
        │
        ├─→ Copy: app.py → app.py.backup.TIMESTAMP
        │
        ▼
┌────────────────────────────────────┐
│  AGENT CORE                        │
│  Send to model with current code   │
└───────┬────────────────────────────┘
        │
        ├─→ Prompt: "Current code: [paste]
        │            Modify to: [request]"
        │
        ▼
┌────────────────────────────────────┐
│  LM ARENA                          │
│  Generate modified code            │
└───────┬────────────────────────────┘
        │
        ├─→ Response: [new code]
        │
        ▼
┌────────────────────────────────────┐
│  FILE MANAGER                      │
│  generate_diff()                   │
└───────┬────────────────────────────┘
        │
        ├─→ Compare: old vs new
        │
        ▼
┌────────────────────────────────────┐
│  CLI INTERFACE                     │
│  Display diff to user              │
└───────┬────────────────────────────┘
        │
        ├─→ [A]pply, [R]eject, [V]iew full
        │
        ▼
┌────────────────────────────────────┐
│  USER APPROVAL                     │
└───────┬────────────────────────────┘
        │
    ┌───┴───┐
    │       │
  Apply   Reject
    │       │
    ▼       └──→ STOP (backup remains)
┌────────────────────────────────────┐
│  FILE MANAGER                      │
│  atomic_write()                    │
└───────┬────────────────────────────┘
        │
        ├─→ Write: app.py.tmp.RANDOM
        ├─→ fsync()
        ├─→ Rename: tmp → app.py
        │
        ▼
┌────────────────────────────────────┐
│  SESSION MANAGER                   │
│  Update file_index.json            │
└───────┬────────────────────────────┘
        │
        ├─→ Log: modification, new hash, backup path
        │
        ▼
      DONE
    (Backup preserved for rollback)
```

---

## DIAGRAM 5: SESSION LIFECYCLE

```
NEW USER
    │
    ▼
arenaagent init
    │
    ▼
┌────────────────────────────────────┐
│  SESSION MANAGER                   │
│  create_session()                  │
└───────┬────────────────────────────┘
        │
        ├─→ Generate: UUID v4
        ├─→ Create: ~/.arenaagent/sessions/UUID/
        ├─→ Create: metadata.json
        ├─→ Create: conversation_history.json
        ├─→ Create: file_index.json
        ├─→ Create: execution_log.json
        │
        ▼
    SESSION: abc-123
        │
        ├─→ User works on project
        │
        ▼
    Multiple prompts
        │
        ├─→ Each prompt appends to conversation_history
        ├─→ Each file appends to file_index
        ├─→ Each execution appends to execution_log
        │
        ▼
    User closes terminal
        │
        ├─→ All data persisted to disk
        │
        ▼
    Days later...
        │
        ▼
arenaagent ask "continue project"
        │
        ▼
┌────────────────────────────────────┐
│  SESSION MANAGER                   │
│  load_latest_session()             │
└───────┬────────────────────────────┘
        │
        ├─→ Scan: all metadata.json files
        ├─→ Sort: by last_updated
        ├─→ Select: most recent (abc-123)
        │
        ▼
┌────────────────────────────────────┐
│  SESSION MANAGER                   │
│  Load full context                 │
└───────┬────────────────────────────┘
        │
        ├─→ Read: conversation_history (all messages)
        ├─→ Read: file_index (all files)
        ├─→ Read: execution_log (all runs)
        │
        ▼
    Context fully restored!
        │
        ├─→ User continues as if never stopped
        │
        ▼
    User starts new project
        │
        ▼
arenaagent sessions new
        │
        ▼
┌────────────────────────────────────┐
│  SESSION MANAGER                   │
│  create_session()                  │
└───────┬────────────────────────────┘
        │
        ├─→ New session: def-456
        ├─→ Independent from abc-123
        │
        ▼
    User switches between sessions
        │
        ▼
arenaagent sessions switch abc-123
        │
        ├─→ Active session = abc-123
        │
arenaagent sessions switch def-456
        │
        ├─→ Active session = def-456
        │
        ▼
    Both sessions preserved independently
```

---

## DIAGRAM 6: DATA PERSISTENCE FLOW

```
ANY WRITE OPERATION
        │
        ▼
┌────────────────────────────────────┐
│  Prepare data in memory            │
└───────┬────────────────────────────┘
        │
        ├─→ Serialize to JSON
        │
        ▼
┌────────────────────────────────────┐
│  Create temp file                  │
│  path.tmp.{random_id}              │
└───────┬────────────────────────────┘
        │
        ├─→ Write data to temp file
        │
        ▼
┌────────────────────────────────────┐
│  fsync() - Force disk write        │
└───────┬────────────────────────────┘
        │
        ├─→ Ensure data on physical disk
        │
        ▼
┌────────────────────────────────────┐
│  os.replace(tmp, target)           │
│  ATOMIC OPERATION                  │
└───────┬────────────────────────────┘
        │
        ├─→ Atomic rename on all platforms
        │
        ▼
┌────────────────────────────────────┐
│  Cleanup temp file (if exists)     │
└───────┬────────────────────────────┘
        │
        ▼
      DONE
        
GUARANTEE:
  File contains either:
  • Complete old data, OR
  • Complete new data
  NEVER partial/corrupted data
  
Even if:
  • Process crashes
  • System loses power
  • Disk full (fails before write)
```

---

## DIAGRAM 7: BROWSER AUTOMATION FLOW

```
FIRST RUN (init)
        │
        ▼
┌────────────────────────────────────┐
│  BROWSER CONNECTOR                 │
│  launch(headless=False)            │
└───────┬────────────────────────────┘
        │
        ├─→ Create profile dir:
        │   ~/.arenaagent/browser/
        │
        ▼
┌────────────────────────────────────┐
│  PLAYWRIGHT                        │
│  Launch Chromium with profile      │
└───────┬────────────────────────────┘
        │
        ├─→ Browser window opens
        │
        ▼
┌────────────────────────────────────┐
│  Navigate: chat.lmsys.org          │
└───────┬────────────────────────────┘
        │
        ▼
    LM Arena login page
        │
        ├─→ User clicks "Sign in with Google"
        ├─→ User enters credentials
        ├─→ OAuth flow completes
        │
        ▼
┌────────────────────────────────────┐
│  Cookies saved to profile          │
│  ~/.arenaagent/browser/Default/    │
│         Cookies (encrypted)        │
└───────┬────────────────────────────┘
        │
        ├─→ Close browser
        │
        ▼
    Profile persisted!
        │
        ▼
SUBSEQUENT RUNS
        │
        ▼
┌────────────────────────────────────┐
│  BROWSER CONNECTOR                 │
│  launch(headless=True)             │
└───────┬────────────────────────────┘
        │
        ├─→ Load existing profile
        │
        ▼
┌────────────────────────────────────┐
│  PLAYWRIGHT                        │
│  Chromium with saved cookies       │
└───────┬────────────────────────────┘
        │
        ├─→ Already logged in!
        │
        ▼
┌────────────────────────────────────┐
│  Navigate: chat.lmsys.org          │
│  → Directly to chat (no login)     │
└────────────────────────────────────┘
```

---

## DIAGRAM 8: CONCURRENT SAFETY (Edge Case)

```
RARE SCENARIO: Two processes running simultaneously

Process A                      Process B
    │                             │
    ├─→ arenaagent ask "X"        ├─→ arenaagent ask "Y"
    │                             │
    ▼                             ▼
Load session                   Load session
  abc-123                        abc-123
    │                             │
    │  Both processes have same session
    │                             │
    ▼                             ▼
Send to model                  Send to model
    │                             │
    ▼                             ▼
Get response                   Get response
    │                             │
    ├─→ Try to write to          ├─→ Try to write to
    │   conversation_history     │   conversation_history
    │                             │
    ▼                             ▼
┌─────────────────────────────────────────────────┐
│  FILE WRITE CONFLICT DETECTED                   │
└─────────────────────────────────────────────────┘
    │                             │
    ▼                             ▼
Read current                   Read current
message count                  message count
    │                             │
    ├─→ 10 messages               ├─→ 10 messages
    │                             │
    ▼                             ▼
New message                    New message
  ID = 11                        ID = 11
    │                             │
    ▼                             ▼
Write attempt                  Write attempt
    │                             │
┌───┴───────────────────────────────┴───┐
│  Process A wins (wrote first)         │
└───┬───────────────────────────────────┘
    │                             │
    ▼                             ▼
Success                        Failure (file changed)
    │                             │
    │                             ├─→ Re-read file
    │                             ├─→ Count = 11 now
    │                             ├─→ New ID = 12
    │                             ├─→ Retry write
    │                             ▼
    │                          Success
    │                             │
    ▼                             ▼
  DONE                          DONE

RESULT: Both messages saved, properly ordered
```

---

*System flow diagrams complete. Ready for implementation.*
# ArenaAgent - System Architecture

## Phase 2: System Planning and Architecture

---

## 1. SYSTEM OVERVIEW

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           USER (CLI)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CLI INTERFACE (Click)                      │
│  Commands: init, ask, history, rollback, sessions               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT CORE                               │
│  - Orchestrates all operations                                  │
│  - Manages state and workflow                                   │
└─────┬────────────┬────────────┬────────────┬────────────────────┘
      │            │            │            │
      ▼            ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Browser  │ │ Session  │ │ Executor │ │   File   │
│Connector │ │ Manager  │ │  Engine  │ │ Manager  │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │            │
     ▼            ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│LM Arena  │ │   JSON   │ │Subprocess│ │Local FS  │
│(Browser) │ │  Files   │ │ (OS)     │ │(Workspace)│
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

---

## 2. ARCHITECTURE LAYERS

### Layer 1: User Interface
- **Component:** CLI Interface (Click framework)
- **Responsibility:** Parse commands, display output
- **No business logic:** Just routing to Agent Core

### Layer 2: Application Logic
- **Component:** Agent Core
- **Responsibility:** Orchestration, workflow management
- **Coordinates:** All other modules

### Layer 3: Domain Services
- **Components:** Browser Connector, Session Manager, Executor, File Manager
- **Responsibility:** Specific domain operations
- **Independent:** Can be tested in isolation

### Layer 4: External Systems
- **Components:** LM Arena, File System, OS Subprocess
- **Responsibility:** External interactions
- **Abstracted:** Through service layer

---

## 3. COMPONENT DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Layer                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  cli.py                                                         │
│  ├── @click.command('init')      → agent.initialize()          │
│  ├── @click.command('ask')       → agent.send_prompt()         │
│  ├── @click.command('history')   → agent.show_history()        │
│  └── @click.command('rollback')  → agent.rollback_file()       │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Agent Core Layer                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  agent.py                                                       │
│  ├── AgentCore                                                  │
│  │   ├── initialize()          → Setup browser + session       │
│  │   ├── send_prompt()         → Orchestrate full flow         │
│  │   ├── process_response()    → Parse and act on response     │
│  │   └── handle_error()        → Error recovery workflow       │
│  │                                                              │
│  └── Uses:                                                      │
│      ├── BrowserConnector                                       │
│      ├── SessionManager                                         │
│      ├── ExecutorEngine                                         │
│      └── FileManager                                            │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                              │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│              │              │              │                   │
│ browser_     │ session_     │ executor.py  │ file_manager.py   │
│ connector.py │ manager.py   │              │                   │
│              │              │              │                   │
│ Browser      │ Session      │ Executor     │ FileManager       │
│ Connector    │ Manager      │ Engine       │                   │
│              │              │              │                   │
│ • launch()   │ • create()   │ • execute()  │ • create_file()   │
│ • send()     │ • load()     │ • parse_err()│ • backup_file()   │
│ • extract()  │ • save()     │ • retry()    │ • rollback()      │
│ • close()    │ • list()     │ • validate() │ • atomic_write()  │
│              │              │              │                   │
└──────────────┴──────────────┴──────────────┴───────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Systems Layer                       │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│              │              │              │                   │
│  Playwright  │    JSON      │  subprocess  │   pathlib         │
│  (Chromium)  │   (stdlib)   │   (stdlib)   │   (stdlib)        │
│              │              │              │                   │
│  LM Arena    │  File I/O    │  OS Shell    │   File System     │
│  Automation  │  Persistence │  Execution   │   Operations      │
│              │              │              │                   │
└──────────────┴──────────────┴──────────────┴───────────────────┘
```

---

## 4. DATA FLOW DIAGRAM

### Primary Flow: Send Prompt → Execute Code

```
User types: arenaagent "create Flask app"
         │
         ▼
    ┌─────────┐
    │   CLI   │ Parse command
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  Agent  │ Orchestrate flow
    │  Core   │
    └────┬────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
         ▼                                     ▼
    ┌─────────┐                          ┌─────────┐
    │ Session │ Load context             │ Browser │ Launch if needed
    │ Manager │                          │Connector│
    └────┬────┘                          └────┬────┘
         │                                     │
         │ Return: conversation history        │
         │◄────────────────────────────────────┘
         │
         ▼
    ┌─────────┐
    │ Browser │ Send prompt + context
    │Connector│ to LM Arena
    └────┬────┘
         │
         │ Wait for response...
         │
         ▼
    ┌─────────┐
    │ Browser │ Extract response
    │Connector│ from DOM
    └────┬────┘
         │
         │ Return: response text
         │
         ▼
    ┌─────────┐
    │  Agent  │ Parse response
    │  Core   │ (find code blocks)
    └────┬────┘
         │
         ├──► If code found:
         │
         ▼
    ┌─────────┐
    │  File   │ Create file
    │ Manager │ (with backup)
    └────┬────┘
         │
         │ File created
         │
         ▼
    ┌─────────┐
    │Executor │ Execute code
    │ Engine  │
    └────┬────┘
         │
         ├──► If success:
         │    └─► Display output → Save session → Done
         │
         ├──► If error:
         │
         ▼
    ┌─────────┐
    │  Agent  │ Extract error
    │  Core   │ Send back to LM Arena
    └────┬────┘
         │
         │ (Loop back to Browser Connector)
         │
         ▼
    [Retry up to 3 times]
         │
         ▼
    ┌─────────┐
    │ Session │ Save all messages
    │ Manager │ and results
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │   CLI   │ Display results
    └─────────┘
```

---

## 5. MODULE RESPONSIBILITIES

### 5.1 CLI Interface (`cli.py`)

**Purpose:** User command interface

**Responsibilities:**
- Parse command-line arguments
- Route commands to Agent Core
- Display formatted output (via Rich)
- Handle user input prompts

**Does NOT:**
- Contain business logic
- Directly access services
- Manage state

**Interface:**
```python
@click.group()
def cli():
    pass

@cli.command()
@click.argument('prompt')
def ask(prompt: str):
    agent = AgentCore()
    result = agent.send_prompt(prompt)
    display_result(result)
```

---

### 5.2 Agent Core (`agent.py`)

**Purpose:** Central orchestrator

**Responsibilities:**
- Initialize system
- Orchestrate workflow
- Coordinate services
- Error handling
- State management

**Interface:**
```python
class AgentCore:
    def __init__(self):
        self.browser = BrowserConnector()
        self.session = SessionManager()
        self.executor = ExecutorEngine()
        self.file_mgr = FileManager()
    
    def send_prompt(self, prompt: str) -> Result:
        # Load context
        # Send to LM Arena
        # Process response
        # Execute if needed
        # Handle errors
        # Save session
        pass
```

**Key Methods:**
- `initialize()` - Setup browser and session
- `send_prompt(prompt)` - Main workflow
- `process_response(response)` - Parse and act
- `handle_error(error)` - Recovery workflow
- `cleanup()` - Graceful shutdown

---

### 5.3 Browser Connector (`browser_connector.py`)

**Purpose:** LM Arena automation

**Responsibilities:**
- Launch Playwright browser
- Manage persistent profile
- Send messages to LM Arena
- Extract responses from DOM
- Handle network errors

**Interface:**
```python
class BrowserConnector:
    def launch(self, headless: bool = True):
        pass
    
    def send_message(self, message: str) -> str:
        pass
    
    def extract_response(self) -> str:
        pass
    
    def close(self):
        pass
```

**Dependencies:**
- Playwright
- Chromium browser

---

### 5.4 Session Manager (`session_manager.py`)

**Purpose:** Conversation persistence

**Responsibilities:**
- Create new sessions
- Load existing sessions
- Save messages
- Manage session metadata
- Handle corruption

**Interface:**
```python
class SessionManager:
    def create_session(self) -> str:  # Returns session_id
        pass
    
    def load_session(self, session_id: str) -> Session:
        pass
    
    def save_message(self, message: Message):
        pass
    
    def list_sessions(self) -> List[SessionMeta]:
        pass
```

**Data Location:**
- `~/.arenaagent/sessions/[session_id]/`

---

### 5.5 Executor Engine (`executor.py`)

**Purpose:** Code execution

**Responsibilities:**
- Parse code blocks from responses
- Execute Python/Bash/Node.js
- Capture output and errors
- Validate safety
- Manage timeouts

**Interface:**
```python
class ExecutorEngine:
    def execute(self, code: str, language: str) -> ExecutionResult:
        pass
    
    def parse_error(self, stderr: str) -> ErrorInfo:
        pass
    
    def validate_command(self, command: str) -> bool:
        pass
```

**Dependencies:**
- subprocess module

---

### 5.6 File Manager (`file_manager.py`)

**Purpose:** Safe file operations

**Responsibilities:**
- Create/modify files
- Automatic backups
- Atomic writes
- Diff generation
- Rollback support

**Interface:**
```python
class FileManager:
    def create_file(self, path: str, content: str):
        pass
    
    def backup_file(self, path: str) -> str:
        pass
    
    def atomic_write(self, path: str, content: str):
        pass
    
    def rollback(self, path: str, timestamp: int):
        pass
```

**Dependencies:**
- pathlib, shutil, tempfile

---

## 6. CONFIGURATION MANAGEMENT

### Config File Location:
`~/.arenaagent/config.json`

### Config Schema:
```json
{
  "version": "1.0",
  "default_model": "claude-3.5-sonnet",
  "default_workspace": "~/arenaagent_workspace/",
  "browser": {
    "profile_path": "~/.arenaagent/browser/",
    "headless": true,
    "timeout": 30
  },
  "execution": {
    "auto_approve": false,
    "timeout": 60,
    "max_retries": 3
  },
  "files": {
    "auto_backup": true,
    "backup_retention_days": 30
  },
  "session": {
    "auto_save": true,
    "context_window_tokens": 50000
  }
}
```

### Config Manager:
```python
class ConfigManager:
    @staticmethod
    def load() -> Config:
        pass
    
    @staticmethod
    def save(config: Config):
        pass
    
    @staticmethod
    def get(key: str, default=None):
        pass
```

---

*Continued in next message...*
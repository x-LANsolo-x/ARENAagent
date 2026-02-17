# ArenaAgent - Terminal Output Design Specifications

## Visual Design and Formatting Standards

---

## 1. COLOR PALETTE

### Primary Colors (Rich Library):

```python
# Semantic Colors
COLORS = {
    # Status indicators
    "success": "green",
    "error": "red", 
    "warning": "yellow",
    "info": "blue",
    
    # UI elements
    "prompt": "cyan",
    "highlight": "magenta",
    "muted": "dim",
    "code": "bright_black on white",
    
    # Message roles
    "user": "bright_cyan",
    "assistant": "bright_green",
    "system": "bright_yellow",
    
    # Accents
    "accent1": "bright_magenta",
    "accent2": "bright_blue",
}
```

### Usage Examples:

```python
from rich.console import Console

console = Console()

# Success message
console.print("✓ File created", style="green")

# Error message
console.print("✗ Failed to execute", style="red")

# User prompt
console.print("Your choice: ", style="cyan", end="")

# Code block
console.print(code, style="bright_black on white")
```

---

## 2. TYPOGRAPHY HIERARCHY

### Text Styles:

```python
STYLES = {
    # Headers
    "title": "bold bright_white",
    "heading": "bold cyan",
    "subheading": "bold",
    
    # Body text
    "body": "default",
    "detail": "dim",
    "emphasis": "bold",
    
    # Special
    "code": "magenta",
    "path": "bright_blue underline",
    "link": "bright_blue underline",
    "timestamp": "dim",
}
```

### Size Hierarchy (via formatting):

```
[TITLE]         ═══════════════════════════
[HEADING]       ━━━━━━━━━━━━━━━━━━━━━━━━━━━
[SUBHEADING]    ────────────────────────────
[BODY]          Regular text
[DETAIL]        Dim text
```

---

## 3. LAYOUT COMPONENTS

### 3.1 Section Dividers

**Heavy Divider (Major sections):**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Light Divider (Sub-sections):**
```
────────────────────────────────────────────────────────
```

**Double Divider (Special emphasis):**
```
═══════════════════════════════════════════════════════
```

### 3.2 Boxes and Panels

**Info Box:**
```
╭─────────────────────────────────────────────────────╮
│                                                     │
│  [ICON] [TITLE]                                     │
│                                                     │
│  [CONTENT]                                          │
│                                                     │
╰─────────────────────────────────────────────────────╯
```

**Code Block:**
```
╭─────────────────────── filename.py ────────────────╮
│                                                     │
│ def hello():                                        │
│     print("Hello, World!")                          │
│                                                     │
╰─────────────────────────────────────────────────────╯
```

**Compact Box:**
```
┌─────────────────────────────────────────────────────┐
│ [CONTENT]                                           │
└─────────────────────────────────────────────────────┘
```

### 3.3 Lists

**Bullet List:**
```
• Item 1
• Item 2
  • Nested item
• Item 3
```

**Numbered List:**
```
1. First step
2. Second step
3. Third step
```

**Checklist:**
```
✓ Completed item
✗ Failed item
⏳ In progress
○ Not started
```

### 3.4 Tables

**Standard Table:**
```
┌──────────┬─────────────────────┬──────────┐
│ Column 1 │ Column 2            │ Column 3 │
├──────────┼─────────────────────┼──────────┤
│ Data 1   │ Data 2              │ Data 3   │
│ Data 4   │ Data 5              │ Data 6   │
└──────────┴─────────────────────┴──────────┘
```

**Compact Table:**
```
ID       Created             Messages  
────────────────────────────────────── 
abc123   2026-02-17 10:30    15
def456   2026-02-16 14:20    8
```

---

## 4. ICON SYSTEM

### Standard Icons:

```python
ICONS = {
    # Status
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    
    # Actions
    "processing": "⚙️",
    "loading": "⏱️",
    "executing": "🚀",
    "waiting": "⏳",
    
    # Objects
    "file": "📝",
    "folder": "📁",
    "session": "💬",
    "browser": "🌐",
    "config": "🔧",
    
    # Navigation
    "next": "→",
    "previous": "←",
    "up": "↑",
    "down": "↓",
    
    # Misc
    "checkmark": "✓",
    "cross": "✗",
    "bullet": "•",
    "arrow": "→",
}
```

### Icon Usage Examples:

```
✓ Success message
✗ Error message
⚠ Warning message
ℹ Info message
⚙️ Processing...
🚀 Executing command
📝 File created
💬 Message sent
```

---

## 5. PROGRESS INDICATORS

### 5.1 Spinner (Short Operations)

**Frames:**
```python
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
```

**Display:**
```
⏱️ Loading session... ⠋
⏱️ Loading session... ⠙
⏱️ Loading session... ⠹
```

### 5.2 Progress Bar (Long Operations)

**Full Progress Bar:**
```
Installing dependencies... 
[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] 100% (4/4)
```

**Partial Progress:**
```
Installing dependencies...
[━━━━━━━━━━━━━━━━━━━━━━━━╺─────────────] 65% (2.6/4)
```

**With Status:**
```
Installing dependencies...
[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] 75% (3/4)

  ✓ flask-3.0.0
  ✓ requests-2.31.0
  ✓ click-8.1.0
  ⏳ playwright-1.40.0 (downloading...)
```

### 5.3 Indeterminate Progress

**Waiting for Response:**
```
💬 Waiting for response...
[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] 5s
[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] 6s
[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] 7s
```

**Pulse Animation:**
```
⏳ Processing... ◐
⏳ Processing... ◓
⏳ Processing... ◑
⏳ Processing... ◒
```

---

## 6. INTERACTIVE ELEMENTS

### 6.1 Single Choice Prompt

```
What would you like to do?

  [C] Create file only
  [R] Create and run
  [V] View full code
  [S] Skip
  [Q] Quit

Your choice: █
```

### 6.2 Yes/No Confirmation

```
Execute this code? [Y/n]: █
```

**Default Yes:**
```
Continue? [Y/n]: █
```

**Default No:**
```
Delete file? [y/N]: █
```

### 6.3 Multi-Select

```
Select backups to delete (space to select, enter to confirm):

  [ ] Backup from 2026-02-17 15:45
  [×] Backup from 2026-02-17 11:20
  [×] Backup from 2026-02-17 10:30
  [ ] Backup from 2026-02-16 14:00

Selected: 2/4
```

### 6.4 Text Input

```
Session name: █

Enter new value (or press Enter to keep default): █

File path: ~/workspace/█
```

---

## 7. CODE DISPLAY

### 7.1 Inline Code

```
Install flask with: `pip install flask`
```

### 7.2 Code Block with Syntax Highlighting

```python
from rich.syntax import Syntax
from rich.console import Console

code = '''
def hello():
    print("Hello, World!")
'''

syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
console = Console()
console.print(syntax)
```

**Output:**
```
╭─────────────────────── hello.py ───────────────────────╮
│  1 def hello():                                        │
│  2     print("Hello, World!")                          │
╰────────────────────────────────────────────────────────╯
```

### 7.3 Diff Display

```diff
╭────────────────────── app.py ──────────────────────╮
│ --- app.py (current)                               │
│ +++ app.py (modified)                              │
│ @@ -1,5 +1,7 @@                                    │
│  from flask import Flask                           │
│ +from flask_jwt_extended import JWTManager         │
│                                                    │
│  app = Flask(__name__)                             │
│ +jwt = JWTManager(app)                             │
╰────────────────────────────────────────────────────╯

Changes:
  + Added: JWT authentication
  + Lines: +2
  - Lines: 0
```

---

## 8. MESSAGE DISPLAY

### 8.1 User Message

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[15] 10:30 AM
👤 You:
  create a Flask REST API for todo list

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 8.2 Assistant Message

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[16] 10:30 AM
🤖 Assistant:

I'll create a Flask REST API with CRUD operations for a todo list.

[Code block displayed]

📝 Files created:
  • app.py
  • models.py

🚀 Execution:
  ✓ Success

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 8.3 System Message

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[17] 10:30 AM
⚙️ System:

Execution error: ModuleNotFoundError
Auto-recovery initiated...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 9. STATUS DISPLAYS

### 9.1 Header with Metadata

```
🔧 ArenaAgent v1.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 Workspace: ~/arenaagent_workspace/
🤖 Model: Claude-3.5-Sonnet
💬 Session: a1b2c3d4 (15 messages)
⏱️ Time: 10:30 AM

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 9.2 Summary Panel

```
╭─────────────────── Summary ───────────────────╮
│                                               │
│  ✓ Created: app.py                            │
│  ✓ Installed: flask, requests                 │
│  ✓ Executed: python app.py                    │
│  ⚠ Warnings: 1                                │
│                                               │
│  Duration: 5.2 seconds                        │
│  Exit code: 0                                 │
│                                               │
╰───────────────────────────────────────────────╯
```

### 9.3 Stats Display

```
📊 Session Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Messages:        24
Files created:   5
Executions:      12
  ✓ Success:     10
  ✗ Failed:      2
Tokens (est):    45,000
Time saved:      ~2 hours

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 10. ERROR DISPLAY TEMPLATES

### 10.1 Standard Error

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✗ Network Error

Problem:
  Cannot reach LM Arena (chat.lmsys.org)

Details:
  Connection timeout after 30 seconds

Suggestions:
  • Check your internet connection
  • Verify access: https://chat.lmsys.org
  • Try again: arenaagent retry

Status:
  ✓ Your work is saved (no data lost)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 10.2 Critical Error with Box

```
╭─────────────────────────────────────────────────────╮
│ ⚠️⚠️⚠️  CRITICAL ERROR  ⚠️⚠️⚠️                           │
│                                                     │
│ Browser crashed unexpectedly                        │
│                                                     │
│ Recovery actions:                                   │
│   ✓ Session saved                                   │
│   ✓ Files preserved                                 │
│   ⏳ Restarting browser...                          │
│                                                     │
│ If this persists:                                   │
│   • Report: github.com/arenaagent/issues           │
│   • Logs: ~/.arenaagent/logs/error.log             │
│                                                     │
╰─────────────────────────────────────────────────────╯
```

---

## 11. RESPONSIVE DESIGN

### Terminal Width Handling:

```python
from rich.console import Console

console = Console()
width = console.width

# Narrow terminal (< 80 columns)
if width < 80:
    # Shorter dividers
    # Compact tables
    # Wrapped text
    pass

# Wide terminal (>= 80 columns)
else:
    # Full-width dividers
    # Expanded tables
    # Side-by-side layouts
    pass
```

### Example Responsive Table:

**Wide (>= 80 cols):**
```
┌──────────┬─────────────────────┬──────────┬────────┐
│ ID       │ Created             │ Messages │ Files  │
├──────────┼─────────────────────┼──────────┼────────┤
│ a1b2c3d4 │ 2026-02-17 10:30 AM │ 15       │ 3      │
└──────────┴─────────────────────┴──────────┴────────┘
```

**Narrow (< 80 cols):**
```
ID: a1b2c3d4
Created: 2026-02-17 10:30
Messages: 15  Files: 3
────────────────────────
```

---

## 12. ANIMATION SPECS

### 12.1 Fade-in Effect (for important messages)

```python
from rich.console import Console
import time

console = Console()

message = "✅ Setup complete!"

# Simulate fade-in with gradient
console.print(message, style="dim")
time.sleep(0.1)
console.print("\r" + message, style="default")
time.sleep(0.1)
console.print("\r" + message, style="bold")
```

### 12.2 Typewriter Effect (for special moments)

```python
def typewriter(text, delay=0.03):
    for char in text:
        console.print(char, end="")
        time.sleep(delay)
    console.print()  # New line
```

---

## 13. ACCESSIBILITY

### Screen Reader Compatibility:

```python
# Always provide text alternatives for icons
console.print("Success (checkmark icon): Task completed")

# Not just: console.print("✓")
```

### Color Blindness Support:

```python
# Don't rely on color alone
# Bad: Green for success, red for error
# Good: ✓ (green) for success, ✗ (red) for error

# Use shapes + color
SUCCESS = "[green]✓[/green]"
ERROR = "[red]✗[/red]"
WARNING = "[yellow]⚠[/yellow]"
```

### High Contrast Mode:

```python
# Provide high contrast option
if config.high_contrast:
    COLORS["success"] = "bright_green on black"
    COLORS["error"] = "bright_red on black"
```

---

## 14. IMPLEMENTATION REFERENCE

### Rich Library Setup:

```python
from rich.console import Console
from rich.theme import Theme

# Custom theme
custom_theme = Theme({
    "success": "green",
    "error": "red",
    "warning": "yellow",
    "info": "blue",
    "prompt": "cyan",
    "code": "magenta",
})

console = Console(theme=custom_theme)

# Usage
console.print("✓ Success", style="success")
console.print("✗ Error", style="error")
```

### Panel Usage:

```python
from rich.panel import Panel

panel = Panel(
    "Your content here",
    title="Panel Title",
    border_style="blue",
    padding=(1, 2)
)

console.print(panel)
```

### Table Usage:

```python
from rich.table import Table

table = Table(title="Sessions")
table.add_column("ID", style="cyan")
table.add_column("Created", style="green")
table.add_column("Messages", justify="right")

table.add_row("a1b2c3d4", "2026-02-17", "15")

console.print(table)
```

---

*Design specifications complete. See UI_UX_DESIGN.md for command designs.*
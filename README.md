# ArenaAgent

**Free AI Coding Assistant using LM Arena**

ArenaAgent is a local Python CLI application that provides autonomous AI-assisted coding without API costs by leveraging LM Arena's free research platform.

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/x-LANsolo-x/ARENAagent)

## ✨ Features

- 🆓 **Zero Cost** - Uses LM Arena (free) instead of paid APIs
- 🤖 **Autonomous Execution** - Generates, executes, and fixes code automatically
- 💾 **Local Storage** - All data stays on your machine (full privacy)
- 🔄 **Error Recovery** - Automatic retry loop with model feedback
- 📝 **Context Persistence** - Conversation history survives restarts
- 🔐 **Safe Operations** - Automatic backups before file modifications
- 🚀 **Multi-Model Access** - Claude, GPT-4, Gemini via LM Arena

## 🎯 Use Cases

- **Students** - Learn AI-assisted coding without subscription costs
- **Hobbyists** - Build personal projects with frontier AI models
- **Developers** - Prototype quickly with autonomous code execution
- **Researchers** - Compare multiple models for free

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- Google account (for LM Arena login)
- 8GB RAM (recommended)

### Install via pip

```bash
pip install arenaagent
```

### Install from source

```bash
git clone https://github.com/x-LANsolo-x/ARENAagent.git
cd ARENAagent
pip install -e .
```

### Post-installation setup

```bash
# Install Playwright browser
playwright install chromium

# Initialize ArenaAgent (one-time setup)
arenaagent init
```

## 🚀 Quick Start

### 1. Initialize (one-time)

```bash
arenaagent init
```

This will:
- Open browser to LM Arena
- Prompt you to log in with Google
- Save your browser profile for future use
- Create initial session

### 2. Send your first prompt

```bash
arenaagent ask "create a Flask REST API for a todo list"
```

ArenaAgent will:
- Send prompt to LM Arena (Claude by default)
- Parse the response for code
- Create files in your workspace
- Execute the code
- Fix errors automatically if they occur

### 3. Continue the conversation

```bash
arenaagent ask "add JWT authentication"
```

Full context is preserved - the model remembers your previous code!

## 📖 Usage Examples

### Create and run code

```bash
arenaagent ask "create a Python script that scrapes Hacker News"
```

### Fix errors automatically

If code fails, ArenaAgent automatically:
1. Captures the error
2. Sends it back to the model
3. Gets a fix
4. Retries execution

### View conversation history

```bash
arenaagent history
```

### Rollback file changes

```bash
arenaagent rollback app.py
```

### Manage sessions

```bash
# List all sessions
arenaagent sessions

# Switch to different session
arenaagent sessions switch <session-id>

# Create new session
arenaagent sessions new
```

## 🛠️ How It Works

```
┌─────────────────────────────────────────┐
│  User types command                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  CLI Interface (Click + Rich)           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Agent Core (Orchestrator)              │
│  - Loads session context                │
│  - Coordinates services                 │
└──────────────┬──────────────────────────┘
               │
       ┌───────┼───────┬────────┐
       │       │       │        │
       ▼       ▼       ▼        ▼
  ┌────────┐ ┌────┐ ┌────┐ ┌────────┐
  │Browser │ │Sess│ │Exec│ │  File  │
  │Connect │ │Mgr │ │Eng │ │Manager │
  └────┬───┘ └──┬─┘ └──┬─┘ └────┬───┘
       │        │      │        │
       ▼        ▼      ▼        ▼
  LM Arena   JSON   OS      Local
  (Browser)  Files  Shell   Files
```

## 📁 Project Structure

```
~/.arenaagent/
├── browser/                  # Persistent browser profile
├── sessions/
│   ├── {session-id}/
│   │   ├── conversation_history.json
│   │   ├── file_index.json
│   │   └── execution_log.json
│   └── ...
└── config.json              # Global configuration

~/arenaagent_workspace/      # Default workspace
├── *.py                     # Your generated files
├── *.backup.TIMESTAMP       # Automatic backups
└── ...
```

## ⚙️ Configuration

Edit `~/.arenaagent/config.json`:

```json
{
  "default_model": "claude-3.5-sonnet",
  "default_workspace": "~/arenaagent_workspace/",
  "browser": {
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
  }
}
```

## 🔒 Security & Privacy

- ✅ **All data local** - No cloud storage
- ✅ **No telemetry** - Zero data collection
- ✅ **Command validation** - Blocks destructive patterns
- ✅ **Workspace isolation** - Optional sandboxing
- ✅ **User approval** - Required for execution (configurable)

**What goes to LM Arena:**
- Only your prompts (not your code)

**What stays local:**
- All conversation history
- All files created
- All execution logs
- Browser credentials (encrypted by Chromium)

## ❌ Limitations

This tool is **NOT** for:
- ❌ Enterprise teams (single-user design)
- ❌ Mission-critical automation (depends on free service)
- ❌ Regulated industries (no compliance certifications)
- ❌ Sub-second latency needs (browser adds 2-3s)

## 🐛 Troubleshooting

### Browser won't launch

```bash
# Reinstall Playwright browser
playwright install --force chromium
```

### Session corrupted

```bash
# ArenaAgent auto-archives corrupted sessions
# Just create a new one:
arenaagent sessions new
```

### Network errors

```bash
# Check if you can access LM Arena:
# Visit https://chat.lmsys.org in your browser
# If yes, retry your command
```

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md)

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [LM Arena](https://lmsys.org/blog/2023-05-03-arena/) - For providing free access to frontier models
- [Playwright](https://playwright.dev/) - For excellent browser automation
- [Click](https://click.palletsprojects.com/) - For CLI framework
- [Rich](https://rich.readthedocs.io/) - For beautiful terminal output

## 📞 Support

- **Documentation:** [GitHub Wiki](https://github.com/x-LANsolo-x/ARENAagent/wiki)
- **Issues:** [GitHub Issues](https://github.com/x-LANsolo-x/ARENAagent/issues)
- **Discussions:** [GitHub Discussions](https://github.com/x-LANsolo-x/ARENAagent/discussions)

## 🗺️ Roadmap

- [x] Phase 1: Requirements Analysis
- [x] Phase 2: System Architecture
- [x] Phase 3: UI/UX Design
- [ ] Phase 4: Implementation
- [ ] Phase 5: Testing
- [ ] Phase 6: Documentation
- [ ] Phase 7: Alpha Release

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Built with ❤️ by developers, for developers**

**Cost:** $0  
**Freedom:** Infinite  
**Privacy:** Complete

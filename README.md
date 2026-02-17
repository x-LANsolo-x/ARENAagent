# ArenaAgent

> **Free AI Coding Assistant powered by LM Arena**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: In Development](https://img.shields.io/badge/status-in%20development-orange.svg)]()

A local-first AI coding assistant that uses [LM Arena](https://lmarena.ai) to provide **free** AI assistance for coding tasks, with autonomous code execution and intelligent error recovery.

---

## 🌟 Features

- **🆓 Zero Cost**: Uses free LM Arena access instead of paid APIs
- **🤖 Autonomous Execution**: Automatically runs generated code
- **🔄 Error Recovery**: Intelligent retry mechanism with AI-assisted debugging
- **💾 Local-First**: All data stored locally as JSON files
- **🔌 Persistent Sessions**: Resume conversations across terminal sessions
- **📁 File Tracking**: Monitors and backs up file modifications
- **🎨 Beautiful CLI**: Rich terminal UI with syntax highlighting

---

## 🚀 Quick Start

> **Note**: Project is currently in **Phase 5 (Implementation)**. Full installation will be available after v0.1.0 release.

### For Developers

```bash
# Clone repository
git clone https://github.com/x-LANsolo-x/ARENAagent.git
cd arenaagent_project

# Set up development environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
make install-dev
playwright install chromium

# Verify setup
python scripts/verify_setup.py

# Start development
# See docs/development/PHASE5_DEVELOPMENT_PLAN.md
```

---

## 📚 Documentation

### 🎯 Getting Started
- **[START_HERE.md](START_HERE.md)** - Navigation guide (start here!)
- **[DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)** - Complete development roadmap
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project organization

### 📖 Development Documentation
- **[Phase 5 Development Plans](docs/development/)** - Complete implementation guide
- **[Quick Reference](docs/development/PHASE5_QUICK_REFERENCE.md)** - Quick lookup guide

### 🎨 Design Documentation
- **[Architecture](design_docs/phase2_design/ARCHITECTURE.md)** - System architecture
- **[API Specification](design_docs/phase2_design/API_SPECIFICATION.md)** - API contracts
- **[System Flows](design_docs/phase3_design/SYSTEM_FLOWS.md)** - Flow diagrams

---

## 🏗️ Architecture

```
User → CLI → AgentCore → Browser (LM Arena) → AI Response
                ↓
         Code Executor → Run Generated Code
                ↓
         File Tracker → Monitor Changes
                ↓
         Session Manager → Save History
```

### Core Components

- **Browser Automation**: Playwright-based LM Arena connector
- **Code Executor**: Safe subprocess execution with timeouts
- **Session Manager**: JSON-based conversation persistence
- **File Tracker**: Monitor and backup file modifications
- **CLI Interface**: Click + Rich for beautiful terminal UI

---

## 🎯 Current Status

### Phase Progress

- ✅ **Phase 1**: Idea and Requirements Complete
- ✅ **Phase 2**: System Design Complete
- ✅ **Phase 3**: UI/UX Design Complete
- ✅ **Phase 4**: Environment Setup Complete
- 🚧 **Phase 5**: Implementation (In Progress)

### Implementation Status

| Component | Status | Progress |
|-----------|--------|----------|
| Data Models | ⚪ Not Started | 0% |
| Configuration | ⚪ Not Started | 0% |
| Session Management | ⚪ Not Started | 0% |
| Utilities | ⚪ Not Started | 0% |
| Browser Automation | ⚪ Not Started | 0% |
| Code Executor | ⚪ Not Started | 0% |
| File Operations | ⚪ Not Started | 0% |
| Core Agent | ⚪ Not Started | 0% |
| CLI Interface | ⚪ Not Started | 0% |
| Tests | ⚪ Not Started | 0% |
| Documentation | 🟡 In Progress | 30% |

**Overall Progress**: ~5% (Design & Planning Complete, Implementation Ready to Start)

---

## 🛠️ Technology Stack

- **Language**: Python 3.11+
- **Browser Automation**: Playwright
- **CLI Framework**: Click
- **Terminal UI**: Rich
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Code Quality**: black, isort, mypy, pylint
- **CI/CD**: GitHub Actions

---

## 📋 Planned Features (v0.1.0)

### CLI Commands
```bash
arenaagent init              # Initialize configuration
arenaagent ask "question"    # Ask a single question
arenaagent chat              # Interactive chat mode
arenaagent history           # View conversation history
arenaagent config            # Manage settings
```

### Key Capabilities
- ✅ Autonomous code execution
- ✅ Error recovery with retries
- ✅ Session persistence
- ✅ File tracking and backups
- ✅ Multiple model support
- ✅ Configurable behavior

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Create feature branch: `git checkout -b feature/name`
2. Make changes with tests
3. Run quality checks: `make test && make lint`
4. Submit pull request

### Quality Standards

- Type hints on all code
- 80%+ test coverage
- 0 mypy errors
- Pylint score > 9.0/10
- Black/isort formatted

---

## 📅 Roadmap

### v0.1.0 (Target: Q1 2026)
- ✅ Complete design and architecture
- 🚧 Core implementation
- ⚪ Testing and documentation
- ⚪ Initial release

### v0.2.0 (Future)
- Multi-model support
- Streaming responses
- Better syntax highlighting
- Git integration

### v0.3.0 (Future)
- Plugin system
- VS Code extension
- Web interface
- Collaboration features

---

## 📊 Project Statistics

| Metric | Current | Target (v0.1.0) |
|--------|---------|-----------------|
| Lines of Code | ~15 | ~5,000 |
| Test Coverage | 0% | 80%+ |
| Modules | 9 (empty) | 9 (complete) |
| Tests | 0 | 150+ |
| Documentation | 30% | 100% |

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LM Arena** for providing free AI access
- **Playwright** team for excellent browser automation
- **Click** and **Rich** for amazing CLI/UI frameworks
- Open source community for inspiration and tools

---

## 📬 Contact

- **Repository**: [GitHub](https://github.com/x-LANsolo-x/ARENAagent)
- **Issues**: [GitHub Issues](https://github.com/x-LANsolo-x/ARENAagent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/x-LANsolo-x/ARENAagent/discussions)

---

## ⚡ Quick Links

- [Start Development](START_HERE.md)
- [Development Roadmap](DEVELOPMENT_ROADMAP.md)
- [Implementation Plans](docs/development/)
- [Architecture](design_docs/phase2_design/ARCHITECTURE.md)
- [Contributing Guide](CONTRIBUTING.md)

---

**Status**: 🚧 In Active Development - Phase 5 Implementation

**Want to contribute?** Read [START_HERE.md](START_HERE.md) to get started!

---

*Built with ❤️ by the ArenaAgent Team*

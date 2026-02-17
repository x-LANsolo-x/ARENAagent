# Contributing to ArenaAgent

Thank you for your interest in contributing to ArenaAgent! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and considerate of others. We're all here to build something useful together.

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template**
3. **Include:**
   - Clear description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)
   - Logs if applicable

### Suggesting Features

1. **Check existing feature requests**
2. **Use the feature request template**
3. **Explain:**
   - The problem you're trying to solve
   - Your proposed solution
   - Alternative solutions considered
   - Why this benefits other users

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style guide (below)
   - Add tests for new features
   - Update documentation

4. **Run tests and checks**
   ```bash
   # Run tests
   pytest

   # Run code quality checks
   black arenaagent/
   isort arenaagent/
   mypy arenaagent/
   pylint arenaagent/

   # Or use pre-commit
   pre-commit run --all-files
   ```

5. **Commit your changes**
   ```bash
   git commit -m "feat: add amazing feature"
   ```

   Use conventional commits:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Adding tests
   - `refactor:` - Code refactoring
   - `style:` - Code style changes
   - `chore:` - Maintenance tasks

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Use the PR template
   - Link related issues
   - Describe what changed and why

## Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/x-LANsolo-x/ARENAagent.git
cd ARENAagent
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

### 4. Install pre-commit hooks

```bash
pre-commit install
```

### 5. Install Playwright browser

```bash
playwright install chromium
```

### 6. Run tests

```bash
pytest
```

## Code Style Guide

### Python Style

- **Line length:** 100 characters
- **Formatter:** Black
- **Import sorting:** isort (black profile)
- **Type hints:** Required for all public functions
- **Docstrings:** Google style

Example:

```python
from typing import Optional

def create_session(workspace: str, model: Optional[str] = None) -> str:
    """Create a new ArenaAgent session.

    Args:
        workspace: Path to the workspace directory.
        model: LLM model to use. Defaults to config value.

    Returns:
        Session ID (UUID).

    Raises:
        ValueError: If workspace path is invalid.
    """
    pass
```

### Testing

- Write tests for all new features
- Maintain >80% code coverage
- Use pytest fixtures for common setup
- Mock external services (LM Arena, file system)

Example:

```python
def test_create_session(tmp_path):
    """Test session creation creates all required files."""
    manager = SessionManager(workspace=tmp_path)
    session_id = manager.create_session()

    assert session_id is not None
    assert (tmp_path / session_id / "conversation_history.json").exists()
```

### Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Update architecture docs if design changes

## Project Structure

```
arenaagent/
├── cli/              # CLI interface (Click)
├── core/             # Agent core (orchestrator)
├── browser/          # Browser connector (Playwright)
├── session/          # Session manager
├── executor/         # Code executor
├── files/            # File manager
├── config/           # Configuration
├── models/           # Data models
└── utils/            # Utilities
```

## Testing Guidelines

### Unit Tests

- Test individual functions/methods
- Mock external dependencies
- Fast execution (<1s per test)
- Location: `tests/unit/`

### Integration Tests

- Test component interactions
- Use test fixtures
- May be slower
- Location: `tests/integration/`

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_session.py

# Specific test
pytest tests/unit/test_session.py::test_create_session

# With coverage
pytest --cov=arenaagent --cov-report=html

# Verbose output
pytest -v
```

## Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Build and publish to PyPI

## Questions?

- **Discord:** [Join our server](#)
- **GitHub Discussions:** [Ask here](https://github.com/x-LANsolo-x/ARENAagent/discussions)
- **Email:** hello@arenaagent.dev

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

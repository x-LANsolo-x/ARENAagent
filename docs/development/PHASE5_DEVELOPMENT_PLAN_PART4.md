# Phase 5: Implementation & Development Plan - Part 4

## Final Implementation Phases

---

## PHASE 5.8: Core Agent Logic

**Duration:** 5-7 days  
**Branch:** `feature/core-agent`  
**Dependencies:** All previous phases (5.1-5.7)  
**Priority:** CRITICAL (Integrates everything)

### Overview

Build the main `AgentCore` class that orchestrates all components and implements the request-response-execution-error-recovery loop. This is the brain of the application.

### Success Criteria

- [ ] AgentCore class implemented
- [ ] Request/response cycle working
- [ ] Error recovery loop functional
- [ ] Component integration complete
- [ ] State management working
- [ ] Context tracking working
- [ ] Integration tests passing
- [ ] Code coverage ≥ 80%

---

### Implementation

**File:** `arenaagent/core/agent.py`

**Purpose:** Main agent orchestration and control flow

**Core Workflow:**
```
User Request
    ↓
Add to Session
    ↓
Send to LM Arena (Browser)
    ↓
Receive Response
    ↓
Parse for Code Blocks
    ↓
If Code Found → Execute (Executor)
    ↓
If Error → Send Error Back to LM Arena (Retry)
    ↓
Track File Changes (FileTracker)
    ↓
Update Session History
    ↓
Return Result to User
```

**Implementation:**

```python
"""Core agent logic."""

import asyncio
import re
from typing import Optional, List, Dict, Any
from datetime import datetime

from arenaagent.models.config import Config
from arenaagent.models.session import Session
from arenaagent.models.message import Message
from arenaagent.models.execution import ExecutionResult
from arenaagent.config.manager import ConfigManager
from arenaagent.session.manager import SessionManager
from arenaagent.browser.controller import BrowserController
from arenaagent.browser.lm_arena import LMArenaConnector
from arenaagent.executor.command import CommandExecutor
from arenaagent.files.tracker import FileTracker
from arenaagent.files.backup import BackupManager
from arenaagent.utils.logger import setup_logger, get_logger


class AgentCore:
    """Core agent that orchestrates all components."""
    
    # Regex to extract code blocks from markdown
    CODE_BLOCK_PATTERN = r'```(?:bash|sh|python|shell)?\n(.*?)```'
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the agent.
        
        Args:
            config: Configuration (loads default if None)
        """
        # Load configuration
        self.config_manager = ConfigManager()
        self.config = config or self.config_manager.load()
        
        # Setup logging
        self.logger = setup_logger(
            "arenaagent",
            log_level=self.config.log_level,
            console=True,
            file=True
        )
        
        # Initialize managers
        self.session_manager = SessionManager()
        self.file_tracker = FileTracker(self.config.working_directory)
        self.backup_manager = BackupManager()
        
        # Initialize browser components
        self.browser_controller = BrowserController(self.config)
        self.lm_arena = LMArenaConnector(self.browser_controller, self.config)
        
        # Initialize executor
        self.executor = CommandExecutor(
            working_directory=self.config.working_directory,
            timeout=300
        )
        
        # Current session
        self._current_session: Optional[Session] = None
        
        self.logger.info("AgentCore initialized")
    
    async def start(self) -> None:
        """Start the agent and browser."""
        self.logger.info("Starting ArenaAgent...")
        
        # Start browser
        await self.browser_controller.start()
        await self.lm_arena.connect()
        
        # Select default model
        if self.config.default_model:
            await self.lm_arena.select_model(self.config.default_model)
        
        # Load or create session
        sessions = self.session_manager.list_sessions()
        if sessions:
            self._current_session = sessions[0]  # Load most recent
            self.logger.info(f"Loaded session: {self._current_session.name}")
        else:
            self._current_session = self.session_manager.create_session(
                name=f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            self.logger.info("Created new session")
        
        self.logger.info("ArenaAgent started successfully")
    
    async def stop(self) -> None:
        """Stop the agent and cleanup."""
        self.logger.info("Stopping ArenaAgent...")
        
        # Save current session
        if self._current_session:
            self.session_manager.save_session(self._current_session)
        
        # Stop browser
        await self.browser_controller.stop()
        
        self.logger.info("ArenaAgent stopped")
    
    async def process_request(
        self,
        user_message: str,
        auto_execute: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Process a user request.
        
        Args:
            user_message: User's question or request
            auto_execute: Override config for auto-execution
            
        Returns:
            Dictionary with response and execution results
        """
        if not self._current_session:
            raise RuntimeError("Agent not started. Call start() first.")
        
        # Determine if we should auto-execute
        should_execute = auto_execute if auto_execute is not None else self.config.auto_execute
        
        self.logger.info(f"Processing request: {user_message[:50]}...")
        
        # Add user message to session
        user_msg = Message(role="user", content=user_message)
        self._current_session.add_message(user_msg)
        
        # Send to LM Arena and get response
        await self.lm_arena.send_message(user_message)
        response_text = await self.lm_arena.get_response()
        
        # Add assistant message to session
        assistant_msg = Message(
            role="assistant",
            content=response_text,
            model=self.config.default_model
        )
        self._current_session.add_message(assistant_msg)
        
        # Parse response for code blocks
        code_blocks = self._extract_code_blocks(response_text)
        
        result = {
            'response': response_text,
            'code_blocks': code_blocks,
            'execution_results': [],
            'errors': []
        }
        
        # Execute code if found and auto-execute enabled
        if code_blocks and should_execute:
            self.logger.info(f"Found {len(code_blocks)} code block(s)")
            
            for i, code in enumerate(code_blocks):
                exec_result = await self._execute_with_retry(code)
                result['execution_results'].append(exec_result)
                
                if exec_result.is_error():
                    result['errors'].append(exec_result.get_error_message())
        
        # Save session
        self.session_manager.save_session(self._current_session)
        
        return result
    
    async def _execute_with_retry(
        self,
        command: str,
        max_retries: Optional[int] = None
    ) -> ExecutionResult:
        """Execute command with error recovery.
        
        Args:
            command: Command to execute
            max_retries: Maximum retry attempts
            
        Returns:
            Final execution result
        """
        retries = max_retries or self.config.max_retries
        
        for attempt in range(retries + 1):
            self.logger.info(f"Executing command (attempt {attempt + 1}/{retries + 1})")
            
            # Execute command
            result = await self.executor.execute(command)
            
            # If successful, return
            if result.success:
                self.logger.info("Command executed successfully")
                return result
            
            # If error and retries remaining, ask AI to fix
            if attempt < retries:
                self.logger.warning(f"Command failed, asking AI to fix (retry {attempt + 1})")
                
                # Create error message for AI
                error_msg = self._create_error_message(command, result)
                
                # Send error to AI
                await self.lm_arena.send_message(error_msg)
                fix_response = await self.lm_arena.get_response()
                
                # Extract fixed command
                fixed_commands = self._extract_code_blocks(fix_response)
                if fixed_commands:
                    command = fixed_commands[0]  # Try first suggestion
                    
                    # Add messages to session
                    self._current_session.add_message(Message(role="user", content=error_msg))
                    self._current_session.add_message(Message(role="assistant", content=fix_response))
                else:
                    # No fix provided, return error
                    break
            else:
                self.logger.error(f"Command failed after {retries} retries")
        
        return result
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from markdown text.
        
        Args:
            text: Markdown text with code blocks
            
        Returns:
            List of code strings
        """
        matches = re.findall(self.CODE_BLOCK_PATTERN, text, re.DOTALL)
        return [match.strip() for match in matches]
    
    def _create_error_message(self, command: str, result: ExecutionResult) -> str:
        """Create error message for AI to fix.
        
        Args:
            command: Failed command
            result: Execution result with error
            
        Returns:
            Formatted error message
        """
        return f"""The command failed with an error. Please fix it.

Command:
```bash
{command}
```

Error output:
```
{result.stderr}
```

Exit code: {result.exit_code}

Please provide a corrected version of the command."""
    
    def get_current_session(self) -> Optional[Session]:
        """Get the current active session."""
        return self._current_session
    
    def get_conversation_history(self, max_messages: int = 10) -> List[Message]:
        """Get recent conversation history.
        
        Args:
            max_messages: Maximum messages to return
            
        Returns:
            List of recent messages
        """
        if not self._current_session:
            return []
        
        messages = self._current_session.messages
        return messages[-max_messages:]
```

**Test File:** `tests/integration/test_agent_core.py`

**Test Cases:**
```python
@pytest.mark.asyncio
async def test_agent_start_and_stop()
async def test_process_simple_request()
async def test_process_request_with_code_execution()
async def test_error_recovery_retry()
async def test_session_persistence()
async def test_extract_code_blocks()
async def test_create_error_message()
async def test_get_conversation_history()
```

---

### Core Package Init

**File:** `arenaagent/core/__init__.py`

```python
"""Core agent logic for ArenaAgent."""

from arenaagent.core.agent import AgentCore

__all__ = ["AgentCore"]
```

---

### Phase 5.8 Completion Checklist

- [ ] AgentCore fully implemented
- [ ] All components integrated
- [ ] Request/response cycle working
- [ ] Code execution working
- [ ] Error recovery with retries working
- [ ] Session persistence working
- [ ] All integration tests passing (10+ tests)
- [ ] Code coverage ≥ 80%

### Git Workflow

```bash
git checkout -b feature/core-agent
git add arenaagent/core/agent.py tests/integration/test_agent_core.py
git commit -m "feat: implement AgentCore with full orchestration"
git add arenaagent/core/__init__.py
git commit -m "feat: export AgentCore"
make test
git checkout develop
git merge feature/core-agent
```

---

## PHASE 5.9: CLI Interface

**Duration:** 4-5 days  
**Branch:** `feature/cli-interface`  
**Dependencies:** Phase 5.8 (Core Agent)  
**Priority:** HIGH (User interface)

### Overview

Build the command-line interface using Click and Rich for a beautiful terminal experience.

### Success Criteria

- [ ] All CLI commands implemented
- [ ] Rich terminal UI working
- [ ] Interactive prompts functional
- [ ] Progress indicators
- [ ] Error handling
- [ ] Help documentation
- [ ] Unit tests for commands
- [ ] Code coverage ≥ 75%

---

### Commands to Implement

#### Command 9.1: `arenaagent init`

**File:** `arenaagent/cli/commands/init.py`

**Purpose:** Initialize ArenaAgent for first use

```python
"""Initialize ArenaAgent."""

import click
from rich.console import Console
from rich.panel import Panel

from arenaagent.config.manager import ConfigManager
from arenaagent.session.manager import SessionManager


console = Console()


@click.command()
def init():
    """Initialize ArenaAgent configuration."""
    console.print(Panel.fit(
        "[bold cyan]ArenaAgent Initialization[/bold cyan]",
        border_style="cyan"
    ))
    
    # Create config
    config_manager = ConfigManager()
    config = config_manager.load()
    
    console.print("✓ Configuration created", style="green")
    console.print(f"  Config directory: {config_manager.config_dir}")
    
    # Create session directory
    session_manager = SessionManager()
    console.print("✓ Session directory created", style="green")
    console.print(f"  Sessions directory: {session_manager.session_dir}")
    
    # Success message
    console.print("\n[bold green]✓ ArenaAgent initialized successfully![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Run: [cyan]arenaagent ask \"your question\"[/cyan]")
    console.print("  2. Or:  [cyan]arenaagent chat[/cyan] for interactive mode")
```

---

#### Command 9.2: `arenaagent ask`

**File:** `arenaagent/cli/commands/ask.py`

**Purpose:** Ask a single question

```python
"""Ask a question to ArenaAgent."""

import click
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

from arenaagent.core.agent import AgentCore
from arenaagent.utils.formatters import format_message


console = Console()


@click.command()
@click.argument('question')
@click.option('--no-execute', is_flag=True, help='Don\'t execute code automatically')
@click.option('--model', help='Specify model to use')
def ask(question: str, no_execute: bool, model: str):
    """Ask a question to ArenaAgent.
    
    Example: arenaagent ask "Create a Flask hello world app"
    """
    async def _ask():
        agent = AgentCore()
        
        try:
            # Start agent with progress
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Starting ArenaAgent...", total=None)
                await agent.start()
                progress.update(task, completed=True)
            
            console.print(f"\n[bold]Question:[/bold] {question}\n")
            
            # Process request
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Thinking...", total=None)
                
                result = await agent.process_request(
                    question,
                    auto_execute=not no_execute
                )
                
                progress.update(task, completed=True)
            
            # Display response
            console.print(Panel(
                result['response'],
                title="[bold cyan]Response[/bold cyan]",
                border_style="cyan"
            ))
            
            # Display execution results
            if result['execution_results']:
                console.print("\n[bold]Execution Results:[/bold]\n")
                
                for i, exec_result in enumerate(result['execution_results'], 1):
                    if exec_result.success:
                        console.print(f"[green]✓[/green] Command {i} succeeded")
                        if exec_result.stdout:
                            console.print(Panel(
                                exec_result.stdout,
                                title="Output",
                                border_style="green"
                            ))
                    else:
                        console.print(f"[red]✗[/red] Command {i} failed")
                        if exec_result.stderr:
                            console.print(Panel(
                                exec_result.stderr,
                                title="Error",
                                border_style="red"
                            ))
            
            # Display errors if any
            if result['errors']:
                console.print("\n[bold red]Errors:[/bold red]")
                for error in result['errors']:
                    console.print(f"  • {error}")
        
        finally:
            await agent.stop()
    
    # Run async function
    asyncio.run(_ask())
```

---

#### Command 9.3: `arenaagent chat`

**File:** `arenaagent/cli/commands/chat.py`

**Purpose:** Interactive chat mode

```python
"""Interactive chat mode."""

import click
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from arenaagent.core.agent import AgentCore


console = Console()


@click.command()
def chat():
    """Start interactive chat session."""
    async def _chat():
        agent = AgentCore()
        
        try:
            await agent.start()
            
            console.print(Panel.fit(
                "[bold cyan]ArenaAgent Interactive Chat[/bold cyan]\n"
                "Type your questions below. Commands:\n"
                "  /exit or /quit - Exit chat\n"
                "  /clear - Clear screen\n"
                "  /history - Show conversation history",
                border_style="cyan"
            ))
            
            while True:
                # Get user input
                user_input = Prompt.ask("\n[bold green]You[/bold green]")
                
                # Handle commands
                if user_input.lower() in ['/exit', '/quit']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                if user_input.lower() == '/clear':
                    console.clear()
                    continue
                
                if user_input.lower() == '/history':
                    history = agent.get_conversation_history()
                    console.print("\n[bold]Conversation History:[/bold]\n")
                    for msg in history:
                        role_color = "green" if msg.role == "user" else "cyan"
                        console.print(f"[{role_color}]{msg.role}:[/{role_color}] {msg.content[:100]}...")
                    continue
                
                # Process request
                console.print("\n[bold cyan]Assistant:[/bold cyan]")
                
                result = await agent.process_request(user_input)
                
                # Display response
                console.print(result['response'])
                
                # Display execution results if any
                if result['execution_results']:
                    for exec_result in result['execution_results']:
                        if exec_result.success and exec_result.stdout:
                            console.print(f"\n[dim]{exec_result.stdout}[/dim]")
        
        finally:
            await agent.stop()
    
    asyncio.run(_chat())
```

---

#### Command 9.4: `arenaagent history`

**File:** `arenaagent/cli/commands/history.py`

**Purpose:** Show conversation history

```python
"""Show conversation history."""

import click
from rich.console import Console
from rich.table import Table

from arenaagent.session.manager import SessionManager


console = Console()


@click.command()
@click.option('--limit', default=20, help='Number of messages to show')
@click.option('--session', help='Session ID to show')
def history(limit: int, session: str):
    """Show conversation history."""
    session_manager = SessionManager()
    
    # Get sessions
    sessions = session_manager.list_sessions()
    
    if not sessions:
        console.print("[yellow]No conversation history found.[/yellow]")
        return
    
    # Load specific session or most recent
    if session:
        current_session = session_manager.load_session(session)
    else:
        current_session = sessions[0]
    
    # Display session info
    console.print(f"\n[bold]Session:[/bold] {current_session.name}")
    console.print(f"[dim]Created: {current_session.created_at}[/dim]\n")
    
    # Create table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Time", style="dim")
    table.add_column("Role", style="bold")
    table.add_column("Message")
    
    # Add messages
    messages = current_session.messages[-limit:]
    for msg in messages:
        role_color = "green" if msg.role == "user" else "cyan"
        table.add_row(
            msg.timestamp.strftime("%H:%M:%S"),
            f"[{role_color}]{msg.role}[/{role_color}]",
            msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
        )
    
    console.print(table)
```

---

#### Command 9.5: `arenaagent config`

**File:** `arenaagent/cli/commands/config.py`

**Purpose:** Manage configuration

```python
"""Manage configuration."""

import click
from rich.console import Console
from rich.table import Table

from arenaagent.config.manager import ConfigManager


console = Console()


@click.group()
def config():
    """Manage ArenaAgent configuration."""
    pass


@config.command('show')
def show_config():
    """Show current configuration."""
    config_manager = ConfigManager()
    config = config_manager.get()
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Setting", style="bold")
    table.add_column("Value")
    
    table.add_row("Browser Headless", str(config.browser_headless))
    table.add_row("Auto Execute", str(config.auto_execute))
    table.add_row("Max Retries", str(config.max_retries))
    table.add_row("Default Model", config.default_model)
    table.add_row("Log Level", config.log_level)
    table.add_row("Working Directory", config.working_directory)
    
    console.print(table)


@config.command('set')
@click.argument('key')
@click.argument('value')
def set_config(key: str, value: str):
    """Set a configuration value."""
    config_manager = ConfigManager()
    
    try:
        # Convert value to appropriate type
        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        
        config_manager.update(**{key: value})
        console.print(f"[green]✓[/green] Updated {key} = {value}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@config.command('reset')
def reset_config():
    """Reset configuration to defaults."""
    config_manager = ConfigManager()
    config_manager.reset()
    console.print("[green]✓[/green] Configuration reset to defaults")
```

---

#### Main CLI Entry Point

**File:** `arenaagent/cli/main.py`

**Purpose:** Main Click application

```python
"""Main CLI entry point."""

import click
from arenaagent.cli.commands import init, ask, chat, history, config


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """ArenaAgent - Free AI Coding Assistant using LM Arena.
    
    A local-first AI assistant that uses LM Arena to help with coding tasks,
    automatically execute code, and recover from errors.
    """
    pass


# Add commands
cli.add_command(init.init)
cli.add_command(ask.ask)
cli.add_command(chat.chat)
cli.add_command(history.history)
cli.add_command(config.config)


if __name__ == '__main__':
    cli()
```

---

### CLI Package Init

**File:** `arenaagent/cli/__init__.py`

```python
"""CLI interface for ArenaAgent."""

from arenaagent.cli.main import cli

__all__ = ["cli"]
```

---

### Phase 5.9 Completion Checklist

- [ ] All CLI commands implemented
- [ ] Rich UI working beautifully
- [ ] Interactive chat mode working
- [ ] Commands properly documented
- [ ] Error handling in place
- [ ] All commands tested
- [ ] Help text complete

### Git Workflow

```bash
git checkout -b feature/cli-interface

# Implement commands
git add arenaagent/cli/commands/init.py
git commit -m "feat: implement init command"

git add arenaagent/cli/commands/ask.py
git commit -m "feat: implement ask command"

git add arenaagent/cli/commands/chat.py
git commit -m "feat: implement interactive chat command"

git add arenaagent/cli/commands/history.py
git commit -m "feat: implement history command"

git add arenaagent/cli/commands/config.py
git commit -m "feat: implement config management command"

git add arenaagent/cli/main.py arenaagent/cli/__init__.py
git commit -m "feat: implement main CLI entry point"

make test
git checkout develop
git merge feature/cli-interface
```

---


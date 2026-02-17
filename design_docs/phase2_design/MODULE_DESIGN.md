# ArenaAgent - Detailed Module Design

## Module Specifications and Interfaces

---

## MODULE 1: CLI Interface

### File: `arenaagent/cli.py`

### Purpose:
Entry point for all user interactions. Provides command-line interface using Click framework.

### Dependencies:
```python
import click
from rich.console import Console
from rich.syntax import Syntax
from .agent import AgentCore
from .config import ConfigManager
```

### Class Structure:

```python
# No classes - Click uses decorators on functions

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """ArenaAgent - Free AI coding assistant using LM Arena"""
    pass

@cli.command()
@click.option('--headless/--no-headless', default=True, help='Run browser in headless mode')
def init(headless: bool):
    """Initialize ArenaAgent (one-time setup)"""
    console = Console()
    console.print("[bold blue]🔧 ArenaAgent Setup[/bold blue]")
    
    agent = AgentCore()
    success = agent.initialize(headless=headless)
    
    if success:
        console.print("[green]✓ Setup complete![/green]")
    else:
        console.print("[red]✗ Setup failed[/red]")

@cli.command()
@click.argument('prompt')
@click.option('--model', default=None, help='Model to use (default: config)')
@click.option('--dry-run', is_flag=True, help='Show what would happen without executing')
@click.option('--auto-approve', is_flag=True, help='Auto-approve all operations')
def ask(prompt: str, model: str, dry_run: bool, auto_approve: bool):
    """Send a prompt to the AI"""
    console = Console()
    agent = AgentCore()
    
    # Override config if flags provided
    if model:
        agent.set_model(model)
    if auto_approve:
        agent.set_auto_approve(True)
    
    # Send prompt
    result = agent.send_prompt(prompt, dry_run=dry_run)
    
    # Display result
    display_result(console, result)

@cli.command()
@click.option('--session-id', default=None, help='Specific session to view')
@click.option('--limit', default=10, help='Number of messages to show')
def history(session_id: str, limit: int):
    """View conversation history"""
    console = Console()
    agent = AgentCore()
    
    messages = agent.get_history(session_id=session_id, limit=limit)
    
    for msg in messages:
        display_message(console, msg)

@cli.command()
def sessions():
    """List all sessions"""
    console = Console()
    agent = AgentCore()
    
    sessions = agent.list_sessions()
    
    from rich.table import Table
    table = Table(title="Sessions")
    table.add_column("ID", style="cyan")
    table.add_column("Created", style="green")
    table.add_column("Messages", justify="right")
    
    for session in sessions:
        table.add_row(
            session.id[:8],
            session.created_at.strftime("%Y-%m-%d %H:%M"),
            str(session.message_count)
        )
    
    console.print(table)

@cli.command()
@click.argument('filepath')
@click.option('--timestamp', default=None, help='Specific backup timestamp to restore')
def rollback(filepath: str, timestamp: int):
    """Rollback a file to a previous backup"""
    console = Console()
    agent = AgentCore()
    
    success = agent.rollback_file(filepath, timestamp)
    
    if success:
        console.print(f"[green]✓ Rolled back {filepath}[/green]")
    else:
        console.print(f"[red]✗ Rollback failed[/red]")

@cli.command()
def ps():
    """Show running background processes"""
    console = Console()
    agent = AgentCore()
    
    processes = agent.list_processes()
    
    from rich.table import Table
    table = Table(title="Running Processes")
    table.add_column("PID", style="cyan")
    table.add_column("Command", style="yellow")
    table.add_column("Started", style="green")
    
    for proc in processes:
        table.add_row(
            str(proc.pid),
            proc.command[:50],
            proc.started_at.strftime("%H:%M:%S")
        )
    
    console.print(table)

# Helper functions
def display_result(console: Console, result):
    """Display execution result with formatting"""
    if result.files_created:
        console.print(f"[green]✓ Created: {', '.join(result.files_created)}[/green]")
    
    if result.stdout:
        console.print("\n[bold]Output:[/bold]")
        console.print(result.stdout)
    
    if result.stderr:
        console.print("\n[bold red]Errors:[/bold red]")
        console.print(result.stderr)
    
    if result.error:
        console.print(f"\n[red]✗ {result.error}[/red]")

def display_message(console: Console, message):
    """Display a single message with formatting"""
    if message.role == "user":
        console.print(f"\n[bold cyan]User:[/bold cyan] {message.content}")
    else:
        console.print(f"\n[bold green]Assistant:[/bold green]")
        # Syntax highlight code blocks if present
        if "```" in message.content:
            # Extract and highlight code
            pass
        else:
            console.print(message.content)

if __name__ == '__main__':
    cli()
```

### CLI Command Summary:

| Command | Purpose | Example |
|---------|---------|---------|
| `init` | One-time setup | `arenaagent init` |
| `ask` | Send prompt to AI | `arenaagent ask "create Flask app"` |
| `history` | View conversation | `arenaagent history --limit 20` |
| `sessions` | List all sessions | `arenaagent sessions` |
| `rollback` | Restore file backup | `arenaagent rollback app.py` |
| `ps` | Show running processes | `arenaagent ps` |

---

## MODULE 2: Agent Core

### File: `arenaagent/agent.py`

### Purpose:
Central orchestrator. Coordinates all services and manages application workflow.

### Class: `AgentCore`

```python
from typing import Optional, List
from .browser_connector import BrowserConnector
from .session_manager import SessionManager
from .executor import ExecutorEngine
from .file_manager import FileManager
from .config import ConfigManager
from .models import Result, Message, ExecutionResult

class AgentCore:
    """Main agent orchestrator"""
    
    def __init__(self):
        self.config = ConfigManager.load()
        self.browser: Optional[BrowserConnector] = None
        self.session: Optional[SessionManager] = None
        self.executor = ExecutorEngine(self.config)
        self.file_mgr = FileManager(self.config)
        self.current_session_id: Optional[str] = None
    
    def initialize(self, headless: bool = True) -> bool:
        """
        Initialize ArenaAgent (one-time setup)
        
        Steps:
        1. Create browser profile directory
        2. Launch browser to LM Arena
        3. Wait for user to log in
        4. Save profile
        5. Create default session
        
        Args:
            headless: Run browser in headless mode (False for first setup)
        
        Returns:
            bool: True if successful
        """
        try:
            # Launch browser (headful for login)
            self.browser = BrowserConnector(self.config)
            self.browser.launch(headless=False)  # Always headful for init
            
            # Navigate to LM Arena
            self.browser.navigate_to_lm_arena()
            
            # Wait for user to log in
            print("Please log in to LM Arena in the browser window...")
            logged_in = self.browser.wait_for_login(timeout=300)  # 5 min
            
            if not logged_in:
                print("Login timeout. Please try again.")
                return False
            
            print("Login successful! Saving profile...")
            
            # Close browser (profile is saved)
            self.browser.close()
            
            # Create default session
            self.session = SessionManager(self.config)
            self.current_session_id = self.session.create_session()
            
            print(f"Session created: {self.current_session_id}")
            
            return True
            
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False
    
    def send_prompt(self, prompt: str, dry_run: bool = False) -> Result:
        """
        Send prompt to LM Arena and process response
        
        Workflow:
        1. Load session context
        2. Launch browser if needed
        3. Send prompt + context to LM Arena
        4. Wait for and extract response
        5. Parse response for code blocks
        6. If code found: Create file, execute, handle errors
        7. Save conversation to session
        8. Return results
        
        Args:
            prompt: User's prompt
            dry_run: If True, don't execute, just show plan
        
        Returns:
            Result object with outcomes
        """
        result = Result()
        
        try:
            # Step 1: Load session
            if not self.session:
                self.session = SessionManager(self.config)
                self.current_session_id = self.session.load_latest_session()
            
            context = self.session.get_context(self.current_session_id)
            
            # Step 2: Launch browser if needed
            if not self.browser or not self.browser.is_running():
                self.browser = BrowserConnector(self.config)
                self.browser.launch(headless=self.config.browser.headless)
            
            # Step 3: Send prompt
            full_prompt = self._construct_prompt(prompt, context)
            self.browser.send_message(full_prompt)
            
            # Step 4: Extract response
            response_text = self.browser.extract_response()
            
            # Save user message
            self.session.save_message(Message(
                role="user",
                content=prompt
            ))
            
            # Step 5: Parse response
            parsed = self._parse_response(response_text)
            
            result.response_text = response_text
            result.code_blocks = parsed.code_blocks
            result.files_to_create = parsed.files
            
            if dry_run:
                result.dry_run = True
                return result
            
            # Step 6: Execute if code found
            if parsed.code_blocks:
                exec_result = self._execute_code_blocks(parsed.code_blocks)
                result.execution_results = exec_result
                
                # Handle errors
                if exec_result.has_errors():
                    retry_result = self._handle_execution_errors(exec_result)
                    result.retry_results = retry_result
            
            # Step 7: Save assistant message
            self.session.save_message(Message(
                role="assistant",
                content=response_text,
                metadata={
                    "files_created": result.files_created,
                    "execution_success": not result.has_errors()
                }
            ))
            
            return result
            
        except Exception as e:
            result.error = str(e)
            return result
    
    def _construct_prompt(self, prompt: str, context: List[Message]) -> str:
        """Construct full prompt with context"""
        if not context:
            return prompt
        
        # Build context string
        context_str = "Previous conversation:\n"
        for msg in context[-10:]:  # Last 10 messages
            context_str += f"{msg.role}: {msg.content[:200]}...\n"
        
        return f"{context_str}\n\nCurrent request: {prompt}"
    
    def _parse_response(self, response: str) -> ParsedResponse:
        """Parse response for code blocks and file operations"""
        import re
        
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for language, code in matches:
            code_blocks.append(CodeBlock(
                language=language or 'text',
                code=code.strip()
            ))
        
        # Detect file names from context
        files = self._detect_file_names(response, code_blocks)
        
        return ParsedResponse(
            code_blocks=code_blocks,
            files=files
        )
    
    def _execute_code_blocks(self, code_blocks: List[CodeBlock]) -> ExecutionResult:
        """Execute code blocks and return results"""
        results = []
        
        for block in code_blocks:
            if block.language in ['python', 'bash', 'sh']:
                # Ask user approval
                if not self.config.execution.auto_approve:
                    approved = self._ask_user_approval(block)
                    if not approved:
                        continue
                
                # Execute
                exec_result = self.executor.execute(block.code, block.language)
                results.append(exec_result)
        
        return ExecutionResult(results)
    
    def _handle_execution_errors(self, exec_result: ExecutionResult) -> RetryResult:
        """Handle execution errors with retry loop"""
        max_retries = self.config.execution.max_retries
        
        for attempt in range(max_retries):
            if not exec_result.has_errors():
                break
            
            # Extract error
            error_info = self.executor.parse_error(exec_result.stderr)
            
            # Send error to model
            error_prompt = f"The code resulted in an error:\n\n{error_info.message}\n\nPlease fix this error."
            
            # Get fix from model
            self.browser.send_message(error_prompt)
            fix_response = self.browser.extract_response()
            
            # Parse fix
            parsed_fix = self._parse_response(fix_response)
            
            if not parsed_fix.code_blocks:
                break  # Model didn't provide code fix
            
            # Execute fix
            exec_result = self._execute_code_blocks(parsed_fix.code_blocks)
        
        return RetryResult(
            attempts=attempt + 1,
            final_result=exec_result
        )
    
    def _ask_user_approval(self, code_block: CodeBlock) -> bool:
        """Ask user to approve code execution"""
        from rich.console import Console
        from rich.syntax import Syntax
        
        console = Console()
        console.print("\n[bold]Code to execute:[/bold]")
        syntax = Syntax(code_block.code, code_block.language)
        console.print(syntax)
        
        response = input("\nExecute this code? [Y/n]: ")
        return response.lower() in ['y', 'yes', '']
    
    def _detect_file_names(self, response: str, code_blocks: List[CodeBlock]) -> List[str]:
        """Detect file names from response context"""
        import re
        
        # Look for patterns like "save as app.py" or "create file app.py"
        pattern = r'(?:save as|create|in file|to)\s+([a-zA-Z0-9_.-]+\.(?:py|js|html|css|sh|txt))'
        matches = re.findall(pattern, response, re.IGNORECASE)
        
        return list(set(matches))  # Unique file names
    
    def get_history(self, session_id: str = None, limit: int = 10) -> List[Message]:
        """Get conversation history"""
        if not self.session:
            self.session = SessionManager(self.config)
        
        sid = session_id or self.current_session_id
        return self.session.get_messages(sid, limit=limit)
    
    def list_sessions(self) -> List[SessionMeta]:
        """List all sessions"""
        if not self.session:
            self.session = SessionManager(self.config)
        
        return self.session.list_sessions()
    
    def rollback_file(self, filepath: str, timestamp: int = None) -> bool:
        """Rollback file to backup"""
        return self.file_mgr.rollback(filepath, timestamp)
    
    def list_processes(self) -> List[ProcessInfo]:
        """List running background processes"""
        return self.executor.list_processes()
    
    def set_model(self, model: str):
        """Set model for current session"""
        self.config.default_model = model
    
    def set_auto_approve(self, auto: bool):
        """Set auto-approve for current session"""
        self.config.execution.auto_approve = auto
    
    def cleanup(self):
        """Cleanup resources"""
        if self.browser:
            self.browser.close()
```

### Key Methods Summary:

| Method | Purpose | Returns |
|--------|---------|---------|
| `initialize()` | One-time setup | bool |
| `send_prompt()` | Main workflow | Result |
| `get_history()` | Retrieve messages | List[Message] |
| `list_sessions()` | All sessions | List[SessionMeta] |
| `rollback_file()` | Restore backup | bool |

---

*Continued in next file...*
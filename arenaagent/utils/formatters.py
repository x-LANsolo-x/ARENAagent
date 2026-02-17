"""Formatting utilities for ArenaAgent."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from rich.syntax import Syntax
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

from arenaagent.models.message import Message, MessageRole
from arenaagent.models.execution import ExecutionResult


def format_message(message: Message) -> Panel:
    """Format a message for display using Rich.
    
    Args:
        message: Message object to format
        
    Returns:
        Rich Panel with formatted message
    """
    # Color based on role
    role_colors = {
        MessageRole.USER: "cyan",
        MessageRole.ASSISTANT: "green",
        MessageRole.SYSTEM: "yellow",
    }
    
    color = role_colors.get(message.role, "white")
    
    # Create title with timestamp
    timestamp = format_timestamp(message.timestamp, "%H:%M:%S")
    title = f"[{color}]{message.role.value}[/{color}] ({timestamp})"
    
    # Format content
    content = Text(message.content)
    
    # Add metadata if present
    if message.metadata:
        meta_text = "\n\n[dim]Metadata: " + str(message.metadata) + "[/dim]"
        content.append(meta_text)
    
    return Panel(
        content,
        title=title,
        border_style=color,
        padding=(1, 2),
    )


def format_execution_result(result: ExecutionResult) -> Panel:
    """Format execution result for display.
    
    Args:
        result: ExecutionResult object to format
        
    Returns:
        Rich Panel with formatted execution result
    """
    # Determine panel style based on success
    border_style = "green" if result.success else "red"
    title_prefix = "✓" if result.success else "✗"
    
    # Build content
    lines = []
    lines.append(f"[bold]Command:[/bold] {result.command}")
    lines.append(f"[bold]Exit Code:[/bold] {result.exit_code}")
    lines.append(f"[bold]Duration:[/bold] {result.execution_time:.3f}s")
    
    if result.stdout:
        lines.append("\n[bold]Output:[/bold]")
        lines.append(result.stdout[:1000])  # Limit output length
        if len(result.stdout) > 1000:
            lines.append("[dim]... (truncated)[/dim]")
    
    if result.stderr:
        lines.append("\n[bold red]Error Output:[/bold red]")
        lines.append(f"[red]{result.stderr[:1000]}[/red]")
        if len(result.stderr) > 1000:
            lines.append("[dim]... (truncated)[/dim]")
    
    content = "\n".join(lines)
    
    return Panel(
        content,
        title=f"{title_prefix} Execution Result",
        border_style=border_style,
        padding=(1, 2),
    )


def format_code(code: str, language: str = "python", theme: str = "monokai") -> Syntax:
    """Format code with syntax highlighting.
    
    Args:
        code: Code string to format
        language: Programming language for syntax highlighting
        theme: Color theme for syntax highlighting
        
    Returns:
        Rich Syntax object with highlighted code
    """
    return Syntax(
        code,
        language,
        theme=theme,
        line_numbers=True,
        word_wrap=False,
    )


def format_timestamp(
    dt: datetime,
    format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """Format datetime to string.
    
    Args:
        dt: Datetime object to format
        format_str: Format string (strftime compatible)
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def create_table(
    headers: List[str],
    rows: List[List[Any]],
    title: Optional[str] = None,
    show_lines: bool = False,
) -> Table:
    """Create a Rich table.
    
    Args:
        headers: List of column headers
        rows: List of rows (each row is a list of values)
        title: Optional table title
        show_lines: Whether to show lines between rows
        
    Returns:
        Rich Table object
    """
    table = Table(title=title, show_lines=show_lines, show_header=True, header_style="bold magenta")
    
    # Add columns
    for header in headers:
        table.add_column(header)
    
    # Add rows
    for row in rows:
        # Convert all values to strings
        str_row = [str(val) for val in row]
        table.add_row(*str_row)
    
    return table


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_list(items: List[str], style: str = "bullet") -> str:
    """Format list of items.
    
    Args:
        items: List of items to format
        style: List style ('bullet', 'number', 'dash')
        
    Returns:
        Formatted list string
    """
    if style == "bullet":
        return "\n".join(f"• {item}" for item in items)
    elif style == "number":
        return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
    elif style == "dash":
        return "\n".join(f"- {item}" for item in items)
    else:
        return "\n".join(items)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_progress(current: int, total: int, width: int = 20) -> str:
    """Format progress bar.
    
    Args:
        current: Current progress value
        total: Total value
        width: Width of progress bar in characters
        
    Returns:
        Formatted progress bar string
    """
    if total == 0:
        percentage = 0
    else:
        percentage = min(100, int((current / total) * 100))
    
    filled = int((percentage / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    
    return f"[{bar}] {percentage}%"


def format_key_value(key: str, value: Any, key_width: int = 20) -> str:
    """Format key-value pair for display.
    
    Args:
        key: Key name
        value: Value
        key_width: Width for key column
        
    Returns:
        Formatted key-value string
    """
    key_formatted = f"{key}:".ljust(key_width)
    return f"{key_formatted} {value}"


def format_error(error: Exception, include_traceback: bool = False) -> str:
    """Format error message.
    
    Args:
        error: Exception object
        include_traceback: Whether to include full traceback
        
    Returns:
        Formatted error string
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    result = f"[red][bold]{error_type}:[/bold] {error_msg}[/red]"
    
    if include_traceback:
        import traceback
        tb = traceback.format_exc()
        result += f"\n\n[dim]{tb}[/dim]"
    
    return result

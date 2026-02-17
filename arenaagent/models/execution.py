"""ExecutionResult model for code execution tracking.

This module defines the ExecutionResult class which represents the result
of executing a command or code snippet.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class ExecutionResult:
    """Represents the result of executing a command.
    
    Attributes:
        command: The command that was executed
        stdout: Standard output from the command
        stderr: Standard error from the command
        exit_code: Process exit code (0 = success, non-zero = error)
        duration: Execution time in seconds
        timestamp: When the execution occurred (auto-generated)
        working_directory: Directory where the command was executed
        environment_vars: Environment variables used during execution
    """
    
    command: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    working_directory: str = ""
    environment_vars: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate execution result data after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate execution result data.
        
        Raises:
            ValueError: If command is empty or data is invalid
        """
        # Validate command
        if not self.command or not self.command.strip():
            raise ValueError("command cannot be empty")
        
        # Validate duration
        if self.duration < 0:
            raise ValueError(f"duration cannot be negative, got {self.duration}")
        
        # Validate timestamp
        if not isinstance(self.timestamp, datetime):
            raise ValueError(
                f"timestamp must be a datetime object, got {type(self.timestamp)}"
            )
    
    @property
    def success(self) -> bool:
        """Check if execution was successful.
        
        Returns:
            True if exit_code is 0, False otherwise
        """
        return self.exit_code == 0
    
    def is_error(self) -> bool:
        """Check if execution resulted in an error.
        
        Returns:
            True if exit_code is non-zero, False otherwise
        """
        return not self.success
    
    def get_error_message(self) -> str:
        """Get formatted error message.
        
        Returns:
            Formatted error message with stderr and exit code
        """
        if self.success:
            return ""
        
        error_parts = [f"Command failed with exit code {self.exit_code}"]
        
        if self.stderr:
            error_parts.append(f"Error output:\n{self.stderr}")
        
        if self.stdout:
            error_parts.append(f"Standard output:\n{self.stdout}")
        
        return "\n\n".join(error_parts)
    
    def get_output(self) -> str:
        """Get combined output (stdout + stderr).
        
        Returns:
            Combined stdout and stderr
        """
        parts = []
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append(self.stderr)
        return "\n".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution result to JSON-compatible dictionary.
        
        Returns:
            Dictionary representation of the execution result
        """
        return {
            "command": self.command,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "duration": self.duration,
            "timestamp": self.timestamp.isoformat(),
            "working_directory": self.working_directory,
            "environment_vars": self.environment_vars,
            "success": self.success,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionResult":
        """Create execution result from dictionary.
        
        Args:
            data: Dictionary containing execution result data
            
        Returns:
            New ExecutionResult instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Parse timestamp
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()
        
        return cls(
            command=data["command"],
            stdout=data.get("stdout", ""),
            stderr=data.get("stderr", ""),
            exit_code=data.get("exit_code", 0),
            duration=data.get("duration", 0.0),
            timestamp=timestamp,
            working_directory=data.get("working_directory", ""),
            environment_vars=data.get("environment_vars", {}),
        )
    
    def __repr__(self) -> str:
        """Return detailed string representation of the execution result."""
        status = "SUCCESS" if self.success else f"FAILED (exit {self.exit_code})"
        return (
            f"ExecutionResult(command='{self.command[:50]}...', "
            f"status={status}, duration={self.duration:.2f}s)"
        )
    
    def __str__(self) -> str:
        """Return human-readable string representation."""
        status = "✓" if self.success else "✗"
        return f"{status} {self.command} ({self.duration:.2f}s)"

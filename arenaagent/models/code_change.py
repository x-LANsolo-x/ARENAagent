"""CodeChange model for tracking file modifications.

This module defines the CodeChange class which represents a change made
to a file during code execution or AI-generated modifications.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Literal, Optional
import uuid


@dataclass
class CodeChange:
    """Represents a change made to a code file.
    
    Attributes:
        file_path: Path to the file that was changed
        change_type: Type of change (create, modify, delete)
        content_before: File content before the change (None for create)
        content_after: File content after the change (None for delete)
        id: Unique identifier for the change (auto-generated UUID)
        timestamp: When the change was made (auto-generated)
        description: Human-readable description of the change
        metadata: Additional arbitrary data
    """
    
    file_path: str
    change_type: Literal["create", "modify", "delete"]
    content_before: Optional[str] = None
    content_after: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate code change data after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate code change data.
        
        Raises:
            ValueError: If change_type is invalid or data is inconsistent
        """
        # Validate change_type
        valid_types = ["create", "modify", "delete"]
        if self.change_type not in valid_types:
            raise ValueError(
                f"Invalid change_type '{self.change_type}'. "
                f"Must be one of: {', '.join(valid_types)}"
            )
        
        # Validate file_path
        if not self.file_path or not self.file_path.strip():
            raise ValueError("file_path cannot be empty")
        
        # Validate UUID format
        try:
            uuid.UUID(self.id)
        except ValueError as e:
            raise ValueError(f"Invalid UUID format for change ID: {self.id}") from e
        
        # Validate timestamp
        if not isinstance(self.timestamp, datetime):
            raise ValueError(
                f"timestamp must be a datetime object, got {type(self.timestamp)}"
            )
        
        # Validate content consistency with change_type
        if self.change_type == "create":
            if self.content_before is not None:
                raise ValueError("create changes should not have content_before")
            if self.content_after is None:
                raise ValueError("create changes must have content_after")
        
        elif self.change_type == "modify":
            if self.content_before is None:
                raise ValueError("modify changes must have content_before")
            if self.content_after is None:
                raise ValueError("modify changes must have content_after")
        
        elif self.change_type == "delete":
            if self.content_before is None:
                raise ValueError("delete changes must have content_before")
            if self.content_after is not None:
                raise ValueError("delete changes should not have content_after")
    
    def get_diff_summary(self) -> str:
        """Get a summary of the changes.
        
        Returns:
            Human-readable summary of the change
        """
        if self.change_type == "create":
            lines = len(self.content_after.splitlines()) if self.content_after else 0
            return f"Created {self.file_path} ({lines} lines)"
        
        elif self.change_type == "delete":
            lines = len(self.content_before.splitlines()) if self.content_before else 0
            return f"Deleted {self.file_path} ({lines} lines)"
        
        else:  # modify
            before_lines = len(self.content_before.splitlines()) if self.content_before else 0
            after_lines = len(self.content_after.splitlines()) if self.content_after else 0
            diff = after_lines - before_lines
            sign = "+" if diff > 0 else ""
            return f"Modified {self.file_path} ({sign}{diff} lines)"
    
    def can_rollback(self) -> bool:
        """Check if this change can be rolled back.
        
        Returns:
            True if the change can be rolled back, False otherwise
        """
        # Create changes can be rolled back by deleting
        if self.change_type == "create":
            return True
        
        # Modify changes can be rolled back to previous content
        if self.change_type == "modify" and self.content_before is not None:
            return True
        
        # Delete changes can be rolled back by recreating
        if self.change_type == "delete" and self.content_before is not None:
            return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert code change to JSON-compatible dictionary.
        
        Returns:
            Dictionary representation of the code change
        """
        return {
            "id": self.id,
            "file_path": self.file_path,
            "change_type": self.change_type,
            "content_before": self.content_before,
            "content_after": self.content_after,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodeChange":
        """Create code change from dictionary.
        
        Args:
            data: Dictionary containing code change data
            
        Returns:
            New CodeChange instance
            
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
            id=data.get("id", str(uuid.uuid4())),
            file_path=data["file_path"],
            change_type=data["change_type"],
            content_before=data.get("content_before"),
            content_after=data.get("content_after"),
            timestamp=timestamp,
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )
    
    def __repr__(self) -> str:
        """Return detailed string representation of the code change."""
        return (
            f"CodeChange(id='{self.id[:8]}...', type='{self.change_type}', "
            f"file='{self.file_path}', timestamp={self.timestamp.isoformat()})"
        )
    
    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"[{self.change_type.upper()}] {self.file_path}"

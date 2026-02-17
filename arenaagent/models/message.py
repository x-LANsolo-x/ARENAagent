"""Message model for ArenaAgent conversations.

This module defines the Message class which represents a single message
in a conversation between the user and the AI assistant.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Literal, Optional
import uuid
import json


@dataclass
class Message:
    """Represents a single message in a conversation.
    
    Attributes:
        role: The role of the message sender (user, assistant, or system)
        content: The actual content/text of the message
        id: Unique identifier for the message (auto-generated UUID)
        timestamp: When the message was created (auto-generated)
        model: Optional name of the LM Arena model used for assistant messages
        metadata: Additional arbitrary data associated with the message
    """
    
    role: Literal["user", "assistant", "system"]
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    model: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate message data after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate message data.
        
        Raises:
            ValueError: If role is invalid, content is empty, or other validation fails
        """
        # Validate role
        valid_roles = ["user", "assistant", "system"]
        if self.role not in valid_roles:
            raise ValueError(
                f"Invalid role '{self.role}'. Must be one of: {', '.join(valid_roles)}"
            )
        
        # Validate content
        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty")
        
        # Validate UUID format
        try:
            uuid.UUID(self.id)
        except ValueError as e:
            raise ValueError(f"Invalid UUID format for message ID: {self.id}") from e
        
        # Validate timestamp
        if not isinstance(self.timestamp, datetime):
            raise ValueError(f"Timestamp must be a datetime object, got {type(self.timestamp)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to JSON-compatible dictionary.
        
        Returns:
            Dictionary representation of the message
        """
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "model": self.model,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary.
        
        Args:
            data: Dictionary containing message data
            
        Returns:
            New Message instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Parse timestamp if it's a string
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            role=data["role"],
            content=data["content"],
            timestamp=timestamp,
            model=data.get("model"),
            metadata=data.get("metadata", {}),
        )
    
    def to_json(self) -> str:
        """Convert message to JSON string.
        
        Returns:
            JSON string representation of the message
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """Create message from JSON string.
        
        Args:
            json_str: JSON string containing message data
            
        Returns:
            New Message instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self) -> str:
        """Return detailed string representation of the message."""
        return (
            f"Message(id='{self.id[:8]}...', role='{self.role}', "
            f"content='{self.content[:50]}...', timestamp={self.timestamp.isoformat()})"
        )
    
    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"[{self.role.upper()}] {self.content}"

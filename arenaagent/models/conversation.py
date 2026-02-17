"""Conversation model for ArenaAgent sessions.

This module defines the Conversation class which represents a complete
conversation session with all messages and metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid
import json

from arenaagent.models.message import Message


@dataclass
class Conversation:
    """Represents a complete conversation session.
    
    Attributes:
        id: Unique identifier for the conversation (auto-generated UUID)
        title: Human-readable title for the conversation
        messages: List of messages in chronological order
        created_at: When the conversation was created (auto-generated)
        updated_at: When the conversation was last modified
        metadata: Additional arbitrary data (tags, project info, etc.)
    """
    
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate conversation data after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate conversation data.
        
        Raises:
            ValueError: If title is empty or other validation fails
        """
        # Validate title
        if not self.title or not self.title.strip():
            raise ValueError("Conversation title cannot be empty")
        
        # Validate UUID format
        try:
            uuid.UUID(self.id)
        except ValueError as e:
            raise ValueError(f"Invalid UUID format for conversation ID: {self.id}") from e
        
        # Validate timestamps
        if not isinstance(self.created_at, datetime):
            raise ValueError(f"created_at must be a datetime object, got {type(self.created_at)}")
        if not isinstance(self.updated_at, datetime):
            raise ValueError(f"updated_at must be a datetime object, got {type(self.updated_at)}")
        
        # Validate messages
        if not isinstance(self.messages, list):
            raise ValueError(f"messages must be a list, got {type(self.messages)}")
        
        for i, msg in enumerate(self.messages):
            if not isinstance(msg, Message):
                raise ValueError(f"Message at index {i} is not a Message instance")
    
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation.
        
        Args:
            message: The message to add
        """
        if not isinstance(message, Message):
            raise ValueError("message must be a Message instance")
        
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_messages_by_role(self, role: str) -> List[Message]:
        """Get all messages with a specific role.
        
        Args:
            role: The role to filter by (user, assistant, system)
            
        Returns:
            List of messages with the specified role
        """
        return [msg for msg in self.messages if msg.role == role]
    
    def get_last_message(self) -> Optional[Message]:
        """Get the most recent message.
        
        Returns:
            The last message, or None if conversation is empty
        """
        return self.messages[-1] if self.messages else None
    
    def get_message_count(self) -> int:
        """Get the total number of messages.
        
        Returns:
            Number of messages in the conversation
        """
        return len(self.messages)
    
    def clear_messages(self) -> None:
        """Remove all messages from the conversation."""
        self.messages.clear()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to JSON-compatible dictionary.
        
        Returns:
            Dictionary representation of the conversation
        """
        return {
            "id": self.id,
            "title": self.title,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Create conversation from dictionary.
        
        Args:
            data: Dictionary containing conversation data
            
        Returns:
            New Conversation instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Parse timestamps
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif updated_at is None:
            updated_at = datetime.now()
        
        # Parse messages
        messages = []
        for msg_data in data.get("messages", []):
            if isinstance(msg_data, dict):
                messages.append(Message.from_dict(msg_data))
            elif isinstance(msg_data, Message):
                messages.append(msg_data)
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data["title"],
            messages=messages,
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get("metadata", {}),
        )
    
    def to_json(self) -> str:
        """Convert conversation to JSON string.
        
        Returns:
            JSON string representation of the conversation
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Conversation":
        """Create conversation from JSON string.
        
        Args:
            json_str: JSON string containing conversation data
            
        Returns:
            New Conversation instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_to_file(self, file_path: Path) -> None:
        """Save conversation to a JSON file.
        
        Args:
            file_path: Path where the conversation should be saved
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> "Conversation":
        """Load conversation from a JSON file.
        
        Args:
            file_path: Path to the conversation file
            
        Returns:
            Loaded Conversation instance
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        file_path = Path(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            json_str = f.read()
        
        return cls.from_json(json_str)
    
    def __repr__(self) -> str:
        """Return detailed string representation of the conversation."""
        return (
            f"Conversation(id='{self.id[:8]}...', title='{self.title}', "
            f"messages={len(self.messages)}, created_at={self.created_at.isoformat()})"
        )
    
    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"[{self.title}] {len(self.messages)} messages"

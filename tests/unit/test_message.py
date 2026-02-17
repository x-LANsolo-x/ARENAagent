"""Unit tests for the Message model."""

import json
import pytest
from datetime import datetime
import uuid

from arenaagent.models.message import Message


class TestMessageCreation:
    """Tests for creating Message instances."""
    
    def test_message_creation_with_defaults(self):
        """Test creating a message with default values."""
        msg = Message(role="user", content="Hello, world!")
        
        assert msg.role == "user"
        assert msg.content == "Hello, world!"
        assert msg.id is not None
        assert isinstance(msg.timestamp, datetime)
        assert msg.model is None
        assert msg.metadata == {}
    
    def test_message_creation_with_all_fields(self):
        """Test creating a message with all fields specified."""
        custom_id = str(uuid.uuid4())
        custom_timestamp = datetime(2024, 1, 1, 12, 0, 0)
        
        msg = Message(
            role="assistant",
            content="Test response",
            id=custom_id,
            timestamp=custom_timestamp,
            model="gpt-4",
            metadata={"key": "value"}
        )
        
        assert msg.role == "assistant"
        assert msg.content == "Test response"
        assert msg.id == custom_id
        assert msg.timestamp == custom_timestamp
        assert msg.model == "gpt-4"
        assert msg.metadata == {"key": "value"}
    
    def test_message_auto_generates_uuid(self):
        """Test that message auto-generates a valid UUID."""
        msg = Message(role="user", content="Test")
        
        # Should be a valid UUID
        assert uuid.UUID(msg.id)
    
    def test_message_auto_generates_timestamp(self):
        """Test that message auto-generates a timestamp."""
        before = datetime.now()
        msg = Message(role="user", content="Test")
        after = datetime.now()
        
        assert before <= msg.timestamp <= after


class TestMessageValidation:
    """Tests for message validation."""
    
    def test_validation_invalid_role(self):
        """Test validation fails for invalid role."""
        with pytest.raises(ValueError, match="Invalid role"):
            Message(role="invalid", content="Test")
    
    def test_validation_empty_content(self):
        """Test validation fails for empty content."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            Message(role="user", content="")
    
    def test_validation_whitespace_only_content(self):
        """Test validation fails for whitespace-only content."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            Message(role="user", content="   ")
    
    def test_validation_invalid_uuid(self):
        """Test validation fails for invalid UUID."""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            Message(role="user", content="Test", id="not-a-uuid")
    
    def test_validation_invalid_timestamp_type(self):
        """Test validation fails for invalid timestamp type."""
        with pytest.raises(ValueError, match="must be a datetime object"):
            Message(role="user", content="Test", timestamp="not-a-datetime")


class TestMessageSerialization:
    """Tests for message serialization."""
    
    def test_to_dict(self):
        """Test converting message to dictionary."""
        msg = Message(
            role="user",
            content="Test message",
            model="gpt-4",
            metadata={"test": "data"}
        )
        
        data = msg.to_dict()
        
        assert data["role"] == "user"
        assert data["content"] == "Test message"
        assert data["id"] == msg.id
        assert data["timestamp"] == msg.timestamp.isoformat()
        assert data["model"] == "gpt-4"
        assert data["metadata"] == {"test": "data"}
    
    def test_from_dict(self):
        """Test creating message from dictionary."""
        data = {
            "role": "assistant",
            "content": "Test response",
            "id": str(uuid.uuid4()),
            "timestamp": "2024-01-01T12:00:00",
            "model": "claude-3",
            "metadata": {"key": "value"}
        }
        
        msg = Message.from_dict(data)
        
        assert msg.role == "assistant"
        assert msg.content == "Test response"
        assert msg.id == data["id"]
        assert msg.model == "claude-3"
        assert msg.metadata == {"key": "value"}
    
    def test_serialization_roundtrip(self):
        """Test that serialization roundtrip preserves data."""
        original = Message(
            role="user",
            content="Original message",
            model="test-model",
            metadata={"important": "data"}
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = Message.from_dict(data)
        
        assert restored.role == original.role
        assert restored.content == original.content
        assert restored.id == original.id
        assert restored.model == original.model
        assert restored.metadata == original.metadata
    
    def test_to_json(self):
        """Test converting message to JSON string."""
        msg = Message(role="user", content="Test")
        json_str = msg.to_json()
        
        # Should be valid JSON
        data = json.loads(json_str)
        assert data["role"] == "user"
        assert data["content"] == "Test"
    
    def test_from_json(self):
        """Test creating message from JSON string."""
        json_str = json.dumps({
            "role": "assistant",
            "content": "Test response",
            "id": str(uuid.uuid4()),
            "timestamp": "2024-01-01T12:00:00"
        })
        
        msg = Message.from_json(json_str)
        
        assert msg.role == "assistant"
        assert msg.content == "Test response"


class TestMessageStringRepresentation:
    """Tests for message string representations."""
    
    def test_repr(self):
        """Test __repr__ returns detailed representation."""
        msg = Message(role="user", content="This is a test message that is quite long")
        repr_str = repr(msg)
        
        assert "Message(" in repr_str
        assert "role='user'" in repr_str
        assert msg.id[:8] in repr_str
    
    def test_str(self):
        """Test __str__ returns human-readable representation."""
        msg = Message(role="assistant", content="Hello!")
        str_rep = str(msg)
        
        assert "[ASSISTANT]" in str_rep
        assert "Hello!" in str_rep


class TestMessageRoles:
    """Tests for different message roles."""
    
    def test_user_role(self):
        """Test creating a user message."""
        msg = Message(role="user", content="User question")
        assert msg.role == "user"
    
    def test_assistant_role(self):
        """Test creating an assistant message."""
        msg = Message(role="assistant", content="Assistant response")
        assert msg.role == "assistant"
    
    def test_system_role(self):
        """Test creating a system message."""
        msg = Message(role="system", content="System prompt")
        assert msg.role == "system"

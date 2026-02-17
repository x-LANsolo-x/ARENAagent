"""Unit tests for the Conversation model."""

import json
import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import uuid

from arenaagent.models.conversation import Conversation
from arenaagent.models.message import Message


class TestConversationCreation:
    """Tests for creating Conversation instances."""
    
    def test_conversation_creation_with_defaults(self):
        """Test creating a conversation with default values."""
        conv = Conversation(title="Test Conversation")
        
        assert conv.title == "Test Conversation"
        assert conv.id is not None
        assert isinstance(conv.messages, list)
        assert len(conv.messages) == 0
        assert isinstance(conv.created_at, datetime)
        assert isinstance(conv.updated_at, datetime)
        assert conv.metadata == {}
    
    def test_conversation_creation_with_messages(self):
        """Test creating a conversation with initial messages."""
        msg1 = Message(role="user", content="Hello")
        msg2 = Message(role="assistant", content="Hi there!")
        
        conv = Conversation(title="Chat", messages=[msg1, msg2])
        
        assert len(conv.messages) == 2
        assert conv.messages[0] == msg1
        assert conv.messages[1] == msg2
    
    def test_conversation_auto_generates_uuid(self):
        """Test that conversation auto-generates a valid UUID."""
        conv = Conversation(title="Test")
        
        # Should be a valid UUID
        assert uuid.UUID(conv.id)


class TestConversationValidation:
    """Tests for conversation validation."""
    
    def test_validation_empty_title(self):
        """Test validation fails for empty title."""
        with pytest.raises(ValueError, match="title cannot be empty"):
            Conversation(title="")
    
    def test_validation_whitespace_only_title(self):
        """Test validation fails for whitespace-only title."""
        with pytest.raises(ValueError, match="title cannot be empty"):
            Conversation(title="   ")
    
    def test_validation_invalid_uuid(self):
        """Test validation fails for invalid UUID."""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            Conversation(title="Test", id="not-a-uuid")
    
    def test_validation_invalid_message_type(self):
        """Test validation fails when messages contain non-Message objects."""
        with pytest.raises(ValueError, match="not a Message instance"):
            Conversation(title="Test", messages=["not a message"])


class TestConversationMessageManagement:
    """Tests for managing messages in a conversation."""
    
    def test_add_message(self):
        """Test adding a message to conversation."""
        conv = Conversation(title="Test")
        msg = Message(role="user", content="Hello")
        
        conv.add_message(msg)
        
        assert len(conv.messages) == 1
        assert conv.messages[0] == msg
    
    def test_add_message_updates_timestamp(self):
        """Test that adding a message updates updated_at."""
        conv = Conversation(title="Test")
        original_updated = conv.updated_at
        
        import time
        time.sleep(0.01)  # Small delay to ensure timestamp difference
        
        msg = Message(role="user", content="Hello")
        conv.add_message(msg)
        
        assert conv.updated_at > original_updated
    
    def test_add_message_invalid_type(self):
        """Test that adding non-Message raises error."""
        conv = Conversation(title="Test")
        
        with pytest.raises(ValueError, match="must be a Message instance"):
            conv.add_message("not a message")
    
    def test_get_messages_by_role(self):
        """Test filtering messages by role."""
        conv = Conversation(title="Test")
        conv.add_message(Message(role="user", content="Q1"))
        conv.add_message(Message(role="assistant", content="A1"))
        conv.add_message(Message(role="user", content="Q2"))
        
        user_messages = conv.get_messages_by_role("user")
        assistant_messages = conv.get_messages_by_role("assistant")
        
        assert len(user_messages) == 2
        assert len(assistant_messages) == 1
        assert user_messages[0].content == "Q1"
        assert assistant_messages[0].content == "A1"
    
    def test_get_last_message(self):
        """Test getting the last message."""
        conv = Conversation(title="Test")
        
        # Empty conversation
        assert conv.get_last_message() is None
        
        # Add messages
        msg1 = Message(role="user", content="First")
        msg2 = Message(role="assistant", content="Second")
        conv.add_message(msg1)
        conv.add_message(msg2)
        
        last = conv.get_last_message()
        assert last == msg2
        assert last.content == "Second"
    
    def test_get_message_count(self):
        """Test getting message count."""
        conv = Conversation(title="Test")
        
        assert conv.get_message_count() == 0
        
        conv.add_message(Message(role="user", content="Test"))
        assert conv.get_message_count() == 1
        
        conv.add_message(Message(role="assistant", content="Response"))
        assert conv.get_message_count() == 2
    
    def test_clear_messages(self):
        """Test clearing all messages."""
        conv = Conversation(title="Test")
        conv.add_message(Message(role="user", content="Test"))
        conv.add_message(Message(role="assistant", content="Response"))
        
        assert len(conv.messages) == 2
        
        conv.clear_messages()
        
        assert len(conv.messages) == 0


class TestConversationSerialization:
    """Tests for conversation serialization."""
    
    def test_to_dict(self):
        """Test converting conversation to dictionary."""
        conv = Conversation(title="Test Chat")
        conv.add_message(Message(role="user", content="Hello"))
        
        data = conv.to_dict()
        
        assert data["title"] == "Test Chat"
        assert data["id"] == conv.id
        assert isinstance(data["messages"], list)
        assert len(data["messages"]) == 1
        assert data["messages"][0]["content"] == "Hello"
    
    def test_from_dict(self):
        """Test creating conversation from dictionary."""
        data = {
            "title": "Test",
            "id": str(uuid.uuid4()),
            "messages": [
                {
                    "role": "user",
                    "content": "Hello",
                    "id": str(uuid.uuid4()),
                    "timestamp": "2024-01-01T12:00:00"
                }
            ],
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-01T12:00:00",
            "metadata": {"key": "value"}
        }
        
        conv = Conversation.from_dict(data)
        
        assert conv.title == "Test"
        assert conv.id == data["id"]
        assert len(conv.messages) == 1
        assert conv.messages[0].content == "Hello"
        assert conv.metadata == {"key": "value"}
    
    def test_serialization_roundtrip(self):
        """Test that serialization roundtrip preserves data."""
        original = Conversation(title="Original")
        original.add_message(Message(role="user", content="Test"))
        original.metadata = {"important": "data"}
        
        # Convert to dict and back
        data = original.to_dict()
        restored = Conversation.from_dict(data)
        
        assert restored.title == original.title
        assert restored.id == original.id
        assert len(restored.messages) == len(original.messages)
        assert restored.metadata == original.metadata
    
    def test_to_json(self):
        """Test converting conversation to JSON string."""
        conv = Conversation(title="Test")
        json_str = conv.to_json()
        
        # Should be valid JSON
        data = json.loads(json_str)
        assert data["title"] == "Test"
    
    def test_from_json(self):
        """Test creating conversation from JSON string."""
        json_str = json.dumps({
            "title": "Test",
            "id": str(uuid.uuid4()),
            "messages": [],
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-01T12:00:00"
        })
        
        conv = Conversation.from_json(json_str)
        
        assert conv.title == "Test"


class TestConversationFileOperations:
    """Tests for saving and loading conversations."""
    
    def test_save_to_file(self):
        """Test saving conversation to file."""
        conv = Conversation(title="Test")
        conv.add_message(Message(role="user", content="Hello"))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_conv.json"
            conv.save_to_file(file_path)
            
            assert file_path.exists()
            
            # Verify content
            with open(file_path) as f:
                data = json.load(f)
            assert data["title"] == "Test"
    
    def test_load_from_file(self):
        """Test loading conversation from file."""
        conv = Conversation(title="Loaded")
        conv.add_message(Message(role="user", content="Test message"))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_conv.json"
            conv.save_to_file(file_path)
            
            loaded = Conversation.load_from_file(file_path)
            
            assert loaded.title == conv.title
            assert loaded.id == conv.id
            assert len(loaded.messages) == 1
            assert loaded.messages[0].content == "Test message"
    
    def test_save_creates_parent_directories(self):
        """Test that save creates parent directories if needed."""
        conv = Conversation(title="Test")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "nested" / "dir" / "conv.json"
            conv.save_to_file(file_path)
            
            assert file_path.exists()


class TestConversationStringRepresentation:
    """Tests for conversation string representations."""
    
    def test_repr(self):
        """Test __repr__ returns detailed representation."""
        conv = Conversation(title="My Conversation")
        conv.add_message(Message(role="user", content="Test"))
        repr_str = repr(conv)
        
        assert "Conversation(" in repr_str
        assert "title='My Conversation'" in repr_str
        assert "messages=1" in repr_str
    
    def test_str(self):
        """Test __str__ returns human-readable representation."""
        conv = Conversation(title="Chat Session")
        conv.add_message(Message(role="user", content="Q"))
        conv.add_message(Message(role="assistant", content="A"))
        str_rep = str(conv)
        
        assert "[Chat Session]" in str_rep
        assert "2 messages" in str_rep

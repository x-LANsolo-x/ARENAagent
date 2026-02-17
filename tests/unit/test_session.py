"""Unit tests for the Session and SessionManager classes."""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from arenaagent.session.manager import Session, SessionManager
from arenaagent.models.message import Message
from arenaagent.models.conversation import Conversation


class TestSession:
    """Tests for Session class."""
    
    def test_session_creation_with_defaults(self):
        """Test creating session with default values."""
        session = Session()
        
        assert session.session_id is not None
        assert isinstance(session.session_id, str)
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.updated_at, datetime)
        assert isinstance(session.conversation, Conversation)
        assert isinstance(session.metadata, dict)
        assert len(session.metadata) == 0
    
    def test_session_creation_with_custom_id(self):
        """Test creating session with custom ID."""
        custom_id = "test-session-123"
        session = Session(session_id=custom_id)
        
        assert session.session_id == custom_id
    
    def test_session_creation_with_metadata(self):
        """Test creating session with metadata."""
        metadata = {"user": "test", "purpose": "testing"}
        session = Session(metadata=metadata)
        
        assert session.metadata == metadata
    
    def test_session_add_message(self):
        """Test adding message to session."""
        session = Session()
        message = Message(role="user", content="Hello")
        
        initial_updated_at = session.updated_at
        
        # Add message
        session.add_message(message)
        
        assert len(session.conversation.messages) == 1
        assert session.conversation.messages[0] == message
        assert session.updated_at > initial_updated_at
    
    def test_session_to_dict(self):
        """Test converting session to dictionary."""
        session = Session(
            session_id="test-123",
            metadata={"key": "value"}
        )
        
        session_dict = session.to_dict()
        
        assert isinstance(session_dict, dict)
        assert session_dict["session_id"] == "test-123"
        assert "created_at" in session_dict
        assert "updated_at" in session_dict
        assert "conversation" in session_dict
        assert session_dict["metadata"] == {"key": "value"}
    
    def test_session_from_dict(self):
        """Test creating session from dictionary."""
        data = {
            "session_id": "test-456",
            "created_at": "2026-02-17T10:00:00",
            "updated_at": "2026-02-17T11:00:00",
            "conversation": {
                "messages": [
                    {
                        "id": "msg-1",
                        "role": "user",
                        "content": "Test message",
                        "timestamp": "2026-02-17T10:30:00",
                        "model": None,
                        "metadata": {}
                    }
                ]
            },
            "metadata": {"test": "data"},
            "working_directory": "/tmp/test"
        }
        
        session = Session.from_dict(data)
        
        assert session.session_id == "test-456"
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.updated_at, datetime)
        assert len(session.conversation.messages) == 1
        assert session.metadata == {"test": "data"}
        assert session.working_directory == "/tmp/test"
    
    def test_session_get_message_count(self):
        """Test getting message count."""
        session = Session()
        
        assert session.get_message_count() == 0
        
        session.add_message(Message(role="user", content="Message 1"))
        assert session.get_message_count() == 1
        
        session.add_message(Message(role="assistant", content="Message 2"))
        assert session.get_message_count() == 2
    
    def test_session_get_duration(self):
        """Test getting session duration."""
        session = Session()
        
        # Initially, duration should be ~0
        duration = session.get_duration()
        assert duration >= 0
        assert duration < 1  # Less than 1 second
        
        # Simulate time passing
        session.updated_at = session.created_at + timedelta(minutes=5)
        duration = session.get_duration()
        
        assert duration == 300  # 5 minutes = 300 seconds


class TestSessionManager:
    """Tests for SessionManager class."""
    
    def test_session_manager_initialization(self):
        """Test SessionManager initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            assert manager.sessions_dir == Path(tmpdir)
            assert manager.sessions_dir.exists()
            assert manager._current_session is None
    
    def test_session_manager_default_directory(self):
        """Test SessionManager uses default directory."""
        manager = SessionManager()
        
        expected_dir = Path.home() / ".arenaagent" / "sessions"
        assert manager.sessions_dir == expected_dir
    
    def test_create_session(self):
        """Test creating a new session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            session = manager.create_session()
            
            assert session is not None
            assert isinstance(session, Session)
            assert manager.get_current_session() == session
            
            # Check session directory was created
            session_dir = manager.get_session_path(session.session_id)
            assert session_dir.exists()
    
    def test_create_session_with_custom_id(self):
        """Test creating session with custom ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            custom_id = "my-custom-session"
            session = manager.create_session(session_id=custom_id)
            
            assert session.session_id == custom_id
    
    def test_create_session_with_metadata(self):
        """Test creating session with metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            metadata = {"project": "test", "version": "1.0"}
            session = manager.create_session(metadata=metadata)
            
            assert session.metadata == metadata
    
    def test_save_current_session(self):
        """Test saving current session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            session = manager.create_session()
            
            # Add a message
            session.add_message(Message(role="user", content="Test"))
            
            # Save session
            manager.save_current_session()
            
            # Verify session file exists
            session_file = manager.get_session_path(session.session_id) / "session.json"
            assert session_file.exists()
    
    def test_save_current_session_without_session(self):
        """Test saving current session fails without active session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            with pytest.raises(RuntimeError, match="No current session to save"):
                manager.save_current_session()
    
    def test_load_session(self):
        """Test loading an existing session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            # Create and save a session
            original_session = manager.create_session(session_id="load-test")
            original_session.add_message(Message(role="user", content="Test message"))
            manager.save_current_session()
            
            # Clear current session
            manager._current_session = None
            
            # Load session
            loaded_session = manager.load_session("load-test")
            
            assert loaded_session.session_id == "load-test"
            assert loaded_session.get_message_count() == 1
            assert manager.get_current_session() == loaded_session
    
    def test_load_nonexistent_session(self):
        """Test loading nonexistent session raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            with pytest.raises(FileNotFoundError, match="Session not found"):
                manager.load_session("nonexistent-session")
    
    def test_list_sessions(self):
        """Test listing all sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            # Initially no sessions
            assert len(manager.list_sessions()) == 0
            
            # Create multiple sessions
            session1 = manager.create_session(session_id="session-1")
            manager.save_current_session()
            
            session2 = manager.create_session(session_id="session-2")
            session2.add_message(Message(role="user", content="Hello"))
            manager.save_current_session()
            
            # List sessions
            sessions = manager.list_sessions()
            
            assert len(sessions) == 2
            assert all("session_id" in s for s in sessions)
            assert all("created_at" in s for s in sessions)
            assert all("updated_at" in s for s in sessions)
            assert all("message_count" in s for s in sessions)
    
    def test_list_sessions_sorted_by_updated_at(self):
        """Test sessions are sorted by most recent first."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            # Create sessions
            session1 = manager.create_session(session_id="old-session")
            manager.save_current_session()
            
            session2 = manager.create_session(session_id="new-session")
            session2.add_message(Message(role="user", content="New"))
            manager.save_current_session()
            
            sessions = manager.list_sessions()
            
            # Most recent should be first
            assert sessions[0]["session_id"] == "new-session"
            assert sessions[1]["session_id"] == "old-session"
    
    def test_delete_session(self):
        """Test deleting a session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            session = manager.create_session(session_id="delete-me")
            manager.save_current_session()
            
            session_dir = manager.get_session_path("delete-me")
            assert session_dir.exists()
            
            # Delete session
            manager.delete_session("delete-me")
            
            assert not session_dir.exists()
            assert manager.get_current_session() is None
    
    def test_delete_nonexistent_session(self):
        """Test deleting nonexistent session raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            with pytest.raises(FileNotFoundError, match="Session not found"):
                manager.delete_session("nonexistent")
    
    def test_resume_last_session(self):
        """Test resuming the most recent session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            # Create multiple sessions
            session1 = manager.create_session(session_id="session-1")
            manager.save_current_session()
            
            session2 = manager.create_session(session_id="session-2")
            session2.add_message(Message(role="user", content="Latest"))
            manager.save_current_session()
            
            # Clear current session
            manager._current_session = None
            
            # Resume last session
            resumed = manager.resume_last_session()
            
            assert resumed is not None
            assert resumed.session_id == "session-2"
    
    def test_resume_last_session_with_no_sessions(self):
        """Test resuming last session when none exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            resumed = manager.resume_last_session()
            
            assert resumed is None
    
    def test_add_message_to_current_session(self):
        """Test adding message to current session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            session = manager.create_session()
            
            message = Message(role="user", content="Test message")
            manager.add_message_to_current_session(message)
            
            assert session.get_message_count() == 1
            assert session.conversation.messages[0] == message
    
    def test_add_message_without_current_session(self):
        """Test adding message fails without current session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            message = Message(role="user", content="Test")
            
            with pytest.raises(RuntimeError, match="No current session"):
                manager.add_message_to_current_session(message)
    
    def test_export_session(self):
        """Test exporting session to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            # Create session with data
            session = manager.create_session(session_id="export-test")
            session.add_message(Message(role="user", content="Export me"))
            manager.save_current_session()
            
            # Export session
            export_path = Path(tmpdir) / "exported_session.json"
            manager.export_session("export-test", str(export_path))
            
            assert export_path.exists()
            
            # Verify exported data
            with open(export_path, 'r') as f:
                data = json.load(f)
            
            assert data["session_id"] == "export-test"
            assert len(data["conversation"]["messages"]) == 1
    
    def test_import_session(self):
        """Test importing session from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            # Create import file
            import_data = {
                "session_id": "imported-session",
                "created_at": "2026-02-17T10:00:00",
                "updated_at": "2026-02-17T11:00:00",
                "conversation": {
                    "messages": [
                        {
                            "id": "msg-1",
                            "role": "user",
                            "content": "Imported message",
                            "timestamp": "2026-02-17T10:30:00",
                            "model": None,
                            "metadata": {}
                        }
                    ]
                },
                "metadata": {},
                "working_directory": "/tmp"
            }
            
            import_path = Path(tmpdir) / "import.json"
            with open(import_path, 'w') as f:
                json.dump(import_data, f)
            
            # Import session
            session = manager.import_session(str(import_path))
            
            assert session.session_id == "imported-session"
            assert session.get_message_count() == 1
            assert manager.get_current_session() == session
    
    def test_get_session_path(self):
        """Test getting session directory path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(tmpdir)
            
            path = manager.get_session_path("test-session")
            
            assert path == Path(tmpdir) / "test-session"
            assert isinstance(path, Path)

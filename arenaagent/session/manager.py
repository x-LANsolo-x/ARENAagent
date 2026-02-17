"""Session management for ArenaAgent.

This module provides the SessionManager class for handling session
lifecycle, persistence, and state management.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import uuid

from arenaagent.models.conversation import Conversation
from arenaagent.models.message import Message
from arenaagent.utils.logger import get_logger


class Session:
    """Represents an ArenaAgent session.
    
    Attributes:
        session_id: Unique identifier for the session
        created_at: When the session was created
        updated_at: When the session was last updated
        conversation: Conversation history for this session
        metadata: Additional session metadata
        working_directory: Working directory for this session
    """
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        conversation: Optional[Conversation] = None,
        metadata: Optional[Dict[str, Any]] = None,
        working_directory: Optional[str] = None,
    ):
        """Initialize session.
        
        Args:
            session_id: Unique session ID (auto-generated if None)
            created_at: Creation timestamp (auto-generated if None)
            updated_at: Last update timestamp (auto-generated if None)
            conversation: Conversation instance (created if None)
            metadata: Session metadata
            working_directory: Working directory path
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.conversation = conversation or Conversation()
        self.metadata = metadata or {}
        self.working_directory = working_directory or str(Path.cwd())
    
    def add_message(self, message: Message) -> None:
        """Add message to session conversation.
        
        Args:
            message: Message to add
        """
        self.conversation.add_message(message)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary.
        
        Returns:
            Dictionary representation of session
        """
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "conversation": self.conversation.to_dict(),
            "metadata": self.metadata,
            "working_directory": self.working_directory,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create session from dictionary.
        
        Args:
            data: Dictionary containing session data
            
        Returns:
            New Session instance
        """
        # Parse timestamps
        created_at = datetime.fromisoformat(data["created_at"])
        updated_at = datetime.fromisoformat(data["updated_at"])
        
        # Parse conversation
        conversation = Conversation.from_dict(data["conversation"])
        
        return cls(
            session_id=data["session_id"],
            created_at=created_at,
            updated_at=updated_at,
            conversation=conversation,
            metadata=data.get("metadata", {}),
            working_directory=data.get("working_directory", str(Path.cwd())),
        )
    
    def get_message_count(self) -> int:
        """Get total message count.
        
        Returns:
            Number of messages in session
        """
        return len(self.conversation.messages)
    
    def get_duration(self) -> float:
        """Get session duration in seconds.
        
        Returns:
            Duration from creation to last update in seconds
        """
        delta = self.updated_at - self.created_at
        return delta.total_seconds()


class SessionManager:
    """Manages ArenaAgent sessions with persistence."""
    
    SESSION_FILENAME = "session.json"
    CONVERSATION_FILENAME = "conversation.json"
    METADATA_FILENAME = "metadata.json"
    
    def __init__(self, sessions_dir: Optional[str] = None):
        """Initialize session manager.
        
        Args:
            sessions_dir: Directory for session storage (defaults to ~/.arenaagent/sessions)
        """
        if sessions_dir is None:
            sessions_dir = str(Path.home() / ".arenaagent" / "sessions")
        
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        self._current_session: Optional[Session] = None
        self.logger = get_logger(__name__)
    
    def create_session(
        self,
        session_id: Optional[str] = None,
        working_directory: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """Create a new session.
        
        Args:
            session_id: Optional session ID (auto-generated if None)
            working_directory: Working directory for session
            metadata: Additional session metadata
            
        Returns:
            New Session instance
        """
        session = Session(
            session_id=session_id,
            working_directory=working_directory,
            metadata=metadata,
        )
        
        # Create session directory
        session_dir = self._get_session_dir(session.session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save session
        self._save_session(session)
        self._current_session = session
        
        self.logger.info(f"Created new session: {session.session_id}")
        return session
    
    def load_session(self, session_id: str) -> Session:
        """Load an existing session.
        
        Args:
            session_id: ID of session to load
            
        Returns:
            Loaded Session instance
            
        Raises:
            FileNotFoundError: If session doesn't exist
            ValueError: If session data is invalid
        """
        session_dir = self._get_session_dir(session_id)
        session_file = session_dir / self.SESSION_FILENAME
        
        if not session_file.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session = Session.from_dict(data)
            self._current_session = session
            
            self.logger.info(f"Loaded session: {session_id}")
            return session
            
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid session data: {e}") from e
    
    def save_current_session(self) -> None:
        """Save the current session to disk.
        
        Raises:
            RuntimeError: If no current session exists
        """
        if self._current_session is None:
            raise RuntimeError("No current session to save")
        
        self._save_session(self._current_session)
        self.logger.debug(f"Saved session: {self._current_session.session_id}")
    
    def _save_session(self, session: Session) -> None:
        """Save session to disk.
        
        Args:
            session: Session to save
        """
        session_dir = self._get_session_dir(session.session_id)
        session_file = session_dir / self.SESSION_FILENAME
        
        # Update timestamp
        session.updated_at = datetime.now()
        
        # Atomic write
        temp_file = session_file.with_suffix('.tmp')
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2)
            
            temp_file.replace(session_file)
            
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise RuntimeError(f"Failed to save session: {e}") from e
    
    def get_current_session(self) -> Optional[Session]:
        """Get the current active session.
        
        Returns:
            Current Session instance or None if no session is active
        """
        return self._current_session
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions.
        
        Returns:
            List of session info dictionaries
        """
        sessions = []
        
        for session_dir in self.sessions_dir.iterdir():
            if not session_dir.is_dir():
                continue
            
            session_file = session_dir / self.SESSION_FILENAME
            if not session_file.exists():
                continue
            
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                sessions.append({
                    "session_id": data["session_id"],
                    "created_at": data["created_at"],
                    "updated_at": data["updated_at"],
                    "message_count": len(data["conversation"]["messages"]),
                    "working_directory": data.get("working_directory", ""),
                })
                
            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Skipping invalid session in {session_dir}: {e}")
                continue
        
        # Sort by updated_at (most recent first)
        sessions.sort(key=lambda s: s["updated_at"], reverse=True)
        
        return sessions
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session.
        
        Args:
            session_id: ID of session to delete
            
        Raises:
            FileNotFoundError: If session doesn't exist
        """
        session_dir = self._get_session_dir(session_id)
        
        if not session_dir.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")
        
        # Delete session directory and all contents
        import shutil
        shutil.rmtree(session_dir)
        
        # Clear current session if it was deleted
        if self._current_session and self._current_session.session_id == session_id:
            self._current_session = None
        
        self.logger.info(f"Deleted session: {session_id}")
    
    def resume_last_session(self) -> Optional[Session]:
        """Resume the most recently updated session.
        
        Returns:
            Resumed Session instance or None if no sessions exist
        """
        sessions = self.list_sessions()
        
        if not sessions:
            self.logger.info("No sessions to resume")
            return None
        
        # Load most recent session
        most_recent = sessions[0]
        session = self.load_session(most_recent["session_id"])
        
        self.logger.info(f"Resumed session: {session.session_id}")
        return session
    
    def add_message_to_current_session(self, message: Message) -> None:
        """Add message to current session.
        
        Args:
            message: Message to add
            
        Raises:
            RuntimeError: If no current session exists
        """
        if self._current_session is None:
            raise RuntimeError("No current session")
        
        self._current_session.add_message(message)
        self.save_current_session()
    
    def get_session_path(self, session_id: str) -> Path:
        """Get path to session directory.
        
        Args:
            session_id: Session ID
            
        Returns:
            Path to session directory
        """
        return self._get_session_dir(session_id)
    
    def _get_session_dir(self, session_id: str) -> Path:
        """Get session directory path.
        
        Args:
            session_id: Session ID
            
        Returns:
            Path to session directory
        """
        return self.sessions_dir / session_id
    
    def export_session(self, session_id: str, export_path: str) -> None:
        """Export session to a file.
        
        Args:
            session_id: Session ID to export
            export_path: Path to export file
        """
        session = self.load_session(session_id)
        
        export_data = session.to_dict()
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Exported session {session_id} to {export_path}")
    
    def import_session(self, import_path: str) -> Session:
        """Import session from a file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            Imported Session instance
        """
        with open(import_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        session = Session.from_dict(data)
        
        # Save imported session
        self._save_session(session)
        self._current_session = session
        
        self.logger.info(f"Imported session: {session.session_id}")
        return session

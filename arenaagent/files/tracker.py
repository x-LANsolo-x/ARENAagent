"""File tracking and monitoring for ArenaAgent."""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import difflib
import json

from arenaagent.models.code_change import CodeChange, ChangeType
from arenaagent.utils.logger import get_logger
from arenaagent.utils.file_helpers import read_file_safe


class FileTracker:
    """Tracks file modifications and changes."""
    
    def __init__(self, working_directory: Optional[str] = None):
        """Initialize file tracker.
        
        Args:
            working_directory: Directory to track files in (default: current directory)
        """
        self.working_directory = Path(working_directory) if working_directory else Path.cwd()
        self.logger = get_logger(__name__)
        self._tracked_files: Dict[str, Dict] = {}
        self._snapshots: Dict[str, str] = {}  # Store original file content
    
    def track_file(self, file_path: str) -> None:
        """Start tracking a file.
        
        Args:
            file_path: Path to file to track
        """
        path = Path(file_path)
        
        if not path.exists():
            self.logger.warning(f"File does not exist: {file_path}")
            return
        
        # Read original content
        original_content = read_file_safe(path)
        
        # Calculate file hash
        file_hash = self._calculate_hash(path)
        
        # Store file info
        abs_path = str(path.resolve())
        self._tracked_files[abs_path] = {
            'path': abs_path,
            'original_hash': file_hash,
            'current_hash': file_hash,
            'tracked_at': datetime.now(),
            'modified': False,
            'size': path.stat().st_size if path.exists() else 0,
        }
        
        # Store snapshot
        self._snapshots[abs_path] = original_content
        
        self.logger.info(f"Now tracking: {file_path}")
    
    def untrack_file(self, file_path: str) -> None:
        """Stop tracking a file.
        
        Args:
            file_path: Path to file to stop tracking
        """
        abs_path = str(Path(file_path).resolve())
        
        if abs_path in self._tracked_files:
            del self._tracked_files[abs_path]
            if abs_path in self._snapshots:
                del self._snapshots[abs_path]
            self.logger.info(f"Stopped tracking: {file_path}")
    
    def is_tracked(self, file_path: str) -> bool:
        """Check if a file is being tracked.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is tracked
        """
        abs_path = str(Path(file_path).resolve())
        return abs_path in self._tracked_files
    
    def is_modified(self, file_path: str) -> bool:
        """Check if a tracked file has been modified.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is modified, False otherwise
        """
        abs_path = str(Path(file_path).resolve())
        
        if abs_path not in self._tracked_files:
            return False
        
        path = Path(file_path)
        
        # File was deleted
        if not path.exists():
            return True
        
        # Compare hashes
        current_hash = self._calculate_hash(path)
        original_hash = self._tracked_files[abs_path]['original_hash']
        
        is_modified = current_hash != original_hash
        self._tracked_files[abs_path]['modified'] = is_modified
        self._tracked_files[abs_path]['current_hash'] = current_hash
        
        return is_modified
    
    def get_tracked_files(self) -> List[str]:
        """Get list of all tracked files.
        
        Returns:
            List of tracked file paths
        """
        return list(self._tracked_files.keys())
    
    def get_modified_files(self) -> List[str]:
        """Get list of modified tracked files.
        
        Returns:
            List of file paths that have been modified
        """
        modified = []
        
        for file_path in self._tracked_files:
            if self.is_modified(file_path):
                modified.append(file_path)
        
        return modified
    
    def get_diff(self, file_path: str, context_lines: int = 3) -> Optional[str]:
        """Get unified diff for a modified file.
        
        Args:
            file_path: Path to file
            context_lines: Number of context lines in diff
            
        Returns:
            Unified diff string, or None if not modified
        """
        abs_path = str(Path(file_path).resolve())
        
        if abs_path not in self._tracked_files:
            self.logger.warning(f"File not tracked: {file_path}")
            return None
        
        if not self.is_modified(file_path):
            return None
        
        # Get original and current content
        original_content = self._snapshots.get(abs_path, "")
        
        path = Path(file_path)
        if path.exists():
            current_content = read_file_safe(path)
        else:
            current_content = ""  # File was deleted
        
        # Generate diff
        original_lines = original_content.splitlines(keepends=True)
        current_lines = current_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            current_lines,
            fromfile=f"a/{path.name}",
            tofile=f"b/{path.name}",
            n=context_lines
        )
        
        return ''.join(diff)
    
    def get_change(self, file_path: str) -> Optional[CodeChange]:
        """Get CodeChange object for a modified file.
        
        Args:
            file_path: Path to file
            
        Returns:
            CodeChange object, or None if not modified
        """
        abs_path = str(Path(file_path).resolve())
        
        if abs_path not in self._tracked_files:
            return None
        
        if not self.is_modified(file_path):
            return None
        
        path = Path(file_path)
        original_content = self._snapshots.get(abs_path, "")
        
        # Determine change type
        if not path.exists():
            change_type = ChangeType.DELETE
            current_content = ""
        elif not original_content:
            change_type = ChangeType.CREATE
            current_content = read_file_safe(path)
        else:
            change_type = ChangeType.MODIFY
            current_content = read_file_safe(path)
        
        return CodeChange(
            file_path=str(path),
            change_type=change_type,
            before_content=original_content,
            after_content=current_content,
        )
    
    def get_all_changes(self) -> List[CodeChange]:
        """Get CodeChange objects for all modified files.
        
        Returns:
            List of CodeChange objects
        """
        changes = []
        
        for file_path in self.get_modified_files():
            change = self.get_change(file_path)
            if change:
                changes.append(change)
        
        return changes
    
    def update_snapshot(self, file_path: str) -> None:
        """Update the snapshot for a tracked file.
        
        This marks the current state as the new baseline.
        
        Args:
            file_path: Path to file
        """
        abs_path = str(Path(file_path).resolve())
        
        if abs_path not in self._tracked_files:
            self.logger.warning(f"File not tracked: {file_path}")
            return
        
        path = Path(file_path)
        
        if not path.exists():
            self.logger.warning(f"File does not exist: {file_path}")
            return
        
        # Update snapshot
        current_content = read_file_safe(path)
        self._snapshots[abs_path] = current_content
        
        # Update hash
        current_hash = self._calculate_hash(path)
        self._tracked_files[abs_path]['original_hash'] = current_hash
        self._tracked_files[abs_path]['current_hash'] = current_hash
        self._tracked_files[abs_path]['modified'] = False
        
        self.logger.info(f"Updated snapshot for: {file_path}")
    
    def reset_file(self, file_path: str) -> bool:
        """Reset a file to its original tracked state.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if reset successful, False otherwise
        """
        abs_path = str(Path(file_path).resolve())
        
        if abs_path not in self._tracked_files:
            self.logger.warning(f"File not tracked: {file_path}")
            return False
        
        if abs_path not in self._snapshots:
            self.logger.error(f"No snapshot available for: {file_path}")
            return False
        
        try:
            path = Path(file_path)
            original_content = self._snapshots[abs_path]
            
            # Write original content back
            path.write_text(original_content, encoding='utf-8')
            
            # Update tracking info
            self._tracked_files[abs_path]['current_hash'] = self._tracked_files[abs_path]['original_hash']
            self._tracked_files[abs_path]['modified'] = False
            
            self.logger.info(f"Reset file to original state: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset file {file_path}: {e}")
            return False
    
    def clear(self) -> None:
        """Clear all tracked files."""
        self._tracked_files.clear()
        self._snapshots.clear()
        self.logger.info("Cleared all tracked files")
    
    def get_stats(self) -> Dict:
        """Get statistics about tracked files.
        
        Returns:
            Dictionary with tracking statistics
        """
        total_files = len(self._tracked_files)
        modified_files = len(self.get_modified_files())
        
        return {
            'total_tracked': total_files,
            'modified': modified_files,
            'unmodified': total_files - modified_files,
        }
    
    def export_state(self) -> Dict:
        """Export tracker state to dictionary.
        
        Returns:
            Dictionary representation of tracker state
        """
        return {
            'working_directory': str(self.working_directory),
            'tracked_files': {
                path: {
                    **info,
                    'tracked_at': info['tracked_at'].isoformat()
                }
                for path, info in self._tracked_files.items()
            },
            'snapshots': self._snapshots,
        }
    
    def import_state(self, state: Dict) -> None:
        """Import tracker state from dictionary.
        
        Args:
            state: Dictionary representation of tracker state
        """
        self.working_directory = Path(state['working_directory'])
        
        self._tracked_files = {
            path: {
                **info,
                'tracked_at': datetime.fromisoformat(info['tracked_at'])
            }
            for path, info in state['tracked_files'].items()
        }
        
        self._snapshots = state['snapshots']
        
        self.logger.info(f"Imported tracker state with {len(self._tracked_files)} files")
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of file hash
        """
        sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""

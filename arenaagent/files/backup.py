"""File backup management for ArenaAgent."""

from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import shutil
import json

from arenaagent.utils.logger import get_logger
from arenaagent.utils.file_helpers import ensure_directory, get_file_info


class BackupManager:
    """Manages file backups with versioning and restoration."""
    
    def __init__(self, backup_dir: Optional[str] = None):
        """Initialize backup manager.
        
        Args:
            backup_dir: Directory to store backups (default: ~/.arenaagent/backups)
        """
        if backup_dir:
            self.backup_dir = Path(backup_dir)
        else:
            self.backup_dir = Path.home() / ".arenaagent" / "backups"
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)
        self._metadata_file = self.backup_dir / "backup_metadata.json"
        self._metadata: Dict = self._load_metadata()
    
    def create_backup(self, file_path: str, label: Optional[str] = None) -> Optional[str]:
        """Create a backup of a file.
        
        Args:
            file_path: Path to file to backup
            label: Optional label for the backup
            
        Returns:
            Path to backup file, or None if backup failed
        """
        source_path = Path(file_path)
        
        if not source_path.exists():
            self.logger.error(f"Cannot backup non-existent file: {file_path}")
            return None
        
        try:
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.name}.{timestamp}.backup"
            
            # Create subdirectory based on original file path
            # This helps organize backups for files from different locations
            rel_dir = self._get_backup_subdir(source_path)
            backup_subdir = self.backup_dir / rel_dir
            backup_subdir.mkdir(parents=True, exist_ok=True)
            
            backup_path = backup_subdir / backup_name
            
            # Copy file to backup location
            shutil.copy2(source_path, backup_path)
            
            # Store metadata
            self._add_backup_metadata(
                source_path=str(source_path.resolve()),
                backup_path=str(backup_path),
                timestamp=datetime.now(),
                label=label
            )
            
            self.logger.info(f"Created backup: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create backup for {file_path}: {e}")
            return None
    
    def restore_backup(self, backup_path: str, restore_to: Optional[str] = None) -> bool:
        """Restore a file from backup.
        
        Args:
            backup_path: Path to backup file
            restore_to: Optional path to restore to (default: original location)
            
        Returns:
            True if restore successful, False otherwise
        """
        backup = Path(backup_path)
        
        if not backup.exists():
            self.logger.error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            # Get original file path from metadata
            metadata = self._get_backup_metadata(backup_path)
            
            if restore_to:
                target_path = Path(restore_to)
            elif metadata and 'source_path' in metadata:
                target_path = Path(metadata['source_path'])
            else:
                self.logger.error(f"Cannot determine restore location for {backup_path}")
                return False
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy backup to target location
            shutil.copy2(backup, target_path)
            
            self.logger.info(f"Restored backup from {backup_path} to {target_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore backup {backup_path}: {e}")
            return False
    
    def list_backups(self, file_path: Optional[str] = None) -> List[Dict]:
        """List all backups, optionally filtered by source file.
        
        Args:
            file_path: Optional source file path to filter by
            
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        for backup_path, metadata in self._metadata.items():
            if file_path:
                source_path = Path(file_path).resolve()
                if Path(metadata.get('source_path', '')).resolve() != source_path:
                    continue
            
            backups.append({
                'backup_path': backup_path,
                'source_path': metadata.get('source_path'),
                'timestamp': metadata.get('timestamp'),
                'label': metadata.get('label'),
                'size': Path(backup_path).stat().st_size if Path(backup_path).exists() else 0,
            })
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return backups
    
    def get_latest_backup(self, file_path: str) -> Optional[str]:
        """Get the most recent backup for a file.
        
        Args:
            file_path: Source file path
            
        Returns:
            Path to latest backup, or None if no backups exist
        """
        backups = self.list_backups(file_path)
        
        if backups:
            return backups[0]['backup_path']
        
        return None
    
    def delete_backup(self, backup_path: str) -> bool:
        """Delete a backup file.
        
        Args:
            backup_path: Path to backup file to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        backup = Path(backup_path)
        
        try:
            if backup.exists():
                backup.unlink()
            
            # Remove from metadata
            if backup_path in self._metadata:
                del self._metadata[backup_path]
                self._save_metadata()
            
            self.logger.info(f"Deleted backup: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete backup {backup_path}: {e}")
            return False
    
    def cleanup_old_backups(self, file_path: str, keep_count: int = 5) -> int:
        """Delete old backups for a file, keeping only the most recent ones.
        
        Args:
            file_path: Source file path
            keep_count: Number of recent backups to keep
            
        Returns:
            Number of backups deleted
        """
        backups = self.list_backups(file_path)
        
        if len(backups) <= keep_count:
            return 0
        
        deleted_count = 0
        
        # Delete old backups (keep the most recent keep_count backups)
        for backup in backups[keep_count:]:
            if self.delete_backup(backup['backup_path']):
                deleted_count += 1
        
        self.logger.info(f"Cleaned up {deleted_count} old backups for {file_path}")
        return deleted_count
    
    def cleanup_all_old_backups(self, keep_count: int = 5) -> int:
        """Delete old backups for all files.
        
        Args:
            keep_count: Number of recent backups to keep per file
            
        Returns:
            Total number of backups deleted
        """
        # Group backups by source file
        files_with_backups = set()
        for metadata in self._metadata.values():
            if 'source_path' in metadata:
                files_with_backups.add(metadata['source_path'])
        
        total_deleted = 0
        
        for file_path in files_with_backups:
            deleted = self.cleanup_old_backups(file_path, keep_count)
            total_deleted += deleted
        
        return total_deleted
    
    def verify_backup(self, backup_path: str) -> bool:
        """Verify that a backup file exists and is readable.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if backup is valid, False otherwise
        """
        backup = Path(backup_path)
        
        if not backup.exists():
            self.logger.warning(f"Backup does not exist: {backup_path}")
            return False
        
        if not backup.is_file():
            self.logger.warning(f"Backup is not a file: {backup_path}")
            return False
        
        try:
            # Try to read a small portion to verify accessibility
            with open(backup, 'rb') as f:
                f.read(1024)
            return True
        except Exception as e:
            self.logger.error(f"Backup verification failed for {backup_path}: {e}")
            return False
    
    def get_backup_stats(self) -> Dict:
        """Get statistics about backups.
        
        Returns:
            Dictionary with backup statistics
        """
        total_backups = len(self._metadata)
        total_size = 0
        
        for backup_path in self._metadata:
            path = Path(backup_path)
            if path.exists():
                total_size += path.stat().st_size
        
        # Count unique source files
        source_files = set()
        for metadata in self._metadata.values():
            if 'source_path' in metadata:
                source_files.add(metadata['source_path'])
        
        return {
            'total_backups': total_backups,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'unique_files': len(source_files),
        }
    
    def export_metadata(self) -> Dict:
        """Export backup metadata.
        
        Returns:
            Dictionary with all backup metadata
        """
        return self._metadata.copy()
    
    def _get_backup_subdir(self, source_path: Path) -> str:
        """Generate a subdirectory name for organizing backups.
        
        Args:
            source_path: Original file path
            
        Returns:
            Subdirectory name
        """
        # Use a hash of the parent directory to create unique subdirs
        parent_str = str(source_path.parent.resolve())
        
        # Simple approach: use the last part of the parent path
        # This keeps backups somewhat organized by location
        return source_path.parent.name or "root"
    
    def _add_backup_metadata(
        self,
        source_path: str,
        backup_path: str,
        timestamp: datetime,
        label: Optional[str] = None
    ) -> None:
        """Add metadata for a backup.
        
        Args:
            source_path: Original file path
            backup_path: Backup file path
            timestamp: Backup creation time
            label: Optional backup label
        """
        self._metadata[backup_path] = {
            'source_path': source_path,
            'backup_path': backup_path,
            'timestamp': timestamp.isoformat(),
            'label': label,
        }
        
        self._save_metadata()
    
    def _get_backup_metadata(self, backup_path: str) -> Optional[Dict]:
        """Get metadata for a specific backup.
        
        Args:
            backup_path: Backup file path
            
        Returns:
            Metadata dictionary, or None if not found
        """
        return self._metadata.get(backup_path)
    
    def _load_metadata(self) -> Dict:
        """Load backup metadata from file.
        
        Returns:
            Metadata dictionary
        """
        if not self._metadata_file.exists():
            return {}
        
        try:
            with open(self._metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load backup metadata: {e}")
            return {}
    
    def _save_metadata(self) -> None:
        """Save backup metadata to file."""
        try:
            with open(self._metadata_file, 'w') as f:
                json.dump(self._metadata, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save backup metadata: {e}")

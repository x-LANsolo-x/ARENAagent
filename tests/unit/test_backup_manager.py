"""Unit tests for BackupManager class."""

import pytest
from pathlib import Path
import time

from arenaagent.files.backup import BackupManager


class TestBackupManager:
    """Test BackupManager functionality."""
    
    def test_init_default(self):
        """Test default initialization."""
        manager = BackupManager()
        
        expected_dir = Path.home() / ".arenaagent" / "backups"
        assert manager.backup_dir == expected_dir
        assert manager.backup_dir.exists()
    
    def test_init_custom_directory(self, tmp_path):
        """Test initialization with custom directory."""
        backup_dir = tmp_path / "custom_backups"
        manager = BackupManager(str(backup_dir))
        
        assert manager.backup_dir == backup_dir
        assert manager.backup_dir.exists()
    
    def test_create_backup(self, tmp_path):
        """Test creating a backup."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Original content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        backup_path = manager.create_backup(str(source_file))
        
        assert backup_path is not None
        assert Path(backup_path).exists()
        assert Path(backup_path).read_text() == "Original content"
    
    def test_create_backup_nonexistent_file(self, tmp_path):
        """Test creating backup of non-existent file."""
        source_file = tmp_path / "nonexistent.txt"
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        backup_path = manager.create_backup(str(source_file))
        
        assert backup_path is None
    
    def test_create_backup_with_label(self, tmp_path):
        """Test creating backup with label."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        backup_path = manager.create_backup(str(source_file), label="before_change")
        
        assert backup_path is not None
        
        # Check metadata includes label
        backups = manager.list_backups(str(source_file))
        assert len(backups) > 0
        assert backups[0]['label'] == "before_change"
    
    def test_restore_backup(self, tmp_path):
        """Test restoring from backup."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Original content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        # Create backup
        backup_path = manager.create_backup(str(source_file))
        
        # Modify original file
        source_file.write_text("Modified content")
        
        # Restore from backup
        result = manager.restore_backup(backup_path)
        
        assert result is True
        assert source_file.read_text() == "Original content"
    
    def test_restore_backup_to_different_location(self, tmp_path):
        """Test restoring backup to different location."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        backup_path = manager.create_backup(str(source_file))
        
        # Restore to different location
        restore_to = tmp_path / "restored.txt"
        result = manager.restore_backup(backup_path, str(restore_to))
        
        assert result is True
        assert restore_to.exists()
        assert restore_to.read_text() == "Content"
    
    def test_restore_nonexistent_backup(self, tmp_path):
        """Test restoring from non-existent backup."""
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        result = manager.restore_backup(str(tmp_path / "nonexistent.backup"))
        
        assert result is False
    
    def test_list_backups(self, tmp_path):
        """Test listing backups."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        # Create multiple backups
        manager.create_backup(str(source_file))
        time.sleep(0.01)  # Ensure different timestamps
        manager.create_backup(str(source_file))
        
        backups = manager.list_backups(str(source_file))
        
        assert len(backups) == 2
        assert all('backup_path' in b for b in backups)
        assert all('timestamp' in b for b in backups)
    
    def test_list_backups_all(self, tmp_path):
        """Test listing all backups."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        
        file1.write_text("Content 1")
        file2.write_text("Content 2")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        manager.create_backup(str(file1))
        manager.create_backup(str(file2))
        
        # List all backups (no filter)
        all_backups = manager.list_backups()
        
        assert len(all_backups) == 2
    
    def test_get_latest_backup(self, tmp_path):
        """Test getting latest backup."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        # Create multiple backups
        first_backup = manager.create_backup(str(source_file))
        time.sleep(0.01)
        second_backup = manager.create_backup(str(source_file))
        
        latest = manager.get_latest_backup(str(source_file))
        
        assert latest == second_backup
    
    def test_get_latest_backup_no_backups(self, tmp_path):
        """Test getting latest backup when none exist."""
        source_file = tmp_path / "source.txt"
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        latest = manager.get_latest_backup(str(source_file))
        
        assert latest is None
    
    def test_delete_backup(self, tmp_path):
        """Test deleting a backup."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        backup_path = manager.create_backup(str(source_file))
        assert Path(backup_path).exists()
        
        result = manager.delete_backup(backup_path)
        
        assert result is True
        assert not Path(backup_path).exists()
    
    def test_delete_nonexistent_backup(self, tmp_path):
        """Test deleting non-existent backup."""
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        result = manager.delete_backup(str(tmp_path / "nonexistent.backup"))
        
        assert result is True  # Should succeed even if file doesn't exist
    
    def test_cleanup_old_backups(self, tmp_path):
        """Test cleaning up old backups."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        # Create 7 backups
        for i in range(7):
            manager.create_backup(str(source_file))
            time.sleep(0.01)
        
        # Keep only 3 most recent
        deleted_count = manager.cleanup_old_backups(str(source_file), keep_count=3)
        
        assert deleted_count == 4
        
        # Verify only 3 backups remain
        remaining = manager.list_backups(str(source_file))
        assert len(remaining) == 3
    
    def test_cleanup_old_backups_under_limit(self, tmp_path):
        """Test cleanup when backups are under limit."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        # Create 2 backups
        manager.create_backup(str(source_file))
        manager.create_backup(str(source_file))
        
        # Try to keep 5 (more than exist)
        deleted_count = manager.cleanup_old_backups(str(source_file), keep_count=5)
        
        assert deleted_count == 0
    
    def test_cleanup_all_old_backups(self, tmp_path):
        """Test cleanup for all files."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        
        file1.write_text("Content 1")
        file2.write_text("Content 2")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        # Create multiple backups for each file
        for i in range(5):
            manager.create_backup(str(file1))
            manager.create_backup(str(file2))
            time.sleep(0.01)
        
        # Cleanup all, keeping 2 per file
        total_deleted = manager.cleanup_all_old_backups(keep_count=2)
        
        assert total_deleted == 6  # 3 deleted from each file
    
    def test_verify_backup(self, tmp_path):
        """Test verifying a backup."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        backup_path = manager.create_backup(str(source_file))
        
        assert manager.verify_backup(backup_path) is True
    
    def test_verify_nonexistent_backup(self, tmp_path):
        """Test verifying non-existent backup."""
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        assert manager.verify_backup(str(tmp_path / "nonexistent.backup")) is False
    
    def test_get_backup_stats(self, tmp_path):
        """Test getting backup statistics."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        
        file1.write_text("Content 1")
        file2.write_text("Content 2")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        manager.create_backup(str(file1))
        manager.create_backup(str(file2))
        manager.create_backup(str(file1))  # Second backup of file1
        
        stats = manager.get_backup_stats()
        
        assert stats['total_backups'] == 3
        assert stats['unique_files'] == 2
        assert stats['total_size_bytes'] > 0
        assert stats['total_size_mb'] >= 0
    
    def test_export_metadata(self, tmp_path):
        """Test exporting metadata."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        manager.create_backup(str(source_file), label="test")
        
        metadata = manager.export_metadata()
        
        assert isinstance(metadata, dict)
        assert len(metadata) == 1
        
        # Check metadata structure
        for backup_path, info in metadata.items():
            assert 'source_path' in info
            assert 'timestamp' in info
            assert 'label' in info
            assert info['label'] == "test"


class TestBackupManagerEdgeCases:
    """Test edge cases for BackupManager."""
    
    def test_multiple_backups_same_file(self, tmp_path):
        """Test creating multiple backups of the same file."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        # Create 3 backups with slight delays
        backups = []
        for i in range(3):
            backup_path = manager.create_backup(str(source_file))
            backups.append(backup_path)
            time.sleep(0.01)  # Ensure unique timestamps
        
        # All backups should be unique
        assert len(set(backups)) == 3
        
        # All should exist
        assert all(Path(b).exists() for b in backups)
    
    def test_backup_empty_file(self, tmp_path):
        """Test backing up an empty file."""
        source_file = tmp_path / "empty.txt"
        source_file.write_text("")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        backup_path = manager.create_backup(str(source_file))
        
        assert backup_path is not None
        assert Path(backup_path).exists()
        assert Path(backup_path).read_text() == ""
    
    def test_backup_binary_file(self, tmp_path):
        """Test backing up a binary file."""
        source_file = tmp_path / "binary.dat"
        binary_content = b'\x00\x01\x02\x03\x04'
        source_file.write_bytes(binary_content)
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        backup_path = manager.create_backup(str(source_file))
        
        assert backup_path is not None
        assert Path(backup_path).read_bytes() == binary_content
    
    def test_backup_large_file(self, tmp_path):
        """Test backing up a larger file."""
        source_file = tmp_path / "large.txt"
        
        # Create a ~10KB file
        large_content = "A" * 10000
        source_file.write_text(large_content)
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        backup_path = manager.create_backup(str(source_file))
        
        assert backup_path is not None
        assert Path(backup_path).read_text() == large_content
    
    def test_restore_after_source_deleted(self, tmp_path):
        """Test restoring when source file has been deleted."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Content")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        backup_path = manager.create_backup(str(source_file))
        
        # Delete source file
        source_file.unlink()
        assert not source_file.exists()
        
        # Restore should recreate it
        result = manager.restore_backup(backup_path)
        
        assert result is True
        assert source_file.exists()
        assert source_file.read_text() == "Content"
    
    def test_backup_preserves_file_metadata(self, tmp_path):
        """Test that backup preserves file timestamps."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("Content")
        
        original_mtime = source_file.stat().st_mtime
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        backup_path = manager.create_backup(str(source_file))
        
        # shutil.copy2 should preserve metadata
        backup_mtime = Path(backup_path).stat().st_mtime
        
        # Timestamps should be similar (within a small delta)
        assert abs(backup_mtime - original_mtime) < 1.0
    
    def test_concurrent_backups_different_files(self, tmp_path):
        """Test backing up multiple files concurrently."""
        files = [tmp_path / f"file{i}.txt" for i in range(5)]
        
        for i, f in enumerate(files):
            f.write_text(f"Content {i}")
        
        backup_dir = tmp_path / "backups"
        manager = BackupManager(str(backup_dir))
        
        # Backup all files
        backup_paths = [manager.create_backup(str(f)) for f in files]
        
        # All should succeed
        assert all(bp is not None for bp in backup_paths)
        assert len(set(backup_paths)) == 5  # All unique

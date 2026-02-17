"""Unit tests for file helpers utility module."""

import pytest
from pathlib import Path
from datetime import datetime
import time

from arenaagent.utils.file_helpers import (
    atomic_write,
    safe_delete,
    ensure_directory,
    get_file_size,
    copy_with_backup,
    read_file_safe,
    write_file_safe,
    list_files,
    get_file_info,
    create_backup,
    clean_old_backups,
    is_empty_directory,
    get_unique_filename,
)


class TestAtomicWrite:
    """Test atomic file writing."""
    
    def test_write_new_file(self, tmp_path):
        """Test writing a new file atomically."""
        file_path = tmp_path / "test.txt"
        content = "Test content"
        
        atomic_write(file_path, content)
        
        assert file_path.exists()
        assert file_path.read_text() == content
    
    def test_overwrite_existing_file(self, tmp_path):
        """Test overwriting existing file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Old content")
        
        atomic_write(file_path, "New content")
        
        assert file_path.read_text() == "New content"
    
    def test_create_parent_directories(self, tmp_path):
        """Test that parent directories are created."""
        file_path = tmp_path / "subdir" / "nested" / "test.txt"
        
        atomic_write(file_path, "Content")
        
        assert file_path.exists()
        assert file_path.read_text() == "Content"
    
    def test_unicode_content(self, tmp_path):
        """Test writing Unicode content."""
        file_path = tmp_path / "unicode.txt"
        content = "Hello 世界 🌍"
        
        atomic_write(file_path, content)
        
        assert file_path.read_text() == content


class TestSafeDelete:
    """Test safe file deletion."""
    
    def test_delete_existing_file(self, tmp_path):
        """Test deleting an existing file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Content")
        
        result = safe_delete(file_path)
        
        assert result is True
        assert not file_path.exists()
    
    def test_delete_nonexistent_file(self, tmp_path):
        """Test deleting a non-existent file."""
        file_path = tmp_path / "nonexistent.txt"
        
        result = safe_delete(file_path)
        
        assert result is False
    
    def test_delete_with_permission_error(self, tmp_path):
        """Test handling permission errors gracefully."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Content")
        
        # Make file read-only (on Unix)
        file_path.chmod(0o444)
        
        # Should return False on permission error
        result = safe_delete(file_path)
        
        # Clean up: restore permissions
        file_path.chmod(0o644)
        file_path.unlink()


class TestEnsureDirectory:
    """Test directory creation."""
    
    def test_create_new_directory(self, tmp_path):
        """Test creating a new directory."""
        dir_path = tmp_path / "newdir"
        
        ensure_directory(dir_path)
        
        assert dir_path.exists()
        assert dir_path.is_dir()
    
    def test_create_nested_directories(self, tmp_path):
        """Test creating nested directories."""
        dir_path = tmp_path / "level1" / "level2" / "level3"
        
        ensure_directory(dir_path)
        
        assert dir_path.exists()
        assert dir_path.is_dir()
    
    def test_existing_directory(self, tmp_path):
        """Test with existing directory."""
        dir_path = tmp_path / "existing"
        dir_path.mkdir()
        
        # Should not raise error
        ensure_directory(dir_path)
        
        assert dir_path.exists()


class TestGetFileSize:
    """Test getting file size."""
    
    def test_get_size_of_file(self, tmp_path):
        """Test getting size of existing file."""
        file_path = tmp_path / "test.txt"
        content = "Hello World"
        file_path.write_text(content)
        
        size = get_file_size(file_path)
        
        assert size == len(content.encode('utf-8'))
    
    def test_get_size_of_empty_file(self, tmp_path):
        """Test getting size of empty file."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")
        
        size = get_file_size(file_path)
        
        assert size == 0
    
    def test_get_size_of_nonexistent_file(self, tmp_path):
        """Test getting size of non-existent file."""
        file_path = tmp_path / "nonexistent.txt"
        
        size = get_file_size(file_path)
        
        assert size == 0


class TestCopyWithBackup:
    """Test copying with backup."""
    
    def test_copy_to_new_location(self, tmp_path):
        """Test copying to new location (no backup needed)."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "dest.txt"
        src.write_text("Source content")
        
        backup = copy_with_backup(src, dst)
        
        assert dst.exists()
        assert dst.read_text() == "Source content"
        assert backup is None
    
    def test_copy_with_existing_destination(self, tmp_path):
        """Test copying when destination exists (backup created)."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "dest.txt"
        src.write_text("New content")
        dst.write_text("Old content")
        
        backup = copy_with_backup(src, dst)
        
        assert dst.read_text() == "New content"
        assert backup is not None
        assert backup.exists()
        assert backup.read_text() == "Old content"


class TestReadFileSafe:
    """Test safe file reading."""
    
    def test_read_existing_file(self, tmp_path):
        """Test reading existing file."""
        file_path = tmp_path / "test.txt"
        content = "Test content"
        file_path.write_text(content)
        
        result = read_file_safe(file_path)
        
        assert result == content
    
    def test_read_nonexistent_file(self, tmp_path):
        """Test reading non-existent file returns default."""
        file_path = tmp_path / "nonexistent.txt"
        
        result = read_file_safe(file_path, default="DEFAULT")
        
        assert result == "DEFAULT"
    
    def test_read_with_encoding(self, tmp_path):
        """Test reading with specific encoding."""
        file_path = tmp_path / "unicode.txt"
        content = "Hello 世界"
        file_path.write_text(content, encoding='utf-8')
        
        result = read_file_safe(file_path, encoding='utf-8')
        
        assert result == content


class TestWriteFileSafe:
    """Test safe file writing."""
    
    def test_write_new_file(self, tmp_path):
        """Test writing new file."""
        file_path = tmp_path / "test.txt"
        
        result = write_file_safe(file_path, "Content")
        
        assert result is True
        assert file_path.read_text() == "Content"
    
    def test_write_with_directory_creation(self, tmp_path):
        """Test writing with automatic directory creation."""
        file_path = tmp_path / "subdir" / "test.txt"
        
        result = write_file_safe(file_path, "Content", create_dirs=True)
        
        assert result is True
        assert file_path.exists()
    
    def test_write_without_directory_creation(self, tmp_path):
        """Test writing without directory creation fails."""
        file_path = tmp_path / "nonexistent" / "test.txt"
        
        result = write_file_safe(file_path, "Content", create_dirs=False)
        
        assert result is False


class TestListFiles:
    """Test listing files."""
    
    def test_list_all_files(self, tmp_path):
        """Test listing all files in directory."""
        (tmp_path / "file1.txt").write_text("1")
        (tmp_path / "file2.txt").write_text("2")
        (tmp_path / "file3.py").write_text("3")
        
        files = list_files(tmp_path)
        
        assert len(files) == 3
    
    def test_list_with_pattern(self, tmp_path):
        """Test listing files with glob pattern."""
        (tmp_path / "file1.txt").write_text("1")
        (tmp_path / "file2.txt").write_text("2")
        (tmp_path / "file3.py").write_text("3")
        
        files = list_files(tmp_path, pattern="*.txt")
        
        assert len(files) == 2
    
    def test_list_recursive(self, tmp_path):
        """Test recursive file listing."""
        (tmp_path / "file1.txt").write_text("1")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file2.txt").write_text("2")
        
        files = list_files(tmp_path, pattern="*.txt", recursive=True)
        
        assert len(files) == 2
    
    def test_list_nonexistent_directory(self, tmp_path):
        """Test listing non-existent directory."""
        files = list_files(tmp_path / "nonexistent")
        
        assert files == []


class TestGetFileInfo:
    """Test getting file information."""
    
    def test_get_info_existing_file(self, tmp_path):
        """Test getting info for existing file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Content")
        
        info = get_file_info(file_path)
        
        assert info['exists'] is True
        assert info['is_file'] is True
        assert info['is_dir'] is False
        assert info['size'] > 0
        assert isinstance(info['created'], datetime)
        assert isinstance(info['modified'], datetime)
    
    def test_get_info_directory(self, tmp_path):
        """Test getting info for directory."""
        dir_path = tmp_path / "testdir"
        dir_path.mkdir()
        
        info = get_file_info(dir_path)
        
        assert info['exists'] is True
        assert info['is_file'] is False
        assert info['is_dir'] is True
    
    def test_get_info_nonexistent(self, tmp_path):
        """Test getting info for non-existent file."""
        file_path = tmp_path / "nonexistent.txt"
        
        info = get_file_info(file_path)
        
        assert info['exists'] is False


class TestCreateBackup:
    """Test backup creation."""
    
    def test_create_backup_default_location(self, tmp_path):
        """Test creating backup in same directory."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Original")
        
        backup_path = create_backup(file_path)
        
        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.read_text() == "Original"
        assert ".backup." in str(backup_path)
    
    def test_create_backup_custom_location(self, tmp_path):
        """Test creating backup in custom directory."""
        file_path = tmp_path / "test.txt"
        backup_dir = tmp_path / "backups"
        file_path.write_text("Original")
        
        backup_path = create_backup(file_path, backup_dir)
        
        assert backup_path is not None
        assert backup_path.parent == backup_dir
        assert backup_path.read_text() == "Original"
    
    def test_create_backup_nonexistent_file(self, tmp_path):
        """Test creating backup of non-existent file."""
        file_path = tmp_path / "nonexistent.txt"
        
        backup_path = create_backup(file_path)
        
        assert backup_path is None


class TestCleanOldBackups:
    """Test cleaning old backups."""
    
    def test_clean_old_backups(self, tmp_path):
        """Test cleaning old backup files."""
        # Create multiple backup files with delays to ensure different timestamps
        for i in range(7):
            backup = tmp_path / f"file.backup.{i}"
            backup.write_text(f"Backup {i}")
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        deleted = clean_old_backups(tmp_path, pattern="*.backup.*", keep_count=3)
        
        assert deleted == 4
        remaining = list(tmp_path.glob("*.backup.*"))
        assert len(remaining) == 3
    
    def test_clean_with_fewer_backups_than_keep_count(self, tmp_path):
        """Test cleaning when fewer backups exist than keep_count."""
        (tmp_path / "file.backup.1").write_text("1")
        (tmp_path / "file.backup.2").write_text("2")
        
        deleted = clean_old_backups(tmp_path, keep_count=5)
        
        assert deleted == 0
    
    def test_clean_nonexistent_directory(self, tmp_path):
        """Test cleaning in non-existent directory."""
        deleted = clean_old_backups(tmp_path / "nonexistent")
        
        assert deleted == 0


class TestIsEmptyDirectory:
    """Test checking if directory is empty."""
    
    def test_empty_directory(self, tmp_path):
        """Test with empty directory."""
        dir_path = tmp_path / "empty"
        dir_path.mkdir()
        
        assert is_empty_directory(dir_path) is True
    
    def test_non_empty_directory(self, tmp_path):
        """Test with non-empty directory."""
        dir_path = tmp_path / "nonempty"
        dir_path.mkdir()
        (dir_path / "file.txt").write_text("content")
        
        assert is_empty_directory(dir_path) is False
    
    def test_nonexistent_directory(self, tmp_path):
        """Test with non-existent directory."""
        assert is_empty_directory(tmp_path / "nonexistent") is False


class TestGetUniqueFilename:
    """Test getting unique filename."""
    
    def test_unique_when_not_exists(self, tmp_path):
        """Test when filename doesn't exist."""
        file_path = tmp_path / "test.txt"
        
        result = get_unique_filename(file_path)
        
        assert result == file_path
    
    def test_unique_when_exists(self, tmp_path):
        """Test when filename exists."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("existing")
        
        result = get_unique_filename(file_path)
        
        assert result != file_path
        assert "test_1.txt" in str(result)
    
    def test_multiple_conflicts(self, tmp_path):
        """Test with multiple conflicting files."""
        base = tmp_path / "test.txt"
        base.write_text("0")
        (tmp_path / "test_1.txt").write_text("1")
        (tmp_path / "test_2.txt").write_text("2")
        
        result = get_unique_filename(base)
        
        assert "test_3.txt" in str(result)
    
    def test_custom_separator(self, tmp_path):
        """Test with custom separator."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("existing")
        
        result = get_unique_filename(file_path, separator="-")
        
        assert "test-1.txt" in str(result)

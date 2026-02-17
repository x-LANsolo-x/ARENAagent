"""Unit tests for FileTracker class."""

import pytest
from pathlib import Path
from datetime import datetime

from arenaagent.files.tracker import FileTracker
from arenaagent.models.code_change import ChangeType


class TestFileTracker:
    """Test FileTracker functionality."""
    
    def test_init_default(self):
        """Test default initialization."""
        tracker = FileTracker()
        
        assert tracker.working_directory == Path.cwd()
        assert len(tracker.get_tracked_files()) == 0
    
    def test_init_custom_directory(self, tmp_path):
        """Test initialization with custom directory."""
        tracker = FileTracker(str(tmp_path))
        
        assert tracker.working_directory == tmp_path
    
    def test_track_file(self, tmp_path):
        """Test tracking a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        assert tracker.is_tracked(str(test_file))
        assert len(tracker.get_tracked_files()) == 1
    
    def test_track_nonexistent_file(self, tmp_path):
        """Test tracking a non-existent file."""
        test_file = tmp_path / "nonexistent.txt"
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        # Should not track non-existent files
        assert not tracker.is_tracked(str(test_file))
    
    def test_untrack_file(self, tmp_path):
        """Test untracking a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Content")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        assert tracker.is_tracked(str(test_file))
        
        tracker.untrack_file(str(test_file))
        assert not tracker.is_tracked(str(test_file))
    
    def test_is_modified_unchanged_file(self, tmp_path):
        """Test that unchanged file is not marked as modified."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Original content")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        assert not tracker.is_modified(str(test_file))
    
    def test_is_modified_changed_file(self, tmp_path):
        """Test that modified file is detected."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Original content")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        # Modify the file
        test_file.write_text("Modified content")
        
        assert tracker.is_modified(str(test_file))
    
    def test_is_modified_deleted_file(self, tmp_path):
        """Test that deleted file is marked as modified."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Content")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        # Delete the file
        test_file.unlink()
        
        assert tracker.is_modified(str(test_file))
    
    def test_get_modified_files(self, tmp_path):
        """Test getting list of modified files."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file3 = tmp_path / "file3.txt"
        
        file1.write_text("Content 1")
        file2.write_text("Content 2")
        file3.write_text("Content 3")
        
        tracker = FileTracker()
        tracker.track_file(str(file1))
        tracker.track_file(str(file2))
        tracker.track_file(str(file3))
        
        # Modify only file2
        file2.write_text("Modified content 2")
        
        modified = tracker.get_modified_files()
        
        assert len(modified) == 1
        assert str(file2.resolve()) in modified
    
    def test_get_diff(self, tmp_path):
        """Test generating diff for modified file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3\n")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        # Modify the file
        test_file.write_text("Line 1\nModified Line 2\nLine 3\n")
        
        diff = tracker.get_diff(str(test_file))
        
        assert diff is not None
        assert "Modified Line 2" in diff
        assert "Line 2" in diff
    
    def test_get_diff_unchanged_file(self, tmp_path):
        """Test that unchanged file has no diff."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Content")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        diff = tracker.get_diff(str(test_file))
        
        assert diff is None
    
    def test_get_change_modify(self, tmp_path):
        """Test getting CodeChange for modified file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Original")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        test_file.write_text("Modified")
        
        change = tracker.get_change(str(test_file))
        
        assert change is not None
        assert change.change_type == ChangeType.MODIFY
        assert change.before_content == "Original"
        assert change.after_content == "Modified"
    
    def test_get_change_delete(self, tmp_path):
        """Test getting CodeChange for deleted file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Content")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        test_file.unlink()
        
        change = tracker.get_change(str(test_file))
        
        assert change is not None
        assert change.change_type == ChangeType.DELETE
        assert change.before_content == "Content"
        assert change.after_content == ""
    
    def test_get_all_changes(self, tmp_path):
        """Test getting all changes."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        
        file1.write_text("Content 1")
        file2.write_text("Content 2")
        
        tracker = FileTracker()
        tracker.track_file(str(file1))
        tracker.track_file(str(file2))
        
        # Modify both files
        file1.write_text("Modified 1")
        file2.write_text("Modified 2")
        
        changes = tracker.get_all_changes()
        
        assert len(changes) == 2
        assert all(c.change_type == ChangeType.MODIFY for c in changes)
    
    def test_update_snapshot(self, tmp_path):
        """Test updating snapshot."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Original")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        # Modify file
        test_file.write_text("Modified")
        assert tracker.is_modified(str(test_file))
        
        # Update snapshot
        tracker.update_snapshot(str(test_file))
        
        # Should no longer be modified
        assert not tracker.is_modified(str(test_file))
    
    def test_reset_file(self, tmp_path):
        """Test resetting file to original state."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Original content")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        # Modify file
        test_file.write_text("Modified content")
        assert tracker.is_modified(str(test_file))
        
        # Reset file
        result = tracker.reset_file(str(test_file))
        
        assert result is True
        assert test_file.read_text() == "Original content"
        assert not tracker.is_modified(str(test_file))
    
    def test_reset_untracked_file(self, tmp_path):
        """Test resetting untracked file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Content")
        
        tracker = FileTracker()
        
        result = tracker.reset_file(str(test_file))
        
        assert result is False
    
    def test_clear(self, tmp_path):
        """Test clearing all tracked files."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        
        file1.write_text("Content 1")
        file2.write_text("Content 2")
        
        tracker = FileTracker()
        tracker.track_file(str(file1))
        tracker.track_file(str(file2))
        
        assert len(tracker.get_tracked_files()) == 2
        
        tracker.clear()
        
        assert len(tracker.get_tracked_files()) == 0
    
    def test_get_stats(self, tmp_path):
        """Test getting statistics."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file3 = tmp_path / "file3.txt"
        
        file1.write_text("Content 1")
        file2.write_text("Content 2")
        file3.write_text("Content 3")
        
        tracker = FileTracker()
        tracker.track_file(str(file1))
        tracker.track_file(str(file2))
        tracker.track_file(str(file3))
        
        # Modify one file
        file2.write_text("Modified")
        
        stats = tracker.get_stats()
        
        assert stats['total_tracked'] == 3
        assert stats['modified'] == 1
        assert stats['unmodified'] == 2
    
    def test_export_import_state(self, tmp_path):
        """Test exporting and importing tracker state."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Content")
        
        tracker1 = FileTracker()
        tracker1.track_file(str(test_file))
        
        # Export state
        state = tracker1.export_state()
        
        # Create new tracker and import state
        tracker2 = FileTracker()
        tracker2.import_state(state)
        
        assert tracker2.is_tracked(str(test_file))
        assert len(tracker2.get_tracked_files()) == 1
    
    def test_track_multiple_files(self, tmp_path):
        """Test tracking multiple files."""
        files = [tmp_path / f"file{i}.txt" for i in range(5)]
        
        for f in files:
            f.write_text(f"Content of {f.name}")
        
        tracker = FileTracker()
        
        for f in files:
            tracker.track_file(str(f))
        
        assert len(tracker.get_tracked_files()) == 5
        
        # Modify some files
        files[0].write_text("Modified 0")
        files[2].write_text("Modified 2")
        
        modified = tracker.get_modified_files()
        assert len(modified) == 2


class TestFileTrackerEdgeCases:
    """Test edge cases for FileTracker."""
    
    def test_track_same_file_twice(self, tmp_path):
        """Test tracking the same file twice."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Content")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        tracker.track_file(str(test_file))  # Track again
        
        # Should still only have one tracked file
        assert len(tracker.get_tracked_files()) == 1
    
    def test_modify_then_restore(self, tmp_path):
        """Test modifying and then restoring to original content."""
        test_file = tmp_path / "test.txt"
        original_content = "Original content"
        test_file.write_text(original_content)
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        # Modify
        test_file.write_text("Modified")
        assert tracker.is_modified(str(test_file))
        
        # Restore manually to original
        test_file.write_text(original_content)
        
        # Should no longer be modified (hash matches)
        assert not tracker.is_modified(str(test_file))
    
    def test_empty_file(self, tmp_path):
        """Test tracking an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        assert tracker.is_tracked(str(test_file))
        assert not tracker.is_modified(str(test_file))
    
    def test_binary_file(self, tmp_path):
        """Test tracking a binary file."""
        test_file = tmp_path / "binary.dat"
        test_file.write_bytes(b'\x00\x01\x02\x03\x04')
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        assert tracker.is_tracked(str(test_file))
        
        # Modify binary file
        test_file.write_bytes(b'\x00\x01\x02\x03\x05')
        
        assert tracker.is_modified(str(test_file))
    
    def test_large_file_hash(self, tmp_path):
        """Test hashing a larger file."""
        test_file = tmp_path / "large.txt"
        
        # Create a file larger than the chunk size (8192 bytes)
        content = "A" * 10000
        test_file.write_text(content)
        
        tracker = FileTracker()
        tracker.track_file(str(test_file))
        
        assert tracker.is_tracked(str(test_file))
        assert not tracker.is_modified(str(test_file))

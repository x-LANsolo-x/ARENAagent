"""Unit tests for the CodeChange model."""

import pytest
from datetime import datetime
import uuid

from arenaagent.models.code_change import CodeChange


class TestCodeChangeCreation:
    """Tests for creating CodeChange instances."""
    
    def test_create_change_creation(self):
        """Test creating a 'create' type code change."""
        change = CodeChange(
            file_path="test.py",
            change_type="create",
            content_after="print('hello')"
        )
        
        assert change.file_path == "test.py"
        assert change.change_type == "create"
        assert change.content_before is None
        assert change.content_after == "print('hello')"
        assert change.id is not None
        assert isinstance(change.timestamp, datetime)
    
    def test_modify_change_creation(self):
        """Test creating a 'modify' type code change."""
        change = CodeChange(
            file_path="test.py",
            change_type="modify",
            content_before="print('hello')",
            content_after="print('world')"
        )
        
        assert change.change_type == "modify"
        assert change.content_before == "print('hello')"
        assert change.content_after == "print('world')"
    
    def test_delete_change_creation(self):
        """Test creating a 'delete' type code change."""
        change = CodeChange(
            file_path="test.py",
            change_type="delete",
            content_before="old content"
        )
        
        assert change.change_type == "delete"
        assert change.content_before == "old content"
        assert change.content_after is None
    
    def test_change_with_description(self):
        """Test creating a change with description."""
        change = CodeChange(
            file_path="test.py",
            change_type="create",
            content_after="code",
            description="Added new test file"
        )
        
        assert change.description == "Added new test file"
    
    def test_change_with_metadata(self):
        """Test creating a change with metadata."""
        change = CodeChange(
            file_path="test.py",
            change_type="create",
            content_after="code",
            metadata={"author": "test", "reason": "bug fix"}
        )
        
        assert change.metadata == {"author": "test", "reason": "bug fix"}


class TestCodeChangeValidation:
    """Tests for code change validation."""
    
    def test_validation_invalid_change_type(self):
        """Test validation fails for invalid change type."""
        with pytest.raises(ValueError, match="Invalid change_type"):
            CodeChange(
                file_path="test.py",
                change_type="invalid",
                content_after="code"
            )
    
    def test_validation_empty_file_path(self):
        """Test validation fails for empty file path."""
        with pytest.raises(ValueError, match="file_path cannot be empty"):
            CodeChange(
                file_path="",
                change_type="create",
                content_after="code"
            )
    
    def test_validation_create_with_content_before(self):
        """Test validation fails if create has content_before."""
        with pytest.raises(ValueError, match="should not have content_before"):
            CodeChange(
                file_path="test.py",
                change_type="create",
                content_before="shouldn't be here",
                content_after="new code"
            )
    
    def test_validation_create_without_content_after(self):
        """Test validation fails if create missing content_after."""
        with pytest.raises(ValueError, match="must have content_after"):
            CodeChange(
                file_path="test.py",
                change_type="create"
            )
    
    def test_validation_modify_without_content_before(self):
        """Test validation fails if modify missing content_before."""
        with pytest.raises(ValueError, match="must have content_before"):
            CodeChange(
                file_path="test.py",
                change_type="modify",
                content_after="new code"
            )
    
    def test_validation_modify_without_content_after(self):
        """Test validation fails if modify missing content_after."""
        with pytest.raises(ValueError, match="must have content_after"):
            CodeChange(
                file_path="test.py",
                change_type="modify",
                content_before="old code"
            )
    
    def test_validation_delete_without_content_before(self):
        """Test validation fails if delete missing content_before."""
        with pytest.raises(ValueError, match="must have content_before"):
            CodeChange(
                file_path="test.py",
                change_type="delete"
            )
    
    def test_validation_delete_with_content_after(self):
        """Test validation fails if delete has content_after."""
        with pytest.raises(ValueError, match="should not have content_after"):
            CodeChange(
                file_path="test.py",
                change_type="delete",
                content_before="old code",
                content_after="shouldn't be here"
            )
    
    def test_validation_invalid_uuid(self):
        """Test validation fails for invalid UUID."""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            CodeChange(
                file_path="test.py",
                change_type="create",
                content_after="code",
                id="not-a-uuid"
            )


class TestCodeChangeDiffSummary:
    """Tests for getting diff summaries."""
    
    def test_create_diff_summary(self):
        """Test diff summary for create change."""
        change = CodeChange(
            file_path="new_file.py",
            change_type="create",
            content_after="line1\nline2\nline3"
        )
        
        summary = change.get_diff_summary()
        assert "Created new_file.py" in summary
        assert "3 lines" in summary
    
    def test_delete_diff_summary(self):
        """Test diff summary for delete change."""
        change = CodeChange(
            file_path="old_file.py",
            change_type="delete",
            content_before="line1\nline2"
        )
        
        summary = change.get_diff_summary()
        assert "Deleted old_file.py" in summary
        assert "2 lines" in summary
    
    def test_modify_diff_summary_added_lines(self):
        """Test diff summary for modify change with added lines."""
        change = CodeChange(
            file_path="file.py",
            change_type="modify",
            content_before="line1",
            content_after="line1\nline2\nline3"
        )
        
        summary = change.get_diff_summary()
        assert "Modified file.py" in summary
        assert "+2 lines" in summary
    
    def test_modify_diff_summary_removed_lines(self):
        """Test diff summary for modify change with removed lines."""
        change = CodeChange(
            file_path="file.py",
            change_type="modify",
            content_before="line1\nline2\nline3",
            content_after="line1"
        )
        
        summary = change.get_diff_summary()
        assert "Modified file.py" in summary
        assert "-2 lines" in summary


class TestCodeChangeRollback:
    """Tests for rollback capability."""
    
    def test_create_can_rollback(self):
        """Test that create changes can be rolled back."""
        change = CodeChange(
            file_path="test.py",
            change_type="create",
            content_after="code"
        )
        
        assert change.can_rollback() is True
    
    def test_modify_can_rollback(self):
        """Test that modify changes can be rolled back."""
        change = CodeChange(
            file_path="test.py",
            change_type="modify",
            content_before="old",
            content_after="new"
        )
        
        assert change.can_rollback() is True
    
    def test_delete_can_rollback(self):
        """Test that delete changes can be rolled back."""
        change = CodeChange(
            file_path="test.py",
            change_type="delete",
            content_before="old content"
        )
        
        assert change.can_rollback() is True


class TestCodeChangeSerialization:
    """Tests for code change serialization."""
    
    def test_to_dict(self):
        """Test converting code change to dictionary."""
        change = CodeChange(
            file_path="test.py",
            change_type="modify",
            content_before="old",
            content_after="new",
            description="Updated file"
        )
        
        data = change.to_dict()
        
        assert data["file_path"] == "test.py"
        assert data["change_type"] == "modify"
        assert data["content_before"] == "old"
        assert data["content_after"] == "new"
        assert data["description"] == "Updated file"
        assert data["id"] == change.id
    
    def test_from_dict(self):
        """Test creating code change from dictionary."""
        data = {
            "file_path": "test.py",
            "change_type": "create",
            "content_after": "new code",
            "id": str(uuid.uuid4()),
            "timestamp": "2024-01-01T12:00:00",
            "description": "Test change"
        }
        
        change = CodeChange.from_dict(data)
        
        assert change.file_path == "test.py"
        assert change.change_type == "create"
        assert change.content_after == "new code"
        assert change.description == "Test change"
    
    def test_serialization_roundtrip(self):
        """Test that serialization roundtrip preserves data."""
        original = CodeChange(
            file_path="test.py",
            change_type="modify",
            content_before="old",
            content_after="new",
            description="Test",
            metadata={"key": "value"}
        )
        
        data = original.to_dict()
        restored = CodeChange.from_dict(data)
        
        assert restored.file_path == original.file_path
        assert restored.change_type == original.change_type
        assert restored.content_before == original.content_before
        assert restored.content_after == original.content_after
        assert restored.description == original.description
        assert restored.metadata == original.metadata


class TestCodeChangeStringRepresentation:
    """Tests for code change string representations."""
    
    def test_repr(self):
        """Test __repr__ returns detailed representation."""
        change = CodeChange(
            file_path="test.py",
            change_type="create",
            content_after="code"
        )
        repr_str = repr(change)
        
        assert "CodeChange(" in repr_str
        assert "type='create'" in repr_str
        assert "file='test.py'" in repr_str
    
    def test_str(self):
        """Test __str__ returns human-readable representation."""
        change = CodeChange(
            file_path="test.py",
            change_type="modify",
            content_before="old",
            content_after="new"
        )
        str_rep = str(change)
        
        assert "[MODIFY]" in str_rep
        assert "test.py" in str_rep

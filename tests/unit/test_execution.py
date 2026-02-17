"""Unit tests for the ExecutionResult model."""

import pytest
from datetime import datetime

from arenaagent.models.execution import ExecutionResult


class TestExecutionResultCreation:
    """Tests for creating ExecutionResult instances."""
    
    def test_successful_execution_creation(self):
        """Test creating a successful execution result."""
        result = ExecutionResult(
            command="echo 'hello'",
            stdout="hello\n",
            exit_code=0,
            duration=0.5
        )
        
        assert result.command == "echo 'hello'"
        assert result.stdout == "hello\n"
        assert result.stderr == ""
        assert result.exit_code == 0
        assert result.duration == 0.5
        assert result.success is True
        assert isinstance(result.timestamp, datetime)
    
    def test_failed_execution_creation(self):
        """Test creating a failed execution result."""
        result = ExecutionResult(
            command="invalid_command",
            stderr="command not found",
            exit_code=127,
            duration=0.1
        )
        
        assert result.command == "invalid_command"
        assert result.stderr == "command not found"
        assert result.exit_code == 127
        assert result.success is False
    
    def test_execution_with_environment_vars(self):
        """Test creating execution with environment variables."""
        result = ExecutionResult(
            command="python test.py",
            environment_vars={"PYTHONPATH": "/usr/lib", "DEBUG": "1"}
        )
        
        assert result.environment_vars == {"PYTHONPATH": "/usr/lib", "DEBUG": "1"}
    
    def test_execution_with_working_directory(self):
        """Test creating execution with working directory."""
        result = ExecutionResult(
            command="ls",
            working_directory="/home/user/project"
        )
        
        assert result.working_directory == "/home/user/project"


class TestExecutionResultValidation:
    """Tests for execution result validation."""
    
    def test_validation_empty_command(self):
        """Test validation fails for empty command."""
        with pytest.raises(ValueError, match="command cannot be empty"):
            ExecutionResult(command="")
    
    def test_validation_whitespace_only_command(self):
        """Test validation fails for whitespace-only command."""
        with pytest.raises(ValueError, match="command cannot be empty"):
            ExecutionResult(command="   ")
    
    def test_validation_negative_duration(self):
        """Test validation fails for negative duration."""
        with pytest.raises(ValueError, match="duration cannot be negative"):
            ExecutionResult(command="test", duration=-1.0)
    
    def test_validation_invalid_timestamp_type(self):
        """Test validation fails for invalid timestamp type."""
        with pytest.raises(ValueError, match="must be a datetime object"):
            ExecutionResult(command="test", timestamp="not-a-datetime")


class TestExecutionResultSuccess:
    """Tests for success property and error checking."""
    
    def test_success_property_true(self):
        """Test success property returns True for exit code 0."""
        result = ExecutionResult(command="test", exit_code=0)
        assert result.success is True
    
    def test_success_property_false(self):
        """Test success property returns False for non-zero exit code."""
        result = ExecutionResult(command="test", exit_code=1)
        assert result.success is False
    
    def test_is_error_false_for_success(self):
        """Test is_error returns False for successful execution."""
        result = ExecutionResult(command="test", exit_code=0)
        assert result.is_error() is False
    
    def test_is_error_true_for_failure(self):
        """Test is_error returns True for failed execution."""
        result = ExecutionResult(command="test", exit_code=1)
        assert result.is_error() is True


class TestExecutionResultErrorMessage:
    """Tests for getting error messages."""
    
    def test_error_message_for_success(self):
        """Test error message is empty for successful execution."""
        result = ExecutionResult(command="test", exit_code=0)
        assert result.get_error_message() == ""
    
    def test_error_message_with_stderr(self):
        """Test error message includes stderr."""
        result = ExecutionResult(
            command="test",
            stderr="Error: file not found",
            exit_code=1
        )
        
        error_msg = result.get_error_message()
        assert "exit code 1" in error_msg
        assert "Error: file not found" in error_msg
    
    def test_error_message_with_stdout_and_stderr(self):
        """Test error message includes both stdout and stderr."""
        result = ExecutionResult(
            command="test",
            stdout="Processing...",
            stderr="Error occurred",
            exit_code=2
        )
        
        error_msg = result.get_error_message()
        assert "exit code 2" in error_msg
        assert "Error occurred" in error_msg
        assert "Processing..." in error_msg
    
    def test_error_message_format(self):
        """Test error message is properly formatted."""
        result = ExecutionResult(
            command="test",
            stderr="Test error",
            exit_code=1
        )
        
        error_msg = result.get_error_message()
        assert "Command failed" in error_msg
        assert "Error output:" in error_msg


class TestExecutionResultOutput:
    """Tests for getting combined output."""
    
    def test_get_output_both_stdout_and_stderr(self):
        """Test getting combined output."""
        result = ExecutionResult(
            command="test",
            stdout="Standard output",
            stderr="Error output"
        )
        
        output = result.get_output()
        assert "Standard output" in output
        assert "Error output" in output
    
    def test_get_output_only_stdout(self):
        """Test getting output with only stdout."""
        result = ExecutionResult(
            command="test",
            stdout="Only stdout"
        )
        
        output = result.get_output()
        assert output == "Only stdout"
    
    def test_get_output_only_stderr(self):
        """Test getting output with only stderr."""
        result = ExecutionResult(
            command="test",
            stderr="Only stderr"
        )
        
        output = result.get_output()
        assert output == "Only stderr"
    
    def test_get_output_empty(self):
        """Test getting output when both are empty."""
        result = ExecutionResult(command="test")
        
        output = result.get_output()
        assert output == ""


class TestExecutionResultSerialization:
    """Tests for execution result serialization."""
    
    def test_to_dict(self):
        """Test converting execution result to dictionary."""
        result = ExecutionResult(
            command="python test.py",
            stdout="Test output",
            stderr="",
            exit_code=0,
            duration=1.5,
            working_directory="/home/user",
            environment_vars={"TEST": "1"}
        )
        
        data = result.to_dict()
        
        assert data["command"] == "python test.py"
        assert data["stdout"] == "Test output"
        assert data["exit_code"] == 0
        assert data["duration"] == 1.5
        assert data["success"] is True
        assert data["working_directory"] == "/home/user"
        assert data["environment_vars"] == {"TEST": "1"}
    
    def test_from_dict(self):
        """Test creating execution result from dictionary."""
        data = {
            "command": "echo test",
            "stdout": "test",
            "stderr": "",
            "exit_code": 0,
            "duration": 0.5,
            "timestamp": "2024-01-01T12:00:00",
            "working_directory": "/tmp",
            "environment_vars": {}
        }
        
        result = ExecutionResult.from_dict(data)
        
        assert result.command == "echo test"
        assert result.stdout == "test"
        assert result.exit_code == 0
        assert result.duration == 0.5
        assert result.working_directory == "/tmp"
    
    def test_serialization_roundtrip(self):
        """Test that serialization roundtrip preserves data."""
        original = ExecutionResult(
            command="test command",
            stdout="output",
            stderr="error",
            exit_code=1,
            duration=2.5,
            working_directory="/test",
            environment_vars={"KEY": "value"}
        )
        
        data = original.to_dict()
        restored = ExecutionResult.from_dict(data)
        
        assert restored.command == original.command
        assert restored.stdout == original.stdout
        assert restored.stderr == original.stderr
        assert restored.exit_code == original.exit_code
        assert restored.duration == original.duration
        assert restored.working_directory == original.working_directory
        assert restored.environment_vars == original.environment_vars


class TestExecutionResultStringRepresentation:
    """Tests for execution result string representations."""
    
    def test_repr_success(self):
        """Test __repr__ for successful execution."""
        result = ExecutionResult(
            command="echo 'hello world'",
            exit_code=0,
            duration=0.5
        )
        repr_str = repr(result)
        
        assert "ExecutionResult(" in repr_str
        assert "SUCCESS" in repr_str
        assert "0.50s" in repr_str
    
    def test_repr_failure(self):
        """Test __repr__ for failed execution."""
        result = ExecutionResult(
            command="invalid",
            exit_code=127,
            duration=0.1
        )
        repr_str = repr(result)
        
        assert "ExecutionResult(" in repr_str
        assert "FAILED" in repr_str
        assert "exit 127" in repr_str
    
    def test_str_success(self):
        """Test __str__ for successful execution."""
        result = ExecutionResult(
            command="test command",
            exit_code=0,
            duration=1.2
        )
        str_rep = str(result)
        
        assert "✓" in str_rep
        assert "test command" in str_rep
        assert "1.20s" in str_rep
    
    def test_str_failure(self):
        """Test __str__ for failed execution."""
        result = ExecutionResult(
            command="test command",
            exit_code=1,
            duration=0.5
        )
        str_rep = str(result)
        
        assert "✗" in str_rep
        assert "test command" in str_rep


class TestExecutionResultEdgeCases:
    """Tests for edge cases."""
    
    def test_very_long_output(self):
        """Test handling very long output."""
        long_output = "x" * 10000
        result = ExecutionResult(
            command="test",
            stdout=long_output
        )
        
        assert len(result.stdout) == 10000
        assert result.get_output() == long_output
    
    def test_zero_duration(self):
        """Test execution with zero duration."""
        result = ExecutionResult(
            command="test",
            duration=0.0
        )
        
        assert result.duration == 0.0
    
    def test_multiline_output(self):
        """Test handling multiline output."""
        result = ExecutionResult(
            command="test",
            stdout="line1\nline2\nline3",
            stderr="error1\nerror2"
        )
        
        output = result.get_output()
        assert "line1" in output
        assert "line2" in output
        assert "error1" in output

"""Unit tests for formatters utility module."""

import pytest
from datetime import datetime
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from arenaagent.models.message import Message, MessageRole
from arenaagent.models.execution import ExecutionResult
from arenaagent.utils.formatters import (
    format_message,
    format_execution_result,
    format_code,
    format_timestamp,
    create_table,
    format_file_size,
    format_duration,
    format_list,
    truncate_text,
    format_progress,
    format_key_value,
    format_error,
)


class TestFormatMessage:
    """Test message formatting."""
    
    def test_format_user_message(self):
        """Test formatting a user message."""
        msg = Message(role=MessageRole.USER, content="Hello, assistant!")
        result = format_message(msg)
        
        assert isinstance(result, Panel)
        assert "Hello, assistant!" in str(result)
    
    def test_format_assistant_message(self):
        """Test formatting an assistant message."""
        msg = Message(role=MessageRole.ASSISTANT, content="Hello, user!")
        result = format_message(msg)
        
        assert isinstance(result, Panel)
        assert "Hello, user!" in str(result)
    
    def test_format_system_message(self):
        """Test formatting a system message."""
        msg = Message(role=MessageRole.SYSTEM, content="System notification")
        result = format_message(msg)
        
        assert isinstance(result, Panel)
        assert "System notification" in str(result)
    
    def test_format_message_with_metadata(self):
        """Test formatting message with metadata."""
        msg = Message(
            role=MessageRole.USER,
            content="Test",
            metadata={"key": "value"}
        )
        result = format_message(msg)
        
        assert isinstance(result, Panel)


class TestFormatExecutionResult:
    """Test execution result formatting."""
    
    def test_format_successful_execution(self):
        """Test formatting successful execution."""
        result = ExecutionResult(
            command="echo hello",
            exit_code=0,
            stdout="hello\n",
            stderr="",
            success=True,
            execution_time=0.5
        )
        
        panel = format_execution_result(result)
        assert isinstance(panel, Panel)
    
    def test_format_failed_execution(self):
        """Test formatting failed execution."""
        result = ExecutionResult(
            command="invalid_command",
            exit_code=1,
            stdout="",
            stderr="Command not found",
            success=False,
            execution_time=0.1
        )
        
        panel = format_execution_result(result)
        assert isinstance(panel, Panel)
    
    def test_format_long_output(self):
        """Test that long output is truncated."""
        long_output = "x" * 2000
        result = ExecutionResult(
            command="test",
            exit_code=0,
            stdout=long_output,
            stderr="",
            success=True,
            execution_time=1.0
        )
        
        panel = format_execution_result(result)
        assert isinstance(panel, Panel)


class TestFormatCode:
    """Test code formatting."""
    
    def test_format_python_code(self):
        """Test formatting Python code."""
        code = "def hello():\n    print('Hello')"
        result = format_code(code, "python")
        
        assert isinstance(result, Syntax)
    
    def test_format_javascript_code(self):
        """Test formatting JavaScript code."""
        code = "function hello() { console.log('Hello'); }"
        result = format_code(code, "javascript")
        
        assert isinstance(result, Syntax)
    
    def test_format_with_custom_theme(self):
        """Test formatting with custom theme."""
        code = "print('test')"
        result = format_code(code, "python", theme="dracula")
        
        assert isinstance(result, Syntax)


class TestFormatTimestamp:
    """Test timestamp formatting."""
    
    def test_default_format(self):
        """Test default timestamp format."""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = format_timestamp(dt)
        
        assert result == "2024-01-15 14:30:45"
    
    def test_custom_format(self):
        """Test custom timestamp format."""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = format_timestamp(dt, "%Y-%m-%d")
        
        assert result == "2024-01-15"
    
    def test_time_only_format(self):
        """Test time-only format."""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = format_timestamp(dt, "%H:%M:%S")
        
        assert result == "14:30:45"


class TestCreateTable:
    """Test table creation."""
    
    def test_simple_table(self):
        """Test creating a simple table."""
        headers = ["Name", "Age"]
        rows = [["Alice", 30], ["Bob", 25]]
        
        table = create_table(headers, rows)
        assert isinstance(table, Table)
    
    def test_table_with_title(self):
        """Test creating table with title."""
        headers = ["Col1", "Col2"]
        rows = [["A", "B"]]
        
        table = create_table(headers, rows, title="Test Table")
        assert isinstance(table, Table)
    
    def test_table_with_lines(self):
        """Test creating table with lines."""
        headers = ["Col1", "Col2"]
        rows = [["A", "B"], ["C", "D"]]
        
        table = create_table(headers, rows, show_lines=True)
        assert isinstance(table, Table)
    
    def test_empty_table(self):
        """Test creating empty table."""
        headers = ["Col1", "Col2"]
        rows = []
        
        table = create_table(headers, rows)
        assert isinstance(table, Table)


class TestFormatFileSize:
    """Test file size formatting."""
    
    def test_bytes(self):
        """Test formatting bytes."""
        assert format_file_size(100) == "100.0 B"
        assert format_file_size(500) == "500.0 B"
    
    def test_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(2048) == "2.0 KB"
    
    def test_megabytes(self):
        """Test formatting megabytes."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(5 * 1024 * 1024) == "5.0 MB"
    
    def test_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_zero_size(self):
        """Test formatting zero size."""
        assert format_file_size(0) == "0.0 B"


class TestFormatDuration:
    """Test duration formatting."""
    
    def test_seconds(self):
        """Test formatting seconds."""
        assert format_duration(5.5) == "5.5s"
        assert format_duration(30) == "30.0s"
    
    def test_minutes(self):
        """Test formatting minutes."""
        assert format_duration(60) == "1m 0s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(150) == "2m 30s"
    
    def test_hours(self):
        """Test formatting hours."""
        assert format_duration(3600) == "1h 0m"
        assert format_duration(3660) == "1h 1m"
        assert format_duration(7200) == "2h 0m"
    
    def test_subsecond(self):
        """Test formatting subsecond durations."""
        assert format_duration(0.5) == "0.5s"
        assert format_duration(0.123) == "0.1s"


class TestFormatList:
    """Test list formatting."""
    
    def test_bullet_list(self):
        """Test bullet list formatting."""
        items = ["Item 1", "Item 2", "Item 3"]
        result = format_list(items, style="bullet")
        
        assert "• Item 1" in result
        assert "• Item 2" in result
        assert "• Item 3" in result
    
    def test_numbered_list(self):
        """Test numbered list formatting."""
        items = ["First", "Second", "Third"]
        result = format_list(items, style="number")
        
        assert "1. First" in result
        assert "2. Second" in result
        assert "3. Third" in result
    
    def test_dash_list(self):
        """Test dash list formatting."""
        items = ["One", "Two"]
        result = format_list(items, style="dash")
        
        assert "- One" in result
        assert "- Two" in result
    
    def test_empty_list(self):
        """Test empty list formatting."""
        items = []
        result = format_list(items)
        
        assert result == ""


class TestTruncateText:
    """Test text truncation."""
    
    def test_no_truncation_needed(self):
        """Test text shorter than max length."""
        text = "Short text"
        result = truncate_text(text, max_length=100)
        
        assert result == "Short text"
    
    def test_truncation(self):
        """Test text truncation."""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, max_length=20)
        
        assert len(result) == 20
        assert result.endswith("...")
    
    def test_custom_suffix(self):
        """Test truncation with custom suffix."""
        text = "Long text here"
        result = truncate_text(text, max_length=10, suffix=">>")
        
        assert len(result) == 10
        assert result.endswith(">>")
    
    def test_exact_length(self):
        """Test text exactly at max length."""
        text = "Exact"
        result = truncate_text(text, max_length=5)
        
        assert result == "Exact"


class TestFormatProgress:
    """Test progress bar formatting."""
    
    def test_zero_percent(self):
        """Test 0% progress."""
        result = format_progress(0, 100)
        
        assert "0%" in result
        assert "[" in result
        assert "]" in result
    
    def test_fifty_percent(self):
        """Test 50% progress."""
        result = format_progress(50, 100)
        
        assert "50%" in result
    
    def test_hundred_percent(self):
        """Test 100% progress."""
        result = format_progress(100, 100)
        
        assert "100%" in result
    
    def test_custom_width(self):
        """Test progress bar with custom width."""
        result = format_progress(50, 100, width=10)
        
        assert "50%" in result
    
    def test_zero_total(self):
        """Test progress with zero total."""
        result = format_progress(0, 0)
        
        assert "0%" in result


class TestFormatKeyValue:
    """Test key-value formatting."""
    
    def test_basic_formatting(self):
        """Test basic key-value formatting."""
        result = format_key_value("Name", "Alice")
        
        assert "Name:" in result
        assert "Alice" in result
    
    def test_custom_width(self):
        """Test with custom key width."""
        result = format_key_value("Key", "Value", key_width=10)
        
        assert "Key:" in result
        assert "Value" in result
    
    def test_numeric_value(self):
        """Test with numeric value."""
        result = format_key_value("Count", 42)
        
        assert "Count:" in result
        assert "42" in result


class TestFormatError:
    """Test error formatting."""
    
    def test_simple_error(self):
        """Test formatting simple error."""
        error = ValueError("Test error")
        result = format_error(error)
        
        assert "ValueError" in result
        assert "Test error" in result
    
    def test_error_with_traceback(self):
        """Test formatting error with traceback."""
        error = RuntimeError("Runtime issue")
        result = format_error(error, include_traceback=True)
        
        assert "RuntimeError" in result
        assert "Runtime issue" in result
    
    def test_different_error_types(self):
        """Test formatting different error types."""
        errors = [
            TypeError("Type error"),
            KeyError("key"),
            IOError("IO error"),
        ]
        
        for error in errors:
            result = format_error(error)
            assert type(error).__name__ in result

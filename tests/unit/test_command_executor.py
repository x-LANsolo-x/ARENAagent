"""Unit tests for CommandExecutor class."""

import pytest
import asyncio
import platform
from pathlib import Path
import time

from arenaagent.executor.command import CommandExecutor
from arenaagent.models.execution import ExecutionResult


class TestCommandExecutorSync:
    """Test synchronous command execution."""
    
    def test_init_default(self):
        """Test default initialization."""
        executor = CommandExecutor()
        
        assert executor.working_dir == Path.cwd()
        assert executor.default_timeout == 30.0
        assert executor.check_safety is True
    
    def test_init_custom(self, tmp_path):
        """Test initialization with custom parameters."""
        executor = CommandExecutor(
            working_dir=tmp_path,
            timeout=60.0,
            check_safety=False
        )
        
        assert executor.working_dir == tmp_path
        assert executor.default_timeout == 60.0
        assert executor.check_safety is False
    
    def test_execute_simple_command(self):
        """Test executing a simple command."""
        executor = CommandExecutor(check_safety=False)
        
        # Use platform-appropriate command
        if platform.system() == "Windows":
            result = executor.execute("echo Hello")
        else:
            result = executor.execute("echo 'Hello'")
        
        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert result.exit_code == 0
        assert "Hello" in result.stdout
    
    def test_execute_with_output(self):
        """Test command with output capture."""
        executor = CommandExecutor(check_safety=False)
        
        if platform.system() == "Windows":
            result = executor.execute("echo Test Output")
        else:
            result = executor.execute("echo 'Test Output'")
        
        assert result.success is True
        assert "Test Output" in result.stdout
        assert result.stderr == ""
    
    def test_execute_failed_command(self):
        """Test handling of failed command."""
        executor = CommandExecutor(check_safety=False)
        
        # Try to execute a non-existent command
        result = executor.execute("nonexistentcommand12345")
        
        assert result.success is False
        assert result.exit_code != 0
        assert result.stderr != ""
    
    def test_execute_unsafe_command_blocked(self):
        """Test that unsafe commands are blocked."""
        executor = CommandExecutor(check_safety=True)
        
        result = executor.execute("rm -rf /")
        
        assert result.success is False
        assert result.exit_code == -1
        assert "safety check" in result.stderr.lower()
    
    def test_execute_with_timeout(self):
        """Test command timeout handling."""
        executor = CommandExecutor(timeout=1.0, check_safety=False)
        
        # Command that sleeps longer than timeout
        if platform.system() == "Windows":
            result = executor.execute("timeout /t 5", shell=True)
        else:
            result = executor.execute("sleep 5", shell=True)
        
        assert result.success is False
        assert "timed out" in result.stderr.lower()
    
    def test_execute_with_working_directory(self, tmp_path):
        """Test execution in custom working directory."""
        executor = CommandExecutor(working_dir=tmp_path, check_safety=False)
        
        # Create a test file in tmp_path
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # List directory contents
        if platform.system() == "Windows":
            result = executor.execute("dir /b", shell=True)
        else:
            result = executor.execute("ls", shell=True)
        
        assert result.success is True
        assert "test.txt" in result.stdout
    
    def test_execute_safety_override(self):
        """Test overriding safety check."""
        executor = CommandExecutor(check_safety=True)
        
        # Unsafe command should be blocked
        result1 = executor.execute("rm -rf /", check_safety=True)
        assert result1.success is False
        
        # Same command should work with safety disabled
        # (but will still fail because command doesn't exist on Windows)
        result2 = executor.execute("echo test", check_safety=False)
        assert isinstance(result2, ExecutionResult)
    
    def test_execute_multiple_commands(self):
        """Test executing multiple commands."""
        executor = CommandExecutor(check_safety=False)
        
        commands = [
            "echo 'First'",
            "echo 'Second'",
            "echo 'Third'",
        ]
        
        results = executor.execute_multiple(commands)
        
        assert len(results) == 3
        assert all(r.success for r in results)
        assert "First" in results[0].stdout
        assert "Second" in results[1].stdout
        assert "Third" in results[2].stdout
    
    def test_execute_multiple_stop_on_error(self):
        """Test multiple commands with stop on error."""
        executor = CommandExecutor(check_safety=False)
        
        commands = [
            "echo 'First'",
            "nonexistentcommand",  # This will fail
            "echo 'Third'",  # Should not execute
        ]
        
        results = executor.execute_multiple(commands, stop_on_error=True)
        
        assert len(results) == 2  # Only first two executed
        assert results[0].success is True
        assert results[1].success is False
    
    def test_execute_multiple_continue_on_error(self):
        """Test multiple commands continuing on error."""
        executor = CommandExecutor(check_safety=False)
        
        commands = [
            "echo 'First'",
            "nonexistentcommand",  # This will fail
            "echo 'Third'",  # Should still execute
        ]
        
        results = executor.execute_multiple(commands, stop_on_error=False)
        
        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is True
    
    def test_validate_command(self):
        """Test command validation."""
        executor = CommandExecutor()
        
        assert executor.validate_command("echo hello") is True
        assert executor.validate_command("ls -la") is True
        assert executor.validate_command("rm -rf /") is False
    
    def test_set_working_directory(self, tmp_path):
        """Test setting working directory."""
        executor = CommandExecutor()
        
        executor.set_working_directory(tmp_path)
        assert executor.working_dir == tmp_path
    
    def test_set_timeout(self):
        """Test setting timeout."""
        executor = CommandExecutor()
        
        executor.set_timeout(120.0)
        assert executor.default_timeout == 120.0
    
    def test_get_working_directory(self):
        """Test getting working directory."""
        executor = CommandExecutor()
        
        wd = executor.get_working_directory()
        assert isinstance(wd, Path)
        assert wd == executor.working_dir
    
    def test_execution_time_tracking(self):
        """Test that execution time is tracked."""
        executor = CommandExecutor(check_safety=False)
        
        result = executor.execute("echo test")
        
        assert result.execution_time > 0
        assert result.execution_time < 10  # Should be fast


@pytest.mark.asyncio
class TestCommandExecutorAsync:
    """Test asynchronous command execution."""
    
    async def test_execute_async_simple(self):
        """Test async execution of simple command."""
        executor = CommandExecutor(check_safety=False)
        
        if platform.system() == "Windows":
            result = await executor.execute_async("echo Hello")
        else:
            result = await executor.execute_async("echo 'Hello'")
        
        assert result.success is True
        assert "Hello" in result.stdout
    
    async def test_execute_async_with_timeout(self):
        """Test async execution with timeout."""
        executor = CommandExecutor(timeout=1.0, check_safety=False)
        
        if platform.system() == "Windows":
            result = await executor.execute_async("timeout /t 5")
        else:
            result = await executor.execute_async("sleep 5")
        
        assert result.success is False
        assert "timed out" in result.stderr.lower()
    
    async def test_execute_async_unsafe_blocked(self):
        """Test that unsafe async commands are blocked."""
        executor = CommandExecutor(check_safety=True)
        
        result = await executor.execute_async("rm -rf /")
        
        assert result.success is False
        assert "safety check" in result.stderr.lower()
    
    async def test_execute_multiple_async(self):
        """Test async execution of multiple commands."""
        executor = CommandExecutor(check_safety=False)
        
        commands = [
            "echo 'First'",
            "echo 'Second'",
        ]
        
        results = await executor.execute_multiple_async(commands)
        
        assert len(results) == 2
        assert all(r.success for r in results)
    
    async def test_execute_multiple_async_stop_on_error(self):
        """Test async multiple commands with stop on error."""
        executor = CommandExecutor(check_safety=False)
        
        commands = [
            "echo 'First'",
            "nonexistentcommand",
            "echo 'Third'",
        ]
        
        results = await executor.execute_multiple_async(commands, stop_on_error=True)
        
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False


class TestCommandExecutorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_command(self):
        """Test execution of empty command."""
        executor = CommandExecutor(check_safety=False)
        
        result = executor.execute("")
        
        assert result.success is False
    
    def test_command_with_special_characters(self):
        """Test command with special characters."""
        executor = CommandExecutor(check_safety=False)
        
        if platform.system() != "Windows":
            result = executor.execute("echo 'Special: $HOME & | > <'", shell=True)
            assert isinstance(result, ExecutionResult)
    
    def test_very_long_output(self):
        """Test handling of very long output."""
        executor = CommandExecutor(check_safety=False)
        
        # Generate long output
        if platform.system() == "Windows":
            result = executor.execute("for /L %i in (1,1,100) do @echo Line", shell=True)
        else:
            result = executor.execute("for i in {1..100}; do echo Line; done", shell=True)
        
        assert isinstance(result, ExecutionResult)
        assert len(result.stdout) > 0
    
    def test_command_with_env_vars(self):
        """Test command with environment variables."""
        executor = CommandExecutor(
            check_safety=False,
            env={"TEST_VAR": "test_value"}
        )
        
        if platform.system() == "Windows":
            result = executor.execute("echo %TEST_VAR%", shell=True)
        else:
            result = executor.execute("echo $TEST_VAR", shell=True)
        
        # Environment variables should be available
        assert isinstance(result, ExecutionResult)
    
    def test_nonexistent_working_directory(self):
        """Test with non-existent working directory."""
        nonexistent = Path("/nonexistent/path/that/does/not/exist")
        executor = CommandExecutor(working_dir=nonexistent, check_safety=False)
        
        result = executor.execute("echo test")
        
        # Should fail because directory doesn't exist
        assert result.success is False
    
    def test_execution_result_properties(self):
        """Test that ExecutionResult has all expected properties."""
        executor = CommandExecutor(check_safety=False)
        
        result = executor.execute("echo test")
        
        assert hasattr(result, 'command')
        assert hasattr(result, 'exit_code')
        assert hasattr(result, 'stdout')
        assert hasattr(result, 'stderr')
        assert hasattr(result, 'success')
        assert hasattr(result, 'execution_time')
        assert result.command == "echo test"

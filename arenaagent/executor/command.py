"""Command execution with safety checks and output capture."""

import subprocess
import asyncio
import platform
from pathlib import Path
from typing import Optional, Dict, List
import time
from datetime import datetime
import shlex

from arenaagent.models.execution import ExecutionResult
from arenaagent.utils.logger import get_logger
from arenaagent.utils.validators import is_safe_command


class CommandExecutor:
    """Execute shell commands safely with output capture and timeout handling."""
    
    def __init__(
        self,
        working_dir: Optional[Path] = None,
        timeout: float = 30.0,
        env: Optional[Dict[str, str]] = None,
        check_safety: bool = True,
    ):
        """Initialize command executor.
        
        Args:
            working_dir: Working directory for command execution
            timeout: Default timeout in seconds
            env: Environment variables (None = inherit from parent)
            check_safety: Whether to validate command safety
        """
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.default_timeout = timeout
        self.env = env
        self.check_safety = check_safety
        self.logger = get_logger(__name__)
    
    def execute(
        self,
        command: str,
        timeout: Optional[float] = None,
        check_safety: Optional[bool] = None,
        shell: bool = False,
    ) -> ExecutionResult:
        """Execute a command synchronously.
        
        Args:
            command: Command string to execute
            timeout: Timeout in seconds (None = use default)
            check_safety: Override safety check setting
            shell: Whether to execute through shell
            
        Returns:
            ExecutionResult with command output and status
            
        Raises:
            ValueError: If command is deemed unsafe
            subprocess.TimeoutExpired: If command times out
        """
        timeout = timeout if timeout is not None else self.default_timeout
        check_safety = check_safety if check_safety is not None else self.check_safety
        
        # Safety validation
        if check_safety and not is_safe_command(command):
            self.logger.warning(f"Potentially unsafe command blocked: {command}")
            return ExecutionResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr="Command blocked by safety check",
                success=False,
                execution_time=0.0,
            )
        
        self.logger.info(f"Executing command: {command}")
        
        start_time = time.time()
        
        try:
            # Determine if we're on Windows
            is_windows = platform.system() == "Windows"
            
            # Prepare command for execution
            if shell:
                cmd = command
            else:
                # Split command properly
                if is_windows:
                    # On Windows, use the command as-is for non-shell mode
                    cmd = command
                else:
                    # On Unix, split the command
                    try:
                        cmd = shlex.split(command)
                    except ValueError:
                        # If splitting fails, fall back to shell mode
                        cmd = command
                        shell = True
            
            # Execute command
            process = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self.env,
                shell=shell,
            )
            
            execution_time = time.time() - start_time
            
            # Create result
            result = ExecutionResult(
                command=command,
                exit_code=process.returncode,
                stdout=process.stdout,
                stderr=process.stderr,
                success=(process.returncode == 0),
                execution_time=execution_time,
            )
            
            if result.success:
                self.logger.info(f"Command completed successfully in {execution_time:.2f}s")
            else:
                self.logger.warning(
                    f"Command failed with exit code {result.exit_code} "
                    f"in {execution_time:.2f}s"
                )
            
            return result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            self.logger.error(f"Command timed out after {timeout}s")
            
            return ExecutionResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                success=False,
                execution_time=execution_time,
            )
            
        except FileNotFoundError as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Command not found: {e}")
            
            return ExecutionResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=f"Command not found: {e}",
                success=False,
                execution_time=execution_time,
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Command execution failed: {e}")
            
            return ExecutionResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                success=False,
                execution_time=execution_time,
            )
    
    async def execute_async(
        self,
        command: str,
        timeout: Optional[float] = None,
        check_safety: Optional[bool] = None,
    ) -> ExecutionResult:
        """Execute a command asynchronously.
        
        Args:
            command: Command string to execute
            timeout: Timeout in seconds (None = use default)
            check_safety: Override safety check setting
            
        Returns:
            ExecutionResult with command output and status
        """
        timeout = timeout if timeout is not None else self.default_timeout
        check_safety = check_safety if check_safety is not None else self.check_safety
        
        # Safety validation
        if check_safety and not is_safe_command(command):
            self.logger.warning(f"Potentially unsafe command blocked: {command}")
            return ExecutionResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr="Command blocked by safety check",
                success=False,
                execution_time=0.0,
            )
        
        self.logger.info(f"Executing command (async): {command}")
        
        start_time = time.time()
        
        try:
            # Determine if we're on Windows
            is_windows = platform.system() == "Windows"
            
            # On Windows, use shell for async execution
            if is_windows:
                shell = True
                cmd = command
            else:
                shell = False
                cmd = shlex.split(command)
            
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *([command] if shell else cmd),
                cwd=self.working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self.env,
                shell=shell,
            )
            
            # Wait for completion with timeout
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                stdout = stdout_bytes.decode('utf-8', errors='replace')
                stderr = stderr_bytes.decode('utf-8', errors='replace')
                exit_code = process.returncode
                
            except asyncio.TimeoutError:
                # Kill the process on timeout
                process.kill()
                await process.wait()
                
                execution_time = time.time() - start_time
                self.logger.error(f"Command timed out after {timeout}s")
                
                return ExecutionResult(
                    command=command,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Command timed out after {timeout} seconds",
                    success=False,
                    execution_time=execution_time,
                )
            
            execution_time = time.time() - start_time
            
            # Create result
            result = ExecutionResult(
                command=command,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                success=(exit_code == 0),
                execution_time=execution_time,
            )
            
            if result.success:
                self.logger.info(f"Command completed successfully in {execution_time:.2f}s")
            else:
                self.logger.warning(
                    f"Command failed with exit code {exit_code} "
                    f"in {execution_time:.2f}s"
                )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Command execution failed: {e}")
            
            return ExecutionResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                success=False,
                execution_time=execution_time,
            )
    
    def execute_multiple(
        self,
        commands: List[str],
        stop_on_error: bool = True,
        timeout: Optional[float] = None,
    ) -> List[ExecutionResult]:
        """Execute multiple commands in sequence.
        
        Args:
            commands: List of command strings
            stop_on_error: Stop execution if a command fails
            timeout: Timeout per command
            
        Returns:
            List of ExecutionResult objects
        """
        results = []
        
        for command in commands:
            result = self.execute(command, timeout=timeout)
            results.append(result)
            
            if stop_on_error and not result.success:
                self.logger.warning(
                    f"Stopping execution due to failed command: {command}"
                )
                break
        
        return results
    
    async def execute_multiple_async(
        self,
        commands: List[str],
        stop_on_error: bool = True,
        timeout: Optional[float] = None,
    ) -> List[ExecutionResult]:
        """Execute multiple commands in sequence (async).
        
        Args:
            commands: List of command strings
            stop_on_error: Stop execution if a command fails
            timeout: Timeout per command
            
        Returns:
            List of ExecutionResult objects
        """
        results = []
        
        for command in commands:
            result = await self.execute_async(command, timeout=timeout)
            results.append(result)
            
            if stop_on_error and not result.success:
                self.logger.warning(
                    f"Stopping execution due to failed command: {command}"
                )
                break
        
        return results
    
    def validate_command(self, command: str) -> bool:
        """Validate if a command is safe to execute.
        
        Args:
            command: Command string to validate
            
        Returns:
            True if command is safe, False otherwise
        """
        return is_safe_command(command)
    
    def set_working_directory(self, working_dir: Path) -> None:
        """Set the working directory for command execution.
        
        Args:
            working_dir: New working directory path
        """
        self.working_dir = Path(working_dir)
        self.logger.info(f"Working directory set to: {self.working_dir}")
    
    def set_timeout(self, timeout: float) -> None:
        """Set the default timeout for command execution.
        
        Args:
            timeout: Timeout in seconds
        """
        self.default_timeout = timeout
        self.logger.info(f"Default timeout set to: {timeout}s")
    
    def get_working_directory(self) -> Path:
        """Get the current working directory.
        
        Returns:
            Current working directory path
        """
        return self.working_dir

"""Error detection and classification for command execution."""

import re
from typing import List, Optional, Dict, Tuple
from enum import Enum

from arenaagent.models.execution import ExecutionResult


class ErrorCategory(Enum):
    """Categories of execution errors."""
    
    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_ERROR = "permission_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    MEMORY_ERROR = "memory_error"
    TYPE_ERROR = "type_error"
    VALUE_ERROR = "value_error"
    RUNTIME_ERROR = "runtime_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorPattern:
    """Error detection pattern with category and regex."""
    
    def __init__(self, category: ErrorCategory, pattern: str, description: str):
        """Initialize error pattern.
        
        Args:
            category: Error category
            pattern: Regex pattern to match
            description: Human-readable description
        """
        self.category = category
        self.pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        self.description = description
    
    def matches(self, text: str) -> bool:
        """Check if pattern matches the text.
        
        Args:
            text: Text to check
            
        Returns:
            True if pattern matches
        """
        return bool(self.pattern.search(text))
    
    def find_matches(self, text: str) -> List[str]:
        """Find all matches in text.
        
        Args:
            text: Text to search
            
        Returns:
            List of matched strings
        """
        return self.pattern.findall(text)


class ErrorDetector:
    """Detect and classify errors in command execution output."""
    
    # Predefined error patterns
    ERROR_PATTERNS = [
        # Python errors
        ErrorPattern(
            ErrorCategory.SYNTAX_ERROR,
            r"SyntaxError:.*",
            "Python syntax error"
        ),
        ErrorPattern(
            ErrorCategory.IMPORT_ERROR,
            r"(ImportError|ModuleNotFoundError):.*",
            "Python import error"
        ),
        ErrorPattern(
            ErrorCategory.FILE_NOT_FOUND,
            r"(FileNotFoundError|No such file or directory):.*",
            "File not found"
        ),
        ErrorPattern(
            ErrorCategory.PERMISSION_ERROR,
            r"(PermissionError|Permission denied):.*",
            "Permission denied"
        ),
        ErrorPattern(
            ErrorCategory.TYPE_ERROR,
            r"TypeError:.*",
            "Python type error"
        ),
        ErrorPattern(
            ErrorCategory.VALUE_ERROR,
            r"ValueError:.*",
            "Python value error"
        ),
        ErrorPattern(
            ErrorCategory.MEMORY_ERROR,
            r"(MemoryError|Out of memory):.*",
            "Memory error"
        ),
        
        # Network errors
        ErrorPattern(
            ErrorCategory.NETWORK_ERROR,
            r"(Connection refused|Network is unreachable|Timeout|DNS resolution failed):.*",
            "Network error"
        ),
        
        # Timeout errors
        ErrorPattern(
            ErrorCategory.TIMEOUT_ERROR,
            r"(timed out|timeout|Time limit exceeded):.*",
            "Timeout error"
        ),
        
        # Generic runtime errors
        ErrorPattern(
            ErrorCategory.RUNTIME_ERROR,
            r"(RuntimeError|Error):.*",
            "Runtime error"
        ),
        
        # Shell errors
        ErrorPattern(
            ErrorCategory.FILE_NOT_FOUND,
            r"(command not found|not recognized as an internal or external command):.*",
            "Command not found"
        ),
    ]
    
    def __init__(self):
        """Initialize error detector."""
        self.custom_patterns: List[ErrorPattern] = []
    
    def detect_errors(self, result: ExecutionResult) -> List[Tuple[ErrorCategory, str]]:
        """Detect errors in execution result.
        
        Args:
            result: Execution result to analyze
            
        Returns:
            List of tuples (error_category, error_message)
        """
        errors = []
        
        # Check stderr for errors
        if result.stderr:
            errors.extend(self._scan_text(result.stderr))
        
        # Check stdout for errors (some programs print errors to stdout)
        if result.stdout:
            errors.extend(self._scan_text(result.stdout))
        
        # If no specific errors found but command failed, mark as unknown
        if not errors and not result.success:
            errors.append((
                ErrorCategory.UNKNOWN_ERROR,
                f"Command failed with exit code {result.exit_code}"
            ))
        
        return errors
    
    def _scan_text(self, text: str) -> List[Tuple[ErrorCategory, str]]:
        """Scan text for error patterns.
        
        Args:
            text: Text to scan
            
        Returns:
            List of detected errors
        """
        errors = []
        
        # Check all patterns (built-in + custom)
        all_patterns = self.ERROR_PATTERNS + self.custom_patterns
        
        for pattern in all_patterns:
            if pattern.matches(text):
                matches = pattern.find_matches(text)
                for match in matches:
                    errors.append((pattern.category, match))
        
        return errors
    
    def categorize_error(self, result: ExecutionResult) -> Optional[ErrorCategory]:
        """Get the primary error category for an execution result.
        
        Args:
            result: Execution result to categorize
            
        Returns:
            Primary error category, or None if no errors
        """
        errors = self.detect_errors(result)
        
        if not errors:
            return None
        
        # Return the first (most specific) error category
        return errors[0][0]
    
    def is_retriable(self, result: ExecutionResult) -> bool:
        """Determine if an execution failure is retriable.
        
        Some errors (like network timeouts) are worth retrying,
        while others (like syntax errors) are not.
        
        Args:
            result: Execution result to analyze
            
        Returns:
            True if the error is retriable
        """
        if result.success:
            return False
        
        category = self.categorize_error(result)
        
        # These error types are retriable
        retriable_categories = {
            ErrorCategory.NETWORK_ERROR,
            ErrorCategory.TIMEOUT_ERROR,
            ErrorCategory.UNKNOWN_ERROR,
        }
        
        return category in retriable_categories
    
    def get_error_summary(self, result: ExecutionResult) -> str:
        """Get a human-readable error summary.
        
        Args:
            result: Execution result to summarize
            
        Returns:
            Error summary string
        """
        if result.success:
            return "Command executed successfully"
        
        errors = self.detect_errors(result)
        
        if not errors:
            return f"Command failed with exit code {result.exit_code}"
        
        # Group errors by category
        error_groups: Dict[ErrorCategory, List[str]] = {}
        for category, message in errors:
            if category not in error_groups:
                error_groups[category] = []
            error_groups[category].append(message)
        
        # Build summary
        summary_parts = []
        for category, messages in error_groups.items():
            count = len(messages)
            category_name = category.value.replace('_', ' ').title()
            
            if count == 1:
                summary_parts.append(f"{category_name}: {messages[0]}")
            else:
                summary_parts.append(f"{category_name} ({count} occurrences)")
        
        return " | ".join(summary_parts)
    
    def add_custom_pattern(
        self,
        category: ErrorCategory,
        pattern: str,
        description: str
    ) -> None:
        """Add a custom error pattern.
        
        Args:
            category: Error category
            pattern: Regex pattern
            description: Pattern description
        """
        self.custom_patterns.append(
            ErrorPattern(category, pattern, description)
        )
    
    def suggest_fix(self, result: ExecutionResult) -> Optional[str]:
        """Suggest a fix for the error.
        
        Args:
            result: Execution result with error
            
        Returns:
            Suggested fix, or None if no suggestion available
        """
        category = self.categorize_error(result)
        
        if not category:
            return None
        
        # Suggestions based on error category
        suggestions = {
            ErrorCategory.SYNTAX_ERROR: "Check your code syntax for typos or missing brackets",
            ErrorCategory.IMPORT_ERROR: "Install the missing module using pip or check the import path",
            ErrorCategory.FILE_NOT_FOUND: "Verify the file path exists and is spelled correctly",
            ErrorCategory.PERMISSION_ERROR: "Check file permissions or run with appropriate privileges",
            ErrorCategory.NETWORK_ERROR: "Check your network connection and try again",
            ErrorCategory.TIMEOUT_ERROR: "The operation took too long. Try increasing the timeout or checking system resources",
            ErrorCategory.MEMORY_ERROR: "The operation ran out of memory. Try processing smaller chunks or increasing available memory",
            ErrorCategory.TYPE_ERROR: "Check that you're using the correct data types",
            ErrorCategory.VALUE_ERROR: "Check that input values are in the expected range or format",
        }
        
        return suggestions.get(category)

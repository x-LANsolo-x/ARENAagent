"""Unit tests for ErrorDetector class."""

import pytest
from arenaagent.executor.error_detector import (
    ErrorDetector,
    ErrorCategory,
    ErrorPattern,
)
from arenaagent.models.execution import ExecutionResult


class TestErrorPattern:
    """Test ErrorPattern class."""
    
    def test_pattern_initialization(self):
        """Test creating an error pattern."""
        pattern = ErrorPattern(
            ErrorCategory.SYNTAX_ERROR,
            r"SyntaxError:.*",
            "Python syntax error"
        )
        
        assert pattern.category == ErrorCategory.SYNTAX_ERROR
        assert pattern.description == "Python syntax error"
    
    def test_pattern_matches(self):
        """Test pattern matching."""
        pattern = ErrorPattern(
            ErrorCategory.IMPORT_ERROR,
            r"ImportError:.*",
            "Import error"
        )
        
        assert pattern.matches("ImportError: No module named 'foo'") is True
        assert pattern.matches("SyntaxError: invalid syntax") is False
    
    def test_pattern_find_matches(self):
        """Test finding all matches."""
        pattern = ErrorPattern(
            ErrorCategory.TYPE_ERROR,
            r"TypeError:.*",
            "Type error"
        )
        
        text = "TypeError: unsupported operand\nOther text\nTypeError: cannot concat"
        matches = pattern.find_matches(text)
        
        assert len(matches) == 2
        assert "unsupported operand" in matches[0]
        assert "cannot concat" in matches[1]


class TestErrorDetector:
    """Test ErrorDetector class."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = ErrorDetector()
        
        assert isinstance(detector, ErrorDetector)
        assert len(detector.custom_patterns) == 0
    
    def test_detect_python_syntax_error(self):
        """Test detection of Python syntax errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="python test.py",
            exit_code=1,
            stdout="",
            stderr="SyntaxError: invalid syntax",
            success=False,
            execution_time=0.1
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) > 0
        assert errors[0][0] == ErrorCategory.SYNTAX_ERROR
    
    def test_detect_import_error(self):
        """Test detection of import errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="python script.py",
            exit_code=1,
            stdout="",
            stderr="ImportError: No module named 'requests'",
            success=False,
            execution_time=0.2
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) > 0
        assert errors[0][0] == ErrorCategory.IMPORT_ERROR
    
    def test_detect_file_not_found(self):
        """Test detection of file not found errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="cat missing.txt",
            exit_code=1,
            stdout="",
            stderr="No such file or directory: missing.txt",
            success=False,
            execution_time=0.1
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) > 0
        assert errors[0][0] == ErrorCategory.FILE_NOT_FOUND
    
    def test_detect_permission_error(self):
        """Test detection of permission errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="write file.txt",
            exit_code=1,
            stdout="",
            stderr="PermissionError: Permission denied",
            success=False,
            execution_time=0.1
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) > 0
        assert errors[0][0] == ErrorCategory.PERMISSION_ERROR
    
    def test_detect_network_error(self):
        """Test detection of network errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="curl example.com",
            exit_code=1,
            stdout="",
            stderr="Connection refused",
            success=False,
            execution_time=5.0
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) > 0
        assert errors[0][0] == ErrorCategory.NETWORK_ERROR
    
    def test_detect_timeout_error(self):
        """Test detection of timeout errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="long_running_command",
            exit_code=124,
            stdout="",
            stderr="Command timed out after 30 seconds",
            success=False,
            execution_time=30.0
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) > 0
        assert errors[0][0] == ErrorCategory.TIMEOUT_ERROR
    
    def test_detect_type_error(self):
        """Test detection of type errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="python test.py",
            exit_code=1,
            stdout="",
            stderr="TypeError: unsupported operand type(s) for +: 'int' and 'str'",
            success=False,
            execution_time=0.1
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) > 0
        assert errors[0][0] == ErrorCategory.TYPE_ERROR
    
    def test_detect_value_error(self):
        """Test detection of value errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="python test.py",
            exit_code=1,
            stdout="",
            stderr="ValueError: invalid literal for int() with base 10: 'abc'",
            success=False,
            execution_time=0.1
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) > 0
        assert errors[0][0] == ErrorCategory.VALUE_ERROR
    
    def test_detect_memory_error(self):
        """Test detection of memory errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="python memory_intensive.py",
            exit_code=1,
            stdout="",
            stderr="MemoryError: Out of memory",
            success=False,
            execution_time=10.0
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) > 0
        assert errors[0][0] == ErrorCategory.MEMORY_ERROR
    
    def test_detect_command_not_found(self):
        """Test detection of command not found errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="nonexistentcommand",
            exit_code=127,
            stdout="",
            stderr="command not found: nonexistentcommand",
            success=False,
            execution_time=0.1
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) > 0
        assert errors[0][0] == ErrorCategory.FILE_NOT_FOUND
    
    def test_detect_multiple_errors(self):
        """Test detection of multiple errors in output."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="python test.py",
            exit_code=1,
            stdout="",
            stderr="ImportError: No module 'foo'\nTypeError: bad operand",
            success=False,
            execution_time=0.1
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) >= 2
        categories = [err[0] for err in errors]
        assert ErrorCategory.IMPORT_ERROR in categories
        assert ErrorCategory.TYPE_ERROR in categories
    
    def test_detect_unknown_error(self):
        """Test detection of unknown errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="some command",
            exit_code=1,
            stdout="",
            stderr="Some unknown error occurred",
            success=False,
            execution_time=0.1
        )
        
        errors = detector.detect_errors(result)
        
        # Should detect at least one error
        assert len(errors) > 0
    
    def test_no_errors_on_success(self):
        """Test no errors detected for successful execution."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="echo hello",
            exit_code=0,
            stdout="hello",
            stderr="",
            success=True,
            execution_time=0.1
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) == 0
    
    def test_categorize_error(self):
        """Test error categorization."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="python test.py",
            exit_code=1,
            stdout="",
            stderr="SyntaxError: invalid syntax",
            success=False,
            execution_time=0.1
        )
        
        category = detector.categorize_error(result)
        
        assert category == ErrorCategory.SYNTAX_ERROR
    
    def test_categorize_no_error(self):
        """Test categorization when no errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="echo test",
            exit_code=0,
            stdout="test",
            stderr="",
            success=True,
            execution_time=0.1
        )
        
        category = detector.categorize_error(result)
        
        assert category is None
    
    def test_is_retriable_network_error(self):
        """Test that network errors are retriable."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="curl example.com",
            exit_code=1,
            stdout="",
            stderr="Connection refused",
            success=False,
            execution_time=1.0
        )
        
        assert detector.is_retriable(result) is True
    
    def test_is_retriable_timeout_error(self):
        """Test that timeout errors are retriable."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="long command",
            exit_code=124,
            stdout="",
            stderr="Command timed out",
            success=False,
            execution_time=30.0
        )
        
        assert detector.is_retriable(result) is True
    
    def test_is_not_retriable_syntax_error(self):
        """Test that syntax errors are not retriable."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="python bad.py",
            exit_code=1,
            stdout="",
            stderr="SyntaxError: invalid syntax",
            success=False,
            execution_time=0.1
        )
        
        assert detector.is_retriable(result) is False
    
    def test_is_not_retriable_success(self):
        """Test that successful executions are not retriable."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="echo test",
            exit_code=0,
            stdout="test",
            stderr="",
            success=True,
            execution_time=0.1
        )
        
        assert detector.is_retriable(result) is False
    
    def test_get_error_summary_success(self):
        """Test error summary for successful execution."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="echo test",
            exit_code=0,
            stdout="test",
            stderr="",
            success=True,
            execution_time=0.1
        )
        
        summary = detector.get_error_summary(result)
        
        assert "success" in summary.lower()
    
    def test_get_error_summary_with_errors(self):
        """Test error summary with detected errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="python test.py",
            exit_code=1,
            stdout="",
            stderr="SyntaxError: invalid syntax",
            success=False,
            execution_time=0.1
        )
        
        summary = detector.get_error_summary(result)
        
        assert "syntax" in summary.lower()
    
    def test_get_error_summary_multiple_errors(self):
        """Test error summary with multiple errors."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="python test.py",
            exit_code=1,
            stdout="",
            stderr="ImportError: No module\nTypeError: bad type",
            success=False,
            execution_time=0.1
        )
        
        summary = detector.get_error_summary(result)
        
        assert "import" in summary.lower() or "type" in summary.lower()
    
    def test_add_custom_pattern(self):
        """Test adding custom error pattern."""
        detector = ErrorDetector()
        
        initial_count = len(detector.custom_patterns)
        
        detector.add_custom_pattern(
            ErrorCategory.RUNTIME_ERROR,
            r"CustomError:.*",
            "Custom error pattern"
        )
        
        assert len(detector.custom_patterns) == initial_count + 1
    
    def test_custom_pattern_detection(self):
        """Test that custom patterns are detected."""
        detector = ErrorDetector()
        
        detector.add_custom_pattern(
            ErrorCategory.RUNTIME_ERROR,
            r"MyCustomError:.*",
            "My custom error"
        )
        
        result = ExecutionResult(
            command="test",
            exit_code=1,
            stdout="",
            stderr="MyCustomError: something went wrong",
            success=False,
            execution_time=0.1
        )
        
        errors = detector.detect_errors(result)
        
        assert len(errors) > 0
        assert any(err[0] == ErrorCategory.RUNTIME_ERROR for err in errors)
    
    def test_suggest_fix_syntax_error(self):
        """Test fix suggestion for syntax error."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="python test.py",
            exit_code=1,
            stdout="",
            stderr="SyntaxError: invalid syntax",
            success=False,
            execution_time=0.1
        )
        
        suggestion = detector.suggest_fix(result)
        
        assert suggestion is not None
        assert "syntax" in suggestion.lower()
    
    def test_suggest_fix_import_error(self):
        """Test fix suggestion for import error."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="python test.py",
            exit_code=1,
            stdout="",
            stderr="ImportError: No module named 'requests'",
            success=False,
            execution_time=0.1
        )
        
        suggestion = detector.suggest_fix(result)
        
        assert suggestion is not None
        assert "pip" in suggestion.lower() or "install" in suggestion.lower()
    
    def test_suggest_fix_network_error(self):
        """Test fix suggestion for network error."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="curl example.com",
            exit_code=1,
            stdout="",
            stderr="Connection refused",
            success=False,
            execution_time=1.0
        )
        
        suggestion = detector.suggest_fix(result)
        
        assert suggestion is not None
        assert "network" in suggestion.lower()
    
    def test_suggest_fix_no_suggestion(self):
        """Test no suggestion for successful execution."""
        detector = ErrorDetector()
        
        result = ExecutionResult(
            command="echo test",
            exit_code=0,
            stdout="test",
            stderr="",
            success=True,
            execution_time=0.1
        )
        
        suggestion = detector.suggest_fix(result)
        
        assert suggestion is None


class TestErrorCategory:
    """Test ErrorCategory enum."""
    
    def test_all_categories_exist(self):
        """Test that all expected categories exist."""
        expected_categories = [
            "SYNTAX_ERROR",
            "IMPORT_ERROR",
            "FILE_NOT_FOUND",
            "PERMISSION_ERROR",
            "NETWORK_ERROR",
            "TIMEOUT_ERROR",
            "MEMORY_ERROR",
            "TYPE_ERROR",
            "VALUE_ERROR",
            "RUNTIME_ERROR",
            "UNKNOWN_ERROR",
        ]
        
        for category_name in expected_categories:
            assert hasattr(ErrorCategory, category_name)
    
    def test_category_values(self):
        """Test category values are strings."""
        for category in ErrorCategory:
            assert isinstance(category.value, str)
            assert category.value == category.name.lower()

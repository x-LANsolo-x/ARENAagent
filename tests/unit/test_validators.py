"""Unit tests for validators utility module."""

import pytest
from arenaagent.utils.validators import (
    validate_path,
    validate_url,
    is_safe_command,
    validate_json_structure,
    validate_session_id,
    validate_log_level,
    validate_port,
    validate_timeout,
    validate_retry_count,
    sanitize_filename,
    validate_code_language,
)


class TestValidatePath:
    """Test path validation."""
    
    def test_valid_absolute_path(self):
        """Test validation of valid absolute path."""
        assert validate_path("/tmp/test.txt") is True
        assert validate_path("/home/user/file.py") is True
    
    def test_valid_relative_path(self):
        """Test validation of valid relative path."""
        assert validate_path("test.txt") is True
        assert validate_path("./test.txt") is True
        assert validate_path("../test.txt") is True
    
    def test_invalid_path_with_null(self):
        """Test that paths with null characters are invalid."""
        assert validate_path("/tmp/test\0.txt") is False
    
    def test_must_exist_parameter(self, tmp_path):
        """Test must_exist parameter."""
        existing_file = tmp_path / "existing.txt"
        existing_file.write_text("test")
        
        # Existing file should be valid
        assert validate_path(str(existing_file), must_exist=True) is True
        
        # Non-existing file should be invalid with must_exist=True
        assert validate_path(str(tmp_path / "nonexistent.txt"), must_exist=True) is False
        
        # Non-existing file should be valid with must_exist=False
        assert validate_path(str(tmp_path / "nonexistent.txt"), must_exist=False) is True


class TestValidateUrl:
    """Test URL validation."""
    
    def test_valid_http_url(self):
        """Test validation of valid HTTP URLs."""
        assert validate_url("http://example.com") is True
        assert validate_url("http://example.com/path") is True
        assert validate_url("http://example.com:8080") is True
    
    def test_valid_https_url(self):
        """Test validation of valid HTTPS URLs."""
        assert validate_url("https://example.com") is True
        assert validate_url("https://example.com/path/to/page") is True
    
    def test_valid_url_with_query(self):
        """Test URLs with query parameters."""
        assert validate_url("https://example.com?key=value") is True
        assert validate_url("https://example.com/path?key1=val1&key2=val2") is True
    
    def test_invalid_url_no_scheme(self):
        """Test that URLs without scheme are invalid."""
        assert validate_url("example.com") is False
        assert validate_url("www.example.com") is False
    
    def test_invalid_url_no_netloc(self):
        """Test that URLs without netloc are invalid."""
        assert validate_url("http://") is False
        assert validate_url("https://") is False
    
    def test_invalid_url_malformed(self):
        """Test malformed URLs."""
        assert validate_url("not a url") is False
        assert validate_url("") is False


class TestIsSafeCommand:
    """Test command safety validation."""
    
    def test_safe_commands(self):
        """Test that safe commands are recognized."""
        assert is_safe_command("ls -la") is True
        assert is_safe_command("echo hello") is True
        assert is_safe_command("python script.py") is True
        assert is_safe_command("git status") is True
        assert is_safe_command("cat file.txt") is True
    
    def test_dangerous_rm_rf(self):
        """Test that rm -rf is blocked."""
        assert is_safe_command("rm -rf /") is False
        assert is_safe_command("rm -fr /tmp") is False
        assert is_safe_command("rm -rf *") is False
    
    def test_dangerous_dd(self):
        """Test that dd commands are blocked."""
        assert is_safe_command("dd if=/dev/zero of=/dev/sda") is False
    
    def test_dangerous_format(self):
        """Test that format commands are blocked."""
        assert is_safe_command("mkfs /dev/sda") is False
        assert is_safe_command("format c:") is False
    
    def test_dangerous_shutdown(self):
        """Test that shutdown commands are blocked."""
        assert is_safe_command("shutdown -h now") is False
        assert is_safe_command("reboot") is False
        assert is_safe_command("halt") is False
        assert is_safe_command("poweroff") is False
    
    def test_dangerous_chmod_777(self):
        """Test that chmod 777 -R is blocked."""
        assert is_safe_command("chmod -R 777 /") is False


class TestValidateJsonStructure:
    """Test JSON structure validation."""
    
    def test_valid_structure(self):
        """Test validation of valid JSON structure."""
        data = {"name": "test", "value": 123}
        assert validate_json_structure(data, ["name", "value"]) is True
    
    def test_valid_structure_extra_keys(self):
        """Test that extra keys are allowed."""
        data = {"name": "test", "value": 123, "extra": "data"}
        assert validate_json_structure(data, ["name", "value"]) is True
    
    def test_invalid_structure_missing_key(self):
        """Test that missing required keys are detected."""
        data = {"name": "test"}
        assert validate_json_structure(data, ["name", "value"]) is False
    
    def test_invalid_not_dict(self):
        """Test that non-dict data is invalid."""
        assert validate_json_structure([], ["key"]) is False
        assert validate_json_structure("string", ["key"]) is False
        assert validate_json_structure(123, ["key"]) is False
    
    def test_empty_required_keys(self):
        """Test with empty required keys list."""
        assert validate_json_structure({}, []) is True
        assert validate_json_structure({"key": "value"}, []) is True


class TestValidateSessionId:
    """Test session ID validation."""
    
    def test_valid_session_ids(self):
        """Test valid session ID formats."""
        assert validate_session_id("session123") is True
        assert validate_session_id("session-123") is True
        assert validate_session_id("session_123") is True
        assert validate_session_id("abc123-xyz_789") is True
    
    def test_invalid_empty_session_id(self):
        """Test that empty session ID is invalid."""
        assert validate_session_id("") is False
    
    def test_invalid_special_characters(self):
        """Test that special characters are invalid."""
        assert validate_session_id("session@123") is False
        assert validate_session_id("session#123") is False
        assert validate_session_id("session 123") is False
        assert validate_session_id("session/123") is False
    
    def test_invalid_too_long(self):
        """Test that overly long session IDs are invalid."""
        long_id = "a" * 256
        assert validate_session_id(long_id) is False


class TestValidateLogLevel:
    """Test log level validation."""
    
    def test_valid_log_levels(self):
        """Test valid log levels."""
        assert validate_log_level("DEBUG") is True
        assert validate_log_level("INFO") is True
        assert validate_log_level("WARNING") is True
        assert validate_log_level("ERROR") is True
        assert validate_log_level("CRITICAL") is True
    
    def test_valid_lowercase(self):
        """Test that lowercase levels are accepted."""
        assert validate_log_level("debug") is True
        assert validate_log_level("info") is True
        assert validate_log_level("warning") is True
    
    def test_invalid_log_level(self):
        """Test invalid log levels."""
        assert validate_log_level("INVALID") is False
        assert validate_log_level("TRACE") is False
        assert validate_log_level("") is False


class TestValidatePort:
    """Test port number validation."""
    
    def test_valid_ports(self):
        """Test valid port numbers."""
        assert validate_port(80) is True
        assert validate_port(443) is True
        assert validate_port(8080) is True
        assert validate_port(1) is True
        assert validate_port(65535) is True
    
    def test_invalid_port_zero(self):
        """Test that port 0 is invalid."""
        assert validate_port(0) is False
    
    def test_invalid_port_negative(self):
        """Test that negative ports are invalid."""
        assert validate_port(-1) is False
        assert validate_port(-8080) is False
    
    def test_invalid_port_too_high(self):
        """Test that ports > 65535 are invalid."""
        assert validate_port(65536) is False
        assert validate_port(100000) is False
    
    def test_invalid_port_not_int(self):
        """Test that non-integer ports are invalid."""
        assert validate_port("8080") is False
        assert validate_port(80.5) is False


class TestValidateTimeout:
    """Test timeout validation."""
    
    def test_valid_timeouts(self):
        """Test valid timeout values."""
        assert validate_timeout(1.0) is True
        assert validate_timeout(30) is True
        assert validate_timeout(0.5) is True
        assert validate_timeout(100.5) is True
    
    def test_invalid_zero_timeout(self):
        """Test that zero timeout is invalid."""
        assert validate_timeout(0) is False
        assert validate_timeout(0.0) is False
    
    def test_invalid_negative_timeout(self):
        """Test that negative timeouts are invalid."""
        assert validate_timeout(-1) is False
        assert validate_timeout(-10.5) is False
    
    def test_invalid_timeout_not_number(self):
        """Test that non-numeric timeouts are invalid."""
        assert validate_timeout("30") is False
        assert validate_timeout(None) is False


class TestValidateRetryCount:
    """Test retry count validation."""
    
    def test_valid_retry_counts(self):
        """Test valid retry counts."""
        assert validate_retry_count(0) is True
        assert validate_retry_count(1) is True
        assert validate_retry_count(3) is True
        assert validate_retry_count(10) is True
    
    def test_invalid_negative_retries(self):
        """Test that negative retries are invalid."""
        assert validate_retry_count(-1) is False
        assert validate_retry_count(-10) is False
    
    def test_invalid_not_int(self):
        """Test that non-integer retries are invalid."""
        assert validate_retry_count(3.5) is False
        assert validate_retry_count("3") is False


class TestSanitizeFilename:
    """Test filename sanitization."""
    
    def test_clean_filename(self):
        """Test that clean filenames pass through."""
        assert sanitize_filename("test.txt") == "test.txt"
        assert sanitize_filename("my-file_123.py") == "my-file_123.py"
    
    def test_remove_dangerous_characters(self):
        """Test removal of dangerous characters."""
        assert sanitize_filename("test/file.txt") == "testfile.txt"
        assert sanitize_filename("test\\file.txt") == "testfile.txt"
        assert sanitize_filename("test:file.txt") == "testfile.txt"
        assert sanitize_filename("test*file.txt") == "testfile.txt"
    
    def test_trim_spaces(self):
        """Test trimming of leading/trailing spaces."""
        assert sanitize_filename("  test.txt  ") == "test.txt"
        assert sanitize_filename("test.txt ") == "test.txt"
    
    def test_replace_multiple_spaces(self):
        """Test replacement of multiple spaces."""
        assert sanitize_filename("test    file.txt") == "test file.txt"
    
    def test_length_limit(self):
        """Test filename length limiting."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".txt")
    
    def test_empty_filename(self):
        """Test that empty filenames get default."""
        assert sanitize_filename("") == "unnamed"
        assert sanitize_filename("***") == "unnamed"


class TestValidateCodeLanguage:
    """Test code language validation."""
    
    def test_valid_languages(self):
        """Test valid programming languages."""
        assert validate_code_language("python") is True
        assert validate_code_language("javascript") is True
        assert validate_code_language("java") is True
        assert validate_code_language("cpp") is True
        assert validate_code_language("c++") is True
    
    def test_valid_markup_languages(self):
        """Test valid markup languages."""
        assert validate_code_language("html") is True
        assert validate_code_language("css") is True
        assert validate_code_language("xml") is True
        assert validate_code_language("json") is True
    
    def test_valid_case_insensitive(self):
        """Test that validation is case-insensitive."""
        assert validate_code_language("Python") is True
        assert validate_code_language("PYTHON") is True
        assert validate_code_language("JavaScript") is True
    
    def test_invalid_language(self):
        """Test invalid language names."""
        assert validate_code_language("notaprogramminglanguage") is False
        assert validate_code_language("xyz") is False
        assert validate_code_language("") is False

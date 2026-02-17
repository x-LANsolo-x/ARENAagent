"""Validation utilities for ArenaAgent."""

from pathlib import Path
from typing import Any, Dict, List
import re
from urllib.parse import urlparse


def validate_path(path: str, must_exist: bool = False) -> bool:
    """Validate file/directory path.
    
    Args:
        path: Path string to validate
        must_exist: If True, path must exist on filesystem
        
    Returns:
        True if path is valid, False otherwise
    """
    try:
        p = Path(path)
        
        # Check for invalid characters
        if '\0' in path:
            return False
            
        # Check if path exists if required
        if must_exist and not p.exists():
            return False
            
        return True
    except (ValueError, OSError):
        return False


def validate_url(url: str) -> bool:
    """Validate URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_safe_command(command: str) -> bool:
    """Check if command is safe to execute.
    
    Blocks potentially dangerous commands like:
    - rm -rf
    - dd
    - Format commands
    - Shutdown/reboot commands
    
    Args:
        command: Command string to validate
        
    Returns:
        True if command appears safe, False if potentially dangerous
    """
    # List of dangerous command patterns
    dangerous_patterns = [
        r'\brm\s+-rf\b',
        r'\brm\s+-fr\b',
        r'\bdd\b.*if=.*of=',
        r'\bmkfs\b',
        r'\bformat\b',
        r'\bshutdown\b',
        r'\breboot\b',
        r'\bhalt\b',
        r'\bpoweroff\b',
        r'\b:\(\)\s*{\s*:\s*\|\s*:\s*&\s*}\s*;\s*:\b',  # Fork bomb
        r'>\s*/dev/(sd[a-z]|hd[a-z]|nvme)',  # Writing to disk devices
        r'\bchmod\s+-R\s+777',  # Chmod 777 recursive
        r'\bchown\s+-R',  # Chown recursive (can be dangerous)
        r'/dev/null',  # Sometimes used maliciously
    ]
    
    command_lower = command.lower()
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command_lower, re.IGNORECASE):
            return False
    
    return True


def validate_json_structure(data: Any, required_keys: List[str]) -> bool:
    """Validate JSON structure has required keys.
    
    Args:
        data: Data structure to validate (usually dict)
        required_keys: List of required key names
        
    Returns:
        True if all required keys present, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    return all(key in data for key in required_keys)


def validate_session_id(session_id: str) -> bool:
    """Validate session ID format.
    
    Session IDs should be alphanumeric with hyphens/underscores.
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not session_id:
        return False
    
    # Allow alphanumeric, hyphens, and underscores
    # Length between 1 and 255 characters
    pattern = r'^[a-zA-Z0-9_-]{1,255}$'
    return bool(re.match(pattern, session_id))


def validate_log_level(level: str) -> bool:
    """Validate logging level.
    
    Args:
        level: Log level string
        
    Returns:
        True if valid log level, False otherwise
    """
    valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
    return level.upper() in valid_levels


def validate_port(port: int) -> bool:
    """Validate port number.
    
    Args:
        port: Port number to validate
        
    Returns:
        True if valid port (1-65535), False otherwise
    """
    return isinstance(port, int) and 1 <= port <= 65535


def validate_timeout(timeout: float) -> bool:
    """Validate timeout value.
    
    Args:
        timeout: Timeout value in seconds
        
    Returns:
        True if valid timeout (positive number), False otherwise
    """
    try:
        return float(timeout) > 0
    except (ValueError, TypeError):
        return False


def validate_retry_count(retries: int) -> bool:
    """Validate retry count.
    
    Args:
        retries: Number of retries
        
    Returns:
        True if valid (non-negative integer), False otherwise
    """
    return isinstance(retries, int) and retries >= 0


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove or replace dangerous characters
    # Keep alphanumeric, dots, hyphens, underscores
    sanitized = re.sub(r'[^\w\s.-]', '', filename)
    
    # Replace multiple spaces with single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Trim spaces from ends
    sanitized = sanitized.strip()
    
    # Limit length to 255 characters (common filesystem limit)
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        if ext:
            max_name_len = 255 - len(ext) - 1
            sanitized = f"{name[:max_name_len]}.{ext}"
        else:
            sanitized = sanitized[:255]
    
    return sanitized or 'unnamed'


def validate_code_language(language: str) -> bool:
    """Validate programming language identifier.
    
    Args:
        language: Programming language name
        
    Returns:
        True if recognized language, False otherwise
    """
    recognized_languages = {
        'python', 'javascript', 'typescript', 'java', 'c', 'cpp', 'c++',
        'csharp', 'c#', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin',
        'scala', 'r', 'sql', 'html', 'css', 'bash', 'shell', 'powershell',
        'json', 'yaml', 'xml', 'markdown', 'text', 'plaintext'
    }
    
    return language.lower() in recognized_languages

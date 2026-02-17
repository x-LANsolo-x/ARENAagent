"""File operation utilities for ArenaAgent."""

from pathlib import Path
from typing import Union, Optional
import shutil
import tempfile
import os
from datetime import datetime


def atomic_write(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> None:
    """Write file atomically using temp file + rename.
    
    This ensures that the file is either fully written or not written at all,
    preventing corruption from partial writes.
    
    Args:
        file_path: Path to file to write
        content: Content to write
        encoding: File encoding (default: utf-8)
    """
    file_path = Path(file_path)
    
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temporary file in same directory
    # (same directory ensures atomic rename on same filesystem)
    temp_fd, temp_path = tempfile.mkstemp(
        dir=file_path.parent,
        prefix=f".{file_path.name}.",
        suffix=".tmp"
    )
    
    try:
        # Write content to temp file
        with os.fdopen(temp_fd, 'w', encoding=encoding) as f:
            f.write(content)
        
        # Atomic rename
        shutil.move(temp_path, file_path)
        
    except Exception:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def safe_delete(file_path: Union[str, Path]) -> bool:
    """Safely delete file with error handling.
    
    Args:
        file_path: Path to file to delete
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        file_path = Path(file_path)
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except (OSError, PermissionError):
        return False


def ensure_directory(dir_path: Union[str, Path]) -> None:
    """Ensure directory exists, create if not.
    
    Args:
        dir_path: Path to directory
    """
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def get_file_size(file_path: Union[str, Path]) -> int:
    """Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes, or 0 if file doesn't exist
    """
    try:
        return Path(file_path).stat().st_size
    except (OSError, FileNotFoundError):
        return 0


def copy_with_backup(
    src: Union[str, Path],
    dst: Union[str, Path],
    backup_suffix: str = ".backup"
) -> Optional[Path]:
    """Copy file, backing up destination if it exists.
    
    Args:
        src: Source file path
        dst: Destination file path
        backup_suffix: Suffix for backup file
        
    Returns:
        Path to backup file if created, None otherwise
    """
    src = Path(src)
    dst = Path(dst)
    backup_path = None
    
    # Create backup if destination exists
    if dst.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = dst.parent / f"{dst.name}{backup_suffix}.{timestamp}"
        shutil.copy2(dst, backup_path)
    
    # Copy source to destination
    shutil.copy2(src, dst)
    
    return backup_path


def read_file_safe(
    file_path: Union[str, Path],
    encoding: str = 'utf-8',
    default: str = ""
) -> str:
    """Safely read file content with error handling.
    
    Args:
        file_path: Path to file
        encoding: File encoding
        default: Default value if file can't be read
        
    Returns:
        File content or default value
    """
    try:
        return Path(file_path).read_text(encoding=encoding)
    except (OSError, FileNotFoundError, UnicodeDecodeError):
        return default


def write_file_safe(
    file_path: Union[str, Path],
    content: str,
    encoding: str = 'utf-8',
    create_dirs: bool = True
) -> bool:
    """Safely write file content with error handling.
    
    Args:
        file_path: Path to file
        content: Content to write
        encoding: File encoding
        create_dirs: Create parent directories if they don't exist
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(file_path)
        
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_path.write_text(content, encoding=encoding)
        return True
    except (OSError, PermissionError):
        return False


def list_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False
) -> list[Path]:
    """List files in directory matching pattern.
    
    Args:
        directory: Directory path
        pattern: Glob pattern (default: all files)
        recursive: Search recursively if True
        
    Returns:
        List of matching file paths
    """
    directory = Path(directory)
    
    if not directory.exists() or not directory.is_dir():
        return []
    
    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))


def get_file_info(file_path: Union[str, Path]) -> dict:
    """Get file information.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {
            'exists': False,
            'path': str(file_path),
        }
    
    stat = file_path.stat()
    
    return {
        'exists': True,
        'path': str(file_path),
        'size': stat.st_size,
        'created': datetime.fromtimestamp(stat.st_ctime),
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'is_file': file_path.is_file(),
        'is_dir': file_path.is_dir(),
    }


def create_backup(
    file_path: Union[str, Path],
    backup_dir: Optional[Union[str, Path]] = None
) -> Optional[Path]:
    """Create a timestamped backup of a file.
    
    Args:
        file_path: Path to file to backup
        backup_dir: Directory for backup (default: same as original)
        
    Returns:
        Path to backup file, or None if backup failed
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return None
    
    # Determine backup location
    if backup_dir:
        backup_dir = Path(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
    else:
        backup_dir = file_path.parent
    
    # Create timestamped backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{file_path.name}.backup.{timestamp}"
    
    try:
        shutil.copy2(file_path, backup_path)
        return backup_path
    except (OSError, PermissionError):
        return None


def clean_old_backups(
    directory: Union[str, Path],
    pattern: str = "*.backup.*",
    keep_count: int = 5
) -> int:
    """Clean old backup files, keeping only the most recent ones.
    
    Args:
        directory: Directory containing backups
        pattern: Glob pattern for backup files
        keep_count: Number of recent backups to keep
        
    Returns:
        Number of backup files deleted
    """
    directory = Path(directory)
    
    if not directory.exists():
        return 0
    
    # Find all backup files
    backups = sorted(
        directory.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    # Delete old backups
    deleted = 0
    for backup in backups[keep_count:]:
        try:
            backup.unlink()
            deleted += 1
        except OSError:
            pass
    
    return deleted


def is_empty_directory(directory: Union[str, Path]) -> bool:
    """Check if directory is empty.
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory is empty, False otherwise
    """
    directory = Path(directory)
    
    if not directory.exists() or not directory.is_dir():
        return False
    
    return not any(directory.iterdir())


def get_unique_filename(
    file_path: Union[str, Path],
    separator: str = "_"
) -> Path:
    """Get a unique filename by adding a number suffix if file exists.
    
    Args:
        file_path: Desired file path
        separator: Separator before number suffix
        
    Returns:
        Unique file path
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return file_path
    
    # Split name and extension
    stem = file_path.stem
    suffix = file_path.suffix
    parent = file_path.parent
    
    # Try numbered variants
    counter = 1
    while True:
        new_path = parent / f"{stem}{separator}{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1
        
        # Safety limit
        if counter > 10000:
            raise ValueError(f"Could not find unique filename for {file_path}")

"""Configuration management for ArenaAgent.

This module provides the ConfigManager class for handling application
configuration, including loading, saving, and updating settings.
"""

from pathlib import Path
from typing import Optional, Any, Dict
import json
import shutil
from datetime import datetime

from arenaagent.utils.logger import get_logger


class Config:
    """Application configuration data class.
    
    Attributes:
        browser_headless: Run browser in headless mode
        browser_user_data_dir: Directory for browser profile data
        session_dir: Directory for session storage
        model_name: Default LM Arena model to use
        max_retries: Maximum retry attempts for operations
        timeout: Default timeout in seconds
        auto_execute: Automatically execute suggested code
        backup_enabled: Enable automatic file backups
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    
    def __init__(
        self,
        browser_headless: bool = False,
        browser_user_data_dir: str = "",
        session_dir: str = "",
        model_name: str = "claude-3-5-sonnet-20241022",
        max_retries: int = 3,
        timeout: int = 30,
        auto_execute: bool = False,
        backup_enabled: bool = True,
        log_level: str = "INFO",
    ):
        """Initialize configuration."""
        self.browser_headless = browser_headless
        self.browser_user_data_dir = browser_user_data_dir
        self.session_dir = session_dir
        self.model_name = model_name
        self.max_retries = max_retries
        self.timeout = timeout
        self.auto_execute = auto_execute
        self.backup_enabled = backup_enabled
        self.log_level = log_level
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            "browser_headless": self.browser_headless,
            "browser_user_data_dir": self.browser_user_data_dir,
            "session_dir": self.session_dir,
            "model_name": self.model_name,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "auto_execute": self.auto_execute,
            "backup_enabled": self.backup_enabled,
            "log_level": self.log_level,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create configuration from dictionary.
        
        Args:
            data: Dictionary containing configuration data
            
        Returns:
            New Config instance
        """
        return cls(
            browser_headless=data.get("browser_headless", False),
            browser_user_data_dir=data.get("browser_user_data_dir", ""),
            session_dir=data.get("session_dir", ""),
            model_name=data.get("model_name", "claude-3-5-sonnet-20241022"),
            max_retries=data.get("max_retries", 3),
            timeout=data.get("timeout", 30),
            auto_execute=data.get("auto_execute", False),
            backup_enabled=data.get("backup_enabled", True),
            log_level=data.get("log_level", "INFO"),
        )
    
    @classmethod
    def default(cls, base_dir: Optional[Path] = None) -> "Config":
        """Create default configuration.
        
        Args:
            base_dir: Base directory for ArenaAgent data (defaults to ~/.arenaagent)
            
        Returns:
            Default Config instance
        """
        if base_dir is None:
            base_dir = Path.home() / ".arenaagent"
        
        return cls(
            browser_headless=False,
            browser_user_data_dir=str(base_dir / "browser"),
            session_dir=str(base_dir / "sessions"),
            model_name="claude-3-5-sonnet-20241022",
            max_retries=3,
            timeout=30,
            auto_execute=False,
            backup_enabled=True,
            log_level="INFO",
        )
    
    def validate(self) -> None:
        """Validate configuration values.
        
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate max_retries
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        
        # Validate timeout
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        
        # Validate log_level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(
                f"log_level must be one of: {', '.join(valid_log_levels)}"
            )
        
        # Validate directories exist or can be created
        if self.browser_user_data_dir:
            Path(self.browser_user_data_dir).mkdir(parents=True, exist_ok=True)
        
        if self.session_dir:
            Path(self.session_dir).mkdir(parents=True, exist_ok=True)


class ConfigManager:
    """Manages application configuration with persistence."""
    
    DEFAULT_CONFIG_DIR = Path.home() / ".arenaagent"
    CONFIG_FILENAME = "config.json"
    BACKUP_SUFFIX = ".backup"
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_dir: Directory for configuration file (defaults to ~/.arenaagent)
        """
        self.config_dir = Path(config_dir) if config_dir else self.DEFAULT_CONFIG_DIR
        self.config_path = self.config_dir / self.CONFIG_FILENAME
        self._config: Optional[Config] = None
        self.logger = get_logger(__name__)
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Config:
        """Load configuration from file or create default.
        
        Returns:
            Loaded or default Config instance
        """
        if self.config_path.exists():
            try:
                self.logger.info(f"Loading configuration from {self.config_path}")
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                config = Config.from_dict(data)
                config.validate()
                self._config = config
                self.logger.info("Configuration loaded successfully")
                
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.warning(
                    f"Failed to load configuration: {e}. Using default configuration."
                )
                self._config = Config.default(self.config_dir)
                # Save default config
                self.save(self._config)
        else:
            self.logger.info("No configuration file found. Creating default.")
            self._config = Config.default(self.config_dir)
            self.save(self._config)
        
        return self._config
    
    def save(self, config: Config) -> None:
        """Save configuration to file with atomic write.
        
        Args:
            config: Configuration to save
        """
        # Validate before saving
        config.validate()
        
        # Create backup if config file exists
        if self.config_path.exists():
            backup_path = self.config_path.with_suffix(
                self.config_path.suffix + self.BACKUP_SUFFIX
            )
            shutil.copy2(self.config_path, backup_path)
            self.logger.debug(f"Created backup at {backup_path}")
        
        # Atomic write: write to temp file, then rename
        temp_path = self.config_path.with_suffix('.tmp')
        
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2)
            
            # Atomic rename
            temp_path.replace(self.config_path)
            self._config = config
            self.logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise RuntimeError(f"Failed to save configuration: {e}") from e
    
    def get(self) -> Config:
        """Get current configuration.
        
        Returns:
            Current Config instance
        """
        if self._config is None:
            return self.load()
        return self._config
    
    def update(self, **kwargs: Any) -> None:
        """Update specific configuration values.
        
        Args:
            **kwargs: Configuration key-value pairs to update
        """
        config = self.get()
        
        # Update config attributes
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                self.logger.warning(f"Unknown configuration key: {key}")
        
        # Validate and save
        config.validate()
        self.save(config)
        
        self.logger.info(f"Configuration updated: {', '.join(kwargs.keys())}")
    
    def reset(self) -> Config:
        """Reset to default configuration.
        
        Returns:
            Default Config instance
        """
        self.logger.info("Resetting configuration to default")
        
        # Create backup with timestamp
        if self.config_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.config_path.with_name(
                f"{self.config_path.stem}_{timestamp}.backup.json"
            )
            shutil.copy2(self.config_path, backup_path)
            self.logger.info(f"Backed up current config to {backup_path}")
        
        # Reset to default
        default_config = Config.default(self.config_dir)
        self.save(default_config)
        
        return default_config
    
    def get_config_path(self) -> Path:
        """Get configuration file path.
        
        Returns:
            Path to configuration file
        """
        return self.config_path

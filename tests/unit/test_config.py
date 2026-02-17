"""Unit tests for the Config and ConfigManager classes."""

import pytest
import json
import tempfile
from pathlib import Path

from arenaagent.config.manager import Config, ConfigManager


class TestConfig:
    """Tests for Config class."""
    
    def test_config_creation_with_defaults(self):
        """Test creating config with default values."""
        config = Config()
        
        assert config.browser_headless is False
        assert config.model_name == "claude-3-5-sonnet-20241022"
        assert config.max_retries == 3
        assert config.timeout == 30
        assert config.auto_execute is False
        assert config.backup_enabled is True
        assert config.log_level == "INFO"
    
    def test_config_creation_with_custom_values(self):
        """Test creating config with custom values."""
        config = Config(
            browser_headless=True,
            model_name="gpt-4",
            max_retries=5,
            timeout=60,
            auto_execute=True,
            backup_enabled=False,
            log_level="DEBUG"
        )
        
        assert config.browser_headless is True
        assert config.model_name == "gpt-4"
        assert config.max_retries == 5
        assert config.timeout == 60
        assert config.auto_execute is True
        assert config.backup_enabled is False
        assert config.log_level == "DEBUG"
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(
            browser_headless=True,
            model_name="test-model",
            max_retries=2
        )
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["browser_headless"] is True
        assert config_dict["model_name"] == "test-model"
        assert config_dict["max_retries"] == 2
    
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "browser_headless": True,
            "model_name": "test-model",
            "max_retries": 5,
            "timeout": 45,
            "auto_execute": True,
            "backup_enabled": False,
            "log_level": "WARNING"
        }
        
        config = Config.from_dict(data)
        
        assert config.browser_headless is True
        assert config.model_name == "test-model"
        assert config.max_retries == 5
        assert config.timeout == 45
        assert config.auto_execute is True
        assert config.backup_enabled is False
        assert config.log_level == "WARNING"
    
    def test_config_from_dict_with_missing_keys(self):
        """Test creating config from dictionary with missing keys uses defaults."""
        data = {"browser_headless": True}
        
        config = Config.from_dict(data)
        
        assert config.browser_headless is True
        assert config.model_name == "claude-3-5-sonnet-20241022"  # default
        assert config.max_retries == 3  # default
    
    def test_config_default(self):
        """Test creating default config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            config = Config.default(base_dir)
            
            assert config.browser_headless is False
            assert str(base_dir / "browser") in config.browser_user_data_dir
            assert str(base_dir / "sessions") in config.session_dir
    
    def test_config_validate_success(self):
        """Test config validation with valid values."""
        config = Config()
        # Should not raise any exception
        config.validate()
    
    def test_config_validate_negative_max_retries(self):
        """Test config validation fails with negative max_retries."""
        config = Config(max_retries=-1)
        
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            config.validate()
    
    def test_config_validate_zero_timeout(self):
        """Test config validation fails with zero timeout."""
        config = Config(timeout=0)
        
        with pytest.raises(ValueError, match="timeout must be positive"):
            config.validate()
    
    def test_config_validate_negative_timeout(self):
        """Test config validation fails with negative timeout."""
        config = Config(timeout=-10)
        
        with pytest.raises(ValueError, match="timeout must be positive"):
            config.validate()
    
    def test_config_validate_invalid_log_level(self):
        """Test config validation fails with invalid log level."""
        config = Config(log_level="INVALID")
        
        with pytest.raises(ValueError, match="log_level must be one of"):
            config.validate()
    
    def test_config_validate_creates_directories(self):
        """Test config validation creates necessary directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            browser_dir = Path(tmpdir) / "browser"
            session_dir = Path(tmpdir) / "sessions"
            
            config = Config(
                browser_user_data_dir=str(browser_dir),
                session_dir=str(session_dir)
            )
            
            # Directories shouldn't exist yet
            assert not browser_dir.exists()
            assert not session_dir.exists()
            
            # Validate should create them
            config.validate()
            
            assert browser_dir.exists()
            assert session_dir.exists()


class TestConfigManager:
    """Tests for ConfigManager class."""
    
    def test_config_manager_initialization(self):
        """Test ConfigManager initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            
            assert manager.config_dir == Path(tmpdir)
            assert manager.config_path == Path(tmpdir) / "config.json"
            assert manager.config_dir.exists()
    
    def test_config_manager_default_directory(self):
        """Test ConfigManager uses default directory when none specified."""
        manager = ConfigManager()
        
        assert manager.config_dir == Path.home() / ".arenaagent"
    
    def test_load_creates_default_config_when_none_exists(self):
        """Test loading creates default config when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            
            # Config file shouldn't exist yet
            assert not manager.config_path.exists()
            
            config = manager.load()
            
            # Should create default config and save it
            assert manager.config_path.exists()
            assert isinstance(config, Config)
            assert config.model_name == "claude-3-5-sonnet-20241022"
    
    def test_load_reads_existing_config(self):
        """Test loading reads existing config from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            
            # Create a config file manually
            test_data = {
                "browser_headless": True,
                "model_name": "test-model",
                "max_retries": 7,
                "timeout": 50,
                "auto_execute": True,
                "backup_enabled": False,
                "log_level": "DEBUG",
                "browser_user_data_dir": str(Path(tmpdir) / "browser"),
                "session_dir": str(Path(tmpdir) / "sessions"),
            }
            
            with open(config_path, 'w') as f:
                json.dump(test_data, f)
            
            manager = ConfigManager(tmpdir)
            config = manager.load()
            
            assert config.browser_headless is True
            assert config.model_name == "test-model"
            assert config.max_retries == 7
    
    def test_load_handles_corrupted_config(self):
        """Test loading handles corrupted config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            
            # Create corrupted JSON file
            with open(config_path, 'w') as f:
                f.write("{ invalid json }")
            
            manager = ConfigManager(tmpdir)
            config = manager.load()
            
            # Should fall back to default config
            assert isinstance(config, Config)
            assert config.model_name == "claude-3-5-sonnet-20241022"
    
    def test_save_creates_config_file(self):
        """Test saving creates config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            config = Config(browser_headless=True, model_name="test-model")
            
            manager.save(config)
            
            assert manager.config_path.exists()
            
            # Verify saved content
            with open(manager.config_path, 'r') as f:
                data = json.load(f)
            
            assert data["browser_headless"] is True
            assert data["model_name"] == "test-model"
    
    def test_save_creates_backup(self):
        """Test saving creates backup of existing config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            
            # Save initial config
            config1 = Config(model_name="model-v1")
            manager.save(config1)
            
            # Save updated config (should create backup)
            config2 = Config(model_name="model-v2")
            manager.save(config2)
            
            # Check backup exists
            backup_path = manager.config_path.with_suffix('.json.backup')
            assert backup_path.exists()
            
            # Verify backup contains old config
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            assert backup_data["model_name"] == "model-v1"
            
            # Verify current config has new values
            with open(manager.config_path, 'r') as f:
                current_data = json.load(f)
            assert current_data["model_name"] == "model-v2"
    
    def test_save_validates_config(self):
        """Test saving validates config before saving."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            invalid_config = Config(max_retries=-1)
            
            with pytest.raises(ValueError, match="max_retries must be non-negative"):
                manager.save(invalid_config)
    
    def test_get_returns_loaded_config(self):
        """Test get returns loaded config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            
            config = manager.get()
            
            assert isinstance(config, Config)
            assert config == manager._config
    
    def test_get_loads_config_if_not_loaded(self):
        """Test get loads config if not already loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            
            # Ensure config is not loaded
            assert manager._config is None
            
            config = manager.get()
            
            # Should have loaded config
            assert manager._config is not None
            assert isinstance(config, Config)
    
    def test_update_modifies_config_values(self):
        """Test update modifies specific config values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            manager.load()
            
            # Update specific values
            manager.update(browser_headless=True, max_retries=10)
            
            config = manager.get()
            assert config.browser_headless is True
            assert config.max_retries == 10
            
            # Verify saved to file
            with open(manager.config_path, 'r') as f:
                data = json.load(f)
            assert data["browser_headless"] is True
            assert data["max_retries"] == 10
    
    def test_update_ignores_unknown_keys(self):
        """Test update ignores unknown configuration keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            manager.load()
            
            # Should not raise error for unknown key
            manager.update(unknown_key="value")
            
            config = manager.get()
            assert not hasattr(config, "unknown_key")
    
    def test_update_validates_new_values(self):
        """Test update validates new configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            manager.load()
            
            with pytest.raises(ValueError, match="max_retries must be non-negative"):
                manager.update(max_retries=-1)
    
    def test_reset_creates_default_config(self):
        """Test reset creates default configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            
            # Create custom config
            custom_config = Config(browser_headless=True, model_name="custom")
            manager.save(custom_config)
            
            # Reset to default
            default_config = manager.reset()
            
            assert default_config.browser_headless is False
            assert default_config.model_name == "claude-3-5-sonnet-20241022"
    
    def test_reset_creates_timestamped_backup(self):
        """Test reset creates timestamped backup of current config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            
            # Create custom config
            custom_config = Config(model_name="custom")
            manager.save(custom_config)
            
            # Reset
            manager.reset()
            
            # Check for timestamped backup
            backup_files = list(Path(tmpdir).glob("config_*.backup.json"))
            assert len(backup_files) == 1
            
            # Verify backup contains old config
            with open(backup_files[0], 'r') as f:
                backup_data = json.load(f)
            assert backup_data["model_name"] == "custom"
    
    def test_get_config_path_returns_correct_path(self):
        """Test get_config_path returns correct configuration file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(tmpdir)
            
            path = manager.get_config_path()
            
            assert path == Path(tmpdir) / "config.json"
            assert isinstance(path, Path)

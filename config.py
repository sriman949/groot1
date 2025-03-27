"""Configuration management for Groot CLI."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

class Config:
    """Configuration manager for Groot CLI."""

    def __init__(self, config_dir: str = None):
        """Initialize the configuration manager."""
        self.config_dir = config_dir or os.path.expanduser("~/.groot")
        self.config_file = os.path.join(self.config_dir, "config.yaml")
        self.config = {}
        self.load_config()

    def load_config(self):
        """Load configuration from file."""
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)

        # Create default config file if it doesn't exist
        if not os.path.exists(self.config_file):
            self.create_default_config()

        # Load config
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = {}

    def create_default_config(self):
        """Create default configuration file."""
        default_config = {
            "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
            "default_namespace": "default",
            "log_level": "info",
            "max_history": 10,
            "theme": "dark"
        }

        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error creating default config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        # Check environment variables first
        env_key = f"GROOT_{key.upper()}"
        if env_key in os.environ:
            return os.environ[env_key]

        # Then check config file
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set a configuration value."""
        self.config[key] = value

        # Save to file
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self.config.copy()

# Create a singleton instance
config = Config()
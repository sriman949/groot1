"""
Configuration module for Groot
"""

import os
import yaml
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    # OpenAI API key (can be overridden by environment variable)
    "openai_api_key": "",

    # Default namespace
    "default_namespace": "default",

    # Custom resource mappings
    "custom_resources": {
        "prometheusrule": ("monitoring.coreos.com", "v1", "prometheusrules"),
        "servicemonitor": ("monitoring.coreos.com", "v1", "servicemonitors"),
        "ingressroute": ("traefik.containo.us", "v1alpha1", "ingressroutes"),
        "certificate": ("cert-manager.io", "v1", "certificates"),
    },

    # Severity levels for issues
    "severity_levels": {
        "high": ["CrashLoopBackOff", "Error", "ImagePullBackOff", "Failed"],
        "medium": ["Pending", "Terminating"],
        "low": ["Warning"]
    },

    # UI settings
    "ui": {
        "colors": {
            "primary": "green",
            "secondary": "blue",
            "error": "red",
            "warning": "yellow",
            "info": "cyan"
        }
    },

    # Plugin settings
    "plugins": {
        "enabled": True,
        "plugin_dir": "~/.groot/plugins"
    },

    # Web interface settings
    "web": {
        "enabled": True,
        "host": "127.0.0.1",
        "port": 8080,
        "debug": False
    }
}

class Config:
    """Configuration manager for Groot"""

    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self.config_file = os.path.expanduser("~/.groot/config.yaml")
        self.load_config()

        # Override with environment variables
        if os.environ.get("OPENAI_API_KEY"):
            self.config["openai_api_key"] = os.environ.get("OPENAI_API_KEY")

    def load_config(self):
        """Load configuration from file"""
        config_path = Path(self.config_file)

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    user_config = yaml.safe_load(f)
                    if user_config and isinstance(user_config, dict):
                        # Update config with user settings
                        self._update_dict(self.config, user_config)
            except Exception as e:
                print(f"Error loading config file: {e}")

    def save_config(self):
        """Save configuration to file"""
        config_path = Path(self.config_file)

        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config file: {e}")

    def _update_dict(self, target, source):
        """Recursively update a dictionary"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict(target[key], value)
            else:
                target[key] = value

    def get(self, key, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set a configuration value"""
        self.config[key] = value
        self.save_config()

# Create a global config instance
config = Config()
"""
Configuration management for PassAud.
"""

import configparser
import os
from pathlib import Path
from typing import Any

class ConfigManager:
    """Manage application configuration."""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        return os.path.join(Path.home(), ".passaud.conf")
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default configuration."""
        self.config['DEFAULT'] = {
            'api_timeout': '10',
            'max_threads': '4',
            'max_words': '100000',
            'request_delay': '1.5',
            'store_sensitive_data': 'false',
            'max_requests_per_minute': '30',
            'gpu_enabled': 'true',
            'batch_size': '1000',
            'max_bruteforce_length': '8'
        }
        self.config['API_KEYS'] = {}
        self.save_config()
    
    def save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        try:
            return self.config[section][key]
        except KeyError:
            return default
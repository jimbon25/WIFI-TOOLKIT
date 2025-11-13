#!/usr/bin/env python3
"""
WiFi Toolkit Configuration Manager
Handles flexible paths for handshakes, logs, and other data directories
"""

import os
import json
from pathlib import Path

class ConfigManager:
    """Manages WiFi Toolkit configuration and paths"""
    
    DEFAULT_HANDSHAKE_DIR = "handshakes"
    DEFAULT_LOG_DIR = "~/.wifi-toolkit_logs"
    DEFAULT_CRACKING_RESULTS_DIR = "~/.wifi-toolkit_logs/cracking_results"
    
    CONFIG_FILE_NAME = ".wifi_toolkit_config"
    
    def __init__(self):
        """Initialize configuration"""
        self.config = self._load_config()
        self._setup_directories()
    
    def _get_config_path(self):
        """Get config file path (check multiple locations)"""
        cwd_config = os.path.join(os.getcwd(), self.CONFIG_FILE_NAME)
        if os.path.exists(cwd_config):
            return cwd_config
        
        home_config = os.path.join(os.path.expanduser("~"), self.CONFIG_FILE_NAME)
        if os.path.exists(home_config):
            return home_config
        
        return home_config
    
    def _load_config(self):
        """Load configuration from file or use defaults"""
        config_path = self._get_config_path()
        
        default_config = {
            "handshake_dir": self.DEFAULT_HANDSHAKE_DIR,
            "log_dir": self.DEFAULT_LOG_DIR,
            "cracking_results_dir": self.DEFAULT_CRACKING_RESULTS_DIR,
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            else:
                # Save default config
                self._save_config(default_config)
        except (json.JSONDecodeError, IOError):
            print(f"[!] Error reading config, using defaults")
            pass
        
        for key in default_config:
            default_config[key] = os.path.expanduser(default_config[key])
        
        return default_config
    
    def _save_config(self, config):
        """Save configuration to file"""
        config_path = self._get_config_path()
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"[!] Could not save config: {e}")
    
    def _setup_directories(self):
        """Create necessary directories"""
        dirs_to_create = [
            self.config.get("handshake_dir"),
            self.config.get("log_dir"),
            self.config.get("cracking_results_dir"),
        ]
        
        for dir_path in dirs_to_create:
            if dir_path:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except OSError as e:
                    print(f"[!] Could not create directory {dir_path}: {e}")
    
    def get_handshake_dir(self):
        """Get handshake directory path"""
        return self.config.get("handshake_dir", self.DEFAULT_HANDSHAKE_DIR)
    
    def get_log_dir(self):
        """Get log directory path"""
        return self.config.get("log_dir", self.DEFAULT_LOG_DIR)
    
    def get_cracking_results_dir(self):
        """Get cracking results directory path"""
        return self.config.get("cracking_results_dir", self.DEFAULT_CRACKING_RESULTS_DIR)
    
    def set_handshake_dir(self, path):
        """Set custom handshake directory"""
        expanded_path = os.path.expanduser(path)
        self.config["handshake_dir"] = expanded_path
        os.makedirs(expanded_path, exist_ok=True)
        self._save_config(self.config)
        return expanded_path
    
    def set_log_dir(self, path):
        """Set custom log directory"""
        expanded_path = os.path.expanduser(path)
        self.config["log_dir"] = expanded_path
        os.makedirs(expanded_path, exist_ok=True)
        self._save_config(self.config)
        return expanded_path
    
    def set_cracking_results_dir(self, path):
        """Set custom cracking results directory"""
        expanded_path = os.path.expanduser(path)
        self.config["cracking_results_dir"] = expanded_path
        os.makedirs(expanded_path, exist_ok=True)
        self._save_config(self.config)
        return expanded_path
    
    def show_config(self):
        """Display current configuration"""
        print("\n" + "="*60)
        print("WiFi Toolkit Configuration")
        print("="*60)
        print(f"Handshake Directory: {self.get_handshake_dir()}")
        print(f"Log Directory:       {self.get_log_dir()}")
        print(f"Results Directory:   {self.get_cracking_results_dir()}")
        print("="*60 + "\n")
    
    def create_config_file(self):
        """Create/overwrite config file with current settings"""
        config = {
            "handshake_dir": self.get_handshake_dir(),
            "log_dir": self.get_log_dir(),
            "cracking_results_dir": self.get_cracking_results_dir(),
        }
        
        portable_config = {}
        for key, value in config.items():
            if value.startswith(os.path.expanduser("~")):
                portable_config[key] = value.replace(os.path.expanduser("~"), "~")
            else:
                portable_config[key] = value
        
        self._save_config(portable_config)
        return self._get_config_path()


if __name__ == "__main__":
    config = ConfigManager()
    config.show_config()

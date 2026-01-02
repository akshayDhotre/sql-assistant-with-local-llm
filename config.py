"""
Configuration module for SQL Assistant

This module loads and provides access to configuration settings.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration handler."""
    
    _config: Dict[str, Any] = {}
    _loaded: bool = False
    
    @classmethod
    def load(cls, config_path: str = "config.yaml") -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                cls._config = yaml.safe_load(f)
            cls._loaded = True
            return cls._config
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        if not cls._loaded:
            cls.load()
        
        # Support nested keys like "llm.model_path"
        keys = key.split('.')
        value = cls._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Get all configuration."""
        if not cls._loaded:
            cls.load()
        return cls._config

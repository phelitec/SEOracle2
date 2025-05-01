"""
Configuration Manager
====================
Handles loading and validation of configuration settings.
"""

import configparser
import os
import logging
from typing import Dict, Any

class ConfigManager:
    """Manages configuration settings for the SEO Content Generator."""
    
    def __init__(self, config_path: str = "config.ini"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.logger = logging.getLogger("ConfigManager")
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Dict[str, str]]:
        """
        Load and validate configuration from the config file.
        
        Returns:
            Dictionary containing configuration settings
        
        Raises:
            FileNotFoundError: If config file does not exist
            ValueError: If required configuration settings are missing
        """
        if not os.path.exists(self.config_path):
            self.logger.error(f"Arquivo de configuração não encontrado: {self.config_path}")
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")
            
        config = configparser.ConfigParser()
        config.read(self.config_path)
        
        # Convert ConfigParser object to nested dictionary
        config_dict = {
            "openai": {
                "api_key": config.get("OpenAI", "api_key"),
                "model": config.get("OpenAI", "model", fallback="gpt-4o-mini")
            },
            "wordpress": {
                "site_url": config.get("WordPress", "site_url"),
                "username": config.get("WordPress", "username"),
                "app_password": config.get("WordPress", "app_password")
            },
            "keywords": {
                "file": config.get("Keywords", "file", fallback="keywords.txt")
            },
            "content": {
                "posts_per_run": config.getint("Content", "posts_per_run", fallback=1),
                "min_words": config.getint("Content", "min_words", fallback=800),
                "max_words": config.getint("Content", "max_words", fallback=1500),
                "target_category": config.get("Content", "target_category", fallback="")
            },
            "cta": {
                "url": config.get("CTA", "url", fallback=""),
                "text": config.get("CTA", "text", fallback="Quero Crescer")
            }
        }
        
        # Validate required settings
        self._validate_config(config_dict)
        
        return config_dict
    
    def _validate_config(self, config: Dict[str, Dict[str, Any]]) -> None:
        """
        Validate that all required configuration settings are present.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ValueError: If required configuration settings are missing
        """
        required_settings = [
            ("openai", "api_key"),
            ("wordpress", "site_url"),
            ("wordpress", "username"),
            ("wordpress", "app_password")
        ]
        
        missing_settings = []
        
        for section, key in required_settings:
            if not config.get(section, {}).get(key):
                missing_settings.append(f"{section}.{key}")
        
        if missing_settings:
            error_msg = f"Configurações obrigatórias ausentes: {', '.join(missing_settings)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the loaded configuration.
        
        Returns:
            Dictionary containing configuration settings
        """
        return self.config
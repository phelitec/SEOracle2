#!/usr/bin/env python3
"""
SEO Content Generator for WordPress
===================================
Main entry point for the application.

This script processes command line arguments and initiates the content
generation and publishing workflow.
"""

import argparse
import logging
import os
from pathlib import Path

from seo_generator.config_manager import ConfigManager
from seo_generator.content_generator import SEOContentGenerator


def setup_logging():
    """Set up logging configuration"""
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "seo_content_generator.log"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("SEOContentGenerator")


def main():
    """Main entry point for the application"""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Gerador de Conteúdo SEO para WordPress')
    parser.add_argument('--config', default='config.ini', help='Caminho para o arquivo de configuração')
    parser.add_argument('--posts', type=int, help='Número de posts a serem gerados')
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Iniciando SEO Content Generator")
    
    # Check if config file exists
    if not os.path.exists(args.config):
        logger.info(f"Arquivo de configuração '{args.config}' não encontrado. Execute setup.py para criar.")
        return
    
    try:
        # Load configuration
        config_manager = ConfigManager(args.config)
        config = config_manager.get_config()
        
        # Override posts_per_run if provided via command line
        if args.posts:
            config["content"]["posts_per_run"] = str(args.posts)
        
        # Initialize and run the content generator
        generator = SEOContentGenerator(config, logger)
        generator.run()
        
    except Exception as e:
        logger.error(f"Erro na execução principal: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
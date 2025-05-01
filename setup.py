#!/usr/bin/env python3
"""
SEO Content Generator for WordPress - Setup
===========================================
Setup script to create configuration files and directory structure.
"""

import os
import configparser
from pathlib import Path
import getpass
import logging
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Setup console for rich output
console = Console()

def setup_logging():
    """Set up logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "setup.log"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("Setup")

def create_directory_structure():
    """Create necessary directories"""
    directories = ["logs", "seo_generator"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Create __init__.py in the seo_generator directory
    with open(os.path.join("seo_generator", "__init__.py"), "w") as f:
        f.write('"""SEO Content Generator package."""\n')

def create_config_file():
    """Create configuration file interactively"""
    console.print(Panel.fit(
        "[bold green]SEO Content Generator - Configuração Inicial[/bold green]\n"
        "Vamos configurar os parâmetros necessários para o funcionamento do gerador."
    ))
    
    config = configparser.ConfigParser()
    
    # OpenAI section
    console.print("\n[bold]Configuração da OpenAI[/bold]")
    openai_api_key = Prompt.ask("API Key da OpenAI", password=True)
    openai_model = Prompt.ask("Modelo da OpenAI", default="gpt-4o-mini")
    
    config["OpenAI"] = {
        "api_key": openai_api_key,
        "model": openai_model
    }
    
    # WordPress section
    console.print("\n[bold]Configuração do WordPress[/bold]")
    wp_site_url = Prompt.ask("URL do site WordPress (sem barra no final)", default="https://seu-site.com")
    wp_username = Prompt.ask("Nome de usuário WordPress")
    wp_app_password = Prompt.ask("Senha de aplicação WordPress", password=True)
    
    config["WordPress"] = {
        "site_url": wp_site_url,
        "username": wp_username,
        "app_password": wp_app_password
    }
    
    # Keywords section
    console.print("\n[bold]Configuração de palavras-chave[/bold]")
    keywords_file = Prompt.ask("Arquivo de palavras-chave", default="keywords.txt")
    
    config["Keywords"] = {
        "file": keywords_file
    }
    
    # Content section
    console.print("\n[bold]Configuração de conteúdo[/bold]")
    posts_per_run = Prompt.ask("Número de posts por execução", default="1")
    min_words = Prompt.ask("Número mínimo de palavras por post", default="800")
    max_words = Prompt.ask("Número máximo de palavras por post", default="1500")
    target_category = Prompt.ask("Categoria alvo (deixe em branco para nenhuma)", default="")
    
    config["Content"] = {
        "posts_per_run": posts_per_run,
        "min_words": min_words,
        "max_words": max_words,
        "target_category": target_category
    }
    
    # CTA section
    console.print("\n[bold]Configuração do Call-to-Action[/bold]")
    cta_url = Prompt.ask("URL do CTA", default="https://seu-site.com/oferta")
    cta_text = Prompt.ask("Texto do CTA", default="Quero Crescer")
    
    config["CTA"] = {
        "url": cta_url,
        "text": cta_text
    }
    
    # Write config file
    with open("config.ini", "w") as f:
        config.write(f)
    
    console.print("[green]✓[/green] Arquivo de configuração criado com sucesso!")

def create_keywords_file():
    """Create keywords file with example content"""
    keyword_file = "keywords.txt"
    
    # Check if file already exists
    if os.path.exists(keyword_file):
        if not Confirm.ask(f"O arquivo {keyword_file} já existe. Deseja substituí-lo?"):
            return
    
    with open(keyword_file, "w", encoding="utf-8") as f:
        f.write("# Coloque suas palavras-chave aqui (uma por linha)\n")
        f.write("# Você pode adicionar contexto após dois-pontos\n")
        f.write("marketing digital: estratégias para pequenas empresas\n")
        f.write("seo para iniciantes\n")
        f.write("como aumentar tráfego no site\n")
        f.write("conteúdo para redes sociais\n")
        f.write("técnicas de copywriting\n")
    
    console.print(f"[green]✓[/green] Arquivo de palavras-chave {keyword_file} criado com sucesso!")

def create_license_file():
    """Create a MIT license file"""
    license_content = """MIT License

Copyright (c) 2025 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    with open("LICENSE", "w") as f:
        f.write(license_content)
    
    console.print("[green]✓[/green] Arquivo de licença criado com sucesso!")

def main():
    """Main setup function"""
    logger = setup_logging()
    logger.info("Iniciando configuração")
    
    try:
        # Create directory structure
        create_directory_structure()
        logger.info("Estrutura de diretórios criada")
        
        # Create configuration file
        create_config_file()
        logger.info("Arquivo de configuração criado")
        
        # Create keywords file
        create_keywords_file()
        logger.info("Arquivo de palavras-chave criado")
        
        # Create license file
        create_license_file()
        logger.info("Arquivo de licença criado")
        
        console.print(Panel.fit(
            "[bold green]Configuração concluída com sucesso![/bold green]\n"
            "Você pode agora executar o gerador com: [bold]python main.py[/bold]"
        ))
        
    except Exception as e:
        logger.error(f"Erro durante a configuração: {str(e)}", exc_info=True)
        console.print(f"[bold red]Erro durante a configuração: {str(e)}[/bold red]")

if __name__ == "__main__":
    main()
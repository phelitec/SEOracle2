"""
Utility Functions
================
Helper functions for the SEO Content Generator.
"""

import json
import re
import os
import logging
from typing import List, Dict, Any, Optional, Tuple

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract JSON data from text that may contain markdown code blocks or raw JSON.
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        Extracted JSON as dictionary
    """
    # Try to extract JSON from markdown code block
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to extract JSON directly
    json_match = re.search(r'({[\s\S]*})', text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # If all else fails, try to parse the entire text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Return original text if not JSON
        return {"raw_content": text}

def load_keywords(keywords_file: str, logger: logging.Logger) -> List[str]:
    """
    Load keywords from file with different encoding attempts.
    
    Args:
        keywords_file: Path to keywords file
        logger: Logger instance
        
    Returns:
        List of keywords
        
    Raises:
        FileNotFoundError: If keywords file doesn't exist and couldn't be created
        ValueError: If no valid keywords found in file
    """
    if not os.path.exists(keywords_file):
        try:
            with open(keywords_file, "w", encoding="utf-8") as f:
                f.write("# Coloque suas palavras-chave aqui (uma por linha)\n")
                f.write("# Você pode adicionar contexto após dois-pontos\n")
                f.write("marketing digital: estratégias para pequenas empresas\n")
                f.write("seo para iniciantes\n")
            logger.info(f"Arquivo de palavras-chave criado em {keywords_file}")
        except Exception as e:
            logger.error(f"Não foi possível criar o arquivo de palavras-chave: {str(e)}")
            raise FileNotFoundError(f"Não foi possível criar o arquivo de palavras-chave: {str(e)}")
    
    # Try different encodings to read the file
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    lines = []
    
    for encoding in encodings:
        try:
            with open(keywords_file, "r", encoding=encoding) as f:
                lines = f.readlines()
            logger.info(f"Arquivo de palavras-chave lido com sucesso usando codificação {encoding}")
            break
        except UnicodeDecodeError:
            logger.warning(f"Não foi possível ler o arquivo usando codificação {encoding}")
            if encoding == encodings[-1]:
                logger.error("Não foi possível ler o arquivo de palavras-chave com nenhuma codificação.")
                raise ValueError("Não foi possível ler o arquivo de palavras-chave com nenhuma codificação.")
    
    # Filter blank lines and comments
    keywords = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
    
    if not keywords:
        logger.error("Nenhuma palavra-chave encontrada no arquivo. Adicione pelo menos uma palavra-chave.")
        raise ValueError("Nenhuma palavra-chave encontrada no arquivo. Adicione pelo menos uma palavra-chave.")
    
    return keywords

def select_keywords(keywords: List[str], count: int = 1) -> List[str]:
    """
    Select keywords to process in this run.
    
    Args:
        keywords: List of available keywords
        count: Number of keywords to select
        
    Returns:
        List of selected keywords
    """
    # Simple implementation - just take the first N keywords
    # In a more advanced version, could implement rotation, priority, etc.
    return keywords[:min(count, len(keywords))]

def word_count(text: str) -> int:
    """
    Count words in text, handling HTML content.
    
    Args:
        text: Text to count words in
        
    Returns:
        Word count
    """
    # Remove HTML tags
    text_no_html = re.sub(r'<[^>]+>', '', text)
    # Remove multiple spaces
    text_clean = re.sub(r'\s+', ' ', text_no_html).strip()
    # Count words
    return len(text_clean.split())
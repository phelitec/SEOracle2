"""
Image Generator
==============
Module for generating and managing images for SEO content.
"""

import os
import time
import logging
import requests
import base64
import io
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlparse

from openai import OpenAI


class ImageGenerator:
    """Generator for SEO-optimized images using AI."""
    
    def __init__(self, config: Dict[str, Dict[str, Any]], logger: Optional[logging.Logger] = None):
        """
        Initialize the image generator.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance (optional)
        """
        self.config = config
        self.logger = logger or logging.getLogger("ImageGenerator")
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=config["openai"]["api_key"])
        self.image_model = config["openai"].get("image_model", "dall-e-3")
        self.image_quality = config["openai"].get("image_quality", "standard")
        self.image_size = config["openai"].get("image_size", "1024x1024")
        
        # Ensure temp directory exists
        self.temp_dir = config["content"].get("images_temp_dir", "images_temp")
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def generate_featured_image(self, title: str, keyword: str) -> Optional[str]:
        """
        Generate a featured image for a post.
        
        Args:
            title: Post title
            keyword: Target keyword
            
        Returns:
            Path to the generated image or None if failed
        """
        try:
            self.logger.info(f"Gerando imagem destacada para: {title}")
            
            prompt = self._create_image_prompt(title, keyword, is_featured=True)
            image_path = self._generate_and_save_image(prompt, f"featured_{self._sanitize_filename(title)}")
            
            self.logger.info(f"Imagem destacada gerada com sucesso: {image_path}")
            return image_path
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar imagem destacada: {str(e)}")
            return None
    
    def generate_content_images(self, title: str, keyword: str, subtopics: List[str], count: int = 1) -> List[str]:
        """
        Generate images to be inserted in the content.
        
        Args:
            title: Post title
            keyword: Target keyword
            subtopics: List of subtopics in the content
            count: Number of images to generate
            
        Returns:
            List of paths to the generated images
        """
        image_paths = []
        actual_count = min(count, len(subtopics))
        
        try:
            self.logger.info(f"Gerando {actual_count} imagens para o conteúdo sobre: {title}")
            
            for i in range(actual_count):
                subtopic = subtopics[i] if i < len(subtopics) else title
                
                # Create a prompt specific to this subtopic
                prompt = self._create_image_prompt(subtopic, keyword, is_featured=False)
                
                # Generate and save the image
                image_path = self._generate_and_save_image(
                    prompt, 
                    f"content_{i+1}_{self._sanitize_filename(subtopic)}"
                )
                
                if image_path:
                    image_paths.append(image_path)
                    self.logger.info(f"Imagem de conteúdo {i+1} gerada com sucesso: {image_path}")
                
                # Wait between image generations to avoid rate limits
                if i < actual_count - 1:
                    time.sleep(2)
            
            return image_paths
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar imagens de conteúdo: {str(e)}")
            return image_paths
    
    def _create_image_prompt(self, topic: str, keyword: str, is_featured: bool = False) -> str:
        """
        Create an optimized prompt for image generation.
        
        Args:
            topic: Main topic for the image
            keyword: Target keyword
            is_featured: Whether this is for a featured image
            
        Returns:
            Optimized image prompt
        """
        if is_featured:
            # More professional and eye-catching for featured images
            return f"Create a professional, modern featured image for a blog post titled '{topic}'. The image should be relevant to '{keyword}', visually appealing, with good composition and lighting. Make it suitable for SEO and social media sharing. No text overlay. Photorealistic or professional stock photo style."
        else:
            # More illustrative and supportive for content images
            return f"Create an informative illustration related to '{topic}' for a blog post about '{keyword}'. The image should complement the text, be clear and professional. Suitable for web content. No text overlay. Photorealistic or professional stock photo style."
    
    def _generate_and_save_image(self, prompt: str, filename_prefix: str) -> Optional[str]:
        """
        Generate an image using OpenAI and save it locally.
        
        Args:
            prompt: Image generation prompt
            filename_prefix: Prefix for the filename
            
        Returns:
            Path to the saved image or None if failed
        """
        try:
            response = self.openai_client.images.generate(
                model=self.image_model,
                prompt=prompt,
                size=self.image_size,
                quality=self.image_quality,
                n=1,
                response_format="url"  # Use URL for easier handling
            )
            
            # Get the image URL
            image_url = response.data[0].url
            
            # Download the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Generate a unique filename
            timestamp = int(time.time())
            filename = f"{filename_prefix}_{timestamp}.png"
            file_path = os.path.join(self.temp_dir, filename)
            
            # Save the image
            with open(file_path, "wb") as f:
                f.write(image_response.content)
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar e salvar imagem: {str(e)}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be used as a filename.
        
        Args:
            filename: String to sanitize
            
        Returns:
            Sanitized filename
        """
        # Replace special characters
        sanitized = ''.join(c if c.isalnum() or c in ['-', '_'] else '_' for c in filename)
        # Limit length
        return sanitized[:50]

    def cleanup_temp_images(self, image_paths: List[str]) -> None:
        """
        Clean up temporary image files.
        
        Args:
            image_paths: List of image paths to delete
        """
        try:
            for image_path in image_paths:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    self.logger.info(f"Arquivo temporário removido: {image_path}")
        except Exception as e:
            self.logger.error(f"Erro ao limpar arquivos temporários: {str(e)}")

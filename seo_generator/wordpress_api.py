"""
WordPress API Client
==================
Client for interacting with WordPress REST API.
"""

import requests
import logging
from typing import Dict, Any, Optional, Tuple, List

class WordPressClient:
    """Client for interacting with WordPress REST API."""
    
    def __init__(self, site_url: str, username: str, app_password: str, logger: logging.Logger):
        """
        Initialize the WordPress API client.
        
        Args:
            site_url: WordPress site URL
            username: WordPress username
            app_password: WordPress application password
            logger: Logger instance
        """
        self.api_url = f"{site_url}/wp-json/wp/v2"
        self.auth = (username, app_password)
        self.logger = logger
    
    def publish_post(self, title: str, content: str, excerpt: str = "", 
                     category_id: Optional[int] = None, status: str = "draft") -> Dict[str, Any]:
        """
        Publish a post to WordPress.
        
        Args:
            title: Post title
            content: Post content in HTML format
            excerpt: Post excerpt (used as meta description)
            category_id: Category ID (optional)
            status: Post status ('draft', 'publish', etc.)
            
        Returns:
            Response from WordPress API
            
        Raises:
            ConnectionError: If connection to WordPress fails
            Exception: For other errors
        """
        self.logger.info(f"Publicando artigo no WordPress: {title}")
        
        # Prepare post data
        post_data = {
            "title": title,
            "content": content,
            "status": status,
            "excerpt": excerpt,
            "comment_status": "open"
        }
        
        # Add category if provided
        if category_id:
            post_data["categories"] = [category_id]
        
        try:
            # Send post to WordPress
            response = requests.post(
                f"{self.api_url}/posts",
                json=post_data,
                auth=self.auth
            )
            
            response.raise_for_status()  # Raise exception for bad status codes
            
            post_data = response.json()
            self.logger.info(f"Artigo publicado com sucesso! ID: {post_data['id']}")
            return post_data
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Erro HTTP ao publicar artigo: {e.response.status_code} - {e.response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Erro de conexão ao publicar artigo: {str(e)}"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)
            
        except Exception as e:
            error_msg = f"Erro inesperado ao publicar artigo: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_category_id(self, category_name: str) -> Optional[int]:
        """
        Get category ID by name, creating it if it doesn't exist.
        
        Args:
            category_name: Category name
            
        Returns:
            Category ID or None if failed
        """
        try:
            # First try to find the category
            response = requests.get(
                f"{self.api_url}/categories",
                params={"search": category_name},
                auth=self.auth
            )
            
            response.raise_for_status()
            
            categories = response.json()
            for category in categories:
                if category["name"].lower() == category_name.lower():
                    self.logger.info(f"Categoria '{category_name}' encontrada com ID: {category['id']}")
                    return category["id"]
                    
            # If not found, create it
            return self._create_category(category_name)
                
        except Exception as e:
            self.logger.error(f"Erro ao buscar categoria: {str(e)}")
            return None
    
    def _create_category(self, category_name: str) -> Optional[int]:
        """
        Create a new category in WordPress.
        
        Args:
            category_name: Category name
            
        Returns:
            New category ID or None if failed
        """
        try:
            response = requests.post(
                f"{self.api_url}/categories",
                json={"name": category_name},
                auth=self.auth
            )
            
            response.raise_for_status()
            
            category_data = response.json()
            self.logger.info(f"Categoria '{category_name}' criada com ID: {category_data['id']}")
            return category_data["id"]
                
        except Exception as e:
            self.logger.error(f"Erro ao criar categoria: {str(e)}")
            return None
    
    def get_posts(self, per_page: int = 10, page: int = 1) -> List[Dict[str, Any]]:
        """
        Get posts from WordPress.
        
        Args:
            per_page: Number of posts per page
            page: Page number
            
        Returns:
            List of posts
        """
        try:
            response = requests.get(
                f"{self.api_url}/posts",
                params={"per_page": per_page, "page": page},
                auth=self.auth
            )
            
            response.raise_for_status()
            return response.json()
                
        except Exception as e:
            self.logger.error(f"Erro ao obter posts: {str(e)}")
            return []